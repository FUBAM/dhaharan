# Dhaharan Backend API

Backend API untuk aplikasi resep makanan **Dhaharan**.

Project ini dibangun menggunakan **FastAPI**, **SQLAlchemy**, dan **MariaDB/MySQL**, dengan sistem authentication berbasis **JWT**.

---

# Tech Stack

- FastAPI
- SQLAlchemy
- MariaDB / MySQL
- JWT Authentication
- Pydantic
- Uvicorn

---

# Features

## Authentication
- Register
- Login
- Get current authenticated user
- JWT token authentication
- Optional authentication untuk endpoint public

---

## User Management
- Get my profile
- Update profile
- Upload profile image
- Update account
- Change email
- Change password
- Public user profile
- Deactivate account

---

## Recipe Management
- Create recipe
- Update recipe
- Delete recipe (soft delete)
- Public/private visibility
- Assign multiple categories
- Upload recipe cover image
- Get my recipes
- Get public recipes
- Get recipe detail

---

## Recipe Composition
- Ingredient groups
- Ingredients
- Recipe steps
- Multiple images per step

---

## Social Features
- Like / Unlike recipe
- Bookmark / Remove bookmark
- Personal bookmark note
- Comments (flat comments)
- Follow / Unfollow users
- Followers / Following list
- Recipe counters
- Interaction state

---

## Search / Filter / Sort
- Search by recipe title / description
- Filter by category
- Filter by cooking time
- Filter by pork content
- Filter by alcohol content
- Sort by:
  - created_at
  - title
  - cooking_time_minutes

---

# Project Structure

```text
dhaharan-backend/
│
├── app/
│   ├── common/
│   ├── core/
│   ├── modules/
│   │   ├── auth/
│   │   ├── users/
│   │   ├── categories/
│   │   ├── recipes/
│   │   ├── ingredients/
│   │   ├── steps/
│   │   └── social/
│   └── uploads/
│
├── scripts/
│   ├── seed_categories.py
│   └── seed_demo_user.py
│
├── requirements.txt
├── .env
├── .env.example
├── README.md
└── venv/
```

---

# Setup Project

## 1. Clone repository

```bash
git clone <repository-url>
cd dhaharan-backend
```

---

## 2. Buat virtual environment

```bash
python -m venv venv
```

---

## 3. Activate virtual environment

### Windows

```bash
venv\Scripts\activate
```

### Mac / Linux

```bash
source venv/bin/activate
```

---

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Configuration

Copy file:

```bash
.env.example
```

menjadi:

```bash
.env
```

Isi `.env`:

```env
APP_NAME=Dhaharan API
APP_ENV=development
DEBUG=true

DB_HOST=localhost
DB_PORT=3306
DB_NAME=dhaharan
DB_USER=root
DB_PASSWORD=your_password_here

JWT_SECRET_KEY=change-this-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

BASE_URL=http://localhost:8000
```

---

# Database Setup

## 1. Buat database

Masuk ke MariaDB/MySQL lalu jalankan:

```sql
CREATE DATABASE dhaharan;
```

---

## 2. Jalankan SQL schema

Import atau jalankan file SQL schema project ke database:

```text
dhaharan
```

Pastikan seluruh tabel berhasil dibuat tanpa error.

---

# Seed Data

## Seed categories

Untuk mengisi kategori default:

```bash
python scripts/seed_categories.py
```

---

## Seed demo user (optional)

Untuk membuat akun demo:

```bash
python scripts/seed_demo_user.py
```

Akun demo:

```text
email: demo@dhaharan.com
password: password123
```

---

# Menjalankan Server

Jalankan backend:

```bash
uvicorn app.main:app --reload
```

Jika berhasil, server berjalan di:

```text
http://localhost:8000
```

---

# Swagger Documentation

Swagger UI:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

---

# Authentication Flow

## Register

Gunakan endpoint:

```text
POST /api/v1/auth/register
```

---

## Login

Gunakan endpoint:

```text
POST /api/v1/auth/login
```

Response:

```json
{
  "access_token": "your-jwt-token",
  "token_type": "bearer"
}
```

---

## Authorize di Swagger

Klik tombol:

```text
Authorize
```

Masukkan:

```text
Bearer your-jwt-token
```

Contoh:

```text
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

# Upload Folder

File upload disimpan secara lokal di:

```text
app/uploads/
```

Subfolder:

```text
app/uploads/recipe_covers/
app/uploads/recipe_steps/
app/uploads/profiles/
```

Project ini tidak menggunakan cloud storage.

---

# API Endpoint Groups

## Authentication

```text
/api/v1/auth/*
```

---

## Users

```text
/api/v1/users/*
```

---

## Recipes

```text
/api/v1/recipes/*
```

---

## Categories

```text
/api/v1/categories/*
```

---

## Ingredients

```text
/api/v1/ingredients/*
```

---

## Steps

```text
/api/v1/steps/*
```

---

## Social

```text
/api/v1/*
```

---

# Validation Rules

## Register

- email harus unique
- format email harus valid
- password minimum 8 karakter

---

## Upload Image

Allowed file types:

- .jpg
- .jpeg
- .png
- .webp

Maximum file size:

```text
5 MB
```

---

# Notes

- Project ini dirancang untuk local development
- Tidak menggunakan deployment/cloud
- Tidak menggunakan migration tools seperti Alembic
- Database schema dikelola manual
- Fokus project adalah backend API production-like untuk kebutuhan kampus / portfolio

---

# Development Notes

Jika ada perubahan schema database:

- update SQL schema manual
- update SQLAlchemy models
- restart server

---

# Troubleshooting

## Virtual environment error

Jika muncul error:

```text
Fatal error in launcher
```

Hapus virtual environment lalu buat ulang:

### Windows

```bash
rmdir /s /q venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Database connection error

Pastikan:

- MariaDB/MySQL sedang running
- database `dhaharan` sudah dibuat
- konfigurasi `.env` benar

---

## JWT Unauthorized

Pastikan request mengirim header:

```text
Authorization: Bearer your-token
```

---

## Upload image gagal

Pastikan:

- format file sesuai
- ukuran file < 5 MB
- MIME type valid

---

# Status Project

Backend feature-complete.

Fitur yang tersedia:

- authentication
- user profile & account management
- recipe CRUD
- recipe composition
- categories
- ingredients
- steps
- image uploads
- social features
- search / filter / sort
- pagination
- validation hardening

Backend siap digunakan oleh frontend Flutter untuk consume API.