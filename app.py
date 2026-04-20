import streamlit as st
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import snowflake.connector

# Load environment variables
load_dotenv()

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UK Visa Sponsor Navigator",
    page_icon="🇬🇧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {
    --navy:    #0B1628;
    --deep:    #0F1F3D;
    --card:    #132040;
    --border:  #1E3358;
    --accent:  #3B7BFF;
    --gold:    #F5A623;
    --mint:    #00C9A7;
    --text:    #E8EFFF;
    --muted:   #7A92BE;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--navy) !important;
    color: var(--text) !important;
}

/* ── UI FIX: Keep header transparent but visible so sidebar arrow stays ── */
#MainMenu, footer { visibility: hidden; }
header { 
    background-color: rgba(0,0,0,0) !important; 
    visibility: visible !important;
}

.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1400px !important; }

/* ── Hero header ── */
.hero {
    background: linear-gradient(135deg, #0F1F3D 0%, #0B2852 50%, #071830 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 3rem 3.5rem;
    margin-bottom: 2.5rem;
    position: relative;
    overflow: hidden;
}

.hero-tag {
    display: inline-block;
    background: rgba(59,123,255,0.15);
    border: 1px solid rgba(59,123,255,0.4);
    color: #7AAAFF;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.3rem 0.9rem;
    border-radius: 100px;
    margin-bottom: 1.2rem;
}

.hero h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: 2.8rem !important;
    font-weight: 800 !important;
    color: var(--text) !important;
    line-height: 1.1 !important;
    margin: 0 0 0.6rem 0 !important;
}
.hero h1 span { color: var(--accent); }
.hero p { color: var(--muted) !important; font-size: 1.05rem !important; max-width: 560px; }

/* ── Stat cards ── */
.stat-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem 1.6rem;
    transition: border-color 0.2s;
}
.stat-card:hover { border-color: var(--accent); }
.stat-card .label { font-size: 0.72rem; text-transform: uppercase; color: var(--muted); }
.stat-card .value { font-family: 'Syne', sans-serif; font-size: 1.9rem; font-weight: 700; color: var(--text); }
.stat-card .value.accent { color: var(--accent); }
.stat-card .value.gold   { color: var(--gold); }
.stat-card .value.mint   { color: var(--mint); }

