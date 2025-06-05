import streamlit as st
st.set_page_config(page_title="Snowflake Platform Monitoring",page_icon="🧊",layout='wide',initial_sidebar_state='collapsed')
import base64
from streamlit_option_menu import option_menu

from app_pages.dashboard import dashboard
from app_pages.addMonitors import customMonitors
from app_pages.defaultMonitors import defaultMonitors
from app_pages.resultsDashboard import askAssistant
from footer import footer

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

st.session_state['session'].sql("CALL AUTOMATE_DASHBOARD_VIEW()").collect()

def Navigation(): 
    st.markdown("""
    <style>
        /* Hide menu, footer, and header */
        #MainMenu, footer, header {visibility: hidden;}

        /* Remove padding from block container */
        .block-container {
            padding-top: 2.6rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem;
            padding-right: 0rem;
        }

        /* Remove top margin from the body and root containers */
        .main > div {
            padding-top: 0rem !important;
        }
        
        body {
            margin-top: 0rem !important;
            overflow-x: hidden;
            overflow-y: hidden;
        }
    </style>
    """, unsafe_allow_html=True)

    
    if "select_navigation" not in st.session_state:
        st.session_state.select_navigation = "Overview"
        

    logo_base64 = base64.b64encode(open("./Images/tiger_logo.png", "rb").read()).decode()

    st.markdown(f"""
    <div class="custom-topbar">
        <div class="topbar-left">
            <img src="data:image/png;base64,{logo_base64}" class="topbar-logo">
        </div>
        <div class="topbar-center">
            <span class="topbar-title">Snowflake Platform Monitoring</span>
        </div>
    </div>
""", unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=["Overview", 'Create Monitors', 'Default Monitors', 'Ask Assistant'],
        icons=["house", "bi-graph-up-arrow", "bi bi-arrow-repeat", "bi bi-layers","bi-power"],
        default_index=0,
        orientation="horizontal",
        key ="my_menu",
        styles={
                    "container": {
                        "padding": "0!important", 
                        "background-color": "#262730",
                            "border-radius": "0px",
                            },
                    "icon": {"color": "white", "font-size": "18px"},
                    "nav-link": {
                        "color": "white",
                        "font-size": "16px",
                        "text-align": "center",
                        "border-radius": "0px",
                        "margin": "0px",
                        "--hover-color": "#333",
                        "font-family": "Poppins, sans-serif !important"
                    },
                    "nav-link-selected": {"background-color": "#47495c","border-radius": "0px"},
                }
    )
    
    st.session_state.select_navigation = selected
    if(st.session_state.select_navigation == "Overview"):
        dashboard()
    elif(st.session_state.select_navigation == "Create Monitors"):
        customMonitors()
    elif(st.session_state.select_navigation == "Default Monitors"):
        defaultMonitors()
    elif(st.session_state.select_navigation == "Ask Assistant"):
        askAssistant()

    with open("./Styles/Navbar.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    footer()

if __name__=='__main__':
    Navigation()