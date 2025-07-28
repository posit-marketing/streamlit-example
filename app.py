import pandas as pd
import streamlit as st
from pygris import tracts
import geopandas as gp
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="U.S. Trauma Hospital Analytics")

# Add custom CSS styling at the top of your app
st.markdown(
    """
    <style>
        .main-header {
            font-size: 2.5rem;
            margin-top: -50px !important;
            padding-top: 0px !important;
            font-weight: 700;
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Update your title
st.markdown(
    '<h1 class="main-header">🏥 U.S. Trauma Hospital Analytics</h1>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.title("Welcome to the U.S. Trauma Hospital Locations Dashboard")
    st.write(
        "This dashboard provides a comprehensive visualization of U.S. trauma hospital locations across Arizona, California, and Wisconsin. It displays the precise geographical coordinates of designated trauma centers and illustrates the minimum distance from various census tract centroids to the nearest trauma facility."
    )
    st.header("Filter state")
    state = st.selectbox(
        "State",
        options=(
            "AK",
            "AL",
            "AR",
            "AZ",
            "CA",
            "CO",
            "CT",
            "DC",
            "DE",
            "FL",
            "GA",
            "HI",
            "IA",
            "ID",
            "IL",
            "IN",
            "KS",
            "KY",
            "LA",
            "MA",
            "MD",
            "ME",
            "MI",
            "MN",
            "MO",
            "MS",
            "MT",
            "NC",
            "ND",
            "NE",
            "NH",
            "NJ",
            "NM",
            "NV",
            "NY",
            "OH",
            "OK",
            "OR",
            "PA",
            "RI",
            "SC",
            "SD",
            "TN",
            "TX",
            "UT",
            "VA",
            "VT",
            "WA",
            "WI",
            "WV",
            "WY",
        ),
    )
    st.caption(
        'Based on the tutorial "[Distance and proximity analysis in Python](https://walker-data.com/posts/proximity-analysis/)" by Kyle Walker.'
    )


@st.cache_data
def get_data(st_filter):
    state_tracts = tracts(st_filter, cb=True, year=2021, cache=True).to_crs(6571)
    state_tracts = state_tracts.to_crs("EPSG:4326")
    return state_tracts


state_tracts = get_data(state)


@st.cache_data
def load_data(state):
    trauma = gp.read_file("trauma.geojson")
    trauma = trauma[trauma["STATE"] == state]
    return trauma


trauma = load_data(state)

# Add this code after loading the trauma data and before the columns section

# Calculate metrics for the selected state
total_hospitals = len(trauma)

# Count Level I trauma centers (any facility with Level I designation, but not Level II only)
level_i_pattern = r"LEVEL I(?!I)"  # LEVEL I not followed by another I
level_i_centers = trauma[
    trauma["TRAUMA"].str.contains(level_i_pattern, na=False, regex=True)
].shape[0]

# Count Level II trauma centers (any facility with Level II designation, but not Level III only)
level_ii_pattern = r"LEVEL II(?!I)"  # LEVEL II not followed by another I
level_ii_centers = trauma[
    trauma["TRAUMA"].str.contains(level_ii_pattern, na=False, regex=True)
].shape[0]

# Count Level III trauma centers (any facility with Level III designation)
level_iii_pattern = r"LEVEL III(?!I)"  # LEVEL III not followed by another I
level_iii_centers = trauma[
    trauma["TRAUMA"].str.contains(level_iii_pattern, na=False, regex=True)
].shape[0]

# Count helipads
helipads = trauma[trauma["HELIPAD"] == "Y"].shape[0]

# Calculate total number of beds
total_beds = trauma["BEDS"].sum()

# Add this dictionary at the top of your file (after the imports)
state_names = {
    "AK": "Alaska",
    "AL": "Alabama",
    "AR": "Arkansas",
    "AZ": "Arizona",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DC": "District of Columbia",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "IA": "Iowa",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "MA": "Massachusetts",
    "MD": "Maryland",
    "ME": "Maine",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MO": "Missouri",
    "MS": "Mississippi",
    "MT": "Montana",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "NE": "Nebraska",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NV": "Nevada",
    "NY": "New York",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VA": "Virginia",
    "VT": "Vermont",
    "WA": "Washington",
    "WI": "Wisconsin",
    "WV": "West Virginia",
    "WY": "Wyoming",
}

metric_col1, metric_col2, metric_col3, metric_col4, metric_col5, metric_col6 = (
    st.columns(6)
)

# Group metrics into logical sections
st.markdown(f"### 📊 {state_names.get(state, state)} Hospital Overview")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Hospitals", total_hospitals, help="All trauma centers in selected state"
    )

with col2:
    st.metric(
        "Total Beds", f"{total_beds:,}", help="Combined capacity across all centers"
    )

with col3:
    st.metric(
        "Helicopter Ready",
        f"{helipads}/{total_hospitals}",
        help="Hospitals with helipads",
    )

st.markdown("### 🚨 Trauma Level Breakdown")
col4, col5, col6 = st.columns(3)

with col4:
    st.metric("Level I Centers", level_i_centers, help="Highest level trauma care")

with col5:
    st.metric("Level II Centers", level_ii_centers, help="Advanced trauma care")

with col6:
    st.metric("Level III Centers", level_iii_centers, help="General trauma care")

st.divider()  # Add a visual separator

col1, col2 = st.columns(2)

with st.container():
    with col1:
        st.subheader("🗺️ Geographic Distribution")
        st.map(trauma)

    # Replace your raw data section with a more polished table
    with col2:
        st.subheader("🏥 Hospital Directory")

        # Create a more user-friendly data display
        display_data = trauma[
            ["NAME", "CITY", "STATE", "TRAUMA", "BEDS", "HELIPAD", "OWNER"]
        ].copy()
        display_data["HELIPAD"] = display_data["HELIPAD"].map({"Y": "✅", "N": "❌"})
        display_data.columns = [
            "Hospital Name",
            "City",
            "State",
            "Trauma Level",
            "Beds",
            "Helipad",
            "Owner Type",
        ]

        # Add search functionality
        search_term = st.text_input(
            "🔍 Search hospitals:", placeholder="Enter hospital name or city..."
        )
        if search_term:
            mask = display_data["Hospital Name"].str.contains(
                search_term, case=False, na=False
            ) | display_data["City"].str.contains(search_term, case=False, na=False)
            display_data = display_data[mask]

        st.dataframe(display_data, use_container_width=True, height=400)

        state_tracts = state_tracts.to_crs(6571)
        trauma = trauma.to_crs(6571)
        state_buffer = gp.GeoDataFrame(geometry=state_tracts.dissolve().buffer(100000))
        state_trauma = gp.sjoin(trauma, state_buffer, how="inner")
        tract_centroids = state_tracts.centroid
        dist = tract_centroids.geometry.apply(
            lambda g: state_trauma.distance(g, align=False)
        )
        min_dist = dist.min(axis="columns") / 1000
        hist_values = np.histogram(min_dist, bins=24, range=(0, 24))[0]

# Replace your current distance plotting section with this:

# Prepare data for visualization
min_distances_df = pd.DataFrame(
    {"distance_km": min_dist, "tract_id": range(len(min_dist))}
)

# Calculate statistics
mean_dist = min_distances_df["distance_km"].mean()
median_dist = min_distances_df["distance_km"].median()

# Create beautiful interactive Plotly histogram
fig = go.Figure()

# Add the main histogram
fig.add_trace(
    go.Histogram(
        x=min_distances_df["distance_km"],
        nbinsx=30,
        name="Census Tracts",
        marker=dict(color="#2E86AB", opacity=0.8, line=dict(color="white", width=1)),
        hovertemplate="<b>Distance Range:</b> %{x:.1f} km<br>"
        + "<b>Number of Tracts:</b> %{y}<br>"
        + "<b>Percentage:</b> %{y:.0f} tracts<br>"
        + "<extra></extra>",
    )
)

# Add mean line with annotation
fig.add_vline(
    x=mean_dist,
    line_dash="dash",
    line_color="#006400",
    line_width=2,
    annotation_text=f"Mean: {mean_dist:.1f} km",
    annotation_position="top right",
    annotation_font=dict(size=16, color="#006400"),
)

# Add median line with annotation
fig.add_vline(
    x=median_dist,
    line_dash="dash",
    line_color="#301934",
    line_width=2,
    annotation_text=f"Median: {median_dist:.1f} km",
    annotation_position="bottom right",
    annotation_font=dict(size=16, color="#301934"),
)

# Update layout for professional appearance
fig.update_layout(
    title=dict(
        text=f"Distance to Nearest Trauma Center in {state_names.get(state, state)}<br><sub>Distribution across {len(min_distances_df):,} census tracts</sub>",
        x=0.5,
        font=dict(size=18, color="#2c3e50", family="Arial, sans-serif"),
    ),
    xaxis=dict(
        title="Distance to Nearest Trauma Center (km)",
        title_font=dict(size=14, color="#2c3e50"),
        tickfont=dict(size=11),
        gridcolor="#ecf0f1",
        showgrid=True,
        zeroline=False,
    ),
    yaxis=dict(
        title="Number of Census Tracts",
        title_font=dict(size=14, color="#2c3e50"),
        tickfont=dict(size=11),
        gridcolor="#ecf0f1",
        showgrid=True,
        zeroline=False,
    ),
    plot_bgcolor="white",
    paper_bgcolor="white",
    showlegend=False,
    font=dict(family="Arial, sans-serif"),
    margin=dict(t=100, r=40, b=60, l=60),
    height=500,
    dragmode="pan",  # Allow panning instead of selection
)

# Display the plot in Streamlit
st.plotly_chart(fig, use_container_width=True)

# Add insights section with expandable details
with st.expander("📊 Distance Analysis Insights", expanded=False):
    insight_col1, insight_col2, insight_col3 = st.columns(3)

    with insight_col1:
        st.metric("Mean Distance", f"{mean_dist:.1f} km")
        st.metric("Median Distance", f"{median_dist:.1f} km")

    with insight_col2:
        within_10km = (min_distances_df["distance_km"] <= 10).sum()
        within_10km_pct = (min_distances_df["distance_km"] <= 10).mean() * 100
        st.metric("Within 10km", f"{within_10km:,} tracts", f"{within_10km_pct:.1f}%")

        over_50km = (min_distances_df["distance_km"] > 50).sum()
        over_50km_pct = (min_distances_df["distance_km"] > 50).mean() * 100
        st.metric("Over 50km", f"{over_50km:,} tracts", f"{over_50km_pct:.1f}%")

    with insight_col3:
        st.metric("Max Distance", f"{min_distances_df['distance_km'].max():.1f} km")
        st.metric("Min Distance", f"{min_distances_df['distance_km'].min():.2f} km")

    # Add a brief interpretation
    st.markdown("---")
    st.markdown(
        f"""
    **Key Insights for {state_names.get(state, state)}:**
    - **{within_10km_pct:.1f}%** of census tracts are within 10km of a trauma center
    - **{over_50km_pct:.1f}%** of tracts are more than 50km from the nearest trauma center
    - The **median distance ({median_dist:.1f} km)** is lower than the **mean distance ({mean_dist:.1f} km)**, 
      indicating some very remote areas pull the average higher
    """
    )

# Add download functionality to sidebar
with st.sidebar:
    st.markdown("---")
    st.header("📥 Export Data")

    # Create download button for the filtered trauma data
    csv = trauma.to_csv(index=False)
    st.download_button(
        label="📊 Download Hospital Data",
        data=csv,
        file_name=f'trauma_hospitals_{state}_{pd.Timestamp.now().strftime("%Y%m%d")}.csv',
        mime="text/csv",
        help=f"Download all trauma hospital data for {state_names.get(state, state)} as CSV file",
    )

    # Optional: Add a summary download as well
    if st.button(
        "📋 Generate Summary Report", help="Create a quick summary of key metrics"
    ):
        summary_data = {
            "State": [state_names.get(state, state)],
            "Total Hospitals": [total_hospitals],
            "Level I Centers": [level_i_centers],
            "Level II Centers": [level_ii_centers],
            "Level III Centers": [level_iii_centers],
            "Total Beds": [total_beds],
            "Hospitals with Helipads": [helipads],
            "Helipad Coverage %": [f"{(helipads/total_hospitals)*100:.1f}%"],
        }
        summary_df = pd.DataFrame(summary_data)
        summary_csv = summary_df.to_csv(index=False)

        st.download_button(
            label="⬇️ Download Summary",
            data=summary_csv,
            file_name=f'trauma_summary_{state}_{pd.Timestamp.now().strftime("%Y%m%d")}.csv',
            mime="text/csv",
        )
