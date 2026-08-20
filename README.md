🇮🇷 [مطالعه به زبان فارسی](README.fa.md)

# 🏟️ SportCenter Reservation API

> A modern asynchronous RESTful API for sports facility reservation built with **FastAPI**, **PostgreSQL**, **Redis**, and **Docker**.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.138-009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue)
![Redis](https://img.shields.io/badge/Redis-8-red)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
[![CI](https://github.com/manialn/SportCenter-Reservation-API/actions/workflows/ci.yml/badge.svg)](https://github.com/manialn/SportCenter-Reservation-API/actions/workflows/ci.yml)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📖 Overview

SportCenter Reservation API is a production-oriented backend project that simulates a complete sports facility reservation system.

It demonstrates modern backend development practices including asynchronous programming, layered architecture, JWT authentication, Redis integration, Dockerized deployment, database migrations, and automated testing.

The project is designed to be scalable and maintainable by separating business logic from infrastructure components.

---

## 🎯 Problem & Scenario

In a real sports facility, users need a reliable way to discover available time slots and reserve them without conflicts, while facility managers need to manage facilities, schedules, and time slots.

For example, a user wants to reserve a football field for a specific time. The system checks whether the facility and time slot are available, prevents double booking even when multiple requests arrive simultaneously, processes the payment, and confirms the booking after a successful payment.

At the same time, administrators can manage facilities, weekly schedules, and available time slots through the API.

This project solves these problems by providing a centralized reservation system with authentication, role-based authorization, concurrency-safe booking logic, payment abstraction, caching, rate limiting, and persistent data management.

---

## 🌐 Live Demo

The API is publicly deployed on Render.

**Base URL**

<https://sportcenter-reservation-api.onrender.com>

**Swagger Documentation**

<https://sportcenter-reservation-api.onrender.com/docs>

> **Note:** This project is deployed on Render's free tier, so the initial request may take a few moments while the service wakes up. Access to the live demo may also be limited in some regions or networks.

---

## ✨ Features

- 🔐 JWT Authentication (Access & Refresh Tokens)
- 🔄 Refresh Token Rotation & Revocation
- 🔒 Secure Refresh Token Storage with JTI
- 👤 Role-Based Authorization (Admin & User)
- 🔑 Redis-based OTP Verification
- ✅ GitHub Actions Continuous Integration (CI)
- ☁️ Deployment on Render
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
| Containerization | Docker & Docker Compose |
| Deployment | Render |
| CI | GitHub Actions |

---

## 📂 Project Structure

```text

.
├── .github/
│   └── workflows/
├── alembic/
├── app/
│   ├── cache/
│   ├── core/
│   ├── enumsfile/
│   ├── gateways/
│   ├── limiter/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── test/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   └── models.py
├── logs/
├── .dockerignore
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── requirements.txt
├── README.md
└── README.fa.md

---

## 📚 API Modules

| Module | Description |
|---------|-------------|
| Authentication | Login, JWT, Refresh Token Rotation & Revocation, OTP, Password Reset |
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
docker compose run --rm app pytest app/test -v
```

Run a specific test file:

```bash
docker compose run --rm app pytest app/test/test_booking.py -v
```

Run a specific test:

```bash
docker compose run --rm app pytest app/test/test_booking.py::test_create_booking -v
```
The test suite includes asynchronous API integration tests, JWT unit tests, and Redis integration tests for caching and rate limiting.

> **Note:** The complete test suite is automatically executed on every push and pull request using GitHub Actions (CI).

The project uses a dedicated PostgreSQL test database to ensure complete isolation between development and testing data.

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
- Refresh token persistence and revocation with PostgreSQL
- Redis for OTP, caching, and rate limiting
- Payment abstraction with mock implementation
- Alembic database migrations
- Centralized structured logging

---

## 🚀 Future Improvements

- Real payment gateway integration
- SMS / Email OTP providers
- Background task processing (Celery / RQ)
- Continuous Deployment (CD)
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