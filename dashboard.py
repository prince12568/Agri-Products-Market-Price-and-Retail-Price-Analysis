"""
AgriSight — Market & Retail Price Analytics Dashboard
Run:  streamlit run dashboard.py
Requires dashboard_dataset.csv in the same folder.
"""
#To run streamlit run dashboard.py
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ╔══════════════════════════════════════════════════════════════════════╗
# ║  PAGE CONFIG                                                         ║
# ╚══════════════════════════════════════════════════════════════════════╝
st.set_page_config(
    page_title="AgriSight Analytics",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ╔══════════════════════════════════════════════════════════════════════╗
# ║  GLOBAL CSS                                                          ║
# ╚══════════════════════════════════════════════════════════════════════╝
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.main .block-container { padding: 1.5rem 2rem 3rem; max-width: 1400px; }
header[data-testid="stHeader"] { display: none; }

/* Sidebar */
[data-testid="stSidebar"] { background: #0F2318; }
[data-testid="stSidebar"] * { color: #C8DFC9 !important; }
[data-testid="stSidebar"] .stRadio label {
    background: rgba(255,255,255,0.04); border-radius: 10px;
    padding: 0.55rem 0.9rem; margin-bottom: 4px; display: block;
    transition: background .2s; font-size: 0.875rem;
}
[data-testid="stSidebar"] .stRadio label:hover { background: rgba(255,255,255,0.09); }
[data-testid="stSidebar"] hr { border-color: #1E3A2F !important; }

/* Metric cards */
[data-testid="metric-container"] {
    background: #FFFFFF; border-radius: 16px;
    padding: 1.1rem 1.3rem !important;
    border: 1px solid #E8E3D8;
    box-shadow: 0 2px 12px rgba(0,0,0,.055);
    transition: transform .2s, box-shadow .2s;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,.1);
}
[data-testid="stMetricLabel"] {
    font-size:.7rem !important; font-weight:600 !important;
    letter-spacing:.08em !important; text-transform:uppercase !important;
    color:#8A8A8A !important;
}
[data-testid="stMetricValue"] {
    font-family:'Playfair Display',serif !important;
    font-size:2rem !important; font-weight:700 !important; color:#1E3A2F !important;
}

/* Section titles */
.sec-title {
    font-family:'Playfair Display',serif; font-size:1.4rem; font-weight:700;
    color:#1E3A2F; margin-bottom:.2rem; line-height:1.3;
}
.sec-desc { font-size:.82rem; color:#8A8A8A; margin-bottom:1.1rem; }

/* Insight card */
.insight-card {
    background:linear-gradient(135deg,#FDF6E8,#FDF0D5);
    border:1px solid #F5C46E; border-left:4px solid #C8821A;
    border-radius:14px; padding:1.1rem 1.4rem; margin-bottom:1.4rem;
}
.insight-card h4 {
    font-family:'Playfair Display',serif; font-size:.95rem;
    color:#C8821A; margin-bottom:.5rem;
}
.insight-card p { font-size:.81rem; color:#5A4010; line-height:1.75; margin:0; }

/* Fancy divider */
.fancy-divider {
    height:1px;
    background:linear-gradient(90deg,transparent,#E0DAD0 20%,#E0DAD0 80%,transparent);
    margin:1.5rem 0; border:none;
}

/* Big stat */
.big-stat { text-align:center; padding:1.25rem .75rem; background:#F7F4EE; border-radius:14px; }
.big-stat-val { font-family:'Playfair Display',serif; font-size:2.4rem; font-weight:700; color:#1E3A2F; line-height:1; }
.big-stat-label { font-size:.72rem; font-weight:600; letter-spacing:.07em; text-transform:uppercase; color:#8A8A8A; margin-top:5px; }
.big-stat-sub { font-size:.74rem; color:#AAAAAA; margin-top:2px; }
</style>
""", unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════════════╗
# ║  CONSTANTS                                                           ║
# ╚══════════════════════════════════════════════════════════════════════╝
CAT_COLORS = {
    "Spices":     "#C8821A",
    "Fruits":     "#4A8C5C",
    "Vegetables": "#2D5A40",
    "Pulses":     "#D4622A",
    "Cereals":    "#3B7EBF",
    "Flowers":    "#9B6B9B",
    "Livestock":  "#1E3A2F",
}
STORAGE_COLORS = {
    "No Cold Storage":   "#2D5A40",
    "Cold Storage Safe": "#4A8C5C",
    "Cold Sensitive":    "#C8DFC9",
}
SEASON_COLORS = ["#1E3A2F","#2D5A40","#4A8C5C","#C8821A","#D4622A","#F5C46E"]

BASE = dict(
    font=dict(family="Plus Jakarta Sans, sans-serif", size=12),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=45, b=10),
    title_font=dict(family="Playfair Display, serif", size=15, color="#1E3A2F"),
)
GC = "#F0EDE5"   # grid colour

# ╔══════════════════════════════════════════════════════════════════════╗
# ║  DATA — loaded once from the real CSV                                ║
# ╚══════════════════════════════════════════════════════════════════════╝
CSV_PATH = os.path.join(os.path.dirname(__file__), "dashboard_dataset.csv")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Name"] = df["Name"].str.strip().str.title()
    df["Spread"] = df["Retail_Price_Avg"] - df["Price_per_kg"]
    return df

df = load_data(CSV_PATH)

# ╔══════════════════════════════════════════════════════════════════════╗
# ║  SIDEBAR                                                             ║
# ╚══════════════════════════════════════════════════════════════════════╝
with st.sidebar:
    st.markdown("""
    <div style='padding:1.2rem 0 .5rem;text-align:center;'>
      <div style='font-size:2.2rem;'>🌾</div>
      <div style='font-family:Playfair Display,serif;font-size:1.4rem;
                  font-weight:700;color:#FFF;margin-top:4px;'>AgriSight</div>
      <div style='font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;
                  color:#4A8C5C;margin-top:2px;'>Market Analytics</div>
    </div>""", unsafe_allow_html=True)
    st.divider()

    page = st.radio("", [
        "🏠  Overview",
        "💰  Price Analysis",
        "📈  Markup & Profit",
        "🌡  Storage & Season",
        "🏆  Rankings",
    ], label_visibility="collapsed")

    st.divider()

    all_cats = sorted(df["Category"].unique())
    cat_filter = st.multiselect(
        "Filter by Category", options=all_cats, default=all_cats,
    )

    all_storages = sorted(df["Storage_Type"].unique())
    storage_filter = st.multiselect(
        "Filter by Storage", options=all_storages, default=all_storages,
    )

    price_min, price_max = float(df["Price_per_kg"].min()), float(df["Price_per_kg"].max())
    price_range = st.slider(
        "Market Price Range (₹/kg)",
        min_value=price_min, max_value=price_max,
        value=(price_min, price_max), step=10.0,
    )

    st.divider()
    st.markdown(f"""
    <div style='font-size:.72rem;color:#4A8C5C;line-height:1.9;'>
    📦 &nbsp;{len(df)} Products<br>
    🗂 &nbsp;{df['Category'].nunique()} Categories<br>
    🗺 &nbsp;Gujarat & Maharashtra<br>
    📡 &nbsp;piplanapane.in · BigBasket
    </div>""", unsafe_allow_html=True)

# ── Apply filters ──────────────────────────────────────────────────────────
dff = df[
    df["Category"].isin(cat_filter) &
    df["Storage_Type"].isin(storage_filter) &
    df["Price_per_kg"].between(*price_range)
].copy()

# Plotly scatter marker size must be >= 0.
# Markup has negative values (e.g. cardamom -0.13, dry ginger -0.42).
# Markup_Size clips those to 0; real Markup stays for axes/hover/colour.
dff["Markup_Size"] = dff["Markup"].clip(lower=0)

# ╔══════════════════════════════════════════════════════════════════════╗
# ║  HELPERS                                                             ║
# ╚══════════════════════════════════════════════════════════════════════╝
def sec(title, desc=""):
    st.markdown(f'<div class="sec-title">{title}</div>', unsafe_allow_html=True)
    if desc:
        st.markdown(f'<div class="sec-desc">{desc}</div>', unsafe_allow_html=True)

def insight(title, body):
    st.markdown(f"""
    <div class="insight-card">
      <h4>💡 {title}</h4><p>{body}</p>
    </div>""", unsafe_allow_html=True)

def fdiv():
    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

def big_stats(stats):
    cols = st.columns(len(stats))
    for col, (val, label, sub) in zip(cols, stats):
        with col:
            st.markdown(f"""
            <div class="big-stat">
              <div class="big-stat-val">{val}</div>
              <div class="big-stat-label">{label}</div>
              <div class="big-stat-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

def cat_summary(data):
    return (
        data.groupby("Category")
        .agg(Count=("Name","count"),
             Avg_Price=("Price_per_kg","mean"),
             Avg_Retail=("Retail_Price_Avg","mean"),
             Avg_Markup=("Markup","mean"))
        .reset_index()
        .round(2)
    )

# ╔══════════════════════════════════════════════════════════════════════╗
# ║  PAGE — OVERVIEW                                                     ║
# ╚══════════════════════════════════════════════════════════════════════╝
if "Overview" in page:

    # Hero
    med_price = df["Price_per_kg"].median()
    max_markup = df["Markup"].max()
    corr = df["Price_per_kg"].corr(df["Retail_Price_Avg"])
    st.markdown(f"""
    <div style="background:linear-gradient(120deg,#0F2318,#1E3A2F 55%,#2D5A40);
                border-radius:20px;padding:2.2rem 2.5rem;margin-bottom:1.6rem;
                display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
      <div>
        <div style="font-family:'Playfair Display',serif;font-size:2.4rem;
                    font-weight:700;color:#FFF;line-height:1.15;">Agri Market Intelligence</div>
        <div style="color:#C8DFC9;font-size:.88rem;margin-top:6px;font-weight:300;">
          Direct-to-Consumer Viability Study · {len(df)} Products · {df['Category'].nunique()} Categories · India
        </div>
      </div>
      <div style="display:flex;gap:2rem;flex-wrap:wrap;">
        <div style="text-align:center;">
          <div style="font-family:'Playfair Display',serif;font-size:2rem;font-weight:700;color:#F5C46E;">{corr:.2f}</div>
          <div style="font-size:.7rem;color:#C8DFC9;letter-spacing:.06em;text-transform:uppercase;">Price Correlation</div>
        </div>
        <div style="text-align:center;">
          <div style="font-family:'Playfair Display',serif;font-size:2rem;font-weight:700;color:#F5C46E;">{max_markup:.0f}×</div>
          <div style="font-size:.7rem;color:#C8DFC9;letter-spacing:.06em;text-transform:uppercase;">Max Markup</div>
        </div>
        <div style="text-align:center;">
          <div style="font-family:'Playfair Display',serif;font-size:2rem;font-weight:700;color:#F5C46E;">₹{med_price:.0f}</div>
          <div style="font-size:.7rem;color:#C8DFC9;letter-spacing:.06em;text-transform:uppercase;">Median Price</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # KPIs from real data
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Total Products",    f"{len(dff)}",
              f"of {len(df)} total")
    c2.metric("Median Mkt Price",  f"₹{dff['Price_per_kg'].median():.0f}",
              f"max ₹{dff['Price_per_kg'].max():,.0f}")
    c3.metric("Avg Retail Price",  f"₹{dff['Retail_Price_Avg'].mean():.0f}",
              f"avg spread ₹{dff['Spread'].mean():.0f}")
    c4.metric("Avg Markup",        f"{dff['Markup'].mean():.2f}×",
              f"max {dff['Markup'].max():.1f}×")
    c5.metric("Cold Storage Safe", f"{(dff['Storage_Type']=='Cold Storage Safe').sum()}",
              f"{(dff['Storage_Type']=='Cold Storage Safe').mean()*100:.1f}% of filtered")
    c6.metric("Negative Markup",   f"{(dff['Markup']<0).sum()} items",
              "oversupply signals")

    fdiv()

    # Treemap + donut
    sec("Product Landscape", "Composition by category and storage type")
    col1, col2 = st.columns([3, 2])

    with col1:
        cs = cat_summary(dff)
        fig = px.treemap(
            cs, path=["Category"], values="Count",
            color="Avg_Markup",
            color_continuous_scale=[[0,"#C8DFC9"],[0.4,"#4A8C5C"],[1,"#0F2318"]],
            custom_data=["Avg_Price","Avg_Markup","Avg_Retail"],
            title="Category Treemap — size=products, colour=avg markup",
        )
        fig.update_traces(
            hovertemplate=(
                "<b>%{label}</b><br>Products: %{value}<br>"
                "Avg Market ₹: %{customdata[0]:.0f}<br>"
                "Avg Markup: %{customdata[1]:.2f}×<br>"
                "Avg Retail ₹: %{customdata[2]:.0f}<extra></extra>"
            ),
            textinfo="label+value",
        )
        fig.update_layout(**BASE, coloraxis_showscale=False, height=340)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st_counts = dff["Storage_Type"].value_counts().reset_index()
        st_counts.columns = ["Storage_Type","Count"]
        fig2 = px.pie(
            st_counts, values="Count", names="Storage_Type",
            color="Storage_Type", color_discrete_map=STORAGE_COLORS,
            hole=0.58, title="Storage Type Distribution",
        )
        fig2.update_traces(textinfo="percent+label", textfont_size=11)
        fig2.update_layout(**BASE, showlegend=False, height=340)
        st.plotly_chart(fig2, use_container_width=True)

    fdiv()

    # Season bar + sunburst
    sec("Seasonality Overview", "When crops grow and how categories align with seasons")
    col1, col2 = st.columns(2)

    with col1:
        ssn = dff["Season"].value_counts().reset_index()
        ssn.columns = ["Season","Count"]
        fig3 = px.bar(
            ssn.sort_values("Count", ascending=False),
            x="Season", y="Count",
            color="Season", color_discrete_sequence=SEASON_COLORS,
            text="Count", title="Products by Season",
        )
        fig3.update_traces(textposition="outside", width=0.6)
        fig3.update_layout(**BASE, showlegend=False,
                           xaxis=dict(gridcolor="rgba(0,0,0,0)", title=None),
                           yaxis=dict(gridcolor=GC, title="Count"))
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        fig4 = px.sunburst(
            dff, path=["Storage_Type","Category"],
            color="Category", color_discrete_map=CAT_COLORS,
            title="Storage → Category Breakdown",
        )
        fig4.update_layout(**BASE, height=320)
        fig4.update_traces(textfont=dict(size=11))
        st.plotly_chart(fig4, use_container_width=True)

    insight("Core Finding",
        "Profit in this dataset is <b>not driven by price — it is driven by storage capability "
        f"and perishability</b>. Cold-storage-safe items average {df[df['Storage_Type']=='Cold Storage Safe']['Markup'].mean():.2f}× markup "
        f"vs {df[df['Storage_Type']=='No Cold Storage']['Markup'].mean():.2f}× for no-storage items. "
        "Livestock and flowers carry the highest markup potential while cereals and pulses operate on thin margins."
    )

# ╔══════════════════════════════════════════════════════════════════════╗
# ║  PAGE — PRICE ANALYSIS                                               ║
# ╚══════════════════════════════════════════════════════════════════════╝
elif "Price" in page:

    sec("Market & Retail Price Deep Dive",
        "Distribution, correlation and category-level comparisons from real data")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Price Correlation",  f"{dff['Price_per_kg'].corr(dff['Retail_Price_Avg']):.2f}",
              "Market ↔ Retail")
    c2.metric("Avg Price Spread",   f"₹{dff['Spread'].mean():.0f}/kg",
              "Retail − Market")
    c3.metric("Most Expensive",     f"₹{dff['Price_per_kg'].max():,.0f}",
              dff.loc[dff['Price_per_kg'].idxmax(),'Name'])
    c4.metric("Cheapest Item",      f"₹{dff['Price_per_kg'].min():.1f}",
              dff.loc[dff['Price_per_kg'].idxmin(),'Name'])

    fdiv()

    # Scatter — single df, all column strings
    sec("Market vs Retail Correlation",
        f"r = {dff['Price_per_kg'].corr(dff['Retail_Price_Avg']):.2f} — strong positive linear relationship")

    fig_sc = px.scatter(
        dff,                            # ← single df, no merge
        x="Price_per_kg",
        y="Retail_Price_Avg",
        color="Category",
        color_discrete_map=CAT_COLORS,
        size="Markup_Size",             # clipped >= 0; real Markup used for hover
        size_max=22,
        opacity=0.70,
        hover_name="Name",
        hover_data={"Markup": ":.2f", "Storage_Type": True},
        labels={"Price_per_kg": "Market Price (₹/kg)",
                "Retail_Price_Avg": "Retail Price (₹/kg)"},
        title="Market Price vs Retail Price — bubble size = markup",
    )
    # trendline from actual data
    m = np.polyfit(dff["Price_per_kg"], dff["Retail_Price_Avg"], 1)
    x_line = np.linspace(dff["Price_per_kg"].min(), dff["Price_per_kg"].max(), 200)
    fig_sc.add_trace(go.Scatter(
        x=x_line, y=np.polyval(m, x_line),
        mode="lines",
        line=dict(color="#C8821A", dash="dash", width=2),
        name=f"Trend  r={dff['Price_per_kg'].corr(dff['Retail_Price_Avg']):.2f}",
        showlegend=True,
    ))
    fig_sc.update_layout(**BASE, height=420,
                         xaxis=dict(gridcolor=GC),
                         yaxis=dict(gridcolor=GC),
                         legend=dict(orientation="h", y=-0.18))
    st.plotly_chart(fig_sc, use_container_width=True)

    fdiv()

    col1, col2 = st.columns(2)

    with col1:
        sec("Avg Market Price by Category")
        cs = cat_summary(dff).sort_values("Avg_Price", ascending=True)
        fig_bp = px.bar(
            cs, y="Category", x="Avg_Price", orientation="h",
            color="Category", color_discrete_map=CAT_COLORS,
            text=cs["Avg_Price"].apply(lambda v: f"₹{v:.0f}"),
            title="Average Market Price (₹/kg)",
        )
        fig_bp.update_traces(textposition="outside")
        fig_bp.update_layout(**BASE, showlegend=False, height=320,
                             xaxis=dict(gridcolor=GC, title="₹/kg"),
                             yaxis=dict(gridcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig_bp, use_container_width=True)

    with col2:
        sec("Market vs Retail — Side by Side")
        cs2 = cat_summary(dff).sort_values("Avg_Price", ascending=True)
        fig_ov = go.Figure()
        fig_ov.add_trace(go.Bar(
            y=cs2["Category"], x=cs2["Avg_Price"], orientation="h",
            name="Market Price", marker_color="rgba(45,90,64,0.55)",
            marker_line=dict(color="#2D5A40", width=1.2),
        ))
        fig_ov.add_trace(go.Bar(
            y=cs2["Category"], x=cs2["Avg_Retail"], orientation="h",
            name="Retail Price", marker_color="rgba(200,130,26,0.55)",
            marker_line=dict(color="#C8821A", width=1.2),
        ))
        fig_ov.update_layout(**BASE, barmode="overlay", height=320,
                             title="Market vs Retail (overlay)",
                             xaxis=dict(gridcolor=GC, title="₹/kg"),
                             yaxis=dict(gridcolor="rgba(0,0,0,0)"),
                             legend=dict(orientation="h", y=-0.22))
        st.plotly_chart(fig_ov, use_container_width=True)

    fdiv()

    col1, col2 = st.columns(2)
    with col1:
        sec("Retail Price Distribution")
        fig_hist = px.histogram(
            dff, x="Retail_Price_Avg",
            nbins=20, color_discrete_sequence=["#C8821A"],
            title="Retail Price — right-skewed distribution",
            labels={"Retail_Price_Avg": "Retail Price (₹/kg)"},
        )
        fig_hist.update_layout(**BASE,
                               xaxis=dict(gridcolor="rgba(0,0,0,0)"),
                               yaxis=dict(gridcolor=GC, title="Count"))
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        sec("Price Spread by Category")
        fig_box = px.box(
            dff, y="Category", x="Price_per_kg",
            color="Category", color_discrete_map=CAT_COLORS,
            orientation="h", points="outliers",
            hover_name="Name",
            title="Market Price Spread (box plot)",
            labels={"Price_per_kg": "₹/kg"},
        )
        fig_box.update_layout(**BASE, showlegend=False, height=340,
                              xaxis=dict(gridcolor=GC),
                              yaxis=dict(gridcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig_box, use_container_width=True)

    fdiv()

    # Correlation heatmap from actual data
    sec("Correlation Matrix", "Numeric variable relationships from real data")
    num_cols = ["Price_per_kg","Storage_Code","Retail_Price_Avg","Markup"]
    corr_mat = dff[num_cols].corr().round(2)
    fig_corr = go.Figure(go.Heatmap(
        z=corr_mat.values,
        x=corr_mat.columns.tolist(),
        y=corr_mat.index.tolist(),
        colorscale=[[0,"#3B7EBF"],[0.5,"#F7F4EE"],[1,"#C8821A"]],
        zmin=-1, zmax=1,
        text=corr_mat.values, texttemplate="%{text}",
        textfont=dict(size=14, color="white"),
    ))
    fig_corr.update_layout(**BASE, height=320, title="Pearson Correlation Heatmap")
    st.plotly_chart(fig_corr, use_container_width=True)

    insight("Price Dynamics",
        "Market price and retail price are strongly correlated — confirming supply-chain margins are "
        "relatively fixed percentages. However, markup shows <b>no significant correlation with price</b>, "
        "meaning expensive items do NOT guarantee high markup. "
        "<b>Cheap perishables like flowers and livestock are the true profit engines.</b>"
    )

# ╔══════════════════════════════════════════════════════════════════════╗
# ║  PAGE — MARKUP & PROFIT                                              ║
# ╚══════════════════════════════════════════════════════════════════════╝
elif "Markup" in page:

    sec("Profit Margin Analysis", "Where the real money is — and isn't")

    best_cat = cat_summary(dff).sort_values("Avg_Markup", ascending=False).iloc[0]
    worst_cat = cat_summary(dff).sort_values("Avg_Markup").iloc[0]
    cold_mk = dff[dff["Storage_Type"]=="Cold Storage Safe"]["Markup"].mean()
    no_mk   = dff[dff["Storage_Type"]=="No Cold Storage"]["Markup"].mean()

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Best Category",    best_cat["Category"],
              f"{best_cat['Avg_Markup']:.2f}× avg markup")
    c2.metric("Worst Category",   worst_cat["Category"],
              f"{worst_cat['Avg_Markup']:.2f}× avg markup")
    c3.metric("Cold Storage Lift",f"{cold_mk/no_mk:.1f}× higher",
              f"vs no-storage")
    c4.metric("Max Item Markup",  f"{dff['Markup'].max():.1f}×",
              dff.loc[dff['Markup'].idxmax(),'Name'])
    c5.metric("Negative Markup",  f"{(dff['Markup']<0).sum()} items",
              "oversupply / pricing issue")

    fdiv()

    col1, col2 = st.columns([3, 2])

    with col1:
        sec("Average Markup by Category")
        cs = cat_summary(dff).sort_values("Avg_Markup", ascending=True)
        fig_mc = px.bar(
            cs, y="Category", x="Avg_Markup", orientation="h",
            color="Category", color_discrete_map=CAT_COLORS,
            text=cs["Avg_Markup"].apply(lambda v: f"{v:.2f}×"),
            title="Mean Markup (×) by Category",
        )
        fig_mc.update_traces(textposition="outside")
        fig_mc.update_layout(**BASE, showlegend=False, height=360,
                             xaxis=dict(gridcolor=GC, title="Avg Markup (×)"),
                             yaxis=dict(gridcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig_mc, use_container_width=True)

    with col2:
        sec("Markup Radar Profile")
        cs_r = cat_summary(dff)
        cats_r  = cs_r["Category"].tolist()
        mkup_r  = cs_r["Avg_Markup"].tolist()
        fig_rad = go.Figure(go.Scatterpolar(
            r=mkup_r + [mkup_r[0]],
            theta=cats_r + [cats_r[0]],
            fill="toself",
            fillcolor="rgba(74,140,92,0.18)",
            line=dict(color="#4A8C5C", width=2),
        ))
        fig_rad.update_layout(**BASE, height=360,
                              title="Markup Profile — Radar",
                              polar=dict(
                                  bgcolor="rgba(0,0,0,0)",
                                  radialaxis=dict(
                                      visible=True, gridcolor=GC,
                                      range=[0, max(mkup_r)+2],
                                  ),
                                  angularaxis=dict(gridcolor=GC),
                              ))
        st.plotly_chart(fig_rad, use_container_width=True)

    fdiv()

    # Storage markup comparison
    sec("Markup by Storage Type", "Cold storage is the single biggest lever for profitability")

    st_mk = (
        dff.groupby("Storage_Type")["Markup"]
        .agg(["mean","median","std","count"])
        .round(3).reset_index()
    )
    st_mk.columns = ["Storage_Type","Avg_Markup","Median_Markup","Std_Markup","Count"]

    col1, col2 = st.columns(2)
    with col1:
        fig_smk = px.bar(
            st_mk.sort_values("Avg_Markup"),
            x="Storage_Type", y="Avg_Markup",
            color="Storage_Type", color_discrete_map=STORAGE_COLORS,
            text=st_mk.sort_values("Avg_Markup")["Avg_Markup"].apply(lambda v: f"{v:.2f}×"),
            title="Average Markup by Storage Type",
        )
        fig_smk.update_traces(textposition="outside", width=0.5)
        fig_smk.update_layout(**BASE, showlegend=False,
                              xaxis=dict(gridcolor="rgba(0,0,0,0)", title=None),
                              yaxis=dict(gridcolor=GC, title="Avg Markup (×)"))
        st.plotly_chart(fig_smk, use_container_width=True)

    with col2:
        fig_vln = px.violin(
            dff, x="Storage_Type", y="Markup",
            color="Storage_Type", color_discrete_map=STORAGE_COLORS,
            box=True, points="outliers",
            hover_name="Name",
            title="Markup Distribution — Violin",
        )
        fig_vln.update_layout(**BASE, showlegend=False,
                              xaxis_title=None,
                              yaxis=dict(gridcolor=GC, title="Markup (×)"))
        st.plotly_chart(fig_vln, use_container_width=True)

    fdiv()

    col1, col2 = st.columns(2)
    with col1:
        sec("Markup Distribution")
        fig_mhist = px.histogram(
            dff, x="Markup", nbins=25,
            color_discrete_sequence=["#2D5A40"],
            title="Markup — right-skewed, most items ≤ 2×",
            labels={"Markup": "Markup (×)"},
        )
        fig_mhist.update_layout(**BASE,
                                xaxis=dict(gridcolor="rgba(0,0,0,0)"),
                                yaxis=dict(gridcolor=GC, title="Count"))
        st.plotly_chart(fig_mhist, use_container_width=True)

    with col2:
        sec("Loss-Making Items (Negative Markup)")
        df_neg = dff[dff["Markup"] < 0].sort_values("Markup")[
            ["Name","Category","Price_per_kg","Retail_Price_Avg","Markup"]
        ]
        if df_neg.empty:
            st.info("No negative-markup items in the current filter.")
        else:
            fig_neg = px.bar(
                df_neg, y="Name", x="Markup", orientation="h",
                color="Category", color_discrete_map=CAT_COLORS,
                text=df_neg["Markup"].apply(lambda v: f"{v:.3f}"),
                title="Items with Negative Markup",
                labels={"Markup": "Markup (×)", "Name": ""},
            )
            fig_neg.update_traces(textposition="outside")
            fig_neg.update_layout(**BASE, showlegend=False,
                                  xaxis=dict(gridcolor=GC),
                                  yaxis=dict(gridcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig_neg, use_container_width=True)

    insight("The Cold Storage Opportunity",
        f"Cold-storage-safe products earn <b>{cold_mk:.2f}× average markup</b> vs "
        f"{no_mk:.2f}× for no-storage items — a {cold_mk/no_mk:.1f}× advantage. "
        "Storage eliminates forced selling at harvest-time lows. "
        "Perishables like strawberries, flowers, and livestock benefit most."
    )

# ╔══════════════════════════════════════════════════════════════════════╗
# ║  PAGE — STORAGE & SEASON                                             ║
# ╚══════════════════════════════════════════════════════════════════════╝
elif "Storage" in page:

    sec("Infrastructure & Seasonality Analysis",
        "How storage capability and crop timing shape profitability")

    ssn_mk = dff.groupby("Season")["Markup"].mean()
    all_s_mk = ssn_mk.get("All-season", 0)
    min_s = ssn_mk.idxmin()

    big_stats([
        (f"{(dff['Season']=='All-season').sum()}", "All-Season Crops", "supply year-round"),
        (f"{(dff['Storage_Type']=='No Cold Storage').sum()}", "No Cold Storage", "highest loss risk"),
        (f"{dff[dff['Storage_Type']=='Cold Storage Safe']['Markup'].mean():.2f}×", "Cold-Safe Markup", "best avg markup"),
        (f"₹{dff[dff['Season']=='Multi-season']['Price_per_kg'].mean():.0f}", "Multi-season Avg", "highest price season"),
        (f"{all_s_mk:.2f}×", "All-Season Markup", "consistent demand"),
    ])

    fdiv()

    col1, col2 = st.columns(2)

    with col1:
        sec("Market Price by Season")
        ssn_price = (
            dff.groupby("Season")
            .agg(Avg_Price=("Price_per_kg","mean"), Count=("Name","count"))
            .reset_index().sort_values("Avg_Price", ascending=False)
        )
        fig_sp = px.bar(
            ssn_price, x="Season", y="Avg_Price",
            color="Season", color_discrete_sequence=SEASON_COLORS,
            text=ssn_price["Avg_Price"].apply(lambda v: f"₹{v:.0f}"),
            title="Avg Market Price by Season (₹/kg)",
        )
        fig_sp.update_traces(textposition="outside", width=0.6)
        fig_sp.update_layout(**BASE, showlegend=False,
                             xaxis=dict(gridcolor="rgba(0,0,0,0)", title=None),
                             yaxis=dict(gridcolor=GC, title="₹/kg"))
        st.plotly_chart(fig_sp, use_container_width=True)

    with col2:
        sec("Markup by Season")
        ssn_mk2 = (
            dff.groupby("Season")
            .agg(Avg_Markup=("Markup","mean"))
            .reset_index().sort_values("Avg_Markup", ascending=False)
        )
        fig_sm = px.bar(
            ssn_mk2, x="Season", y="Avg_Markup",
            color="Season", color_discrete_sequence=SEASON_COLORS,
            text=ssn_mk2["Avg_Markup"].apply(lambda v: f"{v:.2f}×"),
            title="Avg Markup by Season (×)",
        )
        fig_sm.update_traces(textposition="outside", width=0.6)
        fig_sm.update_layout(**BASE, showlegend=False,
                             xaxis=dict(gridcolor="rgba(0,0,0,0)", title=None),
                             yaxis=dict(gridcolor=GC, title="Markup (×)"))
        st.plotly_chart(fig_sm, use_container_width=True)

    fdiv()

    # Real crosstab heatmap
    sec("Category × Season Heatmap", "Item counts from actual data")
    ct = pd.crosstab(dff["Category"], dff["Season"])
    fig_hm = px.imshow(
        ct,
        text_auto=True,
        color_continuous_scale=[[0,"#F7F4EE"],[0.15,"#C8DFC9"],[0.45,"#4A8C5C"],[1,"#0F2318"]],
        title="Products per Category × Season (actual counts)",
        aspect="auto",
    )
    fig_hm.update_traces(textfont=dict(size=13))
    fig_hm.update_layout(**BASE, height=380,
                         xaxis_title="Season", yaxis_title="Category",
                         coloraxis_colorbar_title="Count")
    st.plotly_chart(fig_hm, use_container_width=True)

    fdiv()

    col1, col2 = st.columns(2)

    with col1:
        sec("Price Spread by Storage Type")
        fig_vst = px.violin(
            dff, x="Storage_Type", y="Price_per_kg",
            color="Storage_Type", color_discrete_map=STORAGE_COLORS,
            box=True, points="outliers",
            hover_name="Name",
            title="Market Price Distribution by Storage",
        )
        fig_vst.update_layout(**BASE, showlegend=False,
                              xaxis_title=None,
                              yaxis=dict(gridcolor=GC, title="₹/kg"))
        st.plotly_chart(fig_vst, use_container_width=True)

    with col2:
        sec("Storage Need by Category")
        stacked = (
            dff.groupby(["Category","Storage_Type"])
            .size().reset_index(name="Count")
        )
        fig_stk = px.bar(
            stacked, x="Category", y="Count",
            color="Storage_Type", color_discrete_map=STORAGE_COLORS,
            barmode="stack",
            title="Storage Requirement per Category",
        )
        fig_stk.update_layout(**BASE,
                              xaxis=dict(gridcolor="rgba(0,0,0,0)", title=None),
                              yaxis=dict(gridcolor=GC, title="Count"),
                              legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig_stk, use_container_width=True)

    insight("Seasonality & Storage — Combined Effect",
        "All-season crops achieve the highest markup because demand is steady year-round. "
        f"{min_s} crops suffer the lowest margins ({ssn_mk[min_s]:.2f}×) from seasonal oversupply. "
        "Investing in cold storage lets even seasonal crops shift from distress selling "
        "to strategic selling — potentially doubling or tripling margins."
    )

# ╔══════════════════════════════════════════════════════════════════════╗
# ║  PAGE — RANKINGS                                                     ║
# ╚══════════════════════════════════════════════════════════════════════╝
elif "Rankings" in page:

    sec("Best Opportunities for D2C Farming",
        "Highest price items, highest markup items, and the profit sweet-spot")

    sub = st.radio("", [
        "🥇 Top Expensive",
        "📈 Top Markup",
        "🎯 Opportunity Matrix",
        "📋 Full Summary Table",
    ], horizontal=True, label_visibility="collapsed")

    cat_sel = st.selectbox("Filter by category",
                           ["All"] + sorted(dff["Category"].unique()), index=0)

    fdiv()

    # Single filtered frame used for ALL sub-pages — no external Series
    df_view = dff if cat_sel == "All" else dff[dff["Category"] == cat_sel]

    if df_view.empty:
        st.info("No items match the selected filter. Adjust the sidebar or category selector.")
        st.stop()

    if "Expensive" in sub:
        sec(f"Top 15 — Most Expensive Items  ({cat_sel})")
        top_exp = df_view.nlargest(15, "Price_per_kg").reset_index(drop=True)
        col1, col2 = st.columns([3, 2])
        with col1:
            fig_e = px.bar(
                top_exp.sort_values("Price_per_kg"),
                y="Name", x="Price_per_kg", orientation="h",
                color="Category", color_discrete_map=CAT_COLORS,
                text=top_exp.sort_values("Price_per_kg")["Price_per_kg"].apply(
                    lambda v: f"₹{v:,.0f}"),
                title="Market Price (₹/kg)",
                labels={"Price_per_kg": "₹/kg", "Name": ""},
            )
            fig_e.update_traces(textposition="outside")
            fig_e.update_layout(**BASE, showlegend=False, height=440,
                                xaxis=dict(gridcolor=GC),
                                yaxis=dict(gridcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig_e, use_container_width=True)

        with col2:
            fig_pie = px.pie(
                top_exp, names="Category", hole=0.5,
                color="Category", color_discrete_map=CAT_COLORS,
                title="Category Split",
            )
            fig_pie.update_layout(**BASE)
            st.plotly_chart(fig_pie, use_container_width=True)
            st.dataframe(
                top_exp[["Name","Category","Price_per_kg","Retail_Price_Avg","Markup"]]
                .style
                .background_gradient(subset=["Price_per_kg"], cmap="Oranges")
                .format({"Price_per_kg": "₹{:,.0f}",
                         "Retail_Price_Avg": "₹{:,.0f}",
                         "Markup": "{:.2f}×"}),
                use_container_width=True, hide_index=True,
            )

    elif "Markup" in sub:
        sec(f"Top 15 — Highest Markup Items  ({cat_sel})")
        top_mrk = df_view.nlargest(15, "Markup").reset_index(drop=True)
        col1, col2 = st.columns([3, 2])
        with col1:
            fig_m = px.bar(
                top_mrk.sort_values("Markup"),
                y="Name", x="Markup", orientation="h",
                color="Category", color_discrete_map=CAT_COLORS,
                text=top_mrk.sort_values("Markup")["Markup"].apply(
                    lambda v: f"{v:.2f}×"),
                title="Markup (×)",
                labels={"Markup": "Markup (×)", "Name": ""},
            )
            fig_m.update_traces(textposition="outside")
            fig_m.update_layout(**BASE, showlegend=False, height=440,
                                xaxis=dict(gridcolor=GC),
                                yaxis=dict(gridcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig_m, use_container_width=True)

        with col2:
            fig_pie2 = px.pie(
                top_mrk, names="Category", hole=0.5,
                color="Category", color_discrete_map=CAT_COLORS,
                title="Category Split",
            )
            fig_pie2.update_layout(**BASE)
            st.plotly_chart(fig_pie2, use_container_width=True)
            st.dataframe(
                top_mrk[["Name","Category","Price_per_kg","Retail_Price_Avg","Markup"]]
                .style
                .background_gradient(subset=["Markup"], cmap="Greens")
                .format({"Price_per_kg": "₹{:,.0f}",
                         "Retail_Price_Avg": "₹{:,.0f}",
                         "Markup": "{:.2f}×"}),
                use_container_width=True, hide_index=True,
            )

    elif "Matrix" in sub:
        sec("D2C Opportunity Matrix",
            "Sweet spot: low market price + high markup — ideal for scaling")

        # All data lives in df_view; x/y/size/color/text are column strings → no ShapeError
        fig_bub = px.scatter(
            df_view.reset_index(drop=True),   # ← single source of truth
            x="Price_per_kg",
            y="Markup",
            color="Category",
            size="Markup_Size",               # clipped >= 0; real Markup on axes/hover
            size_max=55,
            opacity=0.72,
            color_discrete_map=CAT_COLORS,
            hover_name="Name",                # ← column in df_view ✓
            hover_data={
                "Storage_Type": True,
                "Season": True,
                "Price_per_kg": ":.0f",
                "Markup": ":.2f",
            },
            text="Name",                      # ← column in df_view ✓
            labels={"Price_per_kg": "Market Price (₹/kg)",
                    "Markup": "Markup (×)"},
            title="Price vs Markup — Bubble size = markup potential",
        )
        fig_bub.add_vline(
            x=df_view["Price_per_kg"].median(),
            line_dash="dot", line_color="#AAAAAA", opacity=0.6,
            annotation_text="Median price",
            annotation_position="top right",
        )
        fig_bub.add_hline(
            y=df_view["Markup"].median(),
            line_dash="dot", line_color="#AAAAAA", opacity=0.6,
            annotation_text="Median markup",
            annotation_position="right",
        )
        fig_bub.add_annotation(
            x=df_view["Price_per_kg"].quantile(0.1),
            y=df_view["Markup"].quantile(0.9),
            text="🎯 D2C Sweet Spot<br>Low Price · High Markup",
            showarrow=False,
            font=dict(size=10, color="#1E6B30"),
            bgcolor="#E5F2EA", bordercolor="#4A8C5C",
            borderwidth=1, borderpad=6,
        )
        fig_bub.update_traces(textposition="top center", textfont=dict(size=8))
        fig_bub.update_layout(**BASE, height=520,
                              xaxis=dict(gridcolor=GC),
                              yaxis=dict(gridcolor=GC),
                              legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig_bub, use_container_width=True)

    elif "Summary" in sub:
        sec("Full Category Summary Table")
        summ = (
            dff.groupby("Category")
            .agg(
                Products=("Name","count"),
                Avg_Market_Price=("Price_per_kg","mean"),
                Median_Price=("Price_per_kg","median"),
                Avg_Retail=("Retail_Price_Avg","mean"),
                Avg_Markup=("Markup","mean"),
                Max_Markup=("Markup","max"),
                Negative_Markup=("Markup", lambda x: (x < 0).sum()),
            )
            .reset_index().round(2)
        )
        summ["Recommendation"] = summ["Avg_Markup"].apply(
            lambda v:
                "🟢 High Priority D2C" if v >= 3.0 else
                "🟡 Moderate Potential" if v >= 1.8 else
                "🔴 Low Priority"
        )
        st.dataframe(
            summ.style
            .background_gradient(subset=["Avg_Markup"], cmap="Greens")
            .background_gradient(subset=["Avg_Market_Price"], cmap="Oranges")
            .format({
                "Avg_Market_Price": "₹{:.0f}",
                "Median_Price":     "₹{:.0f}",
                "Avg_Retail":       "₹{:.0f}",
                "Avg_Markup":       "{:.2f}×",
                "Max_Markup":       "{:.1f}×",
            }),
            use_container_width=True, hide_index=True,
        )

    fdiv()
    insight("Top D2C Opportunities",
        "The most scalable D2C plays combine <b>low market price + high markup</b>. "
        f"The single best item in your dataset is "
        f"<b>{dff.loc[dff['Markup'].idxmax(),'Name']}</b> "
        f"({dff['Markup'].max():.1f}× markup at "
        f"₹{dff.loc[dff['Markup'].idxmax(),'Price_per_kg']:.0f}/kg). "
        "Flowers, livestock, and certain fruits offer consistently high returns with cold storage."
    )

# ╔══════════════════════════════════════════════════════════════════════╗
# ║  FOOTER                                                              ║
# ╚══════════════════════════════════════════════════════════════════════╝
st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
            flex-wrap:wrap;gap:.5rem;padding-bottom:1.5rem;">
  <span style="font-size:.75rem;color:#AAAAAA;">
    🌾 AgriSight · {len(df)} Agricultural Products · Gujarat &amp; Maharashtra
  </span>
  <span style="font-size:.75rem;color:#AAAAAA;">
    Data: piplanapane.in &nbsp;·&nbsp; BigBasket &nbsp;·&nbsp; Major Project Report
  </span>
</div>""", unsafe_allow_html=True)