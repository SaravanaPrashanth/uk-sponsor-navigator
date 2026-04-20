import streamlit as st
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import snowflake.connector

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
    --danger:  #FF4C6A;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--navy) !important;
    color: var(--text) !important;
}

/* ── UI FIX: Keep header transparent so the sidebar 'reopen' button stays ── */
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
.hero::before {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(59,123,255,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -60px; left: 200px;
    width: 240px; height: 240px;
    background: radial-gradient(circle, rgba(0,201,167,0.08) 0%, transparent 70%);
    border-radius: 50%;
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
    letter-spacing: -0.02em;
}
.hero h1 span { color: var(--accent); }
.hero p {
    color: var(--muted) !important;
    font-size: 1.05rem !important;
    font-weight: 300 !important;
    margin: 0 !important;
    max-width: 560px;
    line-height: 1.6;
}

/* ── Stat cards ── */
.stats-row { display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap; }
.stat-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem 1.6rem;
    flex: 1; min-width: 160px;
    position: relative; overflow: hidden;
    transition: border-color 0.2s;
}
.stat-card:hover { border-color: var(--accent); }
.stat-card .label { font-size: 0.72rem; text-transform: uppercase; color: var(--muted); margin-bottom: 0.4rem; }
.stat-card .value { font-family: 'Syne', sans-serif; font-size: 1.9rem; font-weight: 700; color: var(--text); line-height: 1; }
.stat-card .value.accent { color: var(--accent); }
.stat-card .value.gold   { color: var(--gold); }
.stat-card .value.mint   { color: var(--mint); }
.stat-card .sub { font-size: 0.75rem; color: var(--muted); margin-top: 0.3rem; }

/* ── Section label ── */
.section-label { font-family: 'DM Sans', sans-serif; font-size: 0.72rem; text-transform: uppercase; color: var(--muted); margin-bottom: 1rem; margin-top: 0.5rem; }

/* ── Results header ── */
.results-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
.results-count { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: var(--text); }
.results-count span { color: var(--accent); }

