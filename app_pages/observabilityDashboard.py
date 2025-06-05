import streamlit as st
import pandas as pd
import datetime
import random
import plotly.express as px
import networkx as nx
import plotly.graph_objects as go

# Config: Tables and expected intervals
TABLES = {"orders": 6, "customers": 24, "inventory": 12, "monitor_results": 5}
DEPENDENCIES = {
    "orders": {"upstream": ["customers", "inventory"], "downstream": ["sales_report"]},
    "customers": {"upstream": [], "downstream": ["orders"]},
    "inventory": {"upstream": [], "downstream": ["orders"]},
    "sales_report": {"upstream": ["orders"], "downstream": []}
}

# Simulate Freshness Data
def generate_freshness_log(table_name, days=30):
    now = datetime.datetime.now()
    expected_interval = TABLES[table_name]
    data = []

    for i in range(days):
        ref_time = now - datetime.timedelta(days=i)
        delay = random.uniform(0, 2 * expected_interval)
        last_updated = ref_time - datetime.timedelta(hours=delay)
        is_stale = (ref_time - last_updated).total_seconds() / 3600 > expected_interval
        data.append({
            "Date": ref_time.date(),
            "Table": table_name,
            "Reference Time": ref_time,
            "Last Updated": last_updated,
            "Expected Interval (hrs)": expected_interval,
            "Delay (hrs)": round((ref_time - last_updated).total_seconds() / 3600, 2),
            "Status": "❌ Stale" if is_stale else "✅ Fresh"
        })

    return pd.DataFrame(data)

# Simulate Schema Changes
def generate_schema_changes(table_name, days=60, count=10):
    now = datetime.datetime.now()
    types = ["Column Added", "Column Removed", "Data Type Changed", "Column Renamed"]
    data = []
    for _ in range(count):
        change_date = now - datetime.timedelta(days=random.randint(0, days))
        data.append({
            "Change Time": change_date,
            "Date": change_date.date(),
            "Table": table_name,
            "Change Type": random.choice(types),
            "Column": f"col_{random.randint(1,10)}"
        })
    return pd.DataFrame(data)

# Dependency Chart
def plot_dependency_graph(table_name, highlight_table=None):
    G = nx.DiGraph()
    visited = set()

    def add_nodes_edges(node):
        if node in visited:
            return
        visited.add(node)
        for upstream in DEPENDENCIES.get(node, {}).get("upstream", []):
            G.add_edge(upstream, node)
            add_nodes_edges(upstream)
        for downstream in DEPENDENCIES.get(node, {}).get("downstream", []):
            G.add_edge(node, downstream)
            add_nodes_edges(downstream)

    add_nodes_edges(table_name)
    pos = nx.spring_layout(G)
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=1, color='#888'),
                            hoverinfo='none', mode='lines')
    node_x, node_y, texts, colors = [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        texts.append(node)
        colors.append("orange" if node == highlight_table else "skyblue")

    node_trace = go.Scatter(
        x=node_x, y=node_y, mode='markers+text', text=texts, textposition='top center',
        marker=dict(size=20, color=colors, line_width=2)
    )

    fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(
        title='🔗 Table Dependency Graph', titlefont_size=16, showlegend=False, hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False)))
    return fig

# Streamlit UI
st.title("📊 Data Quality Dashboard")

tab1, tab2 = st.tabs(["🕒 Freshness Monitor", "🧬 Schema Changes"])

# ----------------- Freshness Tab --------------------
with tab1:
    st.subheader("🟡 Freshness Summary")
    col1, col2 = st.columns(2)
    with col1:
        from_date_summary = st.date_input("From Date", datetime.date.today() - datetime.timedelta(days=7), key="sum_from")
    with col2:
        to_date_summary = st.date_input("To Date", datetime.date.today(), key="sum_to")

    all_fresh_data = pd.concat([generate_freshness_log(tbl) for tbl in TABLES])
    summary = all_fresh_data[
        (all_fresh_data["Date"] >= from_date_summary) & 
        (all_fresh_data["Date"] <= to_date_summary) &
        (all_fresh_data["Status"] == "❌ Stale")
    ]
    st.info(f"📌 {len(summary)} stale table entries found between **{from_date_summary}** and **{to_date_summary}**.")
    st.dataframe(summary.sort_values(by="Date", ascending=False), use_container_width=True)

    st.markdown("---")
    st.subheader("📈 Freshness History")
    colh1, colh2 = st.columns(2)
    with colh1:
        hist_table = st.selectbox("Select Table", list(TABLES), key="hist_table")
    with colh2:
        hist_days = st.slider("Last N Days", 1, 30, 15, key="hist_days")

    hist_data = generate_freshness_log(hist_table, days=hist_days)
    st.dataframe(hist_data, use_container_width=True)
    fig = px.bar(hist_data, x="Date", y="Delay (hrs)", color="Status",
                 title="Freshness Delay History", color_discrete_map={"✅ Fresh": "green", "❌ Stale": "red"})
    st.plotly_chart(fig, use_container_width=True)

# ----------------- Schema Tab --------------------
with tab2:
    st.subheader("📌 Schema Change Summary")
    col1, col2 = st.columns(2)
    with col1:
        from_date_schema = st.date_input("From Date", datetime.date.today() - datetime.timedelta(days=30), key="schema_from")
    with col2:
        to_date_schema = st.date_input("To Date", datetime.date.today(), key="schema_to")

    schema_all = pd.concat([generate_schema_changes(tbl, count=10) for tbl in TABLES])
    schema_summary = schema_all[
        (schema_all["Date"] >= from_date_schema) &
        (schema_all["Date"] <= to_date_schema)
    ]
    st.success(f"🧬 {len(schema_summary)} schema changes between **{from_date_schema}** and **{to_date_schema}**.")
    st.dataframe(schema_summary.sort_values(by="Date", ascending=False), use_container_width=True)

    # st.markdown("---")
    # st.subheader("🧪 Schema History & Dependencies")
    # colsh1, colsh2 = st.columns(2)
    # with colsh1:
    #     hist_schema_table = st.selectbox("Select Table", list(TABLES), key="schema_hist_table")
    # with colsh2:
    #     hist_schema_days = st.slider("Last N Days", 1, 60, 30, key="schema_hist_days")

    # schema_hist = generate_schema_changes(hist_schema_table, days=hist_schema_days, count=20)
    # st.dataframe(schema_hist.sort_values(by="Date", ascending=False), use_container_width=True)

    # st.markdown("#### 🔄 Dependency Graph")
    # fig_dep = plot_dependency_graph(hist_schema_table, highlight_table=hist_schema_table)
    # st.plotly_chart(fig_dep, use_container_width=True)