/* ── Sponsor cards ── */
.sponsor-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 0.8rem;
}
.sponsor-name { font-family: 'Syne', sans-serif; font-size: 1.05rem; font-weight: 700; color: var(--text); }
.badge { font-size: 0.72rem; padding: 0.25rem 0.7rem; border-radius: 100px; border: 1px solid; }
.badge-blue { background: rgba(59,123,255,0.1); border-color: rgba(59,123,255,0.3); color: #7AAAFF; }
.badge-mint { background: rgba(0,201,167,0.1); border-color: rgba(0,201,167,0.3); color: #00C9A7; }
.badge-purple { background: rgba(147,97,255,0.1); border-color: rgba(147,97,255,0.3); color: #B085FF; }
.badge-gray { background: rgba(122,146,190,0.1); border-color: rgba(122,146,190,0.3); color: #7A92BE; }

.stars { color: var(--gold); font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADING (WITH FAILOVER) ─────────────────────────────────────────────
@st.cache_data
def load_data():
    # 1. Try Snowflake first
    try:
        ctx = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA")
        )
        query = """
        SELECT 
            COMPANY_NAME, ESTIMATED_INDUSTRY as INDUSTRY_TAG, 
            CITY as TOWN_CITY, COUNTY, VISA_ROUTE, 
            RATING_SCORE, GEOGRAPHIC_PRIORITY
        FROM UK_SPONSOR_NAVIGATOR.ANALYTICS.FCT_SPONSORS_ENRICHED
        """
        df = pd.read_sql(query, ctx)
        ctx.close()
        return df
    
    # 2. Failover to local CSV if Snowflake is down/expired
    except Exception as e:
        st.info("💡 Note: Running in offline mode using local data snapshot.")
        # Ensure 'sponsor_data.csv' is uploaded to your GitHub repo root
        if os.path.exists("sponsor_data.csv"):
            return pd.read_csv("sponsor_data.csv")
        else:
            st.error("Error: Snowflake unavailable and sponsor_data.csv not found.")
            return pd.DataFrame()

df = load_data()

# Handle Rating Mapping (ensure consistency between DB and CSV)
rating_map = {'A': 5.0, 'B': 3.0, 'Other': 1.0}
if not df.empty and df['RATING_SCORE'].dtype == object:
    df['RATING_SCORE'] = df['RATING_SCORE'].map(rating_map).fillna(1.0)

# ─── SIDEBAR FILTERS ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-weight:bold; color:#7A92BE; font-size:0.8rem; letter-spacing:1px; margin-bottom:10px;">SEARCH</div>', unsafe_allow_html=True)
    search = st.text_input("", placeholder="Company name...", label_visibility="collapsed")

    all_industries = sorted(df["INDUSTRY_TAG"].dropna().unique().tolist())
    selected_industries = st.multiselect("Industry", all_industries)

    geo_options = ["All"] + sorted(df["GEOGRAPHIC_PRIORITY"].dropna().unique().tolist())
    selected_geo = st.selectbox("Location Priority", geo_options)

    min_rating = st.slider("Min Rating", 1.0, 5.0, 1.0)
    sort_by = st.selectbox("Sort By", ["Rating (High → Low)", "Company Name (A→Z)"])

# ─── FILTERING ────────────────────────────────────────────────────────────────
filtered = df.copy()
if search:
    filtered = filtered[filtered["COMPANY_NAME"].str.contains(search, case=False, na=False)]
if selected_industries:
    filtered = filtered[filtered["INDUSTRY_TAG"].isin(selected_industries)]
if selected_geo != "All":
    filtered = filtered[filtered["GEOGRAPHIC_PRIORITY"] == selected_geo]
filtered = filtered[filtered["RATING_SCORE"] >= min_rating]

if sort_by == "Rating (High → Low)":
    filtered = filtered.sort_values("RATING_SCORE", ascending=False)
else:
    filtered = filtered.sort_values("COMPANY_NAME")

# ─── UI: HERO & STATS ─────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-tag">🇬🇧 dbt · Snowflake · Medallion Architecture</div>
    <h1>UK Visa Sponsor <span>Navigator</span></h1>
    <p>Cleaned, deduplicated and enriched data through a production-grade analytics pipeline.</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="stat-card"><div class="label">Total Cleaned</div><div class="value accent">{len(df):,}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-card"><div class="label">Matching Filters</div><div class="value gold">{len(filtered):,}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-card"><div class="label">Pipeline Status</div><div class="value mint">HEALTHY</div></div>', unsafe_allow_html=True)

# ─── RESULTS DISPLAY ──────────────────────────────────────────────────────────
st.markdown("---")
if filtered.empty:
    st.warning("No sponsors found matching those filters.")
else:
    # Card view — 2 columns
    display_df = filtered.head(50)
    cols = st.columns(2)
    for i, (_, row) in enumerate(display_df.iterrows()):
        with cols[i % 2]:
            rating = float(row["RATING_SCORE"])
            stars = "★" * int(rating) + "☆" * (5 - int(rating))
            
            st.markdown(f"""
            <div class="sponsor-card">
                <div style="display:flex; justify-content:space-between;">
                    <div class="sponsor-name">{row['COMPANY_NAME']}</div>
                    <div style="color:#F5A623; font-weight:700;">{stars} {rating}</div>
                </div>
                <div style="margin-top:10px; display:flex; gap:5px; flex-wrap:wrap;">
                    <span class="badge badge-blue">{row['INDUSTRY_TAG']}</span>
                    <span class="badge badge-gray">{row['TOWN_CITY']}</span>
                    <span class="badge badge-purple">{row['VISA_ROUTE']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding:2rem; color:#7A92BE; font-size:0.8rem;">
    Built by <strong>Saravana Prashanth</strong> · Engineering: Python → Snowflake → dbt
</div>
""", unsafe_allow_html=True)
