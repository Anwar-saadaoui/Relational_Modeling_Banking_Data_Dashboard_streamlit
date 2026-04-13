import streamlit as st
from db import run_query
import pandas as pd


def render_filters() -> dict:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎛️ Filters")

    # --- Agency ---
    agencies_df = run_query("SELECT DISTINCT agence FROM agencies ORDER BY agence")
    agencies = ["All"] + agencies_df["agence"].tolist() if not agencies_df.empty else ["All"]
    selected_agency = st.sidebar.selectbox("🏢 Agency", agencies)

    # --- Segment ---
    segments_df = run_query("SELECT DISTINCT segment_client FROM customers WHERE segment_client IS NOT NULL ORDER BY segment_client")
    segments = ["All"] + segments_df["segment_client"].tolist() if not segments_df.empty else ["All"]
    selected_segment = st.sidebar.selectbox("👤 Customer Segment", segments)

    # --- Product ---
    products_df = run_query("SELECT DISTINCT produit FROM products ORDER BY produit")
    products = ["All"] + products_df["produit"].tolist() if not products_df.empty else ["All"]
    selected_product = st.sidebar.selectbox("📦 Product", products)

    # --- Period ---
    year_range = st.sidebar.slider("📅 Period (Year)", 2022, 2024, (2022, 2024))

    return {
        "agency":   selected_agency,
        "segment":  selected_segment,
        "product":  selected_product,
        "year_min": year_range[0],
        "year_max": year_range[1],
    }


def build_where_clause(filters: dict) -> tuple:
    conditions = [
        "EXTRACT(YEAR FROM t.date_transaction) BETWEEN :year_min AND :year_max"
    ]
    params = {
        "year_min": filters["year_min"],
        "year_max": filters["year_max"],
    }
    if filters["agency"] != "All":
        conditions.append("t.agence = :agency")
        params["agency"] = filters["agency"]
    if filters["segment"] != "All":
        conditions.append("c.segment_client = :segment")
        params["segment"] = filters["segment"]
    if filters["product"] != "All":
        conditions.append("t.produit = :product")
        params["product"] = filters["product"]

    where = "WHERE " + " AND ".join(conditions)
    return where, params
