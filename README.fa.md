🇺🇸 [Read in English](README.md)

# 🏟️ API رزرو مجموعه ورزشی

> یک API مدرن، ناهمگام (Asynchronous) و مبتنی بر REST برای مدیریت رزرو مجموعه‌های ورزشی که با **FastAPI**، **PostgreSQL**، **Redis** و **Docker** توسعه داده شده است.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.138-009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue)
![Redis](https://img.shields.io/badge/Redis-8-red)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📖 معرفی پروژه

SportCenter Reservation API یک پروژه بک‌اند با معماری نزدیک به استانداردهای Production است که فرآیند کامل مدیریت مجموعه‌های ورزشی، زمان‌بندی، رزرو و پرداخت را شبیه‌سازی می‌کند.

در این پروژه از معماری لایه‌ای، برنامه‌نویسی Asynchronous، احراز هویت مبتنی بر JWT، Redis، Docker، Alembic و تست‌های خودکار استفاده شده است تا ساختاری مقیاس‌پذیر، قابل نگهداری و توسعه‌پذیر ایجاد شود.

---

## 🌐 نسخه آنلاین

این API به‌صورت عمومی روی **Render** مستقر (Deploy) شده است.

**آدرس اصلی API**

<https://sportcenter-reservation-api.onrender.com>

**مستندات Swagger**

<https://sportcenter-reservation-api.onrender.com/docs>

> **توجه:** این پروژه روی نسخه رایگان Render میزبانی می‌شود. بسته به اینترنت یا ISP شما، ممکن است برای دسترسی به نسخه آنلاین نیاز به VPN داشته باشید.

---


## ✨ قابلیت‌ها

- 🔐 احراز هویت JWT (Access Token و Refresh Token)
- 👤 مدیریت نقش کاربران (Admin و User)
- 🔑 تأیید OTP با Redis
- 🔄 بازیابی رمز عبور
- 🏟️ مدیریت مجموعه‌های ورزشی
- 📅 مدیریت برنامه هفتگی مجموعه‌ها
- ⏰ مدیریت بازه‌های زمانی (Time Slots)
- 🎫 ایجاد و لغو رزرو
- 🚫 جلوگیری از رزرو تکراری
- 💳 معماری انتزاعی درگاه پرداخت (Payment Gateway)
- 🧪 پیاده‌سازی Mock برای سیستم پرداخت
- ⚡ کش کردن داده‌ها با Redis
- 🚦 محدودسازی درخواست‌ها (Rate Limiting)
- 📝 لاگ‌گیری ساختاریافته
- 🐳 اجرای پروژه با Docker
- 🧪 تست‌های Async

---

## 🚀 تکنولوژی‌های استفاده‌شده

| بخش | فناوری |
|------|---------|
| زبان برنامه‌نویسی | Python 3.13 |
| فریم‌ورک | FastAPI |
| ORM | SQLAlchemy 2.0 |
| پایگاه داده | PostgreSQL |
| کش | Redis |
| احراز هویت | JWT |
| اعتبارسنجی | Pydantic v2 |
| مهاجرت دیتابیس | Alembic |
| تست | Pytest + HTTPX |
| استقرار | Docker & Docker Compose |

---

## 📂 ساختار پروژه

```text
.
├── alembic/
├── app/
│   ├── core/
│   ├── database/
│   ├── dependencies/
│   ├── gateways/
│   ├── limiter/
│   ├── middleware/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   └── main.py
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 📚 ماژول‌های API

| ماژول | توضیحات |
|--------|---------|
| احراز هویت | ورود، JWT، OTP و بازیابی رمز عبور |
| کاربران | مدیریت کاربران |
| مجموعه‌های ورزشی | مدیریت اطلاعات مجموعه‌ها |
| برنامه هفتگی | مدیریت ساعات کاری و زمان‌بندی |
| بازه‌های زمانی | مدیریت Time Slotها |
| رزرو | ایجاد، لغو و مدیریت رزروها |
| پرداخت | مدیریت فرآیند پرداخت |

---

## ⚙️ راه‌اندازی سریع

ابتدا پروژه را دریافت کنید:

```bash
git clone https://github.com/manialn/SportCenter-Reservation-API.git

cd SportCenter-Reservation-API
```

فایل تنظیمات را ایجاد کنید:

```bash
cp .env.example .env
```

سپس پروژه را اجرا کنید:

```bash
docker compose up --build
```

مایگریشن‌های دیتابیس را اعمال کنید:

```bash
docker compose exec app alembic upgrade head
```

مستندات Swagger:

```
http://localhost:8000/docs
```

---

## 🧪 اجرای تست‌ها

اجرای تمامی تست‌ها:

```bash
docker compose exec app pytest
```

اجرای یک فایل تست مشخص:

```bash
docker compose exec app pytest tests/test_booking.py
```

برای جلوگیری از تداخل اطلاعات، تست‌ها روی یک پایگاه داده PostgreSQL مجزا اجرا می‌شوند.

---

## 🔧 متغیرهای محیطی

| متغیر | توضیح |
|--------|-------|
| DATABASE_URL | آدرس اتصال به PostgreSQL |
| POSTGRES_USER | نام کاربری PostgreSQL |
| POSTGRES_PASSWORD | رمز عبور PostgreSQL |
| POSTGRES_DB | نام پایگاه داده |
| REDIS_URL | آدرس Redis |
| SECRET_KEY | کلید JWT |
| ACCESS_TOKEN_EXPIRE_MINUTES | مدت اعتبار Access Token |
| REFRESH_TOKEN_EXPIRE_DAYS | مدت اعتبار Refresh Token |
| OTP_EXPIRE_SECONDS | زمان انقضای OTP |
| OTP_LENGTH | طول کد OTP |
| CACHE_EXPIRE_SECONDS | مدت زمان نگهداری Cache |

برای مشاهده تنظیمات کامل، فایل `.env.example` را بررسی کنید.

---

## 🏗️ معماری پروژه

- معماری کاملاً Asynchronous
- معماری لایه‌ای (Layered Architecture)
- جداسازی Business Logic در Service Layer
- استفاده از SQLAlchemy Async ORM
- Redis برای OTP، Cache و Rate Limiting
- معماری انتزاعی برای درگاه پرداخت با Mock Provider
- مدیریت نسخه دیتابیس با Alembic
- سیستم لاگ‌گیری ساختاریافته

---

## 🚀 توسعه‌های آینده

- اتصال به درگاه‌های پرداخت واقعی
- ارسال OTP از طریق پیامک یا ایمیل
- پردازش وظایف پس‌زمینه
- راه‌اندازی CI/CD
- مانیتورینگ و مشاهده‌پذیری
- اعلان‌های WebSocket
- نسخه‌بندی API

---

## 📄 مجوز

این پروژه تحت مجوز MIT منتشر شده است.

---

## 👨‍💻 توسعه‌دهنده

**مانی سپهری**

GitHub: https://github.com/manialn

---

## ⭐ حمایت

اگر این پروژه برای شما مفید بود، خوشحال می‌شوم با دادن یک ⭐ در GitHub از آن حمایت کنید.