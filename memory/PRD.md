# KasFlow PRD

## Original problem statement
Aplikasi web based + PWA untuk personal cash tracker dengan cash in, cash out, balance, purpose, optional evidence upload, form entry, AI parsing in a later phase, Excel report, and a free database.

## Architecture decisions
- React frontend with mobile-first responsive PWA manifest
- FastAPI backend on port 8001 with MongoDB using existing MONGO_URL and DB_NAME
- Single-user MVP without authentication
- Evidence files uploaded to backend storage; transaction metadata stored in MongoDB

## User personas
- Pemilik/pengguna pribadi yang ingin mencatat arus kas dengan cepat dari ponsel

## Core requirements (static)
- Dashboard balance, cash in, cash out
- Transaction form with amount, type, purpose, date, note, optional evidence
- Recent transactions, filters, delete, Excel export
- PWA-ready mobile experience
- Future natural-language entry with GPT 5.6 Luna

## What is implemented (2026-08-17)
- KasFlow dark organic FinTech dashboard with responsive mobile layout
- Transaction CRUD/list APIs and evidence upload endpoint
- Excel .xlsx export, filters, totals, toasts, modal form, and PWA manifest
- No AI integration yet by design; form-first MVP

## Prioritized backlog
P0: Add AI natural-language transaction parser and confirmation flow
P1: Add installable service worker/offline queue and evidence cloud storage
P1: Add date range and purpose filters plus charts
P2: Add optional authentication and multi-device sync

## Next tasks list
- Integrate GPT 5.6 Luna after user confirms AI budget/key flow
- Add report date range and purpose grouping
- Improve offline-first PWA behavior for Android
