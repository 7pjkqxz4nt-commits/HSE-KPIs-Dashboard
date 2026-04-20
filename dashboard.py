import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

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
trend = filtered_df.groupby("Year").size()

avg_per_year = int(trend.mean()) if len(trend) > 0 else 0

if len(trend) > 0:
    max_year = trend.idxmax()
    max_value = trend.max()
else:
    max_year = "N/A"
    max_value = 0

if len(trend) > 1:
    percent_change = ((trend.iloc[-1] - trend.iloc[0]) / trend.iloc[0]) * 100
else:
    percent_change = 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Fatalities", total_fatalities)
col2.metric("Avg per Year", avg_per_year)
col3.metric("Highest Year", f"{max_year} ({max_value})")

if percent_change > 0:
    col4.metric("Trend %", f"{percent_change:.1f}%", "🔺 Increasing")
else:
    col4.metric("Trend %", f"{percent_change:.1f}%", "🔻 Decreasing")

# ==============================
# DATA PREVIEW
# ==============================
st.subheader("📊 Filtered Data")
st.write(filtered_df.head())

# ==============================
# CHART 1 — TREND
# ==============================
st.subheader("📈 Fatalities Trend")

fig1, ax1 = plt.subplots()
trend.plot(marker='o', ax=ax1)
ax1.set_xlabel("Year")
ax1.set_ylabel("Fatalities")
ax1.grid()

st.pyplot(fig1)

# ==============================
# CHART 2 — AUTHORITY
# ==============================
st.subheader("🏢 Authority Distribution")

auth = filtered_df["Enforcing authority [Note 3]"].value_counts()

fig2, ax2 = plt.subplots()
auth.plot(kind='bar', ax=ax2)
ax2.set_xlabel("Authority")
ax2.set_ylabel("Count")

st.pyplot(fig2)

# ==============================
# CHART 3 — REGION
# ==============================
st.subheader("🌍 Top Risk Regions")

region = filtered_df["Region"].value_counts().head(10)

fig3, ax3 = plt.subplots()
region.plot(kind='bar', ax=ax3)
ax3.set_xlabel("Region")
ax3.set_ylabel("Fatalities")

st.pyplot(fig3)

# ==============================
# CHART 4 — INDUSTRY
# ==============================
st.subheader("🏭 Top Industries by Fatalities")

industry_counts = filtered_df["Industry"].value_counts().head(10)

fig4, ax4 = plt.subplots()
industry_counts.plot(kind='bar', ax=ax4)
ax4.set_xlabel("Industry")
ax4.set_ylabel("Fatalities")

st.pyplot(fig4)

# ==============================
# CHART 5 — ACCIDENT TYPE
# ==============================
st.subheader("⚠️ Fatalities by Accident Type")

accident_counts = filtered_df["Kind of accident"].value_counts().head(10)

fig5, ax5 = plt.subplots()
accident_counts.plot(kind='bar', ax=ax5)
ax5.set_xlabel("Accident Type")
ax5.set_ylabel("Fatalities")

st.pyplot(fig5)

# ==============================
# AI INSIGHTS
# ==============================
st.subheader("🤖 AI Insights")

if len(trend) > 1:
    values = trend.values
    years_list = trend.index.tolist()

    max_value = values.max()
    max_year = years_list[values.argmax()]

    percent_change = ((values[-1] - values[0]) / values[0]) * 100

    st.write(f"⚠️ Highest fatalities: {max_value} in {max_year}")
    st.write(f"📊 Change: {percent_change:.2f}%")

    if percent_change > 0:
        st.error("🚨 Increasing trend — Action required!")
    else:
        st.success("✅ Improving trend — Keep monitoring")

# ==============================
# AI INSIGHT — INDUSTRY
# ==============================
if len(industry_counts) > 0:
    top_industry = industry_counts.index[0]
    top_value = industry_counts.iloc[0]

    st.error(f"🚨 Highest risk industry: {top_industry} ({top_value} fatalities)")

# ==============================
# AI INSIGHT — ACCIDENT
# ==============================
if len(accident_counts) > 0:
    top_accident = accident_counts.index[0]
    top_value = accident_counts.iloc[0]

    st.error(f"🚨 Most dangerous accident type: {top_accident} ({top_value} fatalities)")

# ==============================
# MAP VISUALIZATION
# ==============================
st.subheader("🗺️ Fatalities Map (Region-based)")

map_data = filtered_df["Region"].value_counts().reset_index()
map_data.columns = ["Region", "Fatalities"]

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
