# 🏦 FinanceCore — Banking Data Pipeline & Analytics Dashboard

> End-to-end data engineering project: normalized PostgreSQL database, automated ETL pipeline with SQLAlchemy, and a colorful multi-page Streamlit dashboard — all containerized with Docker.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-FF4B4B?style=flat-square&logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red?style=flat-square)

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Relational Model (3NF)](#relational-model-3nf)
- [Getting Started](#getting-started)
- [Services & Ports](#services--ports)
- [Database Schema](#database-schema)
- [SQL Views](#sql-views)
- [Streamlit Dashboard](#streamlit-dashboard)
- [Analytical SQL Queries](#analytical-sql-queries)
- [Environment Variables](#environment-variables)

---

## Project Overview

FinanceCore is a complete banking data pipeline built for the CCFBS Data Engineering curriculum. Starting from a raw CSV file (`financecore_clean.csv`), the project:

1. Designs a normalized **3NF relational model** with 4 tables
2. Creates a **PostgreSQL database** with full integrity constraints, indexes, and views
3. Loads clean data using **Python + SQLAlchemy** with conflict handling
4. Serves a **multi-page Streamlit dashboard** with real-time analytics, dynamic filters, and CSV export

---

## Tech Stack

| Tool | Role |
|------|------|
| PostgreSQL 15 | Relational database engine |
| Python 3.11 | ETL scripting & dashboard backend |
| SQLAlchemy | ORM / database connector |
| Pandas | CSV parsing, cleaning & transformation |
| Streamlit | Interactive analytics dashboard |
| Plotly | Interactive charts (line, bar, pie, scatter) |
| Seaborn + Matplotlib | Correlation heatmap |
| Docker & Docker Compose | Full containerization |
| pgAdmin 4 | Database GUI |
| python-dotenv | Secure environment variable management |

---

## Project Structure

```
financecore/
├── docker-compose.yml              # Orchestrates all 4 services
├── Dockerfile                      # Python ETL container
├── requirements.txt                # Python loader dependencies
├── .env                            # Credentials (not committed)
├── .env.example                    # Template for environment variables
├── .gitignore
│
├── data/
│   └── financecore_clean.csv       # Source data (not committed)
│
├── sql/
│   ├── 01_create_tables.sql        # Table definitions with constraints
│   ├── 02_create_indexes.sql       # Performance indexes
│   └── 03_create_views.sql         # Analytical SQL views
│
├── scripts/
│   └── load_data.py                # ETL script via SQLAlchemy
│
└── streamlit_app/
    ├── Dockerfile                  # Streamlit container
    ├── requirements.txt            # Dashboard dependencies
    ├── app.py                      # Entry point + navigation
    ├── db.py                       # Cached DB connection
    ├── filters.py                  # Shared sidebar filters
    └── pages/
        ├── __init__.py
        ├── executive.py            # Page 1 — Executive View
        └── risk.py                 # Page 2 — Risk Analysis
```

---

## Relational Model (3NF)

The raw CSV was fully denormalized. After applying 3NF normalization, we separated 4 distinct entities:

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│  customers  │       │ transactions │       │  products   │
│─────────────│       │──────────────│       │─────────────│
│ client_id PK│◄──────│ client_id FK │──────►│ produit  PK │
│ segment_... │       │ agence    FK │       │ categorie   │
│ score_cr... │       │ produit   FK │       └─────────────┘
└─────────────┘       │ montant      │
                      │ montant_eur  │       ┌─────────────┐
                      │ devise       │       │  agencies   │
                      │ type_operat. │◄──────│ agence   PK │
                      │ statut       │       └─────────────┘
                      │ solde_avant  │
                      │ taux_interet │
                      └──────────────┘
```

**3NF compliance:**
- All non-key attributes depend only on the primary key
- `segment_client` and `score_credit_client` belong to `customers`, not `transactions`
- `categorie` belongs to `products`, not `transactions`
- No transitive dependencies anywhere

---

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### 1. Clone the repository

```bash
git clone https://github.com/your-username/financecore.git
cd financecore
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
DB_USER=admin
DB_PASSWORD=admin123
DB_HOST=postgres
DB_PORT=5432
DB_NAME=financecore_db
```

### 3. Add your CSV file

Place `financecore_clean.csv` inside the `data/` folder. Your CSV must contain these columns:

```
transaction_id, client_id, date_transaction, montant, devise,
taux_change_eur, montant_eur, categorie, produit, agence,
type_operation, statut, score_credit_client, segment_client,
solde_avant, taux_interet
```

### 4. Start everything

```bash
docker-compose up --build
```

Docker will automatically run in this order:

1. PostgreSQL starts and runs all SQL files (tables → indexes → views)
2. Python ETL loader inserts the CSV data
3. pgAdmin starts at `http://localhost:8080`
4. Streamlit dashboard starts at `http://localhost:8501`

### 5. Fresh reset

```bash
docker-compose down -v
docker-compose up --build
```

---

## Services & Ports

| Service | URL | Credentials |
|---------|-----|-------------|
| **Streamlit Dashboard** | http://localhost:8501 | — |
| **pgAdmin** | http://localhost:8080 | admin@admin.com / admin123 |
| **PostgreSQL** | localhost:5432 | admin / admin123 |

**Connecting pgAdmin to the database:**
- Host: `postgres`
- Port: `5432`
- Database: `financecore_db`
- Username: `admin`
- Password: `admin123`

---

## Database Schema

### `customers`
| Column | Type | Constraint |
|--------|------|------------|
| client_id | VARCHAR(20) | PRIMARY KEY |
| segment_client | VARCHAR(50) | |
| score_credit_client | NUMERIC(5,2) | |

### `agencies`
| Column | Type | Constraint |
|--------|------|------------|
| agence | VARCHAR(100) | PRIMARY KEY |

### `products`
| Column | Type | Constraint |
|--------|------|------------|
| produit | VARCHAR(100) | PRIMARY KEY |
| categorie | VARCHAR(100) | |

### `transactions`
| Column | Type | Constraint |
|--------|------|------------|
| transaction_id | VARCHAR(20) | PRIMARY KEY |
| client_id | VARCHAR(20) | FK → customers |
| agence | VARCHAR(100) | FK → agencies |
| produit | VARCHAR(100) | FK → products |
| date_transaction | DATE | NOT NULL |
| montant | NUMERIC(15,2) | NOT NULL |
| devise | VARCHAR(10) | |
| taux_change_eur | NUMERIC(10,6) | |
| montant_eur | NUMERIC(15,2) | |
| type_operation | VARCHAR(50) | |
| statut | VARCHAR(30) | |
| solde_avant | NUMERIC(15,2) | |
| taux_interet | NUMERIC(6,4) | |

### Indexes

```sql
idx_transactions_client_id   ON transactions(client_id)
idx_transactions_agence      ON transactions(agence)
idx_transactions_date        ON transactions(date_transaction)
idx_transactions_produit     ON transactions(produit)
idx_transactions_statut      ON transactions(statut)
```

---

## SQL Views

### `vw_transaction_details`
Full denormalized view joining all 4 tables — base for all dashboard queries.

### `vw_agency_monthly_kpi`
Total and average transactions per agency per month.

```sql
SELECT agence, mois, nb_transactions, total_eur, moyenne_eur
FROM vw_agency_monthly_kpi
ORDER BY mois DESC, total_eur DESC;
```

### `vw_client_solde_vs_moyenne`
Compares each client's average balance against the national average using window functions.

```sql
SELECT client_id, segment_client, solde_moyen, moyenne_nationale, statut_solde
FROM vw_client_solde_vs_moyenne
WHERE statut_solde = 'En dessous de la moyenne';
```

### `vw_taux_defaut_segment`
Rejection rate by customer risk segment using `CASE WHEN`.

```sql
SELECT segment_client, total_clients, en_defaut, taux_defaut_pct
FROM vw_taux_defaut_segment
ORDER BY taux_defaut_pct DESC;
```

---

## Streamlit Dashboard

The dashboard has 2 pages accessible from the sidebar. The UI is dark-themed with a colorful, vibrant design.

### 📊 Page 1 — Executive View

| Component | Description |
|-----------|-------------|
| 6 KPI Cards | Total transactions, volume (EUR), active clients, avg amount, completed, rejected |
| Line Chart | Monthly transaction volume by operation type |
| Pie Chart | Customer distribution by segment |
| Horizontal Bar | Revenue by agency with transaction count labels |
| Bar Chart | Revenue by product |
| Data Table | Last 200 transactions with color-coded status and amounts |
| Status Breakdown | Count and volume by status (Complete / Rejeté / En attente) |
| CSV Export | Download filtered data directly from the sidebar |

### ⚠️ Page 2 — Risk Analysis

| Component | Description |
|-----------|-------------|
| 5 Risk KPIs | Avg credit score, total rejections, rejection rate, at-risk clients, total clients |
| Scatter Plot | Credit score vs transaction amount, colored by status |
| Bar Chart | Rejection rate by customer segment |
| Heatmap | Correlation matrix (credit score, amount, interest rate, balance, rejection) |
| Top 10 Risk Table | Highest-risk clients with color-coded rejection rate and credit score |
| Trend Chart | Monthly rejection count and rate over time (dual axis) |
| CSV Export | Download risk-filtered data from the sidebar |

### Dynamic Sidebar Filters

All charts and tables respond in real time to: Agency, Customer Segment, Product, and Year Range (2022–2024).

---

## Analytical SQL Queries

### Total & average transactions per agency

```sql
SELECT agence,
       COUNT(*) AS nb_transactions,
       SUM(ABS(montant_eur)) AS total_eur,
       ROUND(AVG(ABS(montant_eur)), 2) AS moyenne_eur
FROM transactions
GROUP BY agence
ORDER BY total_eur DESC;
```

### Clients below national average balance

```sql
SELECT client_id, segment_client, solde_moyen
FROM vw_client_solde_vs_moyenne
WHERE statut_solde = 'En dessous de la moyenne'
ORDER BY solde_moyen ASC;
```

### Transaction volume by product and month

```sql
SELECT produit,
       DATE_TRUNC('month', date_transaction) AS mois,
       COUNT(*) AS nb,
       SUM(ABS(montant_eur)) AS total_eur
FROM transactions
GROUP BY produit, DATE_TRUNC('month', date_transaction)
ORDER BY mois DESC, total_eur DESC;
```

### Rejection rate by segment (CASE WHEN)

```sql
SELECT c.segment_client,
       COUNT(DISTINCT t.client_id) AS total_clients,
       SUM(CASE WHEN t.statut = 'Rejeté' THEN 1 ELSE 0 END) AS nb_rejets,
       ROUND(
           SUM(CASE WHEN t.statut = 'Rejeté' THEN 1 ELSE 0 END)::NUMERIC
           / NULLIF(COUNT(DISTINCT t.client_id), 0) * 100, 2
       ) AS taux_rejet_pct
FROM transactions t
JOIN customers c ON t.client_id = c.client_id
GROUP BY c.segment_client
ORDER BY taux_rejet_pct DESC;
```

### Top agencies by transaction count (HAVING)

```sql
SELECT agence, COUNT(*) AS nb_transactions
FROM transactions
GROUP BY agence
HAVING COUNT(*) > 100
ORDER BY nb_transactions DESC;
```

### Credit score vs rejection by segment (subquery)

```sql
SELECT segment_client,
       ROUND(AVG(score_credit_client), 1) AS avg_score,
       ROUND(AVG(taux_rejet_pct), 2) AS avg_rejet_pct
FROM (
    SELECT c.segment_client,
           c.score_credit_client,
           ROUND(
               SUM(CASE WHEN t.statut = 'Rejeté' THEN 1 ELSE 0 END)::NUMERIC
               / NULLIF(COUNT(*), 0) * 100, 2
           ) AS taux_rejet_pct
    FROM transactions t
    JOIN customers c ON t.client_id = c.client_id
    GROUP BY c.client_id, c.segment_client, c.score_credit_client
) sub
GROUP BY segment_client
ORDER BY avg_rejet_pct DESC;
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_USER` | PostgreSQL username | admin |
| `DB_PASSWORD` | PostgreSQL password | admin123 |
| `DB_HOST` | Database host (Docker service name) | postgres |
| `DB_PORT` | Database port | 5432 |
| `DB_NAME` | Database name | financecore_db |

> ⚠️ Never commit your `.env` file. Use `.env.example` as the template.

### `.gitignore`

```
.env
data/financecore_clean.csv
__pycache__/
*.pyc
.DS_Store
```

---

## Useful Commands

```bash
# Start all services
docker-compose up --build

# Start in background
docker-compose up -d --build

# Stop all services
docker-compose down

# Full reset (wipes database volume)
docker-compose down -v

# Re-run the data loader only
docker-compose run python

# View logs
docker-compose logs postgres
docker-compose logs python
docker-compose logs streamlit

# Connect to PostgreSQL directly
docker exec -it financecore_db psql -U admin -d financecore_db
```

---

## Author

Project completed as part of the **CCFBS Data Engineering curriculum**.
Assignment period: **April 6 – April 17, 2025**
