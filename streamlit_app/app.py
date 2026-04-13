import streamlit as st

st.set_page_config(
    page_title="FinanceCore Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1a3c5e;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .sub-header {
            font-size: 1rem;
            color: #6c757d;
            text-align: center;
            margin-bottom: 2rem;
        }
        .kpi-card {
            background: linear-gradient(135deg, #1a3c5e, #2e6da4);
            border-radius: 12px;
            padding: 1.2rem;
            color: white;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .kpi-value {
            font-size: 2rem;
            font-weight: 700;
        }
        .kpi-label {
            font-size: 0.85rem;
            opacity: 0.85;
        }
        .stSelectbox label, .stSlider label { color: #1a3c5e; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# Navigation
st.sidebar.markdown("## 🏦 FinanceCore SA")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation",
    ["📊 Executive View", "⚠️ Risk Analysis"],
    label_visibility="collapsed"
)

if page == "📊 Executive View":
    from pages import executive
    executive.show()
elif page == "⚠️ Risk Analysis":
    from pages import risk
    risk.show()
