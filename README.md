# CrediScope — CSV Login + Credit Default Prediction

This version authenticates customers against your private `Credentials.csv`, retrieves the customer's financial row by matching `ID`, predicts default risk, and stores prediction history in MongoDB.

## Folder setup

Copy your own `Credentials.csv` into:

`ml-service/data/Credentials.csv`

The file must contain `ID`, `EMAIL`, `PASSWORD`, `NAME`, `CARD_NO`, and `ACCOUNT_NO` columns (extra columns are ignored). The supplied ZIP intentionally does **not** contain the private credentials file. The credit default dataset and trained model are included.

The backend reads only `ID`, `EMAIL`, `PASSWORD`, and `NAME`. It does not return passwords, card numbers, or account numbers. Customer access is restricted to the ID associated with the authenticated login.

## 1. Configure backend

```powershell
cd ml-service
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `ml-service/.env` and set a strong `TOKEN_SECRET`. Set `MONGODB_URI` and `MONGODB_DB` for MongoDB Atlas or local MongoDB. Keep `.env` private.

## 2. Start FastAPI

```powershell
uvicorn main:app --reload --port 8000
```

Check `http://localhost:8000/health`. Expected flags: `model_loaded`, `credentials_loaded`, and `dataset_loaded` should be `true`. `mongodb_connected` should be `true` if you configured MongoDB.

## 3. Start Next.js

Open a second terminal:

```powershell
cd frontend
npm install
Copy-Item .env.local.example .env.local
npm run dev
```

Open `http://localhost:3000/login` and sign in using the email/password from your `Credentials.csv`.

## How it works

1. FastAPI checks the email/password against `Credentials.csv`.
2. It issues a signed 24-hour bearer token containing the customer's ID.
3. The dashboard's prediction page retrieves that customer's row from `credit_default.csv` using the ID.
4. The model receives only the 22 configured features. `ID` and `dpnm` are excluded from model inputs; `dpnm` is shown separately only as the historical label for retrospective evaluation.
5. Prediction history is stored in MongoDB and scoped to the authenticated customer ID.

## API

- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /health`
- `GET /api/metrics`
- `GET /api/customers/me`
- `GET /api/customers/{customer_id}` (only the signed-in customer's own ID)
- `GET /api/predict/by-id/{customer_id}` (only the signed-in customer's own ID)
- `GET /api/history`
- `GET /api/summary`

## Security and limitations

This is an educational demo using a supplied credentials dataset. The CSV contains plaintext demo passwords, so keep it local, restrict access to it, and never commit or upload it. For production, migrate to a proper identity provider or a database with Argon2id/bcrypt password hashes, HTTPS, rate limiting, secure HttpOnly cookies, audit logging and a privacy/security review. The API computes a SHA-256 digest of each supplied password for constant-time comparison; this is not a substitute for production password storage.

The credit dataset is historical. A prediction for one of its existing IDs is a retrospective demonstration, not a forecast of future default or a real lending decision.
