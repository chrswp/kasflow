"""KasFlow backend API tests - transactions + GridFS evidence"""
import io
import os
import struct
import zlib

import pytest
import requests

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/") if "REACT_APP_BACKEND_URL" in os.environ else None
if not BASE_URL:
    # Load from frontend/.env
    from pathlib import Path
    for line in Path("/app/frontend/.env").read_text().splitlines():
        if line.startswith("REACT_APP_BACKEND_URL="):
            BASE_URL = line.split("=", 1)[1].strip().rstrip("/")
            break

API = f"{BASE_URL}/api"


def _png_bytes() -> bytes:
    """Generate a minimal valid 1x1 PNG."""
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    raw = b"\x00\xff\x00\x00"
    idat = zlib.compress(raw)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


# --- Health ---
def test_root():
    r = requests.get(f"{API}/")
    assert r.status_code == 200
    assert r.json() == {"message": "KasFlow API aktif"}


# --- Transactions listing ---
def test_list_transactions_returns_list():
    r = requests.get(f"{API}/transactions")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# --- Create cash_in ---
def test_create_transaction_cash_in():
    payload = {
        "transaction_type": "cash_in",
        "amount": 15000.5,
        "purpose": "TEST_donation",
        "note": "unit test",
        "transaction_date": "2026-01-15",
    }
    r = requests.post(f"{API}/transactions", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["transaction_type"] == "cash_in"
    assert data["amount"] == 15000.5
    assert data["purpose"] == "TEST_donation"
    assert "id" in data and data["id"]
    assert "created_at" in data and data["created_at"]

    # GET verify persistence
    g = requests.get(f"{API}/transactions").json()
    assert any(t["id"] == data["id"] for t in g)

    # cleanup
    requests.delete(f"{API}/transactions/{data['id']}")


# --- Create cash_out ---
def test_create_transaction_cash_out():
    payload = {
        "transaction_type": "cash_out",
        "amount": 2500,
        "purpose": "TEST_office_supplies",
        "note": "",
        "transaction_date": "2026-01-16",
    }
    r = requests.post(f"{API}/transactions", json=payload)
    assert r.status_code == 200, r.text
    tid = r.json()["id"]
    requests.delete(f"{API}/transactions/{tid}")


# --- Invalid transaction_type ---
def test_create_transaction_invalid_type():
    payload = {
        "transaction_type": "invalid_kind",
        "amount": 100,
        "purpose": "TEST_bad",
        "transaction_date": "2026-01-15",
    }
    r = requests.post(f"{API}/transactions", json=payload)
    assert r.status_code in (400, 422), r.text


# --- Evidence upload PNG ---
def test_upload_evidence_png():
    files = {"file": ("test.png", _png_bytes(), "image/png")}
    r = requests.post(f"{API}/evidence", files=files)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["url"].startswith("/api/evidence/")
    assert data["filename"] == "test.png"


# --- Evidence reject bad content type ---
def test_upload_evidence_invalid_type():
    files = {"file": ("bad.txt", b"hello world", "text/plain")}
    r = requests.post(f"{API}/evidence", files=files)
    assert r.status_code == 400


# --- Evidence GET streams back file ---
def test_get_evidence_streams_content():
    png = _png_bytes()
    files = {"file": ("get.png", png, "image/png")}
    up = requests.post(f"{API}/evidence", files=files).json()
    file_id = up["url"].rsplit("/", 1)[-1]

    r = requests.get(f"{API}{up['url'].replace('/api','')}")
    # correct fetch:
    r = requests.get(f"{BASE_URL}{up['url']}")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("image/png")
    assert r.content == png


# --- Evidence invalid id ---
def test_get_evidence_invalid_objectid():
    r = requests.get(f"{API}/evidence/not-a-valid-id")
    assert r.status_code == 400


# --- Delete transaction cascades GridFS ---
def test_delete_transaction_cascades_evidence():
    # upload evidence
    files = {"file": ("cascade.png", _png_bytes(), "image/png")}
    up = requests.post(f"{API}/evidence", files=files).json()
    evidence_url = up["url"]
    file_id = evidence_url.rsplit("/", 1)[-1]

    # confirm evidence exists
    assert requests.get(f"{BASE_URL}{evidence_url}").status_code == 200

    # create transaction linking evidence
    payload = {
        "transaction_type": "cash_out",
        "amount": 500,
        "purpose": "TEST_cascade",
        "transaction_date": "2026-01-17",
        "evidence_url": evidence_url,
    }
    tx = requests.post(f"{API}/transactions", json=payload).json()
    tid = tx["id"]

    # delete transaction
    d = requests.delete(f"{API}/transactions/{tid}")
    assert d.status_code == 200

    # transaction gone
    g = requests.get(f"{API}/transactions").json()
    assert not any(t["id"] == tid for t in g)

    # evidence gone (404)
    r = requests.get(f"{BASE_URL}{evidence_url}")
    assert r.status_code == 404, f"expected cascade delete, got {r.status_code}"


# --- Delete nonexistent transaction ---
def test_delete_nonexistent_transaction():
    r = requests.delete(f"{API}/transactions/nonexistent-uuid-12345")
    assert r.status_code == 404
