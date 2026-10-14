from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Restaurant Location Intelligence", page_icon="📍", layout="wide")

DATA_PATH = Path(__file__).parent / "Dataset.csv"

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Normalize column names while preserving the original dataset.
    df.columns = [str(c).strip() for c in df.columns]
    for col in ["Latitude", "Longitude", "Aggregate rating", "Price range",
                "Average Cost for two", "Votes"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ["City", "Locality", "Cuisines", "Restaurant Name", "Rating text"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str).str.strip()
    return df

def safe_mean(series):
    values = pd.to_numeric(series, errors="coerce")
    return float(values.mean()) if values.notna().any() else 0.0

df = load_data(str(DATA_PATH))
st.title("📍 Restaurant Location-Based Analysis")
st.caption("Cognifyz Technologies • Machine Learning Task 4 • Explore restaurant distribution, ratings, cuisines, and price ranges.")

required = ["City", "Locality", "Latitude", "Longitude", "Aggregate rating", "Cuisines", "Price range"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error(f"Dataset is missing required columns: {', '.join(missing)}")
    st.stop()

# Exclude impossible (0,0) coordinates from mapping, but retain them in other analyses.
map_df = df.dropna(subset=["Latitude", "Longitude"]).copy()
map_df = map_df[(map_df["Latitude"].between(-90, 90)) &
                (map_df["Longitude"].between(-180, 180)) &
                ~((map_df["Latitude"] == 0) & (map_df["Longitude"] == 0))]

with st.sidebar:
    st.header("Filters")
    cities = sorted(df["City"].dropna().astype(str).unique().tolist())
    chosen_cities = st.multiselect("City", cities, default=[])
    city_df = df[df["City"].isin(chosen_cities)] if chosen_cities else df.copy()
    localities = sorted(city_df["Locality"].dropna().astype(str).unique().tolist())
    chosen_localities = st.multiselect("Locality", localities, default=[])
    ratings = pd.to_numeric(city_df["Aggregate rating"], errors="coerce").dropna()
    min_rating = float(ratings.min()) if not ratings.empty else 0.0
    max_rating = float(ratings.max()) if not ratings.empty else 5.0
    rating_range = st.slider("Aggregate rating", 0.0, 5.0,
                             (max(0.0, min_rating), min(5.0, max_rating)), 0.1)
    price_values = sorted(pd.to_numeric(city_df["Price range"], errors="coerce").dropna().unique().tolist())
    chosen_prices = st.multiselect("Price range", price_values, default=[])
    map_limit = st.slider("Maximum map points", 500, 10000, 5000, 500)

filtered = city_df.copy()
if chosen_localities:
    filtered = filtered[filtered["Locality"].isin(chosen_localities)]
filtered = filtered[
    pd.to_numeric(filtered["Aggregate rating"], errors="coerce").between(rating_range[0], rating_range[1])
]
if chosen_prices:
    filtered = filtered[pd.to_numeric(filtered["Price range"], errors="coerce").isin(chosen_prices)]

filtered_map = map_df[map_df.index.isin(filtered.index)].copy()
if len(filtered_map) > map_limit:
    filtered_map = filtered_map.sample(map_limit, random_state=42)

# Summary metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Restaurants in selection", f"{len(filtered):,}")
m2.metric("Cities", f"{filtered['City'].nunique():,}")
m3.metric("Average rating", f"{safe_mean(filtered['Aggregate rating']):.2f} / 5")
m4.metric("Mapped restaurants", f"{len(filtered_map):,}")

tab_map, tab_area, tab_cuisine, tab_data = st.tabs(
    ["🗺️ Restaurant Map", "🏙️ City & Locality", "🍽️ Cuisines & Prices", "📄 Data Explorer"]
)

with tab_map:
    st.subheader("Geographical distribution")
    st.write("Each point represents a restaurant. Invalid or missing coordinates and (0, 0) coordinates are excluded from the map.")
    if filtered_map.empty:
        st.warning("No valid coordinates match the current filters.")
    else:
        hover_cols = [c for c in ["Restaurant Name", "City", "Locality", "Cuisines",
                                  "Aggregate rating", "Price range"] if c in filtered_map.columns]
        fig = px.scatter_map(
            filtered_map,
            lat="Latitude", lon="Longitude",
            color="Aggregate rating" if filtered_map["Aggregate rating"].notna().any() else None,
            size="Votes" if "Votes" in filtered_map.columns else None,
            size_max=13,
            hover_name="Restaurant Name" if "Restaurant Name" in filtered_map.columns else None,
            hover_data=hover_cols,
            zoom=1,
            height=600,
            map_style="open-street-map",
            title="Restaurant locations"
        )
        fig.update_layout(margin={"r": 0, "t": 45, "l": 0, "b": 0})
        st.plotly_chart(fig, use_container_width=True)
    st.info("Tip: use the City and Locality filters in the sidebar to zoom the analysis to a specific area.")

with tab_area:
    st.subheader("Restaurant concentration by city")
    city_summary = filtered.groupby("City", dropna=False).agg(
        Restaurant_Count=("Restaurant Name", "count"),
        Average_Rating=("Aggregate rating", "mean"),
        Average_Cost_For_Two=("Average Cost for two", "mean"),
        Average_Price_Range=("Price range", "mean"),
        Localities=("Locality", "nunique")
    ).reset_index().sort_values("Restaurant_Count", ascending=False)
    if not city_summary.empty:
        left, right = st.columns(2)
        with left:
            fig = px.bar(city_summary.head(20), x="Restaurant_Count", y="City", orientation="h",
                         title="Top 20 cities by restaurant count", labels={"Restaurant_Count":"Restaurants"})
            fig.update_layout(yaxis={"categoryorder":"total ascending"})
            st.plotly_chart(fig, use_container_width=True)
        with right:
            rating_city = city_summary.dropna(subset=["Average_Rating"]).sort_values("Average_Rating", ascending=False).head(20)
            fig = px.bar(rating_city, x="Average_Rating", y="City", orientation="h",
                         title="Highest average-rated cities (up to 20)", range_x=[0, 5])
            fig.update_layout(yaxis={"categoryorder":"total ascending"})
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(city_summary.round(2), use_container_width=True, hide_index=True)
    else:
        st.warning("No city-level data matches these filters.")

    st.subheader("Locality-level analysis")
    locality_summary = filtered.groupby(["City", "Locality"], dropna=False).agg(
        Restaurant_Count=("Restaurant Name", "count"),
        Average_Rating=("Aggregate rating", "mean"),
        Average_Cost_For_Two=("Average Cost for two", "mean"),
        Average_Price_Range=("Price range", "mean")
    ).reset_index().sort_values("Restaurant_Count", ascending=False)
    st.dataframe(locality_summary.head(100).round(2), use_container_width=True, hide_index=True)
    st.caption("Showing up to 100 localities, ordered by restaurant count.")

with tab_cuisine:
    st.subheader("Cuisine patterns")
    cuisine_rows = filtered[["Cuisines"]].dropna().copy()
    cuisine_rows["Cuisines"] = cuisine_rows["Cuisines"].astype(str).str.split(",")
    cuisine_rows = cuisine_rows.explode("Cuisines")
    cuisine_rows["Cuisines"] = cuisine_rows["Cuisines"].str.strip()
    cuisine_rows = cuisine_rows[cuisine_rows["Cuisines"].ne("") & cuisine_rows["Cuisines"].ne("Unknown")]
    cuisine_counts = cuisine_rows["Cuisines"].value_counts().head(20).rename_axis("Cuisine").reset_index(name="Restaurant_Count")
    if not cuisine_counts.empty:
        fig = px.bar(cuisine_counts.sort_values("Restaurant_Count"), x="Restaurant_Count", y="Cuisine",
                     orientation="h", title="Most common cuisines (top 20)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Cuisine information is unavailable for this selection.")

    st.subheader("Price range distribution")
    price_df = filtered.dropna(subset=["Price range"]).copy()
    if not price_df.empty:
        price_counts = price_df["Price range"].value_counts().sort_index().rename_axis("Price range").reset_index(name="Restaurant_Count")
        fig = px.bar(price_counts, x="Price range", y="Restaurant_Count",
                     title="Restaurants by price range", text="Restaurant_Count")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No price range information for this selection.")

    if "Average Cost for two" in filtered.columns:
        cost = filtered.dropna(subset=["Average Cost for two"])
        if not cost.empty:
            fig = px.histogram(cost, x="Average Cost for two", nbins=30,
                               title="Distribution of average cost for two")
            st.plotly_chart(fig, use_container_width=True)

with tab_data:
    st.subheader("Filtered dataset")
    st.write(f"Showing {len(filtered):,} rows that match the current filters.")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    csv_bytes = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download filtered data (CSV)", data=csv_bytes,
                       file_name="filtered_restaurant_location_analysis.csv", mime="text/csv")
    city_csv = filtered.groupby("City", dropna=False).agg(
        Restaurant_Count=("Restaurant Name", "count"),
        Average_Rating=("Aggregate rating", "mean"),
        Average_Cost_For_Two=("Average Cost for two", "mean"),
        Average_Price_Range=("Price range", "mean")
    ).reset_index().to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download city summary (CSV)", data=city_csv,
                       file_name="city_location_summary.csv", mime="text/csv")

st.divider()
st.caption("Built with Python, Pandas, Plotly, and Streamlit. Results describe the provided dataset and are not a live restaurant directory.")
