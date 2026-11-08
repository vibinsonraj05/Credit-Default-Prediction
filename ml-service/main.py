from pathlib import Path
from datetime import datetime, timezone
import os, json, time, base64, hashlib, hmac

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

try:
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
except ImportError:
    MongoClient = None
    PyMongoError = Exception

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
load_dotenv(BASE / ".env")

MODEL_PATH = BASE / "model" / "default_model.joblib"
METRICS_PATH = BASE / "model" / "metrics.json"
CREDENTIALS_PATH = DATA_DIR / "Credentials.csv"
CREDIT_DATA_PATH = DATA_DIR / "credit_default.csv"

MONGODB_URI = os.getenv("MONGODB_URI", "")
MONGODB_DB = os.getenv("MONGODB_DB", "credit_default_db")
TOKEN_SECRET = os.getenv("TOKEN_SECRET", "")
TOKEN_EXPIRY = 86400

FEATURES = [
    "LIMIT_BAL", "EDUCATION", "MARRIAGE", "AGE",
    "PAY_1", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
    "BILL_AMT1", "BILL_AMT2", "BILL_AMT3", "BILL_AMT4", "BILL_AMT5", "BILL_AMT6",
    "PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6",
]

app = FastAPI(
    title="CrediScope - Credit Default Prediction API",
    description="CSV customer authentication, ML default-risk prediction and MongoDB history.",
    version="2.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if x.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)
model_artifact = None
mongo_client = None
predictions_collection = None
customer_data = None
login_credentials = {}


class LoginInput(BaseModel):
    email: str = Field(..., min_length=5, max_length=254)
    password: str = Field(..., min_length=1, max_length=128)


class CustomerInput(BaseModel):
    LIMIT_BAL: float = Field(..., ge=0)
    EDUCATION: int = Field(..., ge=0, le=6)
    MARRIAGE: int = Field(..., ge=0, le=3)
    AGE: int = Field(..., ge=18, le=100)
    PAY_1: int
    PAY_2: int
    PAY_3: int
    PAY_4: int
    PAY_5: int
    PAY_6: int
    BILL_AMT1: float
    BILL_AMT2: float
    BILL_AMT3: float
    BILL_AMT4: float
    BILL_AMT5: float
    BILL_AMT6: float
    PAY_AMT1: float = Field(..., ge=0)
    PAY_AMT2: float = Field(..., ge=0)
    PAY_AMT3: float = Field(..., ge=0)
    PAY_AMT4: float = Field(..., ge=0)
    PAY_AMT5: float = Field(..., ge=0)
    PAY_AMT6: float = Field(..., ge=0)


def password_digest(password: str) -> str:
    # The source CSV contains generated/demo credentials. Store only a SHA-256
    # digest in process memory, never return or persist the source password.
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def load_login_credentials():
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            f"Missing {CREDENTIALS_PATH}. Copy your Credentials.csv into ml-service/data/."
        )
    df = pd.read_csv(
        CREDENTIALS_PATH,
        usecols=["ID", "EMAIL", "PASSWORD", "NAME"],
        dtype={"EMAIL": "string", "PASSWORD": "string", "NAME": "string"},
        keep_default_na=False,
    )
    df["ID"] = pd.to_numeric(df["ID"], errors="raise").astype("int64")
    df["EMAIL"] = df["EMAIL"].str.strip().str.lower()
    if df["EMAIL"].duplicated().any():
        raise ValueError("Duplicate email addresses found in Credentials.csv")
    accounts = {}
    for row in df.itertuples(index=False):
        email = str(row.EMAIL)
        password = str(row.PASSWORD)
        if email and password:
            accounts[email] = {
                "id": str(int(row.ID)),
                "name": str(row.NAME),
                "password_digest": password_digest(password),
            }
    if not accounts:
        raise ValueError("No valid customer login records found")
    return accounts


def load_customer_dataset():
    if not CREDIT_DATA_PATH.exists():
        raise FileNotFoundError(f"Missing credit dataset: {CREDIT_DATA_PATH}")
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(f"Missing credentials dataset: {CREDENTIALS_PATH}")

    # Read only ID and NAME from the customer file for the dataset join.
    names = pd.read_csv(CREDENTIALS_PATH, usecols=["ID", "NAME"])
    credit = pd.read_csv(CREDIT_DATA_PATH)
    required = ["ID", "dpnm", *FEATURES]
    missing = [c for c in required if c not in credit.columns]
    if missing:
        raise ValueError(f"Credit dataset is missing columns: {missing}")
    names["ID"] = pd.to_numeric(names["ID"], errors="raise").astype("int64")
    credit["ID"] = pd.to_numeric(credit["ID"], errors="raise").astype("int64")
    if names["ID"].duplicated().any() or credit["ID"].duplicated().any():
        raise ValueError("Duplicate customer IDs found in one of the datasets")
    merged = credit.merge(names, on="ID", how="inner", validate="one_to_one")
    if merged.empty:
        raise ValueError("No matching customer IDs between the two CSV files")
    if merged[FEATURES].isna().any().any():
        raise ValueError("Missing values found in model features")
    return merged


