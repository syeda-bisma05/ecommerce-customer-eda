import math
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="E-commerce Customer Dashboard", layout="wide")

AMBER = "#F59E0B"
TEAL = "#2DD4BF"
CARD = "#1E293B"
LIGHT = "#E2E8F0"

plt.rcParams.update({
    "figure.facecolor": CARD, "axes.facecolor": CARD, "savefig.facecolor": CARD,
    "axes.edgecolor": "#94A3B8", "axes.labelcolor": LIGHT,
    "xtick.color": LIGHT, "ytick.color": LIGHT,
    "text.color": LIGHT, "axes.titlecolor": AMBER,
})

st.markdown("""
<style>
h1 {color: #F59E0B;}
h2, h3 {color: #2DD4BF;}
[data-testid="stMetric"] {
    background-color: #1E293B;
    border-left: 5px solid #F59E0B;
    padding: 12px 16px;
    border-radius: 10px;
}
[data-testid="stMetricLabel"] {color: #94A3B8;}
[data-testid="stMetricValue"] {color: #F8FAFC;}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    return pd.read_csv("ecommerce_customers.csv")


df = load_data()
num_cols = ["Avg. Session Length", "Time on App", "Time on Website",
            "Length of Membership", "Yearly Amount Spent"]

st.title("E-commerce Customer Behavior Dashboard")
st.write("This dashboard explores the behavior and spending of 500 customers of an online store.")

# Sidebar filters
st.sidebar.header("Filters")
m_min, m_max = float(math.floor(df["Length of Membership"].min())), float(math.ceil(df["Length of Membership"].max()))
membership = st.sidebar.slider("Length of Membership (years)", m_min, m_max, (m_min, m_max), step=0.1)
s_min, s_max = float(math.floor(df["Yearly Amount Spent"].min())), float(math.ceil(df["Yearly Amount Spent"].max()))
spend = st.sidebar.slider("Yearly Amount Spent", s_min, s_max, (s_min, s_max), step=1.0)
filtered = df[
    df["Length of Membership"].between(membership[0], membership[1])
    & df["Yearly Amount Spent"].between(spend[0], spend[1])
]

if filtered.empty:
    st.warning("No customers match these filters. Please change the filters.")
    st.stop()

# Key numbers
c1, c2, c3, c4 = st.columns(4)
c1.metric("Customers", len(filtered))
c2.metric("Average Yearly Spend", round(filtered["Yearly Amount Spent"].mean(), 2))
c3.metric("Average Membership (years)", round(filtered["Length of Membership"].mean(), 2))
c4.metric("Highest Yearly Spend", round(filtered["Yearly Amount Spent"].max(), 2))

st.divider()


def scatter(col, container):
    with container:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.regplot(x=col, y="Yearly Amount Spent", data=filtered, ax=ax,
                    scatter_kws={"color": AMBER, "alpha": 0.6},
                    line_kws={"color": TEAL})
        ax.set_title(col + " vs Yearly Amount Spent")
        ax.set_xlabel(col)
        ax.set_ylabel("Yearly Amount Spent")
        st.pyplot(fig)
        plt.close(fig)


# Graph 1 (univariate) and Graph 2 (bivariate)
g1, g2 = st.columns(2)

with g1:
    st.subheader("Q1: What is the typical yearly spend?")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.histplot(filtered["Yearly Amount Spent"], kde=True, color=AMBER, ax=ax)
    ax.set_title("Distribution of Yearly Amount Spent")
    ax.set_xlabel("Yearly Amount Spent")
    ax.set_ylabel("Number of Customers")
    st.pyplot(fig)
    plt.close(fig)

with g2:
    st.subheader("Q2: Does more app time mean more spending?")
scatter("Time on App", g2)

g3, g4 = st.columns(2)
with g3:
    st.subheader("Q3: Do longer members spend more?")
scatter("Length of Membership", g3)

with g4:
    st.subheader("Q4: Does website time matter?")
scatter("Time on Website", g4)

st.subheader("Q5: Which columns are related to each other?")
fig, ax = plt.subplots(figsize=(7, 5))
sns.heatmap(filtered[num_cols].corr(), annot=True, cmap="viridis", fmt=".2f", ax=ax)
ax.set_title("Correlation Heatmap of Numeric Columns")
st.pyplot(fig)
plt.close(fig)

st.divider()

# Raw data
if st.checkbox("Show raw data"):
    st.dataframe(filtered)

# Findings
st.header("Main Findings")
st.markdown("""
- Length of Membership has the strongest relationship with Yearly Amount Spent (correlation about 0.81). Longer members spend much more.
- Time on App has a moderate relationship with spending (about 0.50).
- Time on Website has almost no relationship with spending (about 0.00).
- The average customer spends about 499 dollars per year, and the spending data is symmetric.
- Suggestion: keep customers for longer with loyalty rewards and improve the mobile app.
""")