# Product Overview

**RFPGL API** is a finance and accounting backend for **Agung Sedayu Innovation**. It manages the full lifecycle of Request For Payment (RFP) documents, general ledger journals, and financial reporting for a property/land acquisition business.

## Core Domains

- **RFP (Request for Payment)** — Create, approve, void, and track payment requests through a multi-step workflow. Supports manual (bidang/land parcel) and auto-generated RFPs, kasbon (advances), and government tax payments.
- **General Ledger / Journal** — Create, post, edit (with approval), void, and close accounting periods. Journals link to RFP documents and support ASI (intercompany) entries.
- **Financial Reporting** — Trial balance, laporan keuangan (Neraca, Laba Rugi, Cashflow), GL mutation, bidang cost reports, and bank summaries. Reports are generated as Excel or PDF files using PostgreSQL stored functions.
- **Workflow** — Multi-step approval workflow for RFPs and journals, integrated with an external OAuth service. Triggered via Google Cloud Tasks.
- **Masters** — COA, bank, company, customer, worker, project, section, activity, bidang, currency, document type, entry type, and more.

## Integration Points

- **Landrope (client system)** — External API called to validate bidang (land parcels), check komponen biaya, and receive RFP creation from memo/pajak sources.
- **OAuth2 service** — External token validation for user and client authentication.
- **Google Cloud Tasks** — Async task queue for workflow consumption and RFP notifications.
- **Google Cloud Pub/Sub** — Subscribe endpoint for event-driven integrations.

## API Prefix

All routes are served under `/rfpgl/`:
- `/rfpgl/public/api` — Authenticated user routes (role: `RFPGL_USER`)
- `/rfpgl/client/api` — Client system routes (role: `RFPGL_CLIENT`)
- `/rfpgl/workflow/api` — Workflow consumption (no auth middleware, internal)
- `/rfpgl/cloud-tasks/api` — Cloud Task callbacks (validated by shared token)
- `/rfpgl/pubsub/api` — Pub/Sub subscriber endpoint
