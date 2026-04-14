import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from db import run_query
from filters import render_filters, build_where_clause


def show():
    st.markdown('<div class="main-header">📊 Executive View</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">FinanceCore SA — Business Performance Dashboard</div>', unsafe_allow_html=True)

    filters = render_filters()
    # where, params = build_where_clause(filters)
    where = ""
    params = {}

    # ─── Export Button ───────────────────────────────────────────────────────
    export_query = f"""
        SELECT t.transaction_id, t.date_transaction, t.montant_eur,
               t.type_operation, t.statut, t.agence, t.produit,
               c.client_id, c.segment_client, c.score_credit_client
        FROM transactions t
        JOIN customers c ON t.client_id = c.client_id
        {where}
        ORDER BY t.date_transaction DESC
    """
    export_df = run_query(export_query, params)
    if not export_df.empty:
        csv = export_df.to_csv(index=False).encode("utf-8")
        st.sidebar.download_button(
            label="⬇️ Export filtered data (CSV)",
            data=csv,
            file_name="financecore_filtered.csv",
            mime="text/csv"
        )

    # ─── KPI Cards ───────────────────────────────────────────────────────────
    kpi_query = f"""
        SELECT
            COUNT(t.transaction_id) AS nb_transactions,
            ROUND(COALESCE(SUM(t.montant_eur), 0)::NUMERIC, 2) AS total_volume,
            COUNT(DISTINCT t.client_id) AS active_clients,
            ROUND(COALESCE(AVG(t.montant_eur), 0)::NUMERIC, 2) AS avg_transaction
        FROM transactions t
        JOIN customers c ON t.client_id = c.client_id
        {where}
    """
    kpi = run_query(kpi_query, params)

    if not kpi.empty:
        col1, col2, col3, col4 = st.columns(4)
        # metrics = [
        #     (col1, "💳 Total Transactions",   f"{int(kpi['nb_transactions'][0]):,}",        ""),
        #     (col2, "💶 Total Volume (EUR)",    f"€{float(kpi['total_volume'][0]):,.0f}",     ""),
        #     (col3, "👥 Active Customers",      f"{int(kpi['active_clients'][0]):,}",         ""),
        #     (col4, "📈 Avg Transaction (EUR)", f"€{float(kpi['avg_transaction'][0]):,.2f}",  ""),
        # ]

        nb_transactions = kpi['nb_transactions'][0] or 0
        total_volume = kpi['total_volume'][0] or 0
        active_clients = kpi['active_clients'][0] or 0
        avg_transaction = kpi['avg_transaction'][0] or 0

        metrics = [
            (col1, "💳 Total Transactions",   f"{int(nb_transactions):,}", ""),
            (col2, "💶 Total Volume (EUR)",   f"€{float(total_volume):,.0f}", ""),
            (col3, "👥 Active Customers",     f"{int(active_clients):,}", ""),
            (col4, "📈 Avg Transaction (EUR)",f"€{float(avg_transaction):,.2f}", ""),
        ]
        for col, label, value, delta in metrics:
            with col:
                st.metric(label=label, value=value)

    st.markdown("---")

    # ─── Line Chart: Monthly evolution ───────────────────────────────────────
    st.subheader("📈 Monthly Evolution of Transactions (EUR)")
    monthly_query = f"""
        SELECT
            DATE_TRUNC('month', t.date_transaction) AS mois,
            t.type_operation,
            ROUND(SUM(t.montant_eur)::NUMERIC, 2) AS total_eur
        FROM transactions t
        JOIN customers c ON t.client_id = c.client_id
        {where}
        GROUP BY DATE_TRUNC('month', t.date_transaction), t.type_operation
        ORDER BY mois
    """
    monthly_df = run_query(monthly_query, params)
    if not monthly_df.empty:
        monthly_df["mois"] = pd.to_datetime(monthly_df["mois"])
        fig_line = px.line(
            monthly_df, x="mois", y="total_eur", color="type_operation",
            labels={"mois": "Month", "total_eur": "Amount (EUR)", "type_operation": "Operation"},
            color_discrete_sequence=px.colors.qualitative.Set2,
            template="plotly_white"
        )
        fig_line.update_layout(legend_title_text="Operation Type", height=400)
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No data available for this period.")

    st.markdown("---")

    # ─── Bar Charts ──────────────────────────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🏢 Revenue by Agency")
        agency_query = f"""
            SELECT t.agence, ROUND(SUM(t.montant_eur)::NUMERIC, 2) AS total_eur
            FROM transactions t
            JOIN customers c ON t.client_id = c.client_id
            {where}
            GROUP BY t.agence
            ORDER BY total_eur DESC
        """
        agency_df = run_query(agency_query, params)
        if not agency_df.empty:
            fig_agency = px.bar(
                agency_df, x="total_eur", y="agence", orientation="h",
                labels={"total_eur": "Revenue (EUR)", "agence": "Agency"},
                color="total_eur",
                color_continuous_scale="Blues",
                template="plotly_white"
            )
            fig_agency.update_layout(coloraxis_showscale=False, height=400)
            st.plotly_chart(fig_agency, use_container_width=True)

    with col_right:
        st.subheader("📦 Revenue by Product")
        product_query = f"""
            SELECT t.produit, ROUND(SUM(t.montant_eur)::NUMERIC, 2) AS total_eur
            FROM transactions t
            JOIN customers c ON t.client_id = c.client_id
            {where}
            GROUP BY t.produit
            ORDER BY total_eur DESC
        """
        product_df = run_query(product_query, params)
        if not product_df.empty:
            fig_product = px.bar(
                product_df, x="produit", y="total_eur",
                labels={"total_eur": "Revenue (EUR)", "produit": "Product"},
                color="total_eur",
                color_continuous_scale="Teal",
                template="plotly_white"
            )
            fig_product.update_layout(coloraxis_showscale=False, height=400, xaxis_tickangle=-30)
            st.plotly_chart(fig_product, use_container_width=True)

    st.markdown("---")

    # ─── Pie Chart: Customer Segments ────────────────────────────────────────
    st.subheader("🥧 Customer Distribution by Segment")
    segment_query = f"""
        SELECT c.segment_client, COUNT(DISTINCT t.client_id) AS nb_clients
        FROM transactions t
        JOIN customers c ON t.client_id = c.client_id
        {where}
        GROUP BY c.segment_client
    """
    segment_df = run_query(segment_query, params)
    col_pie, col_space = st.columns([1, 1])
    with col_pie:
        if not segment_df.empty:
            fig_pie = px.pie(
                segment_df, names="segment_client", values="nb_clients",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                template="plotly_white",
                hole=0.4
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
