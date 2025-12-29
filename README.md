# Anochat

**Anochat** is a core for an anonymous chat bot (chat-roulette) built upon **Clean Architecture** and **Domain-Driven Design (DDD)** principles. The project focuses on strict typing, separation of concerns, and performance.

## 🛠 Tech Stack

* **Language:** Python 3.14+
* **Web Framework / Bot:** aiogram 3.x
* **Database:** PostgreSQL + asyncpg
* **ORM:** SQLAlchemy 2.0 (Async)
* **Validation:** Pydantic V2
* **Mapping:** manual mappers.

## 🏗 Architecture

The project follows a layered architecture:

1. **Domain Layer**: Contains pure business logic.
* **Aggregates**: `User`, `PrivateChat`, `Message`.
* **Value Objects**: `Reputation`, `Interests`, `MessageContent` (text + media).
* **Protocols (Interfaces)**: Repositories (`IUserRepo`, `IChatRepo`) and UoW (`IChatUoW`).


2. **Application Layer (Use Cases)**: Scenarios that orchestrate the domain logic.
* `StartChat` (creates a unique 1:1 dialog).
* `SendMessage` (validation and sending).
* User Management (`Create`, `Get`, `Update`, `Delete`).


3. **Infrastructure Layer**: Database implementation.
* SQLAlchemy Models (`UserModel`, `PrivateChatModel`, `MessageModel`).
* Mappers (`Model` <-> `Entity`).



## ✨ Current Features

* **Users:**
* Registration and profiling (gender, age, interests).
* Reputation system (likes/dislikes).
* Search settings.


* **1-on-1 Chats:**
* Strict "one active dialog per user" logic.
* Lightweight chat aggregates (store only IDs for performance).


* **Messages:**
* Text messages support (up to 4096 chars).
* Media attachments support (photos/videos).



## 🚀 Installation & Run

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/anochat.git

```


2. **Install dependencies (using Poetry):**
```bash
poetry install

```


3. **Environment Setup:**
Create a `.env` file and specify your database connection parameters and bot token.
4. **Run (example):**
```bash
poetry run python -m anonchat.main

```



## ✅ TODO (Roadmap)

Based on the current analysis of the codebase, the following components need implementation:

* [ ] **Implement `GetCurrentChat` Use Case**: Required to strictly check user status ("busy/free") before starting a new chat.
* [ ] **Implement `GetChatHistory` Use Case**: The repository interface `IMessageRepo` already has `get_by_chat_id` methods, but the use case itself is missing.
* [ ] **Close Chat Logic**: Implement a Use Case for the `PrivateChat.close_chat()` method.
* [ ] **Presentation Layer (Bot Handlers)**: Write `aiogram` handlers that will invoke the implemented Use Cases.
* [ ] **Database Migrations**: Set up `alembic` to create tables based on SQLAlchemy models.
* [ ] **Redis**: Connect Redis for storing temporary FSM states (listed in dependencies, but not yet used in the code).