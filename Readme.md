# 🏢 Organization Management Service

> A robust, multi-tenant backend service built with **FastAPI** and **MongoDB**, featuring dynamic collection-based tenancy, secure authentication, and scalable architecture.

## 📖 Overview
This project implements a **Multi-Tenant SaaS Architecture** where each organization's data is isolated in its own MongoDB collection. It provides a RESTful API for managing organizations, handling secure Admin authentication (JWT), and dynamically syncing data across collections during updates.

---

## 📂 Project Structure

```text
backend-assignment/
├── app/
│   ├── core/           # Config & Security (JWT/Hashing)
│   ├── database/       # MongoDB Connection Logic
│   ├── models/         # Pydantic Schemas
│   ├── routes/         # API Endpoints
│   ├── services/       # Business Logic
│   └── main.py         # Entry Point
├── .env                # Secrets (Ignored by Git)
├── .gitignore
├── requirements.txt
└── README.md
```
---

## 🏗️ High-Level Architecture

The system follows a **Collection-Based Multi-Tenancy** model. A central `Master DB` holds the routing logic and authentication data, while dynamic collections are spawned for each new tenant.

```mermaid
graph TD
    %% -- Client Layer --
    Client([Client / Frontend])
    
    %% -- API Gateway / Application Layer --
    subgraph "FastAPI Application Server"
        Entry[API Router]
        
        subgraph "Security Layer"
            AuthGuard[JWT Dependency Guard]
        end
        
        subgraph "Business Logic Layer (Services)"
            AuthService[Auth Service]
            OrgService[Organization Service]
        end
        
        subgraph "Data Access Layer"
            MasterConn[Master DB Connection]
            TenantConn[Dynamic Tenant Connection]
        end
    end

    %% -- Database Layer --
    subgraph "Database Cluster (MongoDB)"
        subgraph "Master Database"
            Users[(Users Coll)]
            Meta[(Metadata Coll)]
        end
        
        subgraph "Tenant Databases (Dynamic)"
            T1[(org_Tesla)]
            T2[(org_SpaceX)]
            T3[(org_...)]
        end
    end

    %% -- Connections --
    Client -->|HTTP Request| Entry
    
    Entry -->|Login/Public| AuthService
    Entry -->|Protected Routes| AuthGuard
    AuthGuard -->|If Valid| OrgService
    
    AuthService --> MasterConn
    OrgService --> MasterConn
    OrgService -->|Switch Context| TenantConn
    
    MasterConn -->|Read/Write| Users
    MasterConn -->|Read/Write| Meta
    
    TenantConn -->|CRUD Operations| T1
    TenantConn -->|CRUD Operations| T2
    TenantConn -->|CRUD Operations| T3

    %% -- Styling --
    classDef client fill:#2d3436,stroke:#636e72,color:#fff;
    classDef app fill:#f1f2f6,stroke:#dfe6e9,color:#2d3436;
    classDef security fill:#d63031,stroke:#b71540,color:#fff;
    classDef service fill:#0984e3,stroke:#00cec9,color:#fff;
    classDef db fill:#6c5ce7,stroke:#a29bfe,color:#fff;
    classDef tenant fill:#00b894,stroke:#55efc4,color:#fff;

    class Client client;
    class Entry,MasterConn,TenantConn app;
    class AuthGuard security;
    class AuthService,OrgService service;
    class Users,Meta db;
    class T1,T2,T3 tenant;
```

---

## 🚀 Features

* **Multi-Tenancy:**  
  Automatic creation of dedicated collections (`org_<name>`) for data isolation.

* **Secure Authentication:**  
  - JWT (JSON Web Tokens) for stateless session management  
  - Bcrypt hashing for password security

* **Dynamic Operations:**  
  - Create Organization (spawns new collection)  
  - Update Organization (renames collection & syncs metadata)  
  - Delete Organization (cascading delete of Admin, Metadata, Data)

* **Documentation:**  
  Auto-generated interactive API docs via Swagger UI.

---

## 🛠️ Tech Stack

* **Framework:** Python 3.10+, FastAPI  
* **Database:** MongoDB (via PyMongo)  
* **Security:** PyJWT, Passlib, Bcrypt  
* **Server:** Uvicorn (ASGI)

---

## ⚙️ Setup Instructions

Follow these steps to run the application locally.

### 1. Prerequisites
* Python 3.10 or higher  
* MongoDB installed locally OR a MongoDB Atlas connection string

---

### 2. Clone the Repository

```bash
git clone https://github.com/Gautham07s/org-management.git
cd org-management
```

---

### 3. Create Virtual Environment

```bash
# Windows
python -m venv venv
.env\Scriptsctivate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

---

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 5. Environment Configuration

Create a `.env` file in the root directory:

```env
MONGO_URI=mongodb://localhost:27017
DB_NAME=master_db
SECRET_KEY=replace_this_with_a_secure_random_string
ALGORITHM=HS256
```

If using MongoDB Atlas, replace `MONGO_URI` with your cluster connection string.

---

### 6. Run the Application

```bash
uvicorn app.main:app --reload
```

The server will start at:  
**http://127.0.0.1:8000**

---

## 📚 API Documentation

FastAPI provides an automatic, interactive documentation page.

1. Run the server.  
2. Open your browser to:  
   **http://127.0.0.1:8000/docs**

---

### Key Endpoints

| Method | Endpoint        | Description                         | Auth Required |
|--------|------------------|---------------------------------------|---------------|
| POST   | `/org/create`    | Register a new Organization           | ❌ |
| POST   | `/admin/login`   | Login and get Access Token            | ❌ |
| GET    | `/org/get`       | Fetch Org details by name             | ❌ |
| PUT    | `/org/update`    | Rename/Update Org & Sync Data         | ✅ |
| DELETE | `/org/delete`    | Delete Org and all its Data           | ✅ |

---

## 💡 Design Choices & Trade-offs

### 1. Why FastAPI?

* **Speed:** Comparable to Node.js/Go  
* **Productivity:** Built-in validation (Pydantic) and API docs  
* **Async:** Native asynchronous support for database operations  

---

### 2. Database Architecture: Collection-Based Tenancy

* **Decision:** Use a dynamic collection per organization  
* **Benefits:**  
  - Better data isolation than Row-based tenancy  
  - Easier backups and deletions than Database-per-tenant  
  - Ideal “middle ground” for medium-scale SaaS  
* **Trade-off:**  
  At extremely large scale (10,000+ orgs), MongoDB may hit limits on collection count.  
  Future migration: **Sharded database-per-tenant** architecture.

---

### 3. Modular Code Structure

The project follows a Service-Repository pattern:

```
routes → services → database → models
```

This ensures the codebase is clean, maintainable, and testable.

---
