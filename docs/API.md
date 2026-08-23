# API

Base URL:

```text
http://localhost:8000/api/v1
```

Autentifikatsiya — JWT. Login qilgandan keyin token'ni har bir himoyalangan so'rovda yuboring:

```http
Authorization: Bearer <access_token>
```

---

## Endpointlar

| Method | Endpoint | Kim uchun | Nima qiladi |
| --- | --- | --- | --- |
| POST | `/auth/register` | hamma | Ro'yxatdan o'tish |
| POST | `/auth/login` | hamma | Token olish |
| GET | `/auth/me` | login qilgan | O'z ma'lumoti |
| GET | `/listings` | hamma | E'lonlar ro'yxati + qidiruv |
| GET | `/listings/{id}` | hamma | Bitta e'lon |
| POST | `/listings` | login qilgan | E'lon yaratish |
| PATCH | `/listings/{id}` | faqat egasi | E'lonni tahrirlash |
| DELETE | `/listings/{id}` | faqat egasi | E'lonni o'chirish |
| POST | `/listings/{id}/claim` | login qilgan | `ACTIVE` → `CLAIMED` |
| GET | `/me/listings` | login qilgan | O'z e'lonlari |

---

## Auth

### POST /auth/register

Request:

```json
{
  "email": "user@example.com",
  "password": "strong-password"
}
```

Response `201`:

```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2026-05-20T10:00:00Z"
}
```

Email band bo'lsa → `409`.

---

### POST /auth/login

Request:

```json
{
  "email": "user@example.com",
  "password": "strong-password"
}
```

Response `200`:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

Email yoki parol noto'g'ri bo'lsa → `401`. Qaysi biri noto'g'ri ekanini aytmang — ikkalasiga bir xil xabar qaytaring.

---

### GET /auth/me

Token talab qiladi. Response `200`:

```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2026-05-20T10:00:00Z"
}
```

---

## Listings

### GET /listings

Ochiq endpoint, token kerak emas.

Query parametrlar:

| Parametr | Default | Izoh |
| --- | --- | --- |
| `search` | — | `title` bo'yicha qidiruv |
| `type` | — | `LOST` yoki `FOUND` |
| `page` | 1 | Sahifa raqami |
| `page_size` | 20 | Sahifadagi elementlar soni |

Masalan:

```http
GET /api/v1/listings?search=airpods&type=FOUND&page=1&page_size=20
```

Response `200`:

```json
{
  "items": [
    {
      "id": 1,
      "title": "AirPods Pro",
      "description": "Found near the library",
      "type": "FOUND",
      "image": "/media/airpods.jpg",
      "date": "2026-05-20",
      "status": "ACTIVE",
      "created_at": "2026-05-20T10:30:00Z"
    }
  ],
  "total": 1
}
```

Qidiruv **faqat `title`** bo'yicha, oddiy `ILIKE '%airpods%'` yetarli:

```python
# app/listings/repository.py
if search:
    query = query.filter(Listing.title.ilike(f"%{search}%"))
```

---

### GET /listings/{id}

Ochiq endpoint. Response `200` — yuqoridagi listing obyekti. Topilmasa → `404`.

---

### POST /listings

Token talab qiladi. `user_id` request'dan **olinmaydi** — token'dagi userdan olinadi. `status` har doim `ACTIVE` bo'lib yaratiladi.

Request:

```json
{
  "title": "AirPods Pro",
  "description": "Found near the library",
  "type": "FOUND",
  "date": "2026-05-20"
}
```

Response `201` — yaratilgan listing.

Rasm yuklashni qo'shsangiz, `multipart/form-data` ishlating va faylni lokal `media/` papkaga saqlang.

---

### PATCH /listings/{id}

Token talab qiladi va **faqat e'lon egasi** o'zgartira oladi. Faqat yuborilgan maydonlar yangilanadi:

```json
{
  "title": "AirPods Pro (2nd gen)"
}
```

Kodda tekshiruv:

```python
# app/listings/service.py
if listing.user_id != current_user.id:
    raise HTTPException(status_code=403, detail="Not your listing")
```

Response `200` — yangilangan listing.

---

### DELETE /listings/{id}

Token talab qiladi, faqat egasi o'chira oladi. Response `204`, body yo'q.

---

### POST /listings/{id}/claim

Token talab qiladi. Status `ACTIVE` → `CLAIMED`.

Response `200`:

```json
{
  "id": 1,
  "title": "AirPods Pro",
  "status": "CLAIMED"
}
```

Allaqachon claim qilingan bo'lsa → `409`:

```json
{ "detail": "Listing has already been claimed" }
```

---

### GET /me/listings

Token talab qiladi. Faqat shu userning e'lonlari:

```json
{
  "items": [
    { "id": 10, "title": "Black Backpack", "type": "LOST", "status": "ACTIVE" },
    { "id": 11, "title": "AirPods Pro", "type": "FOUND", "status": "CLAIMED" }
  ],
  "total": 2
}
```

---

## Validation

Pydantic schema'da:

| Maydon | Qoida |
| --- | --- |
| `title` | majburiy, 2–100 belgi |
| `description` | majburiy, maksimal 300 belgi |
| `type` | faqat `LOST` yoki `FOUND` |
| `date` | to'g'ri sana |
| `email` | `EmailStr` |
| `password` | minimal 8 belgi |

> Frontend validation — qulaylik uchun. Backend validation — xavfsizlik uchun. Frontendga ishonmang.

---

## Xatoliklar

Bitta formatda qaytaring — FastAPI'ning `HTTPException` allaqachon shunday qiladi:

```json
{ "detail": "Listing not found" }
```

| Status | Qachon |
| --- | --- |
| `200` | OK |
| `201` | Yaratildi |
| `204` | O'chirildi |
| `401` | Login qilinmagan yoki token yaroqsiz |
| `403` | Ruxsat yo'q — o'z e'loni emas |
| `404` | Topilmadi |
| `409` | Email band / allaqachon claim qilingan |
| `422` | Validation xatosi (FastAPI o'zi qaytaradi) |
