from snowflake.snowpark.context import get_active_session

import streamlit as st


st.set_page_config(page_title="Snowflake Monitoring", layout="wide")
st.title("Snowflake Monitoring UI")

if 'session' not in st.session_state:
    st.session_state['session'] = get_active_session()

st.session_state['session'].sql("CALL AUTOMATE_DASHBOARD_VIEW()").collect()

pg = st.navigation([
    st.Page("app_pages/dashboard.py", title="Dashboard", icon="🖥️"),
    st.Page("app_pages/addMonitors.py", title="Add Monitors", icon="➕"),
    st.Page("app_pages/resultsDashboard.py", title="Result Explore", icon="📈")
])
pg.run()
