from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
import logging
import os
import uuid

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")
mongo_client = AsyncIOMotorClient(os.environ["MONGO_URL"])
db = mongo_client[os.environ["DB_NAME"]]
uploads_dir = ROOT_DIR / "uploads"
uploads_dir.mkdir(exist_ok=True)

app = FastAPI(title="KasFlow API")
api = APIRouter(prefix="/api")

class TransactionCreate(BaseModel):
    transaction_type: str = Field(pattern="^(cash_in|cash_out)$")
    amount: float = Field(gt=0)
    purpose: str = Field(min_length=1, max_length=120)
    note: Optional[str] = Field(default="", max_length=500)
    transaction_date: str
    evidence_url: Optional[str] = None

class Transaction(TransactionCreate):
    id: str
    created_at: str

def clean(doc: dict) -> dict:
    doc.pop("_id", None)
    return doc

@api.get("/")
async def root():
    return {"message": "KasFlow API aktif"}

@api.get("/transactions", response_model=List[Transaction])
async def list_transactions():
    docs = await db.transactions.find({}, {"_id": 0}).sort([("transaction_date", -1), ("created_at", -1)]).to_list(1000)
    return [clean(doc) for doc in docs]

@api.post("/transactions", response_model=Transaction)
async def create_transaction(payload: TransactionCreate):
    if payload.transaction_type not in {"cash_in", "cash_out"}:
        raise HTTPException(400, "Tipe transaksi tidak valid")
    transaction = Transaction(id=str(uuid.uuid4()), created_at=datetime.now(timezone.utc).isoformat(), **payload.model_dump())
    doc = transaction.model_dump()
    await db.transactions.insert_one(doc)
    return transaction

@api.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str):
    result = await db.transactions.delete_one({"id": transaction_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Transaksi tidak ditemukan")
    return {"message": "Transaksi dihapus", "id": transaction_id}

@api.post("/evidence")
async def upload_evidence(file: UploadFile = File(...)):
    allowed = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
    if file.content_type not in allowed:
        raise HTTPException(400, "Format bukti harus JPG, PNG, WEBP, atau PDF")
    suffix = Path(file.filename or "evidence").suffix.lower() or ".bin"
    filename = f"{uuid.uuid4()}{suffix}"
    (uploads_dir / filename).write_bytes(await file.read())
    return {"url": f"/uploads/{filename}", "filename": file.filename}

app.include_router(api)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
app.add_middleware(CORSMiddleware, allow_credentials=True, allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","), allow_methods=["*"], allow_headers=["*"])

@app.on_event("shutdown")
async def shutdown():
    mongo_client.close()

logging.basicConfig(level=logging.INFO)