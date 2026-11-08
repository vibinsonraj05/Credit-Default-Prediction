from pathlib import Path
import json
import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier, GradientBoostingClassifier

BASE = Path(__file__).resolve().parent
DATA_PATH = BASE / "data" / "credit_default.csv"
MODEL_DIR = BASE / "model"
MODEL_DIR.mkdir(exist_ok=True)
TARGET = "dpnm"
# ID is a record identifier; SEX is excluded to avoid using a protected attribute.
FEATURES = ["LIMIT_BAL", "EDUCATION", "MARRIAGE", "AGE",
            "PAY_1", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
            "BILL_AMT1", "BILL_AMT2", "BILL_AMT3", "BILL_AMT4", "BILL_AMT5", "BILL_AMT6",
            "PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6"]
CATEGORICAL = ["EDUCATION", "MARRIAGE", "PAY_1", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
NUMERIC = [c for c in FEATURES if c not in CATEGORICAL]


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH, encoding="latin1")
    # Normalize common whitespace/BOM issues without silently guessing the target.
    df.columns = [str(c).strip().replace("\ufeff", "") for c in df.columns]
    if TARGET not in df.columns:
        raise ValueError(f"Target column '{TARGET}' not found. Available columns: {list(df.columns)}")
    missing = [c for c in FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected feature columns: {missing}")
    df = df[FEATURES + [TARGET]].dropna(subset=[TARGET])
    X = df[FEATURES].apply(pd.to_numeric, errors="coerce")
    y = pd.to_numeric(df[TARGET], errors="coerce").astype(int)
    if not set(y.unique()).issubset({0, 1}):
        raise ValueError("Target dpnm must contain only 0 and 1.")

    preprocessor = ColumnTransformer([
        ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), NUMERIC),
        ("categorical", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                                  ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), CATEGORICAL),
    ])
    models = {
        "Logistic Regression": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=350, min_samples_leaf=2, class_weight="balanced_subsample", n_jobs=-1, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=180, learning_rate=0.05, max_depth=2, random_state=42),
        "HistGradientBoosting": HistGradientBoostingClassifier(max_iter=180, learning_rate=0.08, l2_regularization=1.0, random_state=42),
    }
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    results = []
    fitted = {}
    for name, estimator in models.items():
        pipe = Pipeline([("preprocess", preprocessor), ("model", estimator)])
        pipe.fit(X_train, y_train)
        probs = pipe.predict_proba(X_test)[:, 1]
        preds = (probs >= 0.5).astype(int)
        metrics = {
            "model": name,
            "accuracy": round(float(accuracy_score(y_test, preds)), 4),
            "precision": round(float(precision_score(y_test, preds, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, preds, zero_division=0)), 4),
            "f1": round(float(f1_score(y_test, preds, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y_test, probs)), 4),
            "confusion_matrix": confusion_matrix(y_test, preds).tolist(),
        }
        results.append(metrics)
        fitted[name] = pipe
        print(f"{name}: AUC={metrics['roc_auc']:.4f}, F1={metrics['f1']:.4f}, recall={metrics['recall']:.4f}")

    results.sort(key=lambda r: r["roc_auc"], reverse=True)
    best_name = results[0]["model"]
    artifact = {"pipeline": fitted[best_name], "model_name": best_name, "features": FEATURES,
                "target": TARGET, "threshold": 0.5}
    joblib.dump(artifact, MODEL_DIR / "default_model.joblib")
    metadata = {"dataset_rows": int(len(df)), "feature_count": len(FEATURES),
                "default_rate": round(float(y.mean()), 4), "target": TARGET,
                "excluded_columns": ["ID", "SEX"], "best_model": best_name,
                "models": results, "train_rows": len(X_train), "test_rows": len(X_test)}
    (MODEL_DIR / "metrics.json").write_text(json.dumps(metadata, indent=2))
    print(f"\nSaved best model: {best_name}")
    print(f"Metrics: {MODEL_DIR / 'metrics.json'}")

if __name__ == "__main__":
    main()
