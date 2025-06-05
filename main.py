from snowflake.snowpark.context import get_active_session

import streamlit as st


st.set_page_config(page_title="Snowflake Platform Monitoring", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    body {
        font-family: 'Poppins', sans-serif;  /* Apply Poppins font to the entire app */
    }
    .stMarkdown, .stText {
        font-family: 'Poppins', sans-serif;  /* Custom font for markdown and text */
    }
    h1, h2, h3 {
        font-family: 'Poppins', sans-serif;  /* Custom font for headers */
    }
    /* Apply styles for other elements if necessary */
    .stButton {
        font-family: 'Poppins', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
logo_path = "https://www.financialexpress.com/wp-content/uploads/2023/10/My-project-2023-10-17T102736.049.png?w=1024"
col1, col2 = st.columns([1, 4]) 
with col1:
    st.image({logo_path}, width=150)
with col2:
    st.markdown("<h1 style='margin-bottom: 0;color: #E67E22;'>SNOWFLAKE PLATFORM MONITORING</h1>", unsafe_allow_html=True)
st.markdown("---")

if 'session' not in st.session_state:
    from snowflake.snowpark.session import Session

    config = {
        "account": "hdfeymr-tigeranalytics_partner",
        "user": "dwhbi_developer",
        "password": "Tiger@dwhbi1",
        "role": "dwhbi_developer",
        "warehouse": "dwhbi_developer_wh",
        "database": "snowflake_monitoring",
        "schema": "public"
    }

    st.session_state['session'] = Session.builder.configs(config).create()
    # st.session_state['session'] = get_active_session()

st.session_state['session'].sql("CALL AUTOMATE_DASHBOARD_VIEW()").collect()

pg = st.navigation([
    st.Page("app_pages/dashboard.py", title="Overview", icon="🖥️"),
    st.Page("app_pages/addMonitors.py", title="Create Monitors", icon="➕"),
    st.Page("app_pages/resultsDashboard.py", title="Ask Assistant", icon="📈"),
    st.Page("app_pages/defaultMonitors.py", title="Default Monitors", icon="🗄️")
])
pg.run()
