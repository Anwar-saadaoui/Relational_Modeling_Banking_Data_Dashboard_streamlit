import streamlit as st

st.set_page_config(
    page_title="FinanceCore Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp { background: #0f0f1a; color: #ffffff; }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid #e94560;
    }
    
    .kpi-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .kpi-value { font-size: 2.2rem; font-weight: 700; margin: 0.3rem 0; }
    .kpi-label { font-size: 0.8rem; opacity: 0.7; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-delta { font-size: 0.85rem; margin-top: 0.3rem; }

    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #333;
    }

    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        margin: 1.5rem 0 1rem 0;
        padding-left: 0.8rem;
        border-left: 4px solid;
    }

    .stDataFrame { border-radius: 12px; overflow: hidden; }
    
    .stSelectbox > div > div { background: #1a1a2e; color: white; border: 1px solid #e94560; border-radius: 8px; }
    
    div[data-testid="stMarkdownContainer"] h1 {
        background: linear-gradient(90deg, #e94560, #f5a623, #00b4d8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
    }

    .plotly-chart { border-radius: 12px; }
    
    .nav-btn {
        width: 100%;
        padding: 0.7rem;
        margin: 0.2rem 0;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        cursor: pointer;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style='text-align:center; padding: 1rem 0;'>
    <div style='font-size:2.5rem'>🏦</div>
    <div style='font-size:1.2rem; font-weight:800; color:#e94560;'>FinanceCore</div>
    <div style='font-size:0.75rem; color:#888; margin-top:0.2rem;'>Analytics Dashboard</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "",
    ["📊 Executive View", "⚠️ Risk Analysis"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("<div style='color:#888; font-size:0.75rem; text-align:center;'>FinanceCore SA © 2024</div>", unsafe_allow_html=True)

if page == "📊 Executive View":
    from pages import executive
    executive.show()
else:
    from pages import risk
    risk.show()