import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt


if not 'freshness_data' in st.session_state:
    st.session_state['freshness_data'] = None
if not 'schema_changes_data' in st.session_state:
    st.session_state['schema_changes_data'] = None
if not 'freshness_table' in st.session_state:
    st.session_state['freshness_table'] = None
if not 'freshness_records' in st.session_state:
    st.session_state['freshness_records'] = 10
if not 'schema_table' in st.session_state:
    st.session_state['schema_table'] = None
if not 'schema_records' in st.session_state:
    st.session_state['schema_records'] = 10

def get_table_freshness_data():
    if st.session_state['freshness_table'] == None or st.session_state['freshness_table'] == 'ALL':
        query = f"""
        SELECT table_name, 
            last_altered 
        FROM information_schema.tables
        WHERE table_schema = 'PUBLIC'
        LIMIT {st.session_state['freshness_records']}
        """
    else:
        query = f"""
        SELECT table_name, 
            last_altered 
        FROM information_schema.tables
        WHERE table_schema = 'PUBLIC' and table_name = '{st.session_state['freshness_table']}'
        LIMIT {st.session_state['freshness_records']}
        """
    st.session_state['freshness_data'] = st.session_state['session'].sql(query).to_pandas()

def get_schema_changes_data():
    if st.session_state['schema_table'] == None or st.session_state['schema_table'] == 'ALL':
        query = f"""
        SELECT table_name, 
            column_name, 
            data_type, 
            is_nullable 
        FROM information_schema.columns
        WHERE table_schema = 'PUBLIC'
        LIMIT {st.session_state['schema_records']}
        """
    else:
        query = f"""
        SELECT table_name, 
            column_name, 
            data_type, 
            is_nullable 
        FROM information_schema.columns
        WHERE table_schema = 'PUBLIC' and table_name = '{st.session_state['schema_table']}'
        LIMIT {st.session_state['schema_records']}
        """
    st.session_state['schema_changes_data'] = st.session_state['session'].sql(query).to_pandas()

