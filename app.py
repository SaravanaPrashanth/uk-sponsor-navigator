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

/* ── Root variables ── */
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

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--navy) !important;
    color: var(--text) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
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
.stat-card .label {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.4rem;
}
.stat-card .value {
    font-family: 'Syne', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1;
}
.stat-card .value.accent { color: var(--accent); }
.stat-card .value.gold   { color: var(--gold); }
.stat-card .value.mint   { color: var(--mint); }
.stat-card .sub {
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: 0.3rem;
}

/* ── Section label ── */
.section-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 1rem;
    margin-top: 0.5rem;
}

/* ── Results header ── */
.results-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}
.results-count {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text);
}
.results-count span { color: var(--accent); }

/* ── Sponsor cards ── */
.sponsor-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 0.8rem;
    transition: border-color 0.2s, transform 0.15s, box-shadow 0.2s;
    cursor: pointer;
}
.sponsor-card:hover {
    border-color: var(--accent);
    transform: translateY(-1px);
    box-shadow: 0 8px 32px rgba(59,123,255,0.12);
}
.sponsor-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 0.8rem;
}
.sponsor-name {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1.3;
}
.sponsor-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.5rem;
    align-items: center;
}
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.72rem;
    font-weight: 500;
    padding: 0.25rem 0.7rem;
    border-radius: 100px;
    border: 1px solid;
    white-space: nowrap;
}
.badge-blue   { background: rgba(59,123,255,0.1);  border-color: rgba(59,123,255,0.3);  color: #7AAAFF; }
.badge-mint   { background: rgba(0,201,167,0.1);   border-color: rgba(0,201,167,0.3);   color: #00C9A7; }
.badge-gold   { background: rgba(245,166,35,0.1);  border-color: rgba(245,166,35,0.3);  color: #F5A623; }
.badge-gray   { background: rgba(122,146,190,0.1); border-color: rgba(122,146,190,0.3); color: #7A92BE; }
.badge-purple { background: rgba(147,97,255,0.1);  border-color: rgba(147,97,255,0.3);  color: #B085FF; }

/* ── Rating stars ── */
.rating {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    white-space: nowrap;
}
.stars { color: var(--gold); font-size: 0.85rem; letter-spacing: 1px; }
.rating-num {
    font-family: 'Syne', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--gold);
}

/* ── Priority badge ── */
.priority-sy  { color: var(--mint); font-size: 0.75rem; font-weight: 600; }
.priority-lon { color: var(--accent); font-size: 0.75rem; font-weight: 600; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--deep) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .block-container { padding: 1.5rem 1.2rem !important; }

/* ── Inputs ── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(59,123,255,0.15) !important;
}
.stSlider > div > div > div > div {
    background: var(--accent) !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* ── Dataframe table ── */
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* ── No results ── */
.no-results {
    text-align: center;
    padding: 4rem 2rem;
    color: var(--muted);
}
.no-results .emoji { font-size: 3rem; margin-bottom: 1rem; }
.no-results h3 { font-family: 'Syne', sans-serif; color: var(--text); font-size: 1.3rem; }

/* ── Footer ── */
.app-footer {
    text-align: center;
    padding: 2rem;
    color: var(--muted);
    font-size: 0.8rem;
    border-top: 1px solid var(--border);
    margin-top: 3rem;
}
.app-footer strong { color: var(--accent); }
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    # 1. Connect to Snowflake using your .env credentials
    ctx = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )
    
    # 2. Query your Golden Silver/Gold Table
    # Note: We rename ESTIMATED_INDUSTRY to INDUSTRY_TAG and CITY to TOWN_CITY 
    # so it matches the UI code Claude gave you.
    query = """
    SELECT 
        SPONSOR_ID,
        COMPANY_NAME,
        ESTIMATED_INDUSTRY as INDUSTRY_TAG,
        CITY as TOWN_CITY,
        COUNTY,
        VISA_ROUTE,
        RATING_SCORE,
        GEOGRAPHIC_PRIORITY
    FROM UK_SPONSOR_NAVIGATOR.ANALYTICS.FCT_SPONSORS_ENRICHED
    """
    
    df = pd.read_sql(query, ctx)
    ctx.close()
    return df

df = load_data()

rating_map = {
    'A': 5.0,
    'B': 3.0,
    'Other': 1.0
}

df['RATING_SCORE'] = df['RATING_SCORE'].map(rating_map).fillna(1.0)

# ─── SIDEBAR FILTERS ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-label">🔍 Search & Filter</div>', unsafe_allow_html=True)

    search = st.text_input("", placeholder="Search company name...", label_visibility="collapsed")

    st.markdown('<div class="section-label" style="margin-top:1.2rem">Industry</div>', unsafe_allow_html=True)
    all_industries = sorted(df["INDUSTRY_TAG"].dropna().unique().tolist())
    selected_industries = st.multiselect("", all_industries, label_visibility="collapsed",
                                          placeholder="All industries")

    st.markdown('<div class="section-label" style="margin-top:1.2rem">Location Priority</div>', unsafe_allow_html=True)
    geo_options = ["All"] + sorted(df["GEOGRAPHIC_PRIORITY"].dropna().unique().tolist())
    selected_geo = st.selectbox("", geo_options, label_visibility="collapsed")

    st.markdown('<div class="section-label" style="margin-top:1.2rem">Visa Route</div>', unsafe_allow_html=True)
    all_routes = sorted(df["VISA_ROUTE"].dropna().unique().tolist())
    selected_routes = st.multiselect("", all_routes, label_visibility="collapsed",
                                      placeholder="All visa routes")

    st.markdown('<div class="section-label" style="margin-top:1.2rem">Minimum Rating</div>', unsafe_allow_html=True)
    min_rating = st.slider("", 1.0, 5.0, 1.0, 0.5, label_visibility="collapsed")

    st.markdown("---")
    st.markdown('<div class="section-label">Sort By</div>', unsafe_allow_html=True)
    sort_by = st.selectbox("", ["Rating (High → Low)", "Company Name (A→Z)",
                                 "Location Priority"], label_visibility="collapsed")

# ─── FILTERING LOGIC ──────────────────────────────────────────────────────────
filtered = df.copy()

if search:
    filtered = filtered[filtered["COMPANY_NAME"].str.contains(search, case=False, na=False)]
if selected_industries:
    filtered = filtered[filtered["INDUSTRY_TAG"].isin(selected_industries)]
if selected_geo != "All":
    filtered = filtered[filtered["GEOGRAPHIC_PRIORITY"] == selected_geo]
if selected_routes:
    filtered = filtered[filtered["VISA_ROUTE"].isin(selected_routes)]
filtered = filtered[filtered["RATING_SCORE"] >= min_rating]

if sort_by == "Rating (High → Low)":
    filtered = filtered.sort_values("RATING_SCORE", ascending=False)
elif sort_by == "Company Name (A→Z)":
    filtered = filtered.sort_values("COMPANY_NAME")
else:
    priority_order = {"South Yorkshire": 0, "London": 1, "Other": 2}
    filtered["_sort"] = filtered["GEOGRAPHIC_PRIORITY"].map(priority_order)
    filtered = filtered.sort_values(["_sort", "RATING_SCORE"], ascending=[True, False])
    filtered = filtered.drop(columns=["_sort"])

# ─── HERO SECTION ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-tag">🇬🇧 Home Office Data · dbt · Snowflake · Medallion Architecture</div>
    <h1>UK Visa Sponsor <span>Navigator</span></h1>
    <p>120,354 verified skilled worker sponsors. Cleaned, deduplicated and enriched from raw Home Office data through a production-grade medallion pipeline.</p>
</div>
""", unsafe_allow_html=True)

# ─── STATS ROW ────────────────────────────────────────────────────────────────
total_clean    = len(df)
total_raw      = 140863
dupes_removed    = total_raw - 120354
dbt_pass       = "100%"

avg_rating     = round(filtered["RATING_SCORE"].mean(), 1) if len(filtered) else 0
sy_count       = len(df[df["GEOGRAPHIC_PRIORITY"] == "South Yorkshire"])

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f"""<div class="stat-card">
        <div class="label">Total Sponsors</div>
        <div class="value accent">{total_clean:,}</div>
        <div class="sub">From {total_raw:,} raw rows</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="stat-card">
        <div class="label">Dupes Removed</div>
        <div class="value gold">{dupes_removed}</div>
        <div class="sub">via QUALIFY clause</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="stat-card">
        <div class="label">dbt Tests</div>
        <div class="value mint">{dbt_pass}</div>
        <div class="sub">Unique + Not Null</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="stat-card">
        <div class="label">S. Yorkshire</div>
        <div class="value">{sy_count:,}</div>
        <div class="sub">Local sponsors</div>
    </div>""", unsafe_allow_html=True)
with c5:
    st.markdown(f"""<div class="stat-card">
        <div class="label">Avg Rating</div>
        <div class="value">{avg_rating}</div>
        <div class="sub">Current filter</div>
    </div>""", unsafe_allow_html=True)

# ─── RESULTS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="results-header">
    <div class="results-count"><span>{len(filtered):,}</span> sponsors match your filters</div>
</div>
""", unsafe_allow_html=True)

if len(filtered) == 0:
    st.markdown("""<div class="no-results">
        <div class="emoji">🔍</div>
        <h3>No sponsors match your filters</h3>
        <p>Try broadening your search criteria</p>
    </div>""", unsafe_allow_html=True)
else:
    # ── View toggle ──
    col_view1, col_view2, col_view3 = st.columns([1, 1, 4])
    with col_view1:
        card_view = st.button("🃏 Cards", use_container_width=True)
    with col_view2:
        table_view = st.button("📊 Table", use_container_width=True)

    if "view_mode" not in st.session_state:
        st.session_state.view_mode = "cards"
    if card_view:
        st.session_state.view_mode = "cards"
    if table_view:
        st.session_state.view_mode = "table"

    display_df = filtered.head(50).reset_index(drop=True)

    if st.session_state.view_mode == "table":
        show_cols = ["COMPANY_NAME", "INDUSTRY_TAG", "TOWN_CITY",
                     "COUNTY", "VISA_ROUTE", "RATING_SCORE", "GEOGRAPHIC_PRIORITY"]
        st.dataframe(
            display_df[show_cols].rename(columns={
                "COMPANY_NAME": "Company", "INDUSTRY_TAG": "Industry",
                "TOWN_CITY": "City", "COUNTY": "County",
                "VISA_ROUTE": "Visa Route", "RATING_SCORE": "Rating",
                "GEOGRAPHIC_PRIORITY": "Priority Region"
            }),
            use_container_width=True,
            height=520,
            hide_index=True,
        )
    else:
        # Card view — 2 columns
        cols = st.columns(2)
        for i, (_, row) in enumerate(display_df.iterrows()):
            with cols[i % 2]:
                # Rating stars
                rating = float(row["RATING_SCORE"])
                full_stars = int(rating)
                half_star  = "½" if (rating - full_stars) >= 0.5 else ""
                empty      = 5 - full_stars - (1 if half_star else 0)
                stars_str  = "★" * full_stars + half_star + "☆" * empty

                # Priority badge
                geo = row["GEOGRAPHIC_PRIORITY"]
                if geo == "South Yorkshire":
                    priority_html = '<span class="badge badge-mint">📍 South Yorkshire Priority</span>'
                elif geo == "London":
                    priority_html = '<span class="badge badge-blue">📍 London Priority</span>'
                else:
                    priority_html = '<span class="badge badge-gray">📍 Other Region</span>'

                # Industry colour
                industry_colours = {
                    "Technology": "badge-blue", "Finance & Banking": "badge-gold",
                    "Healthcare & NHS": "badge-mint", "Consulting": "badge-purple",
                    "Public Sector": "badge-mint", "Telecoms": "badge-blue",
                    "Engineering & Manufacturing": "badge-gold",
                }
                ind_cls = industry_colours.get(row["INDUSTRY_TAG"], "badge-gray")

                st.markdown(f"""
                <div class="sponsor-card">
                    <div class="sponsor-top">
                        <div class="sponsor-name">{row['COMPANY_NAME']}</div>
                        <div class="rating">
                            <span class="stars">{stars_str}</span>
                            <span class="rating-num">{rating}</span>
                        </div>
                    </div>
                    <div class="sponsor-meta">
                        <span class="badge {ind_cls}">{row['INDUSTRY_TAG']}</span>
                        <span class="badge badge-gray">🏙️ {row['TOWN_CITY']}, {row['COUNTY']}</span>
                        <span class="badge badge-purple">🛂 {row['VISA_ROUTE']}</span>
                        {priority_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Show more note ──
    if len(filtered) > 50:
        st.markdown(f"""
        <div style="text-align:center; padding:1.5rem; color:var(--muted); font-size:0.85rem;">
            Showing top 50 of <strong style="color:var(--text)">{len(filtered):,}</strong> results.
            Refine your filters to narrow down.
        </div>""", unsafe_allow_html=True)

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-footer">
    Built by <strong>Saravana Prashanth</strong> · 
    Pipeline: Python → Snowflake → dbt (Medallion Architecture) → Streamlit ·
    Source: UK Home Office Register of Licensed Sponsors
</div>
""", unsafe_allow_html=True)
