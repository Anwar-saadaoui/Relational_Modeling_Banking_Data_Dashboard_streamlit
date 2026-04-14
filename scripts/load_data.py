from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import pandas as pd
import time
import os

load_dotenv("/app/.env")

time.sleep(8)

DB_USER     = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
DB_HOST     = os.getenv("DB_HOST", "postgres")
DB_PORT     = os.getenv("DB_PORT", "5432")
DB_NAME     = os.getenv("DB_NAME", "financecore_db")

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ─── Load & Clean ────────────────────────────────────────────────
df = pd.read_csv("/data/financecore_clean.csv")
df.columns = df.columns.str.strip().str.lower()

print(f"Total rows before cleaning: {len(df)}")

# Ensure transaction_id exists
if 'transaction_id' not in df.columns:
    df['transaction_id'] = df.index.astype(str)

# Drop rows missing critical FK columns
df = df.dropna(subset=['client_id', 'agence', 'produit', 'transaction_id'])

# Parse and drop invalid dates
df['date_transaction'] = pd.to_datetime(df['date_transaction'], errors='coerce')
df = df.dropna(subset=['date_transaction'])

# Drop duplicate transaction IDs
df = df.drop_duplicates(subset=['transaction_id'])

print(f"Total rows after cleaning: {len(df)}")

# ─── Separate Tables ─────────────────────────────────────────────
customers = df[['client_id', 'segment_client', 'score_credit_client']].drop_duplicates('client_id')

agencies = df[['agence']].drop_duplicates().dropna()

products = df[['produit', 'categorie']].drop_duplicates('produit').dropna(subset=['produit'])

transactions = df[[
    'transaction_id', 'client_id', 'agence', 'produit',
    'date_transaction', 'montant', 'devise', 'taux_change_eur',
    'montant_eur', 'type_operation', 'statut', 'solde_avant', 'taux_interet'
]].copy()

print(f"customers: {len(customers)}, agencies: {len(agencies)}, products: {len(products)}, transactions: {len(transactions)}")

# ─── Insert ──────────────────────────────────────────────────────
def insert_table(dataframe, table_name):
    try:
        with engine.begin() as conn:
            dataframe.to_sql(table_name, conn, if_exists='append', index=False, method='multi')
        print(f"✅ {table_name} inserted ({len(dataframe)} rows)")
    except Exception as e:
        print(f"❌ {table_name} error: {e}")

insert_table(customers,    'customers')
insert_table(agencies,     'agencies')
insert_table(products,     'products')
insert_table(transactions, 'transactions')

# ─── Verify ──────────────────────────────────────────────────────
print("\n--- Row counts ---")
with engine.connect() as conn:
    for table in ['customers', 'agencies', 'products', 'transactions']:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
        print(f"  {table}: {result.scalar()} rows")