# Arxitektura

Papkalar **texnik qatlam bo'yicha emas, modul (feature) bo'yicha** bo'linadi. Har bir modul o'zining router, service, repository va schema'sini o'zi ichida saqlaydi.

```text
app/
├── main.py                 # FastAPI app, router'larni ulash
├── database.py             # engine, SessionLocal, get_db, Base
│
├── core/
│   ├── config.py           # .env dan sozlamalar
│   └── security.py         # parol hash, JWT yaratish/ochish
│
├── users/                  # ro'yxatdan o'tish, login, profil
│   ├── models.py
│   ├── schemas.py
│   ├── repository.py
│   ├── service.py
│   ├── router.py
│   └── dependencies.py     # get_current_user
│
└── listings/               # e'lonlar, qidiruv, claim
    ├── models.py
    ├── schemas.py
    ├── repository.py
    ├── service.py
    └── router.py

tests/
.env.example
requirements.txt
```

Har bir papkada `__init__.py` bo'lishi kerak.

Yangi modul kerak bo'lsa (masalan `comments/`), yangi papka ochasiz — eski modullarga tegmaysiz.

---

## Modul ichidagi fayllar

Har bir modulda bir xil 5 ta fayl:

| Fayl | Nima yoziladi |
| --- | --- |
| `models.py` | SQLAlchemy jadval — ustunlar, `relationship` |
| `schemas.py` | Pydantic — request va response shakllari |
| `repository.py` | Faqat DB query'lari: `db.query()`, `db.add()`, `db.commit()` |
| `service.py` | Biznes qoidalari: ownership, status tekshiruvi, xatolar |
| `router.py` | Endpointlar: `@router.get(...)`, `Depends(...)`, `response_model` |

So'rov shu yo'l bilan o'tadi:

```text
router  →  service  →  repository  →  models
```

Faqat pastga qarab. Repository service'ni chaqirmaydi, service router'ni bilmaydi.

Oson eslab qolish:

* **router** — HTTP biladi, SQL bilmaydi
* **repository** — SQL biladi, HTTP bilmaydi
* **service** — ikkalasini ham bilmaydi, faqat qoidalarni biladi

---

## Misol: claim

`POST /api/v1/listings/{id}/claim` uchta fayldan o'tadi.

### `app/listings/router.py`

```python
router = APIRouter(prefix="/listings", tags=["listings"])


@router.post("/{listing_id}/claim", response_model=ListingOut)
def claim_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.claim(db, listing_id, current_user)
```

Router faqat so'rovni qabul qiladi va service'ga uzatadi. Bu yerda `if` yozilmaydi.

### `app/listings/service.py`

```python
def claim(db: Session, listing_id: int, current_user: User) -> Listing:
    listing = repository.get_by_id(db, listing_id)

    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")

    if listing.status == ListingStatus.CLAIMED:
        raise HTTPException(status_code=409, detail="Listing has already been claimed")

    listing.status = ListingStatus.CLAIMED
    return repository.save(db, listing)
```

Barcha qoidalar shu yerda.

### `app/listings/repository.py`

```python
def get_by_id(db: Session, listing_id: int) -> Listing | None:
    return db.query(Listing).filter(Listing.id == listing_id).first()


def save(db: Session, listing: Listing) -> Listing:
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing
```

Repository shart qo'ymaydi, xato qaytarmaydi — faqat DB bilan gaplashadi.

---

## Misol: ownership

`PATCH /listings/{id}` faqat e'lon egasiga ruxsat etiladi. Bu biznes qoidasi, demak `service.py` da:

```python
def update(db: Session, listing_id: int, data: ListingUpdate, current_user: User) -> Listing:
    listing = repository.get_by_id(db, listing_id)

    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")

    if listing.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your listing")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(listing, field, value)

    return repository.save(db, listing)
```

`exclude_unset=True` — PATCH uchun muhim: faqat yuborilgan maydonlar yangilanadi.

---

## Misol: qidiruv

Filtr va sahifalash — DB ishi, demak `repository.py` da:

```python
def get_many(
    db: Session,
    search: str | None = None,
    type: ListingType | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Listing], int]:
    query = db.query(Listing)

    if search:
        query = query.filter(Listing.title.ilike(f"%{search}%"))
    if type:
        query = query.filter(Listing.type == type)

    total = query.count()
    items = (
        query.order_by(Listing.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total
```

Bu yerda service deyarli hech narsa qilmaydi — shunchaki repository'ni chaqiradi. **Bu normal**, har bir service funksiyasida qoida bo'lishi shart emas.

---

## `core/security.py`

Parol hash va JWT — modullardan tashqarida, chunki ikkalasi ham "biznes qoidasi" emas, quruq utility:

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

Bularni `users/service.py` chaqiradi:

```python
def register(db: Session, data: UserCreate) -> User:
    if repository.get_by_email(db, data.email):
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(email=data.email, password_hash=hash_password(data.password))
    return repository.save(db, user)
```

Email band ekanini tekshirish — **biznes qoidasi**, shuning uchun service'da. Repository faqat `get_by_email` ni bajaradi va `None` qaytaradi.

---

## Modullar bir-birini chaqirsa

`listings` moduli `User` modelini biladi (`listing.user_id`), lekin `users` moduli `listings` haqida bilmasa yaxshi.

Ya'ni bog'lanish bir tomonlama:

```text
listings  →  users
```

Ikki tomonlama import (`users` ham `listings` ni import qilishi) circular import xatosiga olib keladi.

---

## Tez-tez uchraydigan xatolar

**Router'da query yozish**

```python
# ❌ router SQL bilmasligi kerak
@router.get("/{listing_id}")
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    return db.query(Listing).filter(Listing.id == listing_id).first()
```

**Repository'da HTTPException**

```python
# ❌ repository HTTP haqida bilmaydi
def get_by_id(db: Session, listing_id: int):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if listing is None:
        raise HTTPException(404, "Not found")
    return listing
```

`None` qaytaring — nima qilishni service hal qiladi.

**`response_model`siz model qaytarish**

Router har doim Pydantic schema qaytarsin. Aks holda `password_hash` javobga tushib ketishi mumkin.

---

## Eslatma

Bitta endpoint uchun uchta faylga kod yozish kichik loyihada "ortiqcha" tuyulishi mumkin. Bu shunday va normal.

Maqsad — tezlik emas, **kodni bo'lishni o'rganish**. Loyiha kattalashganda: query'ni o'zgartirsangiz `repository.py` ga, qoidani o'zgartirsangiz `service.py` ga tegasiz, qolgani joyida qoladi.
