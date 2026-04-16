import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from db import run_query
from filters import render_filters, build_where_clause

COLORS = ["#e94560", "#f5a623", "#00b4d8", "#7bed9f", "#a29bfe", "#fd79a8", "#fdcb6e", "#00cec9"]
DARK_BG = "#1a1a2e"
PAPER_BG = "#16213e"

def chart_layout(fig, title=""):
    fig.update_layout(
        title=title,
        title_font=dict(color="white", size=14),
        plot_bgcolor=DARK_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(color="white"),
        xaxis=dict(gridcolor="#333", color="white"),
        yaxis=dict(gridcolor="#333", color="white"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="white")),
        margin=dict(l=20, r=20, t=40, b=20),
        height=350
    )
    return fig

def show():
    st.write("EXECUTIVE PAGE LOADED")
    st.markdown("# 📊 Executive View")
    st.markdown("<p style='text-align:center;color:#888;margin-top:-1rem;'>Business Performance Dashboard — FinanceCore SA</p>", unsafe_allow_html=True)
    
    filters = render_filters()
    where, params = build_where_clause(filters)

    # Export
    export_q = f"""
        SELECT t.transaction_id, t.date_transaction, t.montant_eur, t.type_operation,
               t.statut, t.agence, t.produit, c.client_id, c.segment_client
        FROM transactions t JOIN customers c ON t.client_id = c.client_id {where}
        ORDER BY t.date_transaction DESC
    """
    export_df = run_query(export_q, params)
    if not export_df.empty:
        st.sidebar.download_button(
            "⬇️ Export CSV",
            export_df.to_csv(index=False).encode("utf-8"),
            "financecore_export.csv", "text/csv"
        )

    st.markdown("---")

    # ── KPIs ──────────────────────────────────────────────
    kpi_q = f"""
        SELECT
            COUNT(t.transaction_id)                        AS nb_transactions,
            ROUND(SUM(ABS(t.montant_eur))::NUMERIC, 0)    AS total_volume,
            COUNT(DISTINCT t.client_id)                    AS active_clients,
            ROUND(AVG(ABS(t.montant_eur))::NUMERIC, 2)    AS avg_transaction,
            SUM(CASE WHEN t.statut = 'Complete' THEN 1 ELSE 0 END) AS completed,
            SUM(CASE WHEN t.statut = 'Rejeté' THEN 1 ELSE 0 END)   AS rejected
        FROM transactions t JOIN customers c ON t.client_id = c.client_id {where}
    """
    kpi = run_query(kpi_q, params)

    if not kpi.empty:
        k = kpi.iloc[0]
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        kpi_data = [
            (c1, "💳 Transactions",    f"{int(k['nb_transactions']):,}",         "#e94560"),
            (c2, "💶 Volume (EUR)",    f"€{int(k['total_volume']):,}",            "#f5a623"),
            (c3, "👥 Active Clients",  f"{int(k['active_clients']):,}",           "#00b4d8"),
            (c4, "📈 Avg Amount",      f"€{float(k['avg_transaction']):,.2f}",    "#7bed9f"),
            (c5, "✅ Completed",       f"{int(k['completed']):,}",                "#a29bfe"),
            (c6, "❌ Rejected",        f"{int(k['rejected']):,}",                 "#fd79a8"),
        ]
        for col, label, value, color in kpi_data:
            with col:
                st.markdown(f"""
                <div class="kpi-card" style="border-color:{color};">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value" style="color:{color};">{value}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1: Line chart + Donut ──────────────────────────
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="section-title" style="border-color:#e94560;">📈 Monthly Transaction Volume</div>', unsafe_allow_html=True)
        monthly_q = f"""
            SELECT DATE_TRUNC('month', t.date_transaction) AS mois,
                   t.type_operation,
                   ROUND(SUM(ABS(t.montant_eur))::NUMERIC, 2) AS total
            FROM transactions t JOIN customers c ON t.client_id = c.client_id {where}
            GROUP BY DATE_TRUNC('month', t.date_transaction), t.type_operation
            ORDER BY mois
        """
        monthly_df = run_query(monthly_q, params)
        if not monthly_df.empty:
            monthly_df["mois"] = pd.to_datetime(monthly_df["mois"])
            fig = px.line(monthly_df, x="mois", y="total", color="type_operation",
                          color_discrete_sequence=COLORS, markers=True)
            fig = chart_layout(fig)
            fig.update_traces(line=dict(width=2.5))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title" style="border-color:#f5a623;">🥧 By Segment</div>', unsafe_allow_html=True)
        seg_q = f"""
            SELECT c.segment_client, COUNT(DISTINCT t.client_id) AS nb
            FROM transactions t JOIN customers c ON t.client_id = c.client_id {where}
            GROUP BY c.segment_client
        """
        seg_df = run_query(seg_q, params)
        if not seg_df.empty:
            fig = px.pie(seg_df, names="segment_client", values="nb",
                         color_discrete_sequence=COLORS, hole=0.55)
            fig.update_traces(textfont_color="white")
            fig = chart_layout(fig)
            fig.update_layout(showlegend=True, height=350)
            st.plotly_chart(fig, use_container_width=True)

    # ── Row 2: Agency bar + Product bar ───────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-title" style="border-color:#00b4d8;">🏢 Revenue by Agency</div>', unsafe_allow_html=True)
        agency_q = f"""
            SELECT t.agence,
                   ROUND(SUM(ABS(t.montant_eur))::NUMERIC, 0) AS total_eur,
                   COUNT(*) AS nb_transactions
            FROM transactions t JOIN customers c ON t.client_id = c.client_id {where}
            GROUP BY t.agence ORDER BY total_eur DESC
        """
        agency_df = run_query(agency_q, params)
        if not agency_df.empty:
            fig = px.bar(agency_df, x="total_eur", y="agence", orientation="h",
                         color="total_eur", color_continuous_scale=["#00b4d8", "#e94560"],
                         text="nb_transactions")
            fig.update_traces(texttemplate="%{text} txns", textposition="inside",
                              textfont_color="white")
            fig = chart_layout(fig)
            fig.update_layout(coloraxis_showscale=False, yaxis_title="", xaxis_title="Volume (EUR)")
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown('<div class="section-title" style="border-color:#7bed9f;">📦 Revenue by Product</div>', unsafe_allow_html=True)
        prod_q = f"""
            SELECT t.produit,
                   ROUND(SUM(ABS(t.montant_eur))::NUMERIC, 0) AS total_eur,
                   COUNT(*) AS nb
            FROM transactions t JOIN customers c ON t.client_id = c.client_id {where}
            GROUP BY t.produit ORDER BY total_eur DESC
        """
        prod_df = run_query(prod_q, params)
        if not prod_df.empty:
            fig = px.bar(prod_df, x="produit", y="total_eur",
                         color="produit", color_discrete_sequence=COLORS,
                         text="total_eur")
            fig.update_traces(texttemplate="€%{text:,.0f}", textposition="outside",
                              textfont_color="white")
            fig = chart_layout(fig)
            fig.update_layout(showlegend=False, xaxis_tickangle=-30,
                              xaxis_title="", yaxis_title="Volume (EUR)")
            st.plotly_chart(fig, use_container_width=True)

    # ── Data Table ────────────────────────────────────────
    st.markdown('<div class="section-title" style="border-color:#a29bfe;">📋 Transaction Detail Table</div>', unsafe_allow_html=True)
    table_q = f"""
        SELECT t.transaction_id, t.date_transaction::DATE AS date,
               c.client_id, c.segment_client AS segment,
               t.agence, t.produit, t.type_operation AS type,
               ROUND(t.montant_eur::NUMERIC, 2) AS montant_eur,
               t.statut, ROUND(t.solde_avant::NUMERIC, 2) AS solde_avant
        FROM transactions t JOIN customers c ON t.client_id = c.client_id {where}
        ORDER BY t.date_transaction DESC
        LIMIT 200
    """
    table_df = run_query(table_q, params)
    if not table_df.empty:
        def color_statut(val):
            if val == "Complete":   return "color: #7bed9f; font-weight: bold"
            if val == "Rejeté":     return "color: #e94560; font-weight: bold"
            if val == "En attente": return "color: #f5a623; font-weight: bold"
            return ""
        def color_montant(val):
            if isinstance(val, (int, float)):
                return "color: #7bed9f" if val >= 0 else "color: #e94560"
            return ""
        styled = (
            table_df.style
            .map(color_statut, subset=["statut"])
            .map(color_montant, subset=["montant_eur"])
            .format({"montant_eur": "€{:,.2f}", "solde_avant": "€{:,.2f}"})
)
        st.dataframe(styled, use_container_width=True, height=400)
        st.caption(f"Showing top 200 rows out of {len(export_df):,} total transactions")

    # ── Status breakdown ──────────────────────────────────
    st.markdown('<div class="section-title" style="border-color:#fd79a8;">📊 Transaction Status Breakdown</div>', unsafe_allow_html=True)
    col5, col6 = st.columns(2)

    with col5:
        status_q = f"""
            SELECT t.statut, COUNT(*) AS nb,
                   ROUND(SUM(ABS(t.montant_eur))::NUMERIC, 0) AS volume
            FROM transactions t JOIN customers c ON t.client_id = c.client_id {where}
            GROUP BY t.statut
        """
        status_df = run_query(status_q, params)
        if not status_df.empty:
            fig = px.bar(status_df, x="statut", y="nb",
                         color="statut",
                         color_discrete_map={
                             "Complete":   "#7bed9f",
                             "Rejeté":     "#e94560",
                             "En attente": "#f5a623"
                         }, text="nb")
            fig.update_traces(texttemplate="%{text:,}", textposition="outside", textfont_color="white")
            fig = chart_layout(fig, "Count by Status")
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)

    with col6:
        if not status_df.empty:
            fig = px.bar(status_df, x="statut", y="volume",
                         color="statut",
                         color_discrete_map={
                             "Complete":   "#7bed9f",
                             "Rejeté":     "#e94560",
                             "En attente": "#f5a623"
                         }, text="volume")
            fig.update_traces(texttemplate="€%{text:,.0f}", textposition="outside", textfont_color="white")
            fig = chart_layout(fig, "Volume by Status (EUR)")
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Volume (EUR)")
            st.plotly_chart(fig, use_container_width=True)