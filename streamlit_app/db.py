import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import streamlit as st
import logging

load_dotenv("/app/.env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_USER     = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
DB_HOST     = os.getenv("DB_HOST", "postgres")
DB_PORT     = os.getenv("DB_PORT", "5432")
DB_NAME     = os.getenv("DB_NAME", "financecore_db")

@st.cache_resource
def get_engine():
    try:
        engine = create_engine(
            f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
            pool_pre_ping=True
        )
        return engine
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

@st.cache_data(ttl=300)
def run_query(query: str, params: dict = None) -> pd.DataFrame:
    engine = get_engine()
    if engine is None:
        return pd.DataFrame()
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(query), conn, params=params)
    except Exception as e:
        st.error(f"Query error: {e}")
        return pd.DataFrame()