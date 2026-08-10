# ============================================================
# HOTEL BUSINESS ANALYTICS DASHBOARD
# Setup, Data Loading, Cleaning & Filters
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# ------------------------------------------------------------
# 1. PAGE CONFIGURATION
# ------------------------------------------------------------

st.set_page_config(
    page_title="Hotel Business Analytics",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ------------------------------------------------------------
# 2. CUSTOM STYLING
# ------------------------------------------------------------

st.markdown("""
<style>

    .main-title {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .sub-title {
        font-size: 17px;
        color: #6b7280;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 650;
        margin-top: 25px;
        margin-bottom: 10px;
    }

    div[data-testid="stMetric"] {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
    padding: 18px;
    border-radius: 10px;
}

/* KPI label */
div[data-testid="stMetric"] label {
    color: #1e3a5f !important;
}

/* KPI value */
div[data-testid="stMetricValue"] {
    color: #1e3a8a !important;
    font-weight: 700 !important;
}

/* KPI delta, if used */
div[data-testid="stMetricDelta"] {
    color: #1e3a5f !important;
}

    

</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# 3. LOAD DATA
# ------------------------------------------------------------

@st.cache_data
def load_data():

    data = pd.read_csv("hotel_bookings_data.csv")

    return data


df = load_data()


# ------------------------------------------------------------
# 4. DATA CLEANING
# ------------------------------------------------------------

@st.cache_data
def clean_data(data):

    data = data.copy()

    # Handle missing values
    data["children"] = data["children"].fillna(0)
    data["city"] = data["city"].fillna("Unknown")
    data["agent"] = data["agent"].fillna(0)
    data["company"] = data["company"].fillna(0)

    # Handle inconsistent category
    data["meal"] = data["meal"].replace(
        "Undefined",
        "No Meal"
    )

    # Remove duplicate records
    data = data.drop_duplicates()

    # Remove bookings with zero guests
    total_guests = (
        data["adults"]
        + data["children"]
        + data["babies"]
    )

    data = data[total_guests > 0]

    # Remove negative ADR
    data = data[data["adr"] >= 0]

    # Create total stay duration
    data["total_stay_nights"] = (
        data["stays_in_weekend_nights"]
        + data["stays_in_weekdays_nights"]
    )

    return data


df = clean_data(df)


# ------------------------------------------------------------
# 5. CREATE MONTH ORDER
# ------------------------------------------------------------

month_order = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]


# ------------------------------------------------------------
# 6. DASHBOARD HEADER
# ------------------------------------------------------------

st.markdown(
    '<div class="main-title">🏨 Hotel Business Analytics Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'Booking behaviour, seasonality and cancellation analysis'
    '</div>',
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# 7. SIDEBAR FILTERS
# ------------------------------------------------------------

st.sidebar.header("🔎 Dashboard Filters")

st.sidebar.markdown(
    "Use the filters below to explore booking behaviour."
)


# Hotel filter
hotel_options = ["All"] + sorted(df["hotel"].unique().tolist())

selected_hotel = st.sidebar.selectbox(
    "Hotel Type",
    hotel_options
)


# Year filter
year_options = ["All"] + sorted(
    df["arrival_date_year"].unique().tolist()
)

selected_year = st.sidebar.selectbox(
    "Arrival Year",
    year_options
)


# Month filter
month_options = ["All"] + month_order

selected_month = st.sidebar.selectbox(
    "Arrival Month",
    month_options
)


# ------------------------------------------------------------
# 8. APPLY FILTERS
# ------------------------------------------------------------

filtered_df = df.copy()


if selected_hotel != "All":
    filtered_df = filtered_df[
        filtered_df["hotel"] == selected_hotel
    ]


if selected_year != "All":
    filtered_df = filtered_df[
        filtered_df["arrival_date_year"] == selected_year
    ]


if selected_month != "All":
    filtered_df = filtered_df[
        filtered_df["arrival_date_month"] == selected_month
    ]


# ------------------------------------------------------------
# 9. FILTER STATUS
# ------------------------------------------------------------

st.sidebar.markdown("---")

st.sidebar.write(
    f"**Records displayed:** {len(filtered_df):,}"
)

st.sidebar.write(
    f"**Total dataset records:** {len(df):,}"
)


# ------------------------------------------------------------
# 10. BASIC SAFETY CHECK
# ------------------------------------------------------------

if filtered_df.empty:

    st.warning(
        "No bookings match the selected filters. "
        "Please change the filters."
    )

    st.stop()

    # ============================================================


# ------------------------------------------------------------
# 11. KEY PERFORMANCE INDICATORS
# ------------------------------------------------------------

st.markdown(
    '<div class="section-title">📊 Key Performance Indicators</div>',
    unsafe_allow_html=True
)

# Calculate KPIs from currently filtered data
total_bookings = len(filtered_df)

cancelled_bookings = filtered_df["is_canceled"].sum()

cancellation_rate = (
    filtered_df["is_canceled"].mean() * 100
)

average_lead_time = filtered_df["lead_time"].mean()

average_stay = filtered_df["total_stay_nights"].mean()


# Display KPI cards
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Bookings",
        f"{total_bookings:,}"
    )

with col2:
    st.metric(
        "Cancelled Bookings",
        f"{cancelled_bookings:,}"
    )

with col3:
    st.metric(
        "Cancellation Rate",
        f"{cancellation_rate:.1f}%"
    )

with col4:
    st.metric(
        "Avg. Lead Time",
        f"{average_lead_time:.1f} days"
    )

with col5:
    st.metric(
        "Avg. Stay",
        f"{average_stay:.1f} nights"
    )


# ------------------------------------------------------------
# 12. HOTEL TYPE BOOKING ANALYSIS
# ------------------------------------------------------------

st.markdown(
    '<div class="section-title">🏨 Booking Distribution by Hotel Type</div>',
    unsafe_allow_html=True
)

st.write(
    "This section compares booking demand between City Hotel "
    "and Resort Hotel."
)


# Calculate booking counts
hotel_counts = (
    filtered_df["hotel"]
    .value_counts()
    .reindex(
        ["City Hotel", "Resort Hotel"],
        fill_value=0
    )
)


# Calculate percentages
hotel_share = (
    hotel_counts / hotel_counts.sum() * 100
)


# Create two columns
col1, col2 = st.columns([1, 1])


# ------------------------------------------------------------
# 13. HOTEL BOOKING SHARE CHART
# ------------------------------------------------------------

with col1:

    fig, ax = plt.subplots(figsize=(7, 5))

    bars = ax.bar(
        hotel_share.index,
        hotel_share.values
    )

    ax.set_title(
        "Booking Share by Hotel Type",
        fontsize=14,
        fontweight="bold"
    )

    ax.set_xlabel("Hotel Type")
    ax.set_ylabel("Booking Share (%)")

    ax.set_ylim(
        0,
        max(hotel_share.values) * 1.2
    )

    # Add percentage labels
    for bar, value in zip(bars, hotel_share.values):

        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{value:.1f}%",
            ha="center",
            fontweight="bold"
        )

    plt.tight_layout()

    st.pyplot(fig)

    plt.close(fig)


# ------------------------------------------------------------
# 14. HOTEL BOOKING COUNTS
# ------------------------------------------------------------

with col2:

    fig, ax = plt.subplots(figsize=(7, 5))

    bars = ax.bar(
        hotel_counts.index,
        hotel_counts.values
    )

    ax.set_title(
        "Number of Bookings by Hotel Type",
        fontsize=14,
        fontweight="bold"
    )

    ax.set_xlabel("Hotel Type")
    ax.set_ylabel("Number of Bookings")

    # Add booking count labels
    for bar, value in zip(
        bars,
        hotel_counts.values
    ):

        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:,}",
            ha="center",
            va="bottom",
            fontweight="bold"
        )

    plt.tight_layout()

    st.pyplot(fig)

    plt.close(fig)


# ------------------------------------------------------------
# 15. HOTEL TYPE BUSINESS INSIGHT
# ------------------------------------------------------------

most_booked_hotel = hotel_counts.idxmax()

most_booked_share = hotel_share.loc[
    most_booked_hotel
]

st.info(
    f"💡 **Booking Insight:** {most_booked_hotel} "
    f"receives the highest share of bookings in the "
    f"current filter selection, accounting for "
    f"approximately {most_booked_share:.1f}% of bookings."
)


# ------------------------------------------------------------
# 16. MONTHLY BOOKING ANALYSIS
# ------------------------------------------------------------

st.markdown(
    '<div class="section-title">📅 Monthly Booking Trends</div>',
    unsafe_allow_html=True
)

st.write(
    "This analysis shows how booking demand changes across "
    "the arrival months for each hotel type."
)


# Group bookings by month and hotel
monthly_bookings = (
    filtered_df
    .groupby(
        ["arrival_date_month", "hotel"]
    )
    .size()
    .reset_index(
        name="bookings"
    )
)


# Apply chronological month order
monthly_bookings[
    "arrival_date_month"
] = pd.Categorical(
    monthly_bookings["arrival_date_month"],
    categories=month_order,
    ordered=True
)


monthly_bookings = monthly_bookings.sort_values(
    "arrival_date_month"
)


# ------------------------------------------------------------
# 17. MONTHLY BOOKING CHART
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(14, 6)
)

sns.lineplot(
    data=monthly_bookings,
    x="arrival_date_month",
    y="bookings",
    hue="hotel",
    marker="o",
    linewidth=2.5,
    ax=ax
)

ax.set_title(
    "Monthly Bookings by Hotel Type",
    fontsize=15,
    fontweight="bold"
)

ax.set_xlabel("Arrival Month")
ax.set_ylabel("Number of Bookings")

ax.tick_params(
    axis="x",
    rotation=45
)

ax.legend(
    title="Hotel Type"
)

plt.tight_layout()

st.pyplot(fig)

plt.close(fig)


# ------------------------------------------------------------
# 18. BUSIEST AND QUIETEST MONTH
# ------------------------------------------------------------

monthly_total = (
    filtered_df
    .groupby("arrival_date_month")
    .size()
    .reindex(month_order)
    .dropna()
)


if len(monthly_total) > 0:

    busiest_month = monthly_total.idxmax()
    busiest_bookings = int(monthly_total.max())

    quietest_month = monthly_total.idxmin()
    quietest_bookings = int(monthly_total.min())


    # Display two insights
    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Busiest Arrival Month",
            busiest_month,
            f"{busiest_bookings:,} bookings"
        )

    with col2:

        st.metric(
            "Quietest Arrival Month",
            quietest_month,
            f"{quietest_bookings:,} bookings"
        )


# ------------------------------------------------------------
# 19. MONTHLY BUSINESS INSIGHT
# ------------------------------------------------------------

if len(monthly_total) > 0:

    st.info(
        f"📈 **Seasonality Insight:** Booking demand is highest "
        f"in **{busiest_month}** and lowest in "
        f"**{quietest_month}** within the current filter selection. "
        f"These patterns can help management plan room availability, "
        f"staffing and promotional activity."
    )



# ------------------------------------------------------------
# 20. CANCELLATION ANALYSIS
# ------------------------------------------------------------

st.markdown(
    '<div class="section-title">❌ Cancellation Analysis</div>',
    unsafe_allow_html=True
)

st.write(
    "This section examines cancellation behaviour across hotel types "
    "and different stay durations."
)


# ------------------------------------------------------------
# 21. CANCELLATION RATE BY HOTEL TYPE
# ------------------------------------------------------------

cancellation_by_hotel = (
    filtered_df
    .groupby("hotel")["is_canceled"]
    .mean()
    .mul(100)
    .round(2)
)


col1, col2 = st.columns([1, 1])


# ------------------------------------------------------------
# 22. CANCELLATION RATE CHART
# ------------------------------------------------------------

with col1:

    fig, ax = plt.subplots(figsize=(7, 5))

    bars = ax.bar(
        cancellation_by_hotel.index,
        cancellation_by_hotel.values
    )

    ax.set_title(
        "Cancellation Rate by Hotel Type",
        fontsize=14,
        fontweight="bold"
    )

    ax.set_xlabel("Hotel Type")
    ax.set_ylabel("Cancellation Rate (%)")

    ax.set_ylim(
        0,
        max(cancellation_by_hotel.values) * 1.2
    )

    for bar, value in zip(
        bars,
        cancellation_by_hotel.values
    ):

        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{value:.1f}%",
            ha="center",
            fontweight="bold"
        )

    plt.tight_layout()

    st.pyplot(fig)

    plt.close(fig)


# ------------------------------------------------------------
# 23. CANCELLATION STATUS DISTRIBUTION
# ------------------------------------------------------------

with col2:

    cancellation_counts = (
        filtered_df["is_canceled"]
        .value_counts()
        .sort_index()
    )

    cancellation_labels = [
        "Not Cancelled",
        "Cancelled"
    ]

    cancellation_values = [
        cancellation_counts.get(0, 0),
        cancellation_counts.get(1, 0)
    ]

    fig, ax = plt.subplots(figsize=(7, 5))

    ax.bar(
        cancellation_labels,
        cancellation_values
    )

    ax.set_title(
        "Booking Cancellation Distribution",
        fontsize=14,
        fontweight="bold"
    )

    ax.set_xlabel("Booking Status")
    ax.set_ylabel("Number of Bookings")

    for i, value in enumerate(cancellation_values):

        ax.text(
            i,
            value,
            f"{value:,}",
            ha="center",
            va="bottom",
            fontweight="bold"
        )

    plt.tight_layout()

    st.pyplot(fig)

    plt.close(fig)


# ------------------------------------------------------------
# 24. CANCELLATION BUSINESS INSIGHT
# ------------------------------------------------------------

if len(cancellation_by_hotel) > 0:

    highest_cancel_hotel = (
        cancellation_by_hotel.idxmax()
    )

    highest_cancel_rate = (
        cancellation_by_hotel.max()
    )

    st.warning(
        f"⚠️ **Cancellation Insight:** "
        f"{highest_cancel_hotel} has the highest cancellation "
        f"rate at approximately {highest_cancel_rate:.1f}% "
        f"within the current filter selection."
    )


# ------------------------------------------------------------
# 25. STAY DURATION ANALYSIS
# ------------------------------------------------------------

st.markdown(
    '<div class="section-title">🛏️ Stay Duration vs Cancellation</div>',
    unsafe_allow_html=True
)

st.write(
    "This analysis investigates whether cancellation behaviour "
    "changes as the total length of stay increases."
)


# ------------------------------------------------------------
# 26. GROUP BY STAY DURATION
# ------------------------------------------------------------

stay_cancellation = (
    filtered_df
    .groupby(
        ["total_stay_nights", "hotel"]
    )["is_canceled"]
    .agg(
        cancellation_rate="mean",
        booking_count="count"
    )
    .reset_index()
)


stay_cancellation["cancellation_rate"] = (
    stay_cancellation["cancellation_rate"] * 100
)


# ------------------------------------------------------------
# 27. REMOVE VERY SMALL GROUPS
# ------------------------------------------------------------

# Very small groups can produce misleading cancellation rates.
# We keep only stay durations with at least 30 bookings.

stay_analysis = stay_cancellation[
    stay_cancellation["booking_count"] >= 30
].copy()


# ------------------------------------------------------------
# 28. LIMIT EXTREME STAY DURATIONS FOR VISUAL CLARITY
# ------------------------------------------------------------

# Extremely long stays contain very few observations and can
# make the chart difficult to interpret.

stay_analysis = stay_analysis[
    stay_analysis["total_stay_nights"] <= 30
]


# ------------------------------------------------------------
# 29. STAY DURATION CHART
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(14, 6)
)

sns.lineplot(
    data=stay_analysis,
    x="total_stay_nights",
    y="cancellation_rate",
    hue="hotel",
    marker="o",
    linewidth=2.2,
    ax=ax
)

ax.set_title(
    "Cancellation Rate by Length of Stay",
    fontsize=15,
    fontweight="bold"
)

ax.set_xlabel(
    "Total Stay Duration (Nights)"
)

ax.set_ylabel(
    "Cancellation Rate (%)"
)

ax.legend(
    title="Hotel Type"
)

plt.tight_layout()

st.pyplot(fig)

plt.close(fig)


# ------------------------------------------------------------
# 30. STAY DURATION SUMMARY
# ------------------------------------------------------------

if not stay_analysis.empty:

    # Highest cancellation rate for each hotel
    highest_stay_risk = (
        stay_analysis
        .loc[
            stay_analysis
            .groupby("hotel")["cancellation_rate"]
            .idxmax()
        ]
    )

    st.markdown("### 📌 Stay Duration Risk Summary")

    for _, row in highest_stay_risk.iterrows():

        st.write(
            f"**{row['hotel']}** → highest observed "
            f"cancellation rate of "
            f"**{row['cancellation_rate']:.1f}%** "
            f"at approximately "
            f"**{int(row['total_stay_nights'])} nights** "
            f"({int(row['booking_count']):,} bookings)."
        )


# ------------------------------------------------------------
# 31. STAY DURATION BUSINESS INSIGHT
# ------------------------------------------------------------

st.info(
    "💡 **Business Insight:** "
    "Comparing cancellation rates across stay durations "
    "helps identify whether longer bookings represent "
    "greater cancellation risk. Hotels can use this information "
    "to consider deposits, cancellation terms or pricing "
    "strategies for higher-risk booking patterns."
)



# ------------------------------------------------------------
# 32. LEAD TIME ANALYSIS
# ------------------------------------------------------------

st.markdown(
    '<div class="section-title">📆 Lead Time vs Cancellation</div>',
    unsafe_allow_html=True
)

st.write(
    "Lead time represents the number of days between the booking "
    "date and the customer's arrival date. This analysis examines "
    "whether bookings made further in advance have a different "
    "cancellation risk."
)


# ------------------------------------------------------------
# 33. GROUP LEAD TIME
# ------------------------------------------------------------

lead_analysis = (
    filtered_df
    .groupby(
        ["lead_time", "hotel"]
    )["is_canceled"]
    .agg(
        cancellation_rate="mean",
        booking_count="count"
    )
    .reset_index()
)


lead_analysis["cancellation_rate"] = (
    lead_analysis["cancellation_rate"] * 100
)


# ------------------------------------------------------------
# 34. REMOVE VERY SMALL GROUPS
# ------------------------------------------------------------

lead_analysis = lead_analysis[
    lead_analysis["booking_count"] >= 30
].copy()


# ------------------------------------------------------------
# 35. LEAD TIME CHART
# ------------------------------------------------------------

fig, ax = plt.subplots(
    figsize=(14, 6)
)

sns.lineplot(
    data=lead_analysis,
    x="lead_time",
    y="cancellation_rate",
    hue="hotel",
    linewidth=2.2,
    ax=ax
)

ax.set_title(
    "Cancellation Rate by Lead Time",
    fontsize=15,
    fontweight="bold"
)

ax.set_xlabel(
    "Lead Time (Days)"
)

ax.set_ylabel(
    "Cancellation Rate (%)"
)

ax.legend(
    title="Hotel Type"
)

plt.tight_layout()

st.pyplot(fig)

plt.close(fig)


# ------------------------------------------------------------
# 36. LEAD TIME RISK SUMMARY
# ------------------------------------------------------------

st.markdown(
    "### 📌 Lead Time Risk Summary"
)


if not lead_analysis.empty:

    # Overall lowest cancellation point
    lowest_row = lead_analysis.loc[
        lead_analysis["cancellation_rate"].idxmin()
    ]

    # Overall highest cancellation point
    highest_row = lead_analysis.loc[
        lead_analysis["cancellation_rate"].idxmax()
    ]

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Lowest Cancellation Point",
            f"{int(lowest_row['lead_time'])} days",
            f"{lowest_row['cancellation_rate']:.1f}% cancellation"
        )

    with col2:

        st.metric(
            "Highest Cancellation Point",
            f"{int(highest_row['lead_time'])} days",
            f"{highest_row['cancellation_rate']:.1f}% cancellation"
        )

    st.warning(
        f"⚠️ The highest observed cancellation risk occurs at "
        f"approximately **{int(highest_row['lead_time'])} days "
        f"of lead time** for **{highest_row['hotel']}**."
    )


# ------------------------------------------------------------
# 37. LEAD TIME BUSINESS INSIGHT
# ------------------------------------------------------------

st.info(
    "💡 **Lead Time Insight:** "
    "Monitoring cancellation behaviour across booking lead times "
    "can help hotels identify higher-risk advance bookings and "
    "introduce appropriate confirmation, deposit or rescheduling "
    "strategies."
)


# ------------------------------------------------------------
# 38. BUSINESS INSIGHTS SUMMARY
# ------------------------------------------------------------

st.markdown(
    '<div class="section-title">💡 Key Business Insights</div>',
    unsafe_allow_html=True
)


# Calculate current-filter insights
top_hotel = filtered_df["hotel"].value_counts().idxmax()

top_hotel_share = (
    filtered_df["hotel"]
    .value_counts(normalize=True)
    .loc[top_hotel] * 100
)

overall_cancel_rate = (
    filtered_df["is_canceled"].mean() * 100
)

avg_lead = filtered_df["lead_time"].mean()

avg_stay_nights = filtered_df["total_stay_nights"].mean()


# Create insight boxes
col1, col2 = st.columns(2)

with col1:

    st.success(
        f"🏨 **Demand:** {top_hotel} is the most frequently "
        f"booked hotel type, representing approximately "
        f"**{top_hotel_share:.1f}%** of the current booking volume."
    )

    st.info(
        f"📅 **Advance Booking:** Customers book an average of "
        f"**{avg_lead:.1f} days** before arrival."
    )


with col2:

    st.warning(
        f"❌ **Cancellation:** The current overall cancellation "
        f"rate is approximately **{overall_cancel_rate:.1f}%**."
    )

    st.info(
        f"🛏️ **Stay Duration:** The average booking represents "
        f"approximately **{avg_stay_nights:.1f} nights**."
    )


# ------------------------------------------------------------
# 39. BUSINESS RECOMMENDATIONS
# ------------------------------------------------------------

st.markdown(
    '<div class="section-title">🎯 Business Recommendations</div>',
    unsafe_allow_html=True
)


recommendations = [
    (
        "1. Optimize Peak-Season Operations",
        "Use monthly demand patterns to optimize room availability, "
        "staffing and pricing during high-demand periods while "
        "using targeted promotions during quieter periods."
    ),

    (
        "2. Strengthen Cancellation Management",
        "Consider deposits, appropriate cancellation terms and "
        "confirmation reminders for bookings that show higher "
        "cancellation risk."
    ),

    (
        "3. Monitor Long-Stay Bookings",
        "Longer bookings should be monitored for cancellation risk "
        "and may benefit from suitable deposit or cancellation "
        "policies."
    ),

    (
        "4. Manage Advance Bookings",
        "Use confirmation reminders, flexible rescheduling or "
        "advance deposits to improve commitment for bookings "
        "made far ahead of arrival."
    ),

    (
        "5. Focus on City Hotel",
        "Because City Hotel represents a larger share of bookings, "
        "improvements in its cancellation rate could have a "
        "larger overall business impact."
    )
]


for title, description in recommendations:

    with st.container(border=True):

        st.markdown(
            f"**{title}**"
        )

        st.write(
            description
        )


# ------------------------------------------------------------
# 40. PRIMARY RECOMMENDATION
# ------------------------------------------------------------

st.markdown(
    "### ⭐ Highest-Priority Recommendation"
)

st.write(
    "The highest-priority action should be to strengthen "
    "cancellation management for higher-risk bookings. "
    "The hotel can combine advance confirmation reminders "
    "with appropriate deposits or cancellation conditions, "
    "particularly for bookings showing higher cancellation "
    "risk based on lead time and stay duration."
)


# ------------------------------------------------------------
# 41. DASHBOARD CONCLUSION
# ------------------------------------------------------------

st.markdown(
    '<div class="section-title">📌 Dashboard Conclusion</div>',
    unsafe_allow_html=True
)

st.write(
    "This dashboard provides an interactive view of hotel booking "
    "and cancellation behaviour. Users can filter the analysis "
    "by hotel type, arrival year and arrival month to investigate "
    "different booking patterns."
)

st.write(
    "The analysis focuses on three core business questions: "
    "hotel type popularity, the relationship between stay duration "
    "and cancellations, and the relationship between lead time "
    "and cancellations."
)


# ------------------------------------------------------------
# 42. DATASET INFORMATION
# ------------------------------------------------------------

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.caption(
        f"Dataset Records: {len(df):,}"
    )

with col2:
    st.caption(
        f"Filtered Records: {len(filtered_df):,}"
    )

with col3:
    st.caption(
        "Hotel Business Analytics | EDA Project"
    )


# ============================================================
# END OF STREAMLIT DASHBOARD
# ============================================================