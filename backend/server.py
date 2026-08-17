from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
import logging
import os
import uuid

from bson import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")
mongo_client = AsyncIOMotorClient(os.environ["MONGO_URL"])
db = mongo_client[os.environ["DB_NAME"]]
evidence_bucket = AsyncIOMotorGridFSBucket(db, bucket_name="evidence")

app = FastAPI(title="KasFlow API")
api = APIRouter(prefix="/api")

ALLOWED_EVIDENCE_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}

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
    await db.transactions.insert_one(transaction.model_dump())
    return transaction

@api.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str):
    doc = await db.transactions.find_one({"id": transaction_id})
    if not doc:
        raise HTTPException(404, "Transaksi tidak ditemukan")
    evidence_url = doc.get("evidence_url") or ""
    if evidence_url.startswith("/api/evidence/"):
        file_id = evidence_url.rsplit("/", 1)[-1]
        try:
            await evidence_bucket.delete(ObjectId(file_id))
        except Exception:
            logging.warning("Gagal hapus bukti GridFS %s", file_id)
    await db.transactions.delete_one({"id": transaction_id})
    return {"message": "Transaksi dihapus", "id": transaction_id}

@api.post("/evidence")
async def upload_evidence(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_EVIDENCE_TYPES:
        raise HTTPException(400, "Format bukti harus JPG, PNG, WEBP, atau PDF")
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(400, "Ukuran bukti maksimal 10 MB")
    file_id = await evidence_bucket.upload_from_stream(
        file.filename or "evidence",
        contents,
        metadata={"content_type": file.content_type, "uploaded_at": datetime.now(timezone.utc).isoformat()},
    )
    return {"url": f"/api/evidence/{file_id}", "filename": file.filename}

@api.get("/evidence/{file_id}")
async def get_evidence(file_id: str):
    try:
        object_id = ObjectId(file_id)
    except Exception:
        raise HTTPException(400, "ID bukti tidak valid")
    try:
        stream = await evidence_bucket.open_download_stream(object_id)
    except Exception:
        raise HTTPException(404, "Bukti tidak ditemukan")
    content_type = (stream.metadata or {}).get("content_type", "application/octet-stream")
    async def iterator():
        while True:
            chunk = await stream.readchunk()
            if not chunk:
                break
            yield chunk
    headers = {"Content-Disposition": f'inline; filename="{stream.filename}"'}
    return StreamingResponse(iterator(), media_type=content_type, headers=headers)

app.include_router(api)
app.add_middleware(CORSMiddleware, allow_credentials=True, allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","), allow_methods=["*"], allow_headers=["*"])

@app.on_event("shutdown")
async def shutdown():
    mongo_client.close()

logging.basicConfig(level=logging.INFO)
