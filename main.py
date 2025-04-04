from snowflake.snowpark.context import get_active_session

import streamlit as st


st.set_page_config(page_title="Snowflake Monitoring", layout="wide")
st.title("Snowflake Monitoring UI")

if 'session' not in st.session_state:
    st.session_state['session'] = get_active_session()

pg = st.navigation([
    st.Page("app_pages/dashboard.py", title="Dashboard", icon="🖥️"),
    st.Page("app_pages/addMonitors.py", title="Add Monitors", icon="➕")
])
pg.run()
