# Database

**PostgreSQL**. Ikkita jadval: `users` va `listings`.

```text
users  1 ──────── N  listings
```

## Ulanish

`.env` faylda:

```text
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/foundly
```

Driver — `psycopg2-binary`. `app/database.py` da:

```python
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

`get_db` ni `try/finally` bilan yozish muhim — aks holda ulanishlar yopilmay qoladi va DB tez orada yangi so'rovni qabul qilmay qo'yadi.

---

## users

| Ustun | Type | Constraint |
| --- | --- | --- |
| `id` | Integer | PK, autoincrement |
| `email` | String(255) | UNIQUE, NOT NULL |
| `password_hash` | String(255) | NOT NULL |
| `created_at` | DateTime | NOT NULL, default `now()` |

Parol **hech qachon** ochiq saqlanmaydi — `bcrypt` bilan hash qilinadi va `password_hash` ga yoziladi.

---

## listings

| Ustun | Type | Constraint |
| --- | --- | --- |
| `id` | Integer | PK, autoincrement |
| `user_id` | Integer | FK → `users.id`, NOT NULL |
| `title` | String(100) | NOT NULL |
| `description` | Text | NOT NULL |
| `type` | Enum | `LOST` \| `FOUND`, NOT NULL |
| `image` | String(255) | NULL (rasm ixtiyoriy) |
| `date` | Date | NOT NULL — buyum yo'qolgan/topilgan sana |
| `status` | Enum | `ACTIVE` \| `CLAIMED`, default `ACTIVE` |
| `created_at` | DateTime | NOT NULL, default `now()` |

`date` va `created_at` farqli: birinchisi — buyum yo'qolgan kun, ikkinchisi — e'lon joylangan vaqt.

---

## Enum'lar

```python
class ListingType(str, enum.Enum):
    LOST = "LOST"
    FOUND = "FOUND"


class ListingStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    CLAIMED = "CLAIMED"
```

`str` dan meros olish muhim — Pydantic va JSON bilan muammosiz ishlaydi.

---

## Bog'lanish

```python
# models.py
class User(Base):
    __tablename__ = "users"
    ...
    listings = relationship("Listing", back_populates="user")


class Listing(Base):
    __tablename__ = "listings"
    ...
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="listings")
```

Shundan keyin:

* `user.listings` → shu userning barcha e'lonlari
* `listing.user` → e'lon egasi

---

## Index

Ikkitasi yetarli:

```text
users.email       → UNIQUE index (SQLAlchemy'da unique=True o'zi yaratadi)
listings.user_id  → index (My Listings query uchun)
```

Qidiruv `title` bo'yicha oddiy `ILIKE '%...%'` bilan qilinadi. Bunday query index'dan foydalanmaydi, lekin bu loyihadagi ma'lumot hajmida muammo emas.

`ILIKE` — PostgreSQL'ning katta-kichik harfni farqlamaydigan qidiruvi. SQLAlchemy'da `Listing.title.ilike(...)`.

---

## Jadvallarni yaratish

Loyihani boshlashda eng oddiy yo'l — `main.py` da:

```python
Base.metadata.create_all(bind=engine)
```

Bu faqat **mavjud bo'lmagan** jadvallarni yaratadi. Model o'zgarsa (yangi ustun qo'shsangiz), jadvalni o'zgartirmaydi — development'da DB'ni tashlab qayta yaratish eng oson:

```bash
dropdb foundly && createdb foundly
```

Alembic'ni xohlasangiz qo'shing, lekin bu loyiha uchun majburiy emas.
