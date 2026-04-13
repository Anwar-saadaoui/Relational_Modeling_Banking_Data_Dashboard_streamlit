from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import pandas as pd
import time
import os

# ─────────────────────────────
# Load env
# ─────────────────────────────
load_dotenv("/app/.env")

time.sleep(8)

DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "financecore_db")

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ─────────────────────────────
# Load CSV
# ─────────────────────────────
df = pd.read_csv("/data/financecore_clean.csv")


# ───────── SAFE TRANSACTIONS ─────────

df.columns = df.columns.str.strip().str.lower()

# force ID existence
if 'transaction_id' not in df.columns:
    df['transaction_id'] = range(len(df))

# safe date parsing (DO NOT DELETE ROWS YET)
df['date_transaction'] = pd.to_datetime(df['date_transaction'], errors='coerce')

transactions = df[[
    'transaction_id',
    'client_id',
    'agence',
    'produit',
    'date_transaction',
    'montant',
    'montant_eur',
    'type_operation',
    'statut',
    'solde_avant',
    'taux_interet'
]].copy()

# ONLY drop critical missing values
transactions = transactions.dropna(subset=['client_id', 'agence', 'produit'])

# DO NOT DROP date_transaction yet

# Clean column names (IMPORTANT FIX)
df.columns = df.columns.str.strip().str.lower()

print(f"Total rows before cleaning: {len(df)}")

# ─────────────────────────────
# Safety checks
# ─────────────────────────────
required_cols = [
    'date_transaction',
    'agence',
    'produit',
    'client_id'
]

for col in required_cols:
    if col not in df.columns:
        raise Exception(f"Missing column in CSV: {col}")

# Ensure transaction_id exists
if 'transaction_id' not in df.columns:
    df['transaction_id'] = df.index

# Drop invalid rows
df = df.dropna(subset=required_cols)

df['date_transaction'] = pd.to_datetime(df['date_transaction'], errors='coerce')
df = df.dropna(subset=['date_transaction'])

print(f"Total rows after cleaning: {len(df)}")

# ─────────────────────────────
# Tables
# ─────────────────────────────
customers = df[['client_id', 'segment_client', 'score_credit_client']].drop_duplicates('client_id')

agencies = df[['agence']].drop_duplicates().dropna()

products = df[['produit']].drop_duplicates().dropna()

transactions = df[[
    'transaction_id',
    'client_id',
    'agence',
    'produit',
    'date_transaction',
    'montant',
    'montant_eur',
    'type_operation',
    'statut',
    'solde_avant',
    'taux_interet'
]].copy()

print(f"""
customers: {len(customers)}
agencies: {len(agencies)}
products: {len(products)}
transactions: {len(transactions)}
""")

# ─────────────────────────────
# Insert function
# ─────────────────────────────
def insert_table(df, table_name):
    try:
        with engine.begin() as conn:
            df.to_sql(table_name, conn, if_exists='append', index=False, method='multi')
        print(f"✅ {table_name} inserted ({len(df)} rows)")
    except Exception as e:
        print(f"❌ {table_name} error: {e}")

# ─────────────────────────────
# Load data
# ─────────────────────────────
insert_table(customers, 'customers')
insert_table(agencies, 'agencies')
insert_table(products, 'products')
insert_table(transactions, 'transactions')

# ─────────────────────────────
# Verify
# ─────────────────────────────
print("\n--- Row counts ---")
with engine.connect() as conn:
    for table in ['customers', 'agencies', 'products', 'transactions']:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
        print(f"{table}: {result.scalar()} rows")