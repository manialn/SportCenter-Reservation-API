🇮🇷 [مطالعه به زبان فارسی](README.fa.md)

# 🏟️ SportCenter Reservation API

> A modern asynchronous RESTful API for sports facility reservation built with **FastAPI**, **PostgreSQL**, **Redis**, and **Docker**.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.138-009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue)
![Redis](https://img.shields.io/badge/Redis-8-red)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📖 Overview

SportCenter Reservation API is a production-oriented backend project that simulates a complete sports facility reservation system.

It demonstrates modern backend development practices including asynchronous programming, layered architecture, JWT authentication, Redis integration, Dockerized deployment, database migrations, and automated testing.

The project is designed to be scalable and maintainable by separating business logic from infrastructure components.

---

## 🌐 Live Demo

The API is publicly deployed on Render.

**Base URL**

<https://sportcenter-reservation-api.onrender.com>

**Swagger Documentation**

<https://sportcenter-reservation-api.onrender.com/docs>

> **Note:** This project is deployed on Render's free tier. Depending on your network or ISP, a VPN may be required to access the live demo.

---

## ✨ Features

- 🔐 JWT Authentication (Access & Refresh Tokens)
- 👤 Role-Based Authorization (Admin & User)
- 🔑 Redis-based OTP Verification
- 🔄 Password Reset Workflow
- 🏟️ Facility Management
- 📅 Weekly Schedule Management
- ⏰ Time Slot Management
- 🎫 Booking Creation & Cancellation
- 🚫 Double Booking Prevention
- 💳 Payment Gateway Abstraction
- 🧪 Mock Payment Provider
- ⚡ Redis Response Caching
- 🚦 Redis Rate Limiting
- 📝 Structured Logging
- 🐳 Dockerized Development
- 🧪 Async API Testing

---

## 🚀 Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.13 |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL |
| Cache | Redis |
| Authentication | JWT |
| Validation | Pydantic v2 |
| Migrations | Alembic |
| Testing | Pytest + HTTPX |
| Deployment | Docker & Docker Compose |

---

## 📂 Project Structure

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

## 📚 API Modules

| Module | Description |
|---------|-------------|
| Authentication | Login, JWT, OTP, Password Reset |
| Users | User management |
| Facilities | Facility CRUD |
| Facility Schedules | Weekly schedules |
| Time Slots | Reservable time slots |
| Bookings | Reservation management |
| Payments | Payment processing |

---

## ⚙️ Quick Start

Clone the repository:

```bash
git clone https://github.com/manialn/SportCenter-Reservation-API.git
cd SportCenter-Reservation-API
```

Create your environment file:

```bash
cp .env.example .env
```

Run the project:

```bash
docker compose up --build
```

Apply database migrations:

```bash
docker compose exec app alembic upgrade head
```

Open Swagger UI:

```
http://localhost:8000/docs
```

---

## 🧪 Running Tests

Run all tests:

```bash
docker compose exec app pytest
```

Run a specific test:

```bash
docker compose exec app pytest tests/test_booking.py
```

The project uses a dedicated PostgreSQL test database to keep test data isolated from development data.

---

## 🔧 Environment Variables

| Variable | Description |
|----------|-------------|
| DATABASE_URL | PostgreSQL connection |
| POSTGRES_USER | PostgreSQL username |
| POSTGRES_PASSWORD | PostgreSQL password |
| POSTGRES_DB | Database name |
| REDIS_URL | Redis connection |
| SECRET_KEY | JWT secret |
| ACCESS_TOKEN_EXPIRE_MINUTES | Access token lifetime |
| REFRESH_TOKEN_EXPIRE_DAYS | Refresh token lifetime |
| OTP_EXPIRE_SECONDS | OTP expiration |
| OTP_LENGTH | OTP length |
| CACHE_EXPIRE_SECONDS | Cache lifetime |

See `.env.example` for the complete configuration.

---

## 🏗️ Architecture

- Fully asynchronous request handling
- Layered architecture
- Service-based business logic
- SQLAlchemy Async ORM
- Redis for OTP, caching, and rate limiting
- Payment abstraction with mock implementation
- Alembic database migrations
- Centralized structured logging

---

## 🚀 Future Improvements

- Real payment gateway integration
- SMS / Email OTP providers
- Background task processing
- CI/CD pipeline
- Monitoring & Observability
- WebSocket notifications
- API versioning

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Mani Sepehri**

GitHub: https://github.com/manialn

---

## ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.