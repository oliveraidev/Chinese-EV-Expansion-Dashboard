import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Chinese EV Dashboard", layout="centered")

st.title("Chinese EV Expansion Dashboard")

brands = pd.read_csv("../data/brands.csv", sep=";")
models = pd.read_csv("../data/model_specs.csv", sep=";")
expansion = pd.read_csv("../data/expansion_markets.csv", sep=";")

df = models.merge(brands, on="brand", how="left")
df = df.merge(expansion, on="brand", how="left")

brand_filter = st.sidebar.selectbox(
    "Brand",
    ["All"] + sorted(df["brand"].unique())
)

if brand_filter != "All":
    df = df[df["brand"] == brand_filter]

df["price_for_score"] = df["price_eur"].fillna(df["price_eur"].mean())

df["competitiveness_score"] = (
    df["range_km"] / 10
    + df["expansion_score"] * 5
    - df["price_for_score"] / 1000
)

st.subheader("Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Avg price (€)", round(df["price_eur"].mean()))
col2.metric("Avg range (km)", round(df["range_km"].mean()))
col3.metric("Avg battery (kWh)", round(df["battery_kwh"].mean(), 1))
col4.metric("Avg expansion", round(df["expansion_score"].mean(), 1))

st.subheader("EV Models")

st.dataframe(
    df[
        [
            "brand",
            "model",
            "market",
            "price_eur",
            "range_km",
            "range_standard",
            "battery_kwh",
            "battery_type",
            "segment",
            "source_name",
            "data_status"
        ]
    ],
    use_container_width=True,
    height=260
)

st.subheader("Top Export Brands")

ranking = (
    df.groupby("brand")["expansion_score"]
    .mean()
    .sort_values(ascending=False)
)

fig1, ax1 = plt.subplots(figsize=(5, 2.8))
ranking.plot(kind="bar", ax=ax1)
ax1.set_ylabel("Expansion score")
ax1.set_xlabel("")
ax1.tick_params(axis="x", labelrotation=45, labelsize=8)
st.pyplot(fig1, use_container_width=False)

st.subheader("Price vs Range")

plot_df = df.dropna(subset=["price_eur", "range_km"])

fig2, ax2 = plt.subplots(figsize=(5, 3))

ax2.scatter(plot_df["price_eur"], plot_df["range_km"])

for _, row in plot_df.iterrows():
    ax2.annotate(
        row["brand"],
        (row["price_eur"], row["range_km"]),
        fontsize=7
    )

ax2.set_xlabel("Price (€)")
ax2.set_ylabel("Range (km)")
ax2.set_title("Price vs Range", fontsize=10)

st.pyplot(fig2, use_container_width=False)

st.subheader("Average Range by Battery Type")

battery_range = (
    df.groupby("battery_type")["range_km"]
    .mean()
    .sort_values(ascending=False)
)

fig3, ax3 = plt.subplots(figsize=(5, 2.8))
battery_range.plot(kind="bar", ax=ax3)
ax3.set_ylabel("Range (km)")
ax3.set_xlabel("")
ax3.tick_params(axis="x", labelrotation=45, labelsize=8)
st.pyplot(fig3, use_container_width=False)

st.subheader("Competitiveness Ranking")

st.dataframe(
    df[
        ["brand", "model", "competitiveness_score", "data_status"]
    ].sort_values(
        "competitiveness_score",
        ascending=False
    ),
    use_container_width=True,
    height=260
)

st.subheader("Data Notes")

st.write(
    "Vehicle data is manually curated from public sources. "
    "Range standards differ by source, including EV Database real range, WLTP and CLTC. "
    "Expansion score and competitiveness score are custom analytical indices, not official industry metrics."
)