def get_list_of_tables():
    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'PUBLIC'
        """
    return st.session_state['session'].sql(query).to_pandas()['TABLE_NAME'].to_list()

def get_list_of_tables_for_schema():
    query = """
    SELECT distinct table_name, 
    FROM information_schema.columns
    WHERE table_schema = 'PUBLIC'
        """
    return st.session_state['session'].sql(query).to_pandas()['TABLE_NAME'].to_list()

def detect_anomalies(data, metric, threshold=1.5):
    median = data[metric].median()
    std = data[metric].std()
    data["is_anomaly"] = abs(data[metric] - median) > threshold * std
    return data

# Fetch Data
get_table_freshness_data()
get_schema_changes_data()

# Tab 1: Table Freshness
st.title('Snowflake Data Observability Dashboard')

tab1, tab2, tab3 = st.tabs(['Table Freshness', 'Schema Changes', 'Anomalies: Record Count & Job Duration'])

with tab1:
    st.header('Table Freshness')

    col1, col2 = st.columns(2)
    with col1:
        st.selectbox(
            "Select Table(Freshness)",
            options=get_list_of_tables(),
            index=None,
            on_change=get_table_freshness_data,
            key="freshness_table"
        )

    with col2:
        st.slider(
            "Records",
            min_value=10,
            max_value=50,
            step=5,
            on_change=get_table_freshness_data,
            key="freshness_records"
        )

    st.dataframe(st.session_state['freshness_data'], use_container_width=True, hide_index=True)    
    st.session_state['freshness_data']['LAST_ALTERED'] = pd.to_datetime(st.session_state['freshness_data']['LAST_ALTERED'])
    fig = px.line(st.session_state['freshness_data'], x='TABLE_NAME', y='LAST_ALTERED', title='Last Altered Time of Tables')
    st.plotly_chart(fig)

with tab2:
    st.header('Schema Changes')

    col1, col2 = st.columns(2)
    with col1:
        st.selectbox(
            "Select Table(Schema)",
            options=get_list_of_tables_for_schema(),
            index=None,
            on_change=get_schema_changes_data,
            key="schema_table"
        )

    with col2:
        st.slider(
            "Records",
            min_value=10,
            max_value=50,
            step=5,
            on_change=get_schema_changes_data,
            key="schema_records"
        )

    st.dataframe(st.session_state['schema_changes_data'], use_container_width=True, hide_index=True)
    schema_changes_count = st.session_state['schema_changes_data'].groupby('TABLE_NAME').size().reset_index(name='CHANGE_COUNT')

    fig2, ax2 = plt.subplots()
    ax2.bar(schema_changes_count['TABLE_NAME'], schema_changes_count['CHANGE_COUNT'])
    ax2.set_title('Number of Schema Changes Per Table')
    ax2.set_xlabel('Table Name')
    ax2.set_ylabel('Change Count')
    plt.xticks(rotation=90)
    st.pyplot(fig2)

    data_type_changes = st.session_state['schema_changes_data'].groupby('DATA_TYPE').size().reset_index(name='COUNT')
    fig3 = px.pie(data_type_changes, values='COUNT', names='DATA_TYPE', title='Data Types Distribution in Schema Changes')
    st.plotly_chart(fig3)

with tab3:
    st.subheader("🔍 Anomalies: Record Count & Job Duration")

    col1, col2 = st.columns(2)
    with col1:
        from_date = st.date_input("From Date", datetime(2025, 1, 1))
    with col2:
        to_date = st.date_input("To Date", datetime(2025, 1, 31))

    view_option = st.selectbox("View", ["Record Count", "Job Duration", "Both"])

    # Filter data
    summary_df = df[(df["run_date"].dt.date >= from_date) & (df["run_date"].dt.date <= to_date)]
    st.markdown("### 📌 Summary of Anomalies")
    summary_data = []

    for table in tables:
        table_data = summary_df[summary_df["table_name"] == table]
        rc_anomalies = detect_anomalies(table_data.copy(), "record_count")["is_anomaly"].sum()
        jd_anomalies = detect_anomalies(table_data.copy(), "job_duration_sec")["is_anomaly"].sum()
        summary_data.append({
            "Table": table,
            "Record Count Anomalies": rc_anomalies,
            "Job Duration Anomalies": jd_anomalies
        })

    st.dataframe(pd.DataFrame(summary_data))

    st.markdown("### 🔎 Historical Trend for Selected Table")
    selected_table = st.selectbox("Select Table", tables)

    history_df = df[df["table_name"] == selected_table].copy()
    history_df = detect_anomalies(history_df, "record_count")
    history_df = detect_anomalies(history_df, "job_duration_sec")

    if view_option in ["Record Count", "Both"]:
        fig_rc = px.line(
            history_df, x="run_date", y="record_count", title=f"{selected_table} - Record Count Over Time",
            markers=True, color_discrete_sequence=["blue"]
        )
        anomaly_points = history_df[history_df["is_anomaly"]]
        fig_rc.add_scatter(x=anomaly_points["run_date"], y=anomaly_points["record_count"],
                           mode="markers", name="Anomaly", marker=dict(color="red", size=10))
        st.plotly_chart(fig_rc, use_container_width=True)

    if view_option in ["Job Duration", "Both"]:
        fig_jd = px.line(
            history_df, x="run_date", y="job_duration_sec", title=f"{selected_table} - Job Duration Over Time",
            markers=True, color_discrete_sequence=["green"]
        )
        anomaly_points = history_df[history_df["is_anomaly"]]
        fig_jd.add_scatter(x=anomaly_points["run_date"], y=anomaly_points["job_duration_sec"],
                           mode="markers", name="Anomaly", marker=dict(color="orange", size=10))
        st.plotly_chart(fig_jd, use_container_width=True)

