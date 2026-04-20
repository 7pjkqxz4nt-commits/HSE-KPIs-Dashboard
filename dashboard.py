import pandas as pd
import streamlit as st
import plotly.express as px

# ==============================
# LOAD DATA
# ==============================
df = pd.read_excel("../data/fatalities.xlsx")

# ==============================
# CLEAN DATA
# ==============================
df["Year"] = df["Year\n[Note 1]"].astype(str)
df["Year"] = df["Year"].str.replace("p", "")

df.rename(columns={
    "Top-level Industry (SIC section)\n[Note 5]": "Industry"
}, inplace=True)

# ==============================
# TITLE
# ==============================
st.title("🚨 HSE Fatalities Dashboard")

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.header("Filters")

years = st.sidebar.multiselect(
    "Select Year",
    df["Year"].unique(),
    default=df["Year"].unique()
)

regions = st.sidebar.multiselect(
    "Select Region",
    df["Region"].dropna().unique(),
    default=df["Region"].dropna().unique()
)

authorities = st.sidebar.multiselect(
    "Select Authority",
    df["Enforcing authority [Note 3]"].dropna().unique(),
    default=df["Enforcing authority [Note 3]"].dropna().unique()
)

industries = st.sidebar.multiselect(
    "Select Industry",
    df["Industry"].dropna().unique(),
    default=df["Industry"].dropna().unique()
)

accidents = st.sidebar.multiselect(
    "Select Accident Type",
    df["Kind of accident"].dropna().unique(),
    default=df["Kind of accident"].dropna().unique()
)

# ==============================
# APPLY FILTERS
# ==============================
filtered_df = df[
    (df["Year"].isin(years)) &
    (df["Region"].isin(regions)) &
    (df["Enforcing authority [Note 3]"].isin(authorities)) &
    (df["Industry"].isin(industries)) &
    (df["Kind of accident"].isin(accidents))
]

# ==============================
# KPI CARDS
# ==============================
st.subheader("📊 Key Metrics")

total_fatalities = len(filtered_df)
trend = filtered_df.groupby("Year").size().reset_index(name="Fatalities")

avg_per_year = int(trend["Fatalities"].mean()) if len(trend) > 0 else 0

if len(trend) > 0:
    max_row = trend.loc[trend["Fatalities"].idxmax()]
    max_year = max_row["Year"]
    max_value = max_row["Fatalities"]
else:
    max_year, max_value = "N/A", 0

if len(trend) > 1:
    percent_change = ((trend["Fatalities"].iloc[-1] - trend["Fatalities"].iloc[0]) /
                      trend["Fatalities"].iloc[0]) * 100
else:
    percent_change = 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Fatalities", total_fatalities)
col2.metric("Avg per Year", avg_per_year)
col3.metric("Highest Year", f"{max_year} ({max_value})")

if percent_change > 0:
    col4.metric("Trend %", f"{percent_change:.1f}%", "Increasing")
else:
    col4.metric("Trend %", f"{percent_change:.1f}%", "Decreasing")

# ==============================
# DATA PREVIEW
# ==============================
st.subheader("📊 Filtered Data")
st.dataframe(filtered_df)

# ==============================
# CHART 1 — TREND
# ==============================
st.subheader("📈 Fatalities Trend")

fig1 = px.line(trend, x="Year", y="Fatalities", markers=True)
st.plotly_chart(fig1, use_container_width=True)

# ==============================
# CHART 2 — AUTHORITY
# ==============================
st.subheader("🏢 Authority Distribution")

auth = filtered_df["Enforcing authority [Note 3]"].value_counts().reset_index()
auth.columns = ["Authority", "Count"]

fig2 = px.bar(auth, x="Authority", y="Count")
st.plotly_chart(fig2, use_container_width=True)

# ==============================
# CHART 3 — REGION
# ==============================
st.subheader("🌍 Top Risk Regions")

region = filtered_df["Region"].value_counts().head(10).reset_index()
region.columns = ["Region", "Fatalities"]

fig3 = px.bar(region, x="Region", y="Fatalities")
st.plotly_chart(fig3, use_container_width=True)

# ==============================
# CHART 4 — INDUSTRY
# ==============================
st.subheader("🏭 Top Industries")

industry_counts = filtered_df["Industry"].value_counts().head(10).reset_index()
industry_counts.columns = ["Industry", "Fatalities"]

fig4 = px.bar(industry_counts, x="Industry", y="Fatalities")
st.plotly_chart(fig4, use_container_width=True)

# ==============================
# CHART 5 — ACCIDENT TYPE
# ==============================
st.subheader("⚠️ Accident Types")

accident_counts = filtered_df["Kind of accident"].value_counts().head(10).reset_index()
accident_counts.columns = ["Accident", "Fatalities"]

fig5 = px.bar(accident_counts, x="Accident", y="Fatalities")
st.plotly_chart(fig5, use_container_width=True)

# ==============================
# AI INSIGHTS
# ==============================
st.subheader("🤖 AI Insights")

if len(trend) > 1:
    st.write(f"⚠️ Highest fatalities: {max_value} in {max_year}")
    st.write(f"📊 Change: {percent_change:.2f}%")

    if percent_change > 0:
        st.error("🚨 Increasing trend — Action required!")
    else:
        st.success("✅ Improving trend")

# ==============================
# MAP
# ==============================
st.subheader("🗺️ Map")

map_data = region.copy()

region_coords = {
    "London": [51.5074, -0.1278],
    "North West": [53.4808, -2.2426],
    "East Midlands": [52.6369, -1.1398],
    "Yorkshire and The Humber": [53.8008, -1.5491],
    "Scotland": [55.9533, -3.1883]
}

map_data["lat"] = map_data["Region"].map(lambda x: region_coords.get(x, [None, None])[0])
map_data["lon"] = map_data["Region"].map(lambda x: region_coords.get(x, [None, None])[1])

map_data = map_data.dropna()

st.map(map_data.rename(columns={"lat": "latitude", "lon": "longitude"}))