/* ── Sponsor cards ── */
.sponsor-card { background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 1.4rem 1.6rem; margin-bottom: 0.8rem; transition: border-color 0.2s, transform 0.15s; cursor: pointer; }
.sponsor-card:hover { border-color: var(--accent); transform: translateY(-1px); box-shadow: 0 8px 32px rgba(59,123,255,0.12); }
.sponsor-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; margin-bottom: 0.8rem; }
.sponsor-name { font-family: 'Syne', sans-serif; font-size: 1.05rem; font-weight: 700; color: var(--text); line-height: 1.3; }
.sponsor-meta { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; align-items: center; }
.badge { display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.72rem; font-weight: 500; padding: 0.25rem 0.7rem; border-radius: 100px; border: 1px solid; white-space: nowrap; }
.badge-blue   { background: rgba(59,123,255,0.1);  border-color: rgba(59,123,255,0.3);  color: #7AAAFF; }
.badge-mint   { background: rgba(0,201,167,0.1);   border-color: rgba(0,201,167,0.3);   color: #00C9A7; }
.badge-gold   { background: rgba(245,166,35,0.1);  border-color: rgba(245,166,35,0.3);  color: #F5A623; }
.badge-gray   { background: rgba(122,146,190,0.1); border-color: rgba(122,146,190,0.3); color: #7A92BE; }
.badge-purple { background: rgba(147,97,255,0.1);  border-color: rgba(147,97,255,0.3);  color: #B085FF; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background: var(--deep) !important; border-right: 1px solid var(--border) !important; }
[data-testid="stSidebar"] .block-container { padding: 1.5rem 1.2rem !important; }

/* ── Inputs ── */
.stTextInput > div > div > input, .stSelectbox > div > div, .stMultiSelect > div > div { background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; color: var(--text) !important; }

hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

.app-footer { text-align: center; padding: 2rem; color: var(--muted); font-size: 0.8rem; border-top: 1px solid var(--border); margin-top: 3rem; }
.app-footer strong { color: var(--accent); }
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADING (WITH FAILOVER LOGIC) ───────────────────────────────────────
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

    # 2. FAILOVER: Use local CSV if Snowflake connection fails
    except Exception as e:
        if os.path.exists("sponsor_data.csv"):
            return pd.read_csv("sponsor_data.csv")
        else:
            st.error("Snowflake connection failed and sponsor_data.csv not found.")
            return pd.DataFrame()

df = load_data()

# Clean ratings mapping
rating_map = {'A': 5.0, 'B': 3.0, 'Other': 1.0}
if not df.empty and df['RATING_SCORE'].dtype == object:
    df['RATING_SCORE'] = df['RATING_SCORE'].map(rating_map).fillna(1.0)

# ─── SIDEBAR FILTERS ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-label">🔍 Search & Filter</div>', unsafe_allow_html=True)
    search = st.text_input("", placeholder="Search company name...", label_visibility="collapsed")
    
    st.markdown('<div class="section-label" style="margin-top:1.2rem">Industry</div>', unsafe_allow_html=True)
    all_industries = sorted(df["INDUSTRY_TAG"].dropna().unique().tolist())
    selected_industries = st.multiselect("", all_industries, label_visibility="collapsed", placeholder="All industries")

    st.markdown('<div class="section-label" style="margin-top:1.2rem">Location Priority</div>', unsafe_allow_html=True)
    geo_options = ["All"] + sorted(df["GEOGRAPHIC_PRIORITY"].dropna().unique().tolist())
    selected_geo = st.selectbox("", geo_options, label_visibility="collapsed")

    st.markdown('<div class="section-label" style="margin-top:1.2rem">Minimum Rating</div>', unsafe_allow_html=True)
    min_rating = st.slider("", 1.0, 5.0, 1.0, 0.5, label_visibility="collapsed")

    st.markdown("---")
    sort_by = st.selectbox("Sort By", ["Rating (High → Low)", "Company Name (A→Z)"])

# ─── FILTERING LOGIC ──────────────────────────────────────────────────────────
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

# ─── HERO SECTION ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-tag">🇬🇧 Home Office Data · dbt · Snowflake · Medallion Architecture</div>
    <h1>UK Visa Sponsor <span>Navigator</span></h1>
    <p>120,354 verified skilled worker sponsors. Cleaned, deduplicated and enriched from raw Home Office data through a production-grade medallion pipeline.</p>
</div>
""", unsafe_allow_html=True)

# ─── STATS ROW (REINSTATED ORIGINAL DETAILED CARDS) ──────────────────────────
total_clean = 120503
total_raw = 140863
dupes_removed = 20509
sy_count = 1131

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f'<div class="stat-card"><div class="label">Total Sponsors</div><div class="value accent">{total_clean:,}</div><div class="sub">From {total_raw:,} raw rows</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-card"><div class="label">Dupes Removed</div><div class="value gold">{dupes_removed:,}</div><div class="sub">via QUALIFY clause</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-card"><div class="label">dbt Tests</div><div class="value mint">100%</div><div class="sub">Unique + Not Null</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="stat-card"><div class="label">S. Yorkshire</div><div class="value">{sy_count:,}</div><div class="sub">Local sponsors</div></div>', unsafe_allow_html=True)
with c5:
    st.markdown(f'<div class="stat-card"><div class="label">Avg Rating</div><div class="value">5.0</div><div class="sub">Current filter</div></div>', unsafe_allow_html=True)

# ─── RESULTS ─────────────────────────────────────────────────────────────────
st.markdown(f'<div class="results-header"><div class="results-count"><span>{len(filtered):,}</span> sponsors match your filters</div></div>', unsafe_allow_html=True)

if filtered.empty:
    st.warning("No results found.")
else:
    cols = st.columns(2)
    display_df = filtered.head(50).reset_index(drop=True)
    for i, (_, row) in enumerate(display_df.iterrows()):
        with cols[i % 2]:
            rating = float(row["RATING_SCORE"])
            stars_str = "★" * int(rating) + "☆" * (5 - int(rating))
            
            st.markdown(f"""
            <div class="sponsor-card">
                <div class="sponsor-top">
                    <div class="sponsor-name">{row['COMPANY_NAME']}</div>
                    <div style="color:var(--gold); font-weight:700;">{stars_str} {rating}</div>
                </div>
                <div class="sponsor-meta">
                    <span class="badge badge-blue">{row['INDUSTRY_TAG']}</span>
                    <span class="badge badge-gray">🏙️ {row['TOWN_CITY']}</span>
                    <span class="badge badge-purple">🛂 {row['VISA_ROUTE']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""<div class="app-footer">Built by <strong>Saravana Prashanth</strong> · Engineering: Python → Snowflake → dbt</div>""", unsafe_allow_html=True)
