from snowflake.snowpark.context import get_active_session

import streamlit as st


st.set_page_config(page_title="Snowflake Platform Monitoring", layout="wide")
st.title("Snowflake Platform Monitoring")

if 'session' not in st.session_state:
    st.session_state['session'] = get_active_session()

st.session_state['session'].sql("CALL AUTOMATE_DASHBOARD_VIEW()").collect()

pg = st.navigation([
    st.Page("app_pages/dashboard.py", title="Overview", icon="🖥️"),
    st.Page("app_pages/addMonitors.py", title="Create Monitors", icon="➕"),
    st.Page("app_pages/resultsDashboard.py", title="Ask Assistant", icon="📈")
])
pg.run()
