# 👁 Bitespeed Identity Reconciliation

> A backend service that links different contact identities (emails & phone numbers) to the same person — built for the Bitespeed Backend Engineering Task.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)](https://mysql.com)
[![Render](https://img.shields.io/badge/Deployed-Render.com-purple?logo=render)](https://render.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 🌐 Live Demo

| Resource | URL |
|---|---|
| **Live API** | https://bitespeed-identity-f3ft.onrender.com |
| **Swagger Docs** | https://bitespeed-identity-f3ft.onrender.com/docs |
| **ReDoc** | https://bitespeed-identity-f3ft.onrender.com/redoc |
| **GitHub** | https://github.com/yerramsettysuchita/bitespeed-identity |

---

## 📌 Problem Statement

FluxKart.com customers often place orders using different email addresses and phone numbers. Bitespeed needs to identify when these belong to the **same person** and consolidate them into one identity — so personalized experiences can be delivered across all their contact details.

---

## 🧠 How It Works — The Algorithm

Every incoming request to `POST /api/identify` is processed through a **3-case reconciliation algorithm**:

```
Incoming request (email / phoneNumber)
          │
          ▼
┌─────────────────────────────────┐
│  Search contacts table for      │
│  matching email OR phone        │
└─────────────────────────────────┘
          │
    ┌─────┴─────┐
    │           │
  No match   Match found
    │           │
    ▼           ▼
 CASE 1      Resolve to
 Create      root primaries
 new          │
 primary    ┌─┴──────────┐
 contact    │            │
            1 primary  2+ primaries
            │            │
            ▼            ▼
         CASE 2        CASE 3
         New info?     MERGE clusters
         → Create      Demote newer
         secondary     primary →
         contact       secondary
```

### Case 1 — New Contact
No matching email or phone exists → create a brand new `primary` contact.

### Case 2 — Secondary Created
A match is found but the request contains **new information** (new email or phone not seen before) → create a `secondary` contact linked to the oldest primary.

### Case 3 — Primary Merge
The request **links two separate primary clusters** → the newer primary is demoted to `secondary`, and all its children are re-linked to the true (oldest) primary.

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Framework | FastAPI |
| Database | MySQL 8 (Aiven cloud) |
| ORM | SQLAlchemy 2.0 |
| Validation | Pydantic v2 |
| Server | Uvicorn |
| Hosting | Render.com (free tier) |
| Frontend | Vanilla HTML / CSS / JS |

---

## 📁 Project Structure

```
bitespeed-identity/
├── app/
│   ├── __init__.py       # Package init
│   ├── config.py         # Environment variable settings
│   ├── database.py       # SQLAlchemy engine & session
│   ├── models.py         # Contact table ORM model
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── service.py        # ⭐ Core reconciliation algorithm
│   └── routes.py         # FastAPI route handlers
├── frontend/
│   └── index.html        # Full-stack UI served by FastAPI
├── .env                  # Local environment variables (not committed)
├── .env.example          # Template for environment setup
├── .gitignore            # Excludes venv, .env, __pycache__
├── .python-version       # Forces Python 3.11 on Render
├── main.py               # FastAPI app entry point
├── render.yaml           # Render.com deployment config
├── requirements.txt      # Python dependencies
└── README.md
```

---

## 🔌 API Reference

### `POST /api/identify`

Reconcile a contact identity. The core endpoint of this service.

**Request Body:**
```json
{
  "email": "lorraine@hillvalley.edu",
  "phoneNumber": "123456"
}
```

> At least one of `email` or `phoneNumber` must be provided.

**Response:**
```json
{
  "contact": {
    "primaryContatctId": 1,
    "emails": [
      "lorraine@hillvalley.edu",
      "mcfly@hillvalley.edu"
    ],
    "phoneNumbers": ["123456"],
    "secondaryContactIds": [23]
  }
}
```

---

### `GET /api/contacts`

Returns all active contacts in the database. Used by the UI dashboard.

---

### `DELETE /api/contacts/reset`

Deletes all contacts. For demo and testing purposes only.

---

## 🗄 Database Schema

```sql
CREATE TABLE contacts (
  id               INT          PRIMARY KEY AUTO_INCREMENT,
  phone_number     VARCHAR(20)  NULL,
  email            VARCHAR(255) NULL,
  linked_id        INT          NULL,          -- references id of primary contact
  link_precedence  ENUM('primary', 'secondary') NOT NULL,
  created_at       DATETIME     DEFAULT NOW(),
  updated_at       DATETIME     DEFAULT NOW() ON UPDATE NOW(),
  deleted_at       DATETIME     NULL           -- soft delete
);
```

---

## 🧪 Test Cases

| # | Email | Phone | Expected Result |
|---|---|---|---|
| 1 | lorraine@hillvalley.edu | 123456 | New primary created |
| 2 | mcfly@hillvalley.edu | 123456 | Secondary linked to #1 |
| 3 | lorraine@hillvalley.edu | _(empty)_ | Returns existing cluster unchanged |
| 4 | george@hillvalley.edu | 717171 | Two primaries → merge into one |
| 5 | _(empty)_ | 999888 | Phone-only primary |
| 6 | newperson@test.com | _(empty)_ | Email-only primary |

---

## ⚙️ Local Development

### Prerequisites
- Python 3.11+
- MySQL 8.0+

### 1. Clone the repository
```bash
git clone https://github.com/yerramsettysuchita/bitespeed-identity.git
cd bitespeed-identity
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create MySQL database
```sql
CREATE DATABASE bitespeed CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Configure environment
```bash
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/bitespeed
APP_ENV=development
ALLOWED_ORIGINS=*
```

### 6. Run the server
```bash
uvicorn main:app --reload
```

Open **http://localhost:8000** in your browser 🎉

---

## 🚀 Deploy to Render.com

1. Push code to GitHub
2. Create a free MySQL database on [Aiven.io](https://aiven.io)
3. Go to [Render.com](https://render.com) → New Web Service → Connect GitHub repo
4. Set these:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `DATABASE_URL` → your Aiven MySQL URI
   - `APP_ENV` → `production`
   - `ALLOWED_ORIGINS` → `*`
6. Click **Deploy** 🚀

---

## 👩‍💻 Author

**Suchita Yerramsetty**
- GitHub: [@yerramsettysuchita](https://github.com/yerramsettysuchita)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

*Built with ❤️ for the Bitespeed Backend Engineering Task*
