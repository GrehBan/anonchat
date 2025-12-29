# Anochat Core (High-Load Edition)

**Anochat** is a high-performance core for an anonymous chat bot (chat-roulette), built on the principles of **Clean Architecture**, **Domain-Driven Design (DDD)**, and **Event Sourcing (Lite)**.

The architecture is designed to handle high loads: all read and write operations occur in memory (Redis), while persistence to PostgreSQL happens asynchronously via event streams (Redis Streams).

## ⚡ Architecture Features

### 1. Redis First & Write-Behind

Unlike traditional bots, Anochat does not write synchronously to the database.

* **Hot Storage:** Active chats and recent messages are stored in Redis. This ensures instant response times (`< 5ms`).
* **Reliability:** Data is reliably saved to PostgreSQL using the **Write-Behind** pattern. Repositories emit events (`CREATE`, `SAVE`, `CLOSE`) to Redis Streams.
* **Optimization:** Message history uses the **"Timeline + Payload"** pattern with `MGET` to minimize network latency.

### 2. Concurrency Control

A strict distributed locking system is implemented on top of Redis.

* Guarantees dialog uniqueness (a user cannot be in two chats simultaneously).
* Prevents Race Conditions during simultaneous chat creation requests by locking users in a sorted order.

### 3. Clean Architecture

* **Domain:** Pure business logic (Aggregates, Value Objects, Protocols).
* **Application:** Use Cases that manage data flow and transactions.
* **Infrastructure:** Repository implementations based on `redis-py` and `sqlalchemy` (async).

## 🛠 Tech Stack

* **Language:** Python 3.14+
* **In-Memory DB:** Redis 7+ (Storage, Streams, Locks)
* **Persistent DB:** PostgreSQL 16+ (Archive)
* **ORM:** SQLAlchemy 2.0 (Async)
* **Framework:** Aiogram 3.x
* **Utils:** Pydantic V2, AsyncPG, Adaptix

## 📂 Project Structure

```text
anonchat/
├── application/      # Use Cases (Business Scenarios)
│   ├── chat/         # Chat logic (StartChat, GetCurrentChat)
│   ├── message/      # Message logic (SendMessage)
│   └── user/         # User management
├── domain/           # Pure Business Logic (Entities, VOs, Interfaces)
└── infrastructure/   # Data Access Implementation
    ├── cache/        # Redis Key Generators, Locks
    ├── repositories/ # Repositories (Redis implementation)
    └── database/     # SQLAlchemy Models

```

## 🚀 Installation & Setup

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/anochat.git
cd anochat

```


2. **Environment Configuration:**
Create a `.env` file in the root directory:
```env
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/anochat
BOT_TOKEN=your_token_here

```


3. **Install Dependencies:**
```bash
poetry install

```


4. **Run:**
```bash
# Example command to run the bot
poetry run python -m anonchat.main

```



## ✅ Roadmap

Based on the current codebase analysis:

* [x] **Core Domain**: Chat, User, and Message aggregates are implemented.
* [x] **Redis Repositories**: Repositories supporting Streams and Pipelines are ready.
* [x] **Locking Mechanism**: Protection against Race Conditions is implemented.
* [x] **Use Cases**: Main scenarios (`StartChat`, `SendMessage`) are implemented.
* [ ] **Workers**: Implementation of background consumers to move data from Redis Streams to PostgreSQL.
* [ ] **Admin Panel**: Administration interface for statistics and ban management.
* [ ] **Metrics**: Integration with Prometheus/Grafana.