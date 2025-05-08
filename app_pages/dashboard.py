import streamlit as st
import plotly.express as px
import pandas as pd


st.markdown("<h2 style='text-align: left;'>Monitoring Rules</h2>", unsafe_allow_html=True)

def active_rule(id, state, task):
    st.session_state['session'].sql(f"""
        update monitor_metadata set is_active = {not state} where id = '{id}'
        """).collect()
    if not state:
        st.session_state['session'].sql(f"""
            alter task if exists task_{str(task).replace(' ', '_')} resume
            """).collect()
    else:
        st.session_state['session'].sql(f"""
            alter task if exists task_{str(task).replace(' ', '_')} suspend
            """).collect()
        
def edit_rule(id):
    print('change')

def delete_rule(id, task):
    st.session_state['session'].sql(f"""
        delete from monitor_metadata where id = '{id}'
        """).collect()
    st.session_state['session'].sql(f"""
        drop task if exists task_{str(task).replace(' ', '_')}
        """).collect()

def run_rule(task):
    st.session_state['session'].sql(f"""
        execute task task_{str(task).replace(' ', '_')}
        """).collect()
    
def create_metric_card(title, value, icon):
    st.markdown(
        f"""
        <style>
            .metric-card {{
                background-color: #FFFFFF; /* Orange background */
                color: black;
                font-weight: bold;
                font-size: 18px;
                border: none;
                padding: 15px 20px;
                border-radius: 10px;
                text-align: center;
                display: block;
                width: 100%;
                box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2);
                transition: 0.3s;
            }}
            .metric-card:hover {{
                background-color: #E67E22; /* Darker orange on hover */
                transform: scale(1.05); /* Slight zoom effect */
            }}
        </style>
        <div class="metric-card">
            <p style="margin:0; font-size: 16px;">{title}</p>
            <p style="margin:0; font-size: 24px;">{value:,}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

results = st.session_state['session'].sql(f"""SELECT * FROM dashboard_stats_view""").to_pandas()

for i in range(len(results)):
    cols = st.columns(len(results.columns))
    for j, column in enumerate(results.columns):
        with cols[j]:
            create_metric_card(column, results.iloc[i][column], "📊")
import plotly.graph_objects as go

chart_data = st.session_state['session'].sql("""select monitoring_type, count(action_taken) as action_count, date(rule_run_timestamp) as rule_run_timestamp from monitoring_results where action_taken='Yes' group by monitoring_type, rule_run_timestamp order by 3, 2""").to_pandas()
fig = px.bar(chart_data, x="RULE_RUN_TIMESTAMP", y="ACTION_COUNT", title='Actions', width=600, height=450, color='MONITORING_TYPE')
st.plotly_chart(fig, theme=None, use_container_width=True)

data = st.session_state['session'].sql("""
    SELECT 
        *
    FROM SNOWFLAKE_MONITORING.PUBLIC.DASHBOARD_VIEW""").to_pandas()

display_df = data[[
    'IS_ACTIVE', 
    'MONITOR_NAME', 
    'MONITOR_TYPE', 
    'MONITOR_CATEGORY', 
    'MONITOR_SUBCATEGORY', 
    'MONITOR_ACTION', 
    'RESOURCE_NAME',
    'PARAMS',
    'FREQUENCY_NAME',
    'TASK_NAME',
    'EMAIL_ID',
    'CREATED_BY']]

text_search = st.text_input("Search Monitor name, type, category, subcategory, actions, resource name, email_id and created by", value="", placeholder="Type and press enter")
search1 = display_df["MONITOR_NAME"].str.contains(text_search)
search2 = display_df["MONITOR_TYPE"].str.contains(text_search)
search3 = display_df["MONITOR_CATEGORY"].str.contains(text_search)
search4 = display_df["MONITOR_SUBCATEGORY"].str.contains(text_search)
search5 = display_df["MONITOR_ACTION"].str.contains(text_search)
search6 = display_df["RESOURCE_NAME"].str.contains(text_search)
search7 = display_df["EMAIL_ID"].str.contains(text_search)
search8 = display_df["CREATED_BY"].str.contains(text_search)
df_search = display_df[search1 | search2 | search3 | search4 | search5 | search6 | search7 | search8]
if text_search:
    event = st.dataframe(
        df_search, 
        selection_mode=["single-row"], 
        on_select='rerun',
        use_container_width=True,
        hide_index=True,)
else:
    event = st.dataframe(
        display_df, 
        selection_mode=["single-row"], 
        on_select='rerun',
        use_container_width=True,
        hide_index=True,)

checked = event.selection.rows 
row = data.iloc[checked]

try:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.toggle('Active', value=row['IS_ACTIVE'].values[0], key=row['ID'].values[0] + ':active', on_change=active_rule, args=(row['ID'].values[0], row['IS_ACTIVE'].values[0], row['TASK_NAME'].values[0], ), disabled=False if checked else True)
    with col2:
        st.button('Edit', key=row['ID'].values[0] + ':edit', on_click=edit_rule, args=(row['ID'].values[0], ), disabled=False if checked else True)
    with col3:
        st.button('Delete', key=row['ID'].values[0] + ':delete', on_click=delete_rule, args=(row['ID'].values[0], row['TASK_NAME'].values[0], ), disabled=False if checked else True)
    with col4:
        st.button('Run', key=row['ID'].values[0] + ':run', on_click=run_rule, args=(row['TASK_NAME'].values[0], ), disabled=False if checked else True)
    with st.expander("See results"):
        st.dataframe(st.session_state['session'].sql(f"""select * from monitoring_results where rule_id='{row['ID'].values[0]}'"""), hide_index=True, use_container_width=True)
        if st.button(label='', icon=':material/refresh:', key=row['ID'].values[0] + ':refresh', disabled=False if checked else True):
            st.rerun()
except IndexError:
    st.write('Select any rule from above to continue')
