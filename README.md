# Anochat Core (High-Load Edition)

**Anochat** is a high-performance backend core for an anonymous chat bot (chat-roulette), engineered with **Clean Architecture**, **Domain-Driven Design (DDD)**, and **Event Sourcing** principles.

Designed for scalability, Anochat prioritizes **In-Memory** operations for instant user feedback while ensuring data consistency through asynchronous **Write-Behind** synchronization to PostgreSQL.

---

## ⚡ Key Architectural Features

### 1. Redis-First Strategy & Write-Behind

Unlike traditional architectures that write synchronously to a disk-based database, Anochat utilizes Redis as the primary writable storage.

* **Hot Storage:** All active chats, user sessions, and recent message histories are stored in Redis for `< 5ms` latency.
* **Event Streams:** Data persistence is handled asynchronously. Repositories emit events (`SAVE`, `UPDATE`, `DELETE`) to **Redis Streams** immediately after writing to the cache.
* **Consumers:** Background workers consume these streams and synchronize data with PostgreSQL, ensuring zero impact on the main application thread.

### 2. Full Horizontal Scalability (Sharding)

The system supports horizontal scaling for **all** data types through **Stream Sharding**.

* **Users, Chats, and Messages** are distributed across multiple stream shards based on their IDs (e.g., `user_id % 4`).
* This allows you to run multiple parallel worker instances for heavy loads (e.g., message processing) without locking contention.

### 3. Concurrency Control

* **Distributed Locking:** Critical operations, such as `StartChat`, utilize Redis-based distributed locks to prevent race conditions (e.g., a user entering two chats simultaneously).
* **Deadlock Prevention:** Lock acquisition order is sorted deterministically to prevent deadlocks.

### 4. Optimized Message Storage

* **Timeline + Payload Pattern:** Messages are stored using a split approach—metadata in lists for timeline retrieval and payloads in key-value pairs for direct access.
* **Auto-Cleanup:** A dedicated worker actively monitors and trims message history in Redis using non-blocking `SCAN` cursors to maintain optimal memory usage.

---

## 🛠 Tech Stack

* **Language:** Python 3.14+
* **Framework:** Aiogram 3.x (Bot Interface)
* **Storage (Hot):** Redis 7+ (Streams, Pipelines, Pub/Sub)
* **Storage (Cold):** PostgreSQL 16+
* **ORM:** SQLAlchemy 2.0 (Async) + AsyncPG
* **Data Validation:** Pydantic V2 & Adaptix

---

## 📂 Project Structure

```text
anonchat/
├── application/       # Use Cases (Business Orchestration)
│   ├── chat/          # Chat logic (StartChat, GetCurrentChat)
│   ├── message/       # Message handling (SendMessage)
│   └── user/          # User CRUD operations
├── domain/            # Pure Business Logic (Aggregates, VOs, Protocols)
├── infrastructure/    # External interfaces implementation
│   ├── cache/         # Redis keys, Locks, Base Workers
│   ├── database/      # SQLAlchemy models & mappers
│   ├── repositories/  # Redis & SQL Repositories implementation
│   └── uow/           # Unit of Work implementations
└── workers/           # Background Consumers (Data Sync)
    ├── chat_stream.py # Syncs chat lifecycle events (Sharded)
    ├── user_stream.py # Syncs user profiles (Sharded)
    ├── message_stream.py # Syncs messages (Sharded)
    └── cleanup_old_messages.py # Maintenance worker

```

---

## 🚀 Installation

### Prerequisites

* Python 3.14 or higher
* Redis Server (AOF persistence recommended)
* PostgreSQL Database
* Poetry (Package Manager)

### Steps

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/anochat.git
cd anochat

```


2. **Install dependencies:**
```bash
poetry install

```


3. **Environment Configuration:**
Create a `.env` file in the root directory:
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/anochat

# Redis (Master)
REDIS_URL=redis://localhost:6379/0

# Bot
BOT_TOKEN=your_telegram_bot_token

```


4. **Apply Migrations:**
*(Ensure Alembic is configured and run migrations to create tables)*
```bash
alembic upgrade head

```



---

## 🏃 Running the Application

To run the full system, you need to launch the main bot process and the background workers. In a production environment, use `systemd` or `Docker Compose`.

### 1. Main Bot Process

Handles user interactions and writes to Redis.

```bash
poetry run python -m anonchat.main

```

### 2. Background Workers (Consumers)

These workers must run alongside the bot to persist data to PostgreSQL. **All synchronization workers support sharding.**

**Scaling Workers:**
You must run a worker for each shard. By default, `SHARDS_COUNT` is 4.

```bash
# --- User Sync (Sharded) ---
poetry run python -m anonchat.workers.user_stream --shard 0
poetry run python -m anonchat.workers.user_stream --shard 1
# ... up to SHARDS_COUNT-1

# --- Message Sync (Sharded) ---
# Critical for high message throughput
poetry run python -m anonchat.workers.message_stream --shard 0
poetry run python -m anonchat.workers.message_stream --shard 1
# ...

# --- Chat Sync (Sharded) ---
poetry run python -m anonchat.workers.chat_stream --shard 0
poetry run python -m anonchat.workers.chat_stream --shard 1
# ...

```

**Cleanup Worker:**
Keeps Redis memory usage low (Singleton process).

```bash
poetry run python -m anonchat.workers.cleanup_old_messages

```

---

## ✅ Development Status

* [x] **Core Domain:** User, Chat, and Message aggregates fully implemented.
* [x] **High-Load Layer:** Redis Repositories with Pipelining & Streams.
* [x] **Safety:** Distributed Locking for concurrency safety.
* [x] **Persistence:** Sharded background workers for asynchronous SQL syncing.
* [x] **Maintenance:** Automatic Redis cleanup worker.
* [ ] **API/Bot:** Finalizing `aiogram` handlers and presentation layer.
* [ ] **Monitoring:** Prometheus integration for queue length monitoring.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.