import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from db import run_query
from filters import render_filters, build_where_clause

COLORS = ["#e94560", "#f5a623", "#00b4d8", "#7bed9f", "#a29bfe", "#fd79a8"]
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
        height=380
    )
    return fig

def show():
    st.write("RISK PAGE LOADED")
    st.markdown("# ⚠️ Risk Analysis")
    st.markdown("<p style='text-align:center;color:#888;margin-top:-1rem;'>Credit Risk & Customer Scoring — FinanceCore SA</p>", unsafe_allow_html=True)

    filters = render_filters()
    where, params = build_where_clause(filters)

    # Export
    risk_q = f"""
        SELECT t.transaction_id, t.date_transaction, t.montant_eur, t.statut,
               t.agence, t.produit, c.client_id, c.segment_client,
               c.score_credit_client, t.solde_avant, t.taux_interet
        FROM transactions t JOIN customers c ON t.client_id = c.client_id {where}
        ORDER BY c.score_credit_client ASC
    """
    risk_export = run_query(risk_q, params)
    if not risk_export.empty:
        st.sidebar.download_button(
            "⬇️ Export Risk CSV",
            risk_export.to_csv(index=False).encode("utf-8"),
            "financecore_risk.csv", "text/csv"
        )

    st.markdown("---")

    # ── Risk KPIs ──────────────────────────────────────────
    risk_kpi_q = f"""
        SELECT
            ROUND(AVG(c.score_credit_client)::NUMERIC, 1) AS avg_score,
            SUM(CASE WHEN t.statut = 'Rejeté' THEN 1 ELSE 0 END) AS total_rejets,
            COUNT(*) AS total_txn,
            ROUND(
                SUM(CASE WHEN t.statut = 'Rejeté' THEN 1 ELSE 0 END)::NUMERIC
                / NULLIF(COUNT(*), 0) * 100, 2
            ) AS taux_rejet,
            COUNT(DISTINCT CASE WHEN t.statut = 'Rejeté' THEN t.client_id END) AS clients_rejetes,
            COUNT(DISTINCT t.client_id) AS total_clients
        FROM transactions t JOIN customers c ON t.client_id = c.client_id {where}
    """
    kpi = run_query(risk_kpi_q, params)
    if not kpi.empty:
        k = kpi.iloc[0]
        c1, c2, c3, c4, c5 = st.columns(5)
        kpi_data = [
            (c1, "🎯 Avg Credit Score",   f"{k['avg_score']}",                "#00b4d8"),
            (c2, "❌ Total Rejections",   f"{int(k['total_rejets']):,}",       "#e94560"),
            (c3, "📉 Rejection Rate",     f"{k['taux_rejet']}%",              "#f5a623"),
            (c4, "👤 Clients w/ Rejects", f"{int(k['clients_rejetes']):,}",   "#fd79a8"),
            (c5, "👥 Total Clients",      f"{int(k['total_clients']):,}",      "#7bed9f"),
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

    # ── Scatter + Rejection bar ────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title" style="border-color:#e94560; color:white;">🔵 Credit Score vs Amount</div>', unsafe_allow_html=True)
        scatter_q = f"""
            SELECT c.client_id, c.score_credit_client,
                   ABS(t.montant_eur) AS montant_eur,
                   t.statut, c.segment_client
            FROM transactions t JOIN customers c ON t.client_id = c.client_id {where}
            LIMIT 1500
        """
        scatter_df = run_query(scatter_q, params)
        if not scatter_df.empty:
            color_map = {"Complete": "#7bed9f", "Rejeté": "#e94560", "En attente": "#f5a623"}
            fig = px.scatter(scatter_df,
                             x="score_credit_client", y="montant_eur",
                             color="statut", color_discrete_map=color_map,
                             hover_data=["client_id", "segment_client"],
                             opacity=0.75,
                             labels={"score_credit_client": "Credit Score",
                                     "montant_eur": "Amount (EUR)"})
            fig = chart_layout(fig)
            fig.update_layout(legend_title_text="Status")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title" style="border-color:#f5a623; color:white;">📊 Rejection Rate by Segment</div>', unsafe_allow_html=True)
        reject_q = f"""
            SELECT c.segment_client,
                   COUNT(*) AS total,
                   SUM(CASE WHEN t.statut = 'Rejeté' THEN 1 ELSE 0 END) AS rejets,
                   ROUND(
                       SUM(CASE WHEN t.statut = 'Rejeté' THEN 1 ELSE 0 END)::NUMERIC
                       / NULLIF(COUNT(*), 0) * 100, 2
                   ) AS taux_rejet
            FROM transactions t JOIN customers c ON t.client_id = c.client_id {where}
            GROUP BY c.segment_client ORDER BY taux_rejet DESC
        """
        reject_df = run_query(reject_q, params)
        if not reject_df.empty:
            fig = px.bar(reject_df, x="segment_client", y="taux_rejet",
                         color="taux_rejet",
                         color_continuous_scale=["#7bed9f", "#f5a623", "#e94560"],
                         text="taux_rejet")
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", textfont_color="white")
            fig = chart_layout(fig)
            fig.update_layout(coloraxis_showscale=False, xaxis_title="", yaxis_title="Rejection Rate (%)")
            st.plotly_chart(fig, use_container_width=True)

    # ── Heatmap ───────────────────────────────────────────
    st.markdown('<div class="section-title" style="border-color:#00b4d8; color:white;">🌡️ Correlation Heatmap</div>', unsafe_allow_html=True)
    heatmap_q = f"""
        SELECT c.score_credit_client,
               ABS(t.montant_eur) AS montant_eur,
               t.taux_interet,
               t.solde_avant,
               CASE WHEN t.statut = 'Rejeté' THEN 1 ELSE 0 END AS is_rejected
        FROM transactions t JOIN customers c ON t.client_id = c.client_id {where}
    """
    hm_df = run_query(heatmap_q, params)
    if not hm_df.empty:
        hm_df = hm_df.dropna()
        corr = hm_df.corr()
        corr.columns = ["Credit Score", "Amount", "Interest Rate", "Balance", "Rejected"]
        corr.index   = ["Credit Score", "Amount", "Interest Rate", "Balance", "Rejected"]

        fig_hm, ax = plt.subplots(figsize=(9, 4))
        fig_hm.patch.set_facecolor(PAPER_BG)
        ax.set_facecolor(DARK_BG)
        sns.heatmap(corr, annot=True, fmt=".2f",
                    cmap=sns.diverging_palette(220, 20, as_cmap=True),
                    linewidths=0.5, ax=ax,
                    vmin=-1, vmax=1,
                    annot_kws={"size": 11, "color": "white"},
                    cbar_kws={"shrink": 0.8})
        ax.tick_params(colors="white")
        plt.setp(ax.get_xticklabels(), color="white")
        plt.setp(ax.get_yticklabels(), color="white")
        ax.set_title("Feature Correlation Matrix", color="white", fontsize=13, fontweight="bold", pad=10)
        plt.tight_layout()
        st.pyplot(fig_hm)

    # ── Top 10 At-Risk Table ───────────────────────────────
    st.markdown('<div class="section-title" style="border-color:#e94560; color:white;">🚨 Top 10 Highest-Risk Clients</div>', unsafe_allow_html=True)
    top_risk_q = f"""
        SELECT
            c.client_id                                                          AS "Client ID",
            c.segment_client                                                     AS "Segment",
            ROUND(AVG(c.score_credit_client)::NUMERIC, 1)                       AS "Avg Score",
            COUNT(t.transaction_id)                                              AS "# Transactions",
            SUM(CASE WHEN t.statut = 'Rejeté' THEN 1 ELSE 0 END)               AS "# Rejections",
            ROUND(
                SUM(CASE WHEN t.statut = 'Rejeté' THEN 1 ELSE 0 END)::NUMERIC
                / NULLIF(COUNT(*), 0) * 100, 1
            )                                                                    AS "Rejection Rate %",
            ROUND(AVG(t.solde_avant)::NUMERIC, 2)                               AS "Avg Balance"
        FROM transactions t JOIN customers c ON t.client_id = c.client_id {where}
        GROUP BY c.client_id, c.segment_client
        HAVING SUM(CASE WHEN t.statut = 'Rejeté' THEN 1 ELSE 0 END) > 0
        ORDER BY "Rejection Rate %" DESC, "Avg Score" ASC
        LIMIT 10
    """
    top_df = run_query(top_risk_q, params)
    if not top_df.empty:
        def color_rate(val):
            if isinstance(val, (int, float)):
                if val >= 50: return "background-color:#e94560; color:white; font-weight:bold"
                if val >= 25: return "background-color:#f5a623; color:white"
                return "background-color:#2d6a4f; color:#7bed9f"
            return ""
        def color_score(val):
            if isinstance(val, (int, float)):
                if val < 400: return "color:#e94560; font-weight:bold"
                if val < 600: return "color:#f5a623"
                return "color:#7bed9f"
            return ""

        styled = (
            top_df.style
            .map(color_rate,  subset=["Rejection Rate %"])
            .map(color_score, subset=["Avg Score"])
            .format({...})
        )
        st.dataframe(styled, use_container_width=True, height=420)

        st.markdown("""
        <div style='margin-top:0.5rem; font-size:0.8rem; color:#888;'>
        🟢 Low risk (&lt;25%) &nbsp;&nbsp; 🟡 Medium risk (25–50%) &nbsp;&nbsp; 🔴 High risk (&gt;50%)
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success("✅ No high-risk clients found with the current filters!")

    # ── Rejection trend over time ──────────────────────────
    st.markdown('<div class="section-title" style="border-color:#a29bfe; color:white;">📅 Rejection Trend Over Time</div>', unsafe_allow_html=True)
    trend_q = f"""
        SELECT DATE_TRUNC('month', t.date_transaction) AS mois,
               SUM(CASE WHEN t.statut = 'Rejeté' THEN 1 ELSE 0 END) AS rejets,
               COUNT(*) AS total,
               ROUND(
                   SUM(CASE WHEN t.statut = 'Rejeté' THEN 1 ELSE 0 END)::NUMERIC
                   / NULLIF(COUNT(*), 0) * 100, 2
               ) AS taux
        FROM transactions t JOIN customers c ON t.client_id = c.client_id {where}
        GROUP BY DATE_TRUNC('month', t.date_transaction)
        ORDER BY mois
    """
    trend_df = run_query(trend_q, params)
    if not trend_df.empty:
        trend_df["mois"] = pd.to_datetime(trend_df["mois"])
        fig = go.Figure()
        fig.add_trace(go.Bar(x=trend_df["mois"], y=trend_df["total"],
                             name="Total Transactions",
                             marker_color="#a29bfe", opacity=0.5))
        fig.add_trace(go.Bar(x=trend_df["mois"], y=trend_df["rejets"],
                             name="Rejections",
                             marker_color="#e94560"))
        fig.add_trace(go.Scatter(x=trend_df["mois"], y=trend_df["taux"],
                                 name="Rejection Rate %",
                                 yaxis="y2", mode="lines+markers",
                                 line=dict(color="#f5a623", width=2.5)))
        fig.update_layout(
            plot_bgcolor=DARK_BG, paper_bgcolor=PAPER_BG,
            font=dict(color="white"),
            xaxis=dict(gridcolor="#333", color="white"),
            yaxis=dict(gridcolor="#333", color="white", title="Count"),
            yaxis2=dict(overlaying="y", side="right", color="#f5a623",
                        title="Rate %", showgrid=False),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="white")),
            barmode="overlay",
            height=380,
            margin=dict(l=20, r=60, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)