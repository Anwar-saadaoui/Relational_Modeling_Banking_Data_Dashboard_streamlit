import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from db import run_query
from filters import render_filters, build_where_clause


def show():
    st.markdown('<div class="main-header">⚠️ Risk Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">FinanceCore SA — Credit Risk & Customer Scoring</div>', unsafe_allow_html=True)

    filters = render_filters()
    # where, params = build_where_clause(filters)
    where = ""
    params = {}

    # ─── Export Button ───────────────────────────────────────────────────────
    risk_export_query = f"""
        SELECT t.transaction_id, t.date_transaction, t.montant_eur,
               t.statut, t.agence, t.produit,
               c.client_id, c.segment_client, c.score_credit_client,
               t.solde_avant, t.taux_interet
        FROM transactions t
        JOIN customers c ON t.client_id = c.client_id
        {where}
        ORDER BY c.score_credit_client ASC
    """
    risk_df_export = run_query(risk_export_query, params)
    if not risk_df_export.empty:
        csv = risk_df_export.to_csv(index=False).encode("utf-8")
        st.sidebar.download_button(
            label="⬇️ Export risk data (CSV)",
            data=csv,
            file_name="financecore_risk.csv",
            mime="text/csv"
        )

    # ─── Scatter Plot: Credit Score vs Transaction Amount ────────────────────
    st.subheader("🔵 Credit Score vs Transaction Amount")

    scatter_query = f"""
        SELECT
            c.client_id,
            c.score_credit_client,
            t.montant_eur,
            t.statut,
            c.segment_client,
            t.agence
        FROM transactions t
        JOIN customers c ON t.client_id = c.client_id
        {where}
        LIMIT 2000
    """
    scatter_df = run_query(scatter_query, params)

    if not scatter_df.empty:
        scatter_df["risk_color"] = scatter_df["statut"].apply(
            lambda x: "🔴 Rejeté" if x == "Rejeté" else ("🟡 En attente" if x == "En attente" else "🟢 Complété")
        )
        fig_scatter = px.scatter(
            scatter_df,
            x="score_credit_client",
            y="montant_eur",
            color="risk_color",
            hover_data=["client_id", "agence", "segment_client"],
            labels={
                "score_credit_client": "Credit Score",
                "montant_eur": "Transaction Amount (EUR)",
                "risk_color": "Status"
            },
            color_discrete_map={
                "🔴 Rejeté":     "#e74c3c",
                "🟡 En attente": "#f39c12",
                "🟢 Complété":   "#2ecc71"
            },
            template="plotly_white",
            opacity=0.7
        )
        fig_scatter.update_layout(height=450, legend_title_text="Transaction Status")
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")

    # ─── Heatmap: Correlation Matrix ─────────────────────────────────────────
    st.subheader("🌡️ Correlation Heatmap — Credit Score, Amount & Rejection Rate")

    heatmap_query = f"""
        SELECT
            c.score_credit_client,
            t.montant_eur,
            t.taux_interet,
            t.solde_avant,
            CASE WHEN t.statut = 'Rejeté' THEN 1 ELSE 0 END AS is_rejected
        FROM transactions t
        JOIN customers c ON t.client_id = c.client_id
        {where}
    """
    heatmap_df = run_query(heatmap_query, params)

    if not heatmap_df.empty:
        heatmap_df = heatmap_df.dropna()
        corr = heatmap_df.corr()
        corr.columns = ["Credit Score", "Amount (EUR)", "Interest Rate", "Balance Before", "Rejection Rate"]
        corr.index   = ["Credit Score", "Amount (EUR)", "Interest Rate", "Balance Before", "Rejection Rate"]

        fig_hm, ax = plt.subplots(figsize=(8, 5))
        sns.heatmap(
            corr, annot=True, fmt=".2f", cmap="RdYlGn",
            linewidths=0.5, ax=ax, vmin=-1, vmax=1,
            annot_kws={"size": 10}
        )
        ax.set_title("Correlation Matrix", fontsize=13, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig_hm)

    st.markdown("---")

    # ─── Top 10 At-Risk Clients ───────────────────────────────────────────────
    st.subheader("🚨 Top 10 Highest-Risk Clients")

    risk_clients_query = f"""
        SELECT
            c.client_id,
            c.segment_client,
            ROUND(AVG(c.score_credit_client)::NUMERIC, 1)   AS avg_score,
            COUNT(t.transaction_id)                          AS nb_transactions,
            SUM(CASE WHEN t.statut = 'Rejeté' THEN 1 ELSE 0 END) AS nb_rejets,
            ROUND(
                SUM(CASE WHEN t.statut = 'Rejeté' THEN 1 ELSE 0 END)::NUMERIC
                / NULLIF(COUNT(t.transaction_id), 0) * 100, 1
            )                                                AS taux_rejet_pct,
            ROUND(AVG(t.solde_avant)::NUMERIC, 2)            AS avg_solde
        FROM transactions t
        JOIN customers c ON t.client_id = c.client_id
        {where}
        GROUP BY c.client_id, c.segment_client
        HAVING SUM(CASE WHEN t.statut = 'Rejeté' THEN 1 ELSE 0 END) > 0
        ORDER BY taux_rejet_pct DESC, avg_score ASC
        LIMIT 10
    """
    risk_clients_df = run_query(risk_clients_query, params)

    if not risk_clients_df.empty:
        def color_risk(val):
            if isinstance(val, float) or isinstance(val, int):
                if val >= 50:
                    return "background-color: #e74c3c; color: white; font-weight: bold"
                elif val >= 25:
                    return "background-color: #f39c12; color: white"
                else:
                    return "background-color: #2ecc71; color: white"
            return ""

        def color_score(val):
            if isinstance(val, float) or isinstance(val, int):
                if val < 400:
                    return "background-color: #e74c3c; color: white"
                elif val < 600:
                    return "background-color: #f39c12; color: white"
                else:
                    return "background-color: #2ecc71; color: white"
            return ""

        risk_clients_df.columns = [
            "Client ID", "Segment", "Avg Credit Score",
            "# Transactions", "# Rejections", "Rejection Rate (%)", "Avg Balance"
        ]

        styled = (
            risk_clients_df.style
            .applymap(color_risk,  subset=["Rejection Rate (%)"])
            .applymap(color_score, subset=["Avg Credit Score"])
            .format({
                "Avg Credit Score": "{:.1f}",
                "Rejection Rate (%)": "{:.1f}%",
                "Avg Balance": "€{:,.2f}"
            })
        )
        st.dataframe(styled, use_container_width=True, height=380)

        # Legend
        st.markdown("""
        **Color legend:**
        🟢 Low risk &nbsp;&nbsp; 🟡 Medium risk &nbsp;&nbsp; 🔴 High risk
        """)

    else:
        st.success("✅ No high-risk clients found with current filters!")

    st.markdown("---")

    # ─── Rejection Rate by Segment (Bar) ─────────────────────────────────────
    st.subheader("📊 Rejection Rate by Customer Segment")

    reject_segment_query = f"""
        SELECT
            c.segment_client,
            COUNT(t.transaction_id) AS total,
            SUM(CASE WHEN t.statut = 'Rejeté' THEN 1 ELSE 0 END) AS rejets,
            ROUND(
                SUM(CASE WHEN t.statut = 'Rejeté' THEN 1 ELSE 0 END)::NUMERIC
                / NULLIF(COUNT(t.transaction_id), 0) * 100, 2
            ) AS taux_rejet
        FROM transactions t
        JOIN customers c ON t.client_id = c.client_id
        {where}
        GROUP BY c.segment_client
        ORDER BY taux_rejet DESC
    """
    reject_segment_df = run_query(reject_segment_query, params)

    if not reject_segment_df.empty:
        fig_bar = px.bar(
            reject_segment_df,
            x="segment_client", y="taux_rejet",
            color="taux_rejet",
            color_continuous_scale=["#2ecc71", "#f39c12", "#e74c3c"],
            labels={"segment_client": "Segment", "taux_rejet": "Rejection Rate (%)"},
            template="plotly_white",
            text="taux_rejet"
        )
        fig_bar.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_bar.update_layout(coloraxis_showscale=False, height=380)
        st.plotly_chart(fig_bar, use_container_width=True)