def make_token(user_id: str, email: str, name: str) -> str:
    if not TOKEN_SECRET:
        raise HTTPException(503, "TOKEN_SECRET is not configured in ml-service/.env")
    payload = {
        "sub": user_id,
        "email": email,
        "name": name,
        "exp": int(time.time()) + TOKEN_EXPIRY,
    }
    encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    signature = hmac.new(TOKEN_SECRET.encode(), encoded.encode(), hashlib.sha256).hexdigest()
    return encoded + "." + signature


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)):
    if not credentials:
        raise HTTPException(401, "Please log in to continue")
    if not TOKEN_SECRET:
        raise HTTPException(503, "TOKEN_SECRET is not configured")
    try:
        payload, signature = credentials.credentials.split(".")
        expected = hmac.new(TOKEN_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError("Invalid signature")
        decoded = base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))
        data = json.loads(decoded)
        if int(data["exp"]) < int(time.time()):
            raise ValueError("Expired token")
        return {"id": str(data["sub"]), "email": data["email"], "name": data.get("name", "Customer")}
    except Exception:
        raise HTTPException(401, "Session expired. Please log in again")


@app.on_event("startup")
def startup():
    global model_artifact, mongo_client, predictions_collection, customer_data, login_credentials

    if MODEL_PATH.exists():
        model_artifact = joblib.load(MODEL_PATH)
        print("ML model loaded")
    else:
        print(f"WARNING: Model file not found: {MODEL_PATH}")

    try:
        login_credentials = load_login_credentials()
        customer_data = load_customer_dataset()
        print(f"Loaded {len(login_credentials)} login accounts and {len(customer_data)} customer rows")
    except Exception as exc:
        login_credentials = {}
        customer_data = None
        print(f"Customer CSV loading failed: {exc}")

    if not MONGODB_URI:
        print("MONGODB_URI is not configured; prediction history will not persist")
        return
    if MongoClient is None:
        print("pymongo is not installed")
        return
    try:
        mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        mongo_client.admin.command("ping")
        db = mongo_client[MONGODB_DB]
        predictions_collection = db["predictions"]
        predictions_collection.create_index([("user_id", 1), ("created_at", -1)])
        print("MongoDB connected")
    except Exception as exc:
        mongo_client = None
        predictions_collection = None
        print(f"MongoDB connection failed: {exc}")


@app.post("/api/auth/login")
def login(body: LoginInput):
    if not login_credentials:
        raise HTTPException(503, "Customer credentials are not loaded. Check Credentials.csv path and backend logs.")
    email = body.email.strip().lower()
    account = login_credentials.get(email)
    supplied_digest = password_digest(body.password)
    if account is None or not hmac.compare_digest(supplied_digest, account["password_digest"]):
        raise HTTPException(401, "Incorrect email or password")
    token = make_token(account["id"], email, account["name"])
    return {
        "token": token,
        "user": {"id": account["id"], "name": account["name"], "email": email},
    }


@app.get("/api/auth/me")
def me(user=Depends(current_user)):
    return {"user": user}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model_artifact is not None,
        "mongodb_connected": predictions_collection is not None,
        "credentials_loaded": bool(login_credentials),
        "dataset_loaded": customer_data is not None,
        "total_customers": len(customer_data) if customer_data is not None else 0,
    }


@app.get("/api/metrics")
def metrics():
    if not METRICS_PATH.exists():
        raise HTTPException(503, "Model metrics not found. Run python train.py")
    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))


def get_prediction(X: pd.DataFrame):
    if model_artifact is None:
        raise HTTPException(503, "ML model is not loaded. Run python train.py")
    probability = float(model_artifact["pipeline"].predict_proba(X[FEATURES])[0, 1])
    threshold = float(model_artifact.get("threshold", 0.5))
    prediction = int(probability >= threshold)
    return {
        "prediction": prediction,
        "label": "Likely to default" if prediction else "No default predicted",
        "probability": round(probability, 4),
        "risk": "High" if probability >= 0.65 else "Moderate" if probability >= 0.35 else "Low",
        "threshold": threshold,
        "model": model_artifact.get("model_name", "Selected model"),
    }


def find_customer(customer_id: int, user: dict):
    if customer_data is None:
        raise HTTPException(503, "Customer dataset is not loaded. Check CSV files.")
    # A login maps to exactly one customer ID; do not permit cross-customer lookup.
    if str(customer_id) != str(user["id"]):
        raise HTTPException(403, "You can only access the customer record linked to your login")
    matches = customer_data[customer_data["ID"] == customer_id]
    if matches.empty:
        raise HTTPException(404, "Customer ID not found in credit dataset")
    return matches.iloc[0]


@app.get("/api/customers/me")
def customer_me(user=Depends(current_user)):
    row = find_customer(int(user["id"]), user)
    return {
        "customer_id": int(row["ID"]),
        "customer_name": str(row["NAME"]),
        "credit_limit": float(row["LIMIT_BAL"]),
        "age": int(row["AGE"]),
        "education": int(row["EDUCATION"]),
        "marriage": int(row["MARRIAGE"]),
    }


@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: int, user=Depends(current_user)):
    row = find_customer(customer_id, user)
    return {
        "customer_id": int(row["ID"]),
        "customer_name": str(row["NAME"]),
        "credit_limit": float(row["LIMIT_BAL"]),
        "age": int(row["AGE"]),
        "education": int(row["EDUCATION"]),
        "marriage": int(row["MARRIAGE"]),
    }


@app.get("/api/predict/by-id/{customer_id}")
def predict_by_id(customer_id: int, user=Depends(current_user)):
    row = find_customer(customer_id, user)
    X = pd.DataFrame([[row[col] for col in FEATURES]], columns=FEATURES)
    result = get_prediction(X)
    result.update({
        "customer_id": int(row["ID"]),
        "customer_name": str(row["NAME"]),
        "credit_limit": float(row["LIMIT_BAL"]),
        "age": int(row["AGE"]),
        "prediction_type": "customer_id",
        # This is the historical label for retrospective evaluation only.
        "historical_actual_default": int(row["dpnm"]),
    })
    if predictions_collection is not None:
        try:
            saved = predictions_collection.insert_one({
                "user_id": user["id"],
                "user_email": user["email"],
                "prediction_type": "customer_id",
                "customer_id": int(row["ID"]),
                "customer_name": str(row["NAME"]),
                "result": result,
                "created_at": datetime.now(timezone.utc),
            })
            result["id"] = str(saved.inserted_id)
        except PyMongoError as exc:
            print(f"Prediction history save failed: {exc}")
    return result


@app.post("/api/predict")
def predict_manual(customer: CustomerInput, user=Depends(current_user)):
    X = pd.DataFrame([[getattr(customer, f) for f in FEATURES]], columns=FEATURES)
    result = get_prediction(X)
    if predictions_collection is not None:
        try:
            saved = predictions_collection.insert_one({
                "user_id": user["id"],
                "user_email": user["email"],
                "prediction_type": "manual",
                "result": result,
                "created_at": datetime.now(timezone.utc),
            })
            result["id"] = str(saved.inserted_id)
        except PyMongoError as exc:
            print(f"Prediction history save failed: {exc}")
    return result


@app.get("/api/history")
def history(limit: int = 50, user=Depends(current_user)):
    if predictions_collection is None:
        return {"items": [], "database_connected": False}
    docs = list(predictions_collection.find(
        {"user_id": user["id"]},
        {"_id": 1, "result": 1, "customer_id": 1, "customer_name": 1, "prediction_type": 1, "created_at": 1},
    ).sort("created_at", -1).limit(min(max(limit, 1), 100)))
    for doc in docs:
        doc["id"] = str(doc.pop("_id"))
        doc["created_at"] = doc["created_at"].isoformat()
    return {"items": docs, "database_connected": True}


@app.get("/api/summary")
def summary(user=Depends(current_user)):
    if predictions_collection is None:
        return {"total_predictions": 0, "default_predictions": 0, "no_default_predictions": 0, "database_connected": False}
    query = {"user_id": user["id"]}
    total = predictions_collection.count_documents(query)
    defaults = predictions_collection.count_documents({**query, "result.prediction": 1})
    return {
        "total_predictions": total,
        "default_predictions": defaults,
        "no_default_predictions": total - defaults,
        "database_connected": True,
    }


@app.get("/")
def root():
    return {"application": "CrediScope", "message": "Credit Default Prediction API is running", "docs": "/docs"}
