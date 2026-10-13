import pickle
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from database import (
    init_db, save_scan, save_report,
    get_recent_scans, get_stats
)

# ---------------------------------------------------------------
# 1. ABSOLUTE PATHS
# ---------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "sms_scam_model.pkl"

# ---------------------------------------------------------------
# 2. SETUP
# ---------------------------------------------------------------
init_db()

with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

app = FastAPI(title="SMS Scam Detector")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# ---------------------------------------------------------------
# 3. REQUEST MODELS
# ---------------------------------------------------------------
class ScanRequest(BaseModel):
    message: str

class ReportRequest(BaseModel):
    scan_id: int
    feedback: str
    comment: str = ""


# ---------------------------------------------------------------
# 4. CORE PREDICTION HELPER
# ---------------------------------------------------------------
def predict_and_save(message: str, source: str = 'web'):
    prediction = model.predict([message])[0]
    proba = model.predict_proba([message])[0]
    confidence = float(proba[prediction])

    scan_id = save_scan(message, int(prediction), confidence, source)

    return {
        'scan_id': scan_id,
        'message': message,
        'prediction': int(prediction),
        'label': 'FRAUD' if prediction == 1 else 'NORMAL',
        'confidence': confidence,
        'probability_fraud': float(proba[1]),
        'probability_normal': float(proba[0]),
    }


# ---------------------------------------------------------------
# 5. HTML PAGE
# ---------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    recent = get_recent_scans(limit=8)
    stats = get_stats()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "recent": recent,
            "stats": stats,
        }
    )


# ---------------------------------------------------------------
# 6. API ENDPOINTS
# ---------------------------------------------------------------
@app.post("/api/scan")
async def api_scan(payload: ScanRequest):
    msg = payload.message.strip()
    if not msg:
        return JSONResponse({'error': 'Empty message'}, status_code=400)

    result = predict_and_save(msg, source='web')
    return result


@app.post("/api/report")
async def api_report(payload: ReportRequest):
    if payload.feedback not in ('correct', 'wrong'):
        return JSONResponse(
            {'error': "feedback must be 'correct' or 'wrong'"},
            status_code=400
        )
    save_report(payload.scan_id, payload.feedback, payload.comment)
    return {'status': 'ok', 'scan_id': payload.scan_id}


@app.get("/api/recent")
async def api_recent(limit: int = 10):
    return {'scans': get_recent_scans(limit=limit)}


@app.get("/api/stats")
async def api_stats():
    return get_stats()


# ---------------------------------------------------------------
# 7. RUN DIRECTLY
# ---------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)