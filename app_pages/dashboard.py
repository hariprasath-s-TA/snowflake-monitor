import streamlit as st
from streamlit_extras.stylable_container import stylable_container


st.header("Monitoring Rules")

def active_rule(id, state, task):
    st.session_state['session'].sql(f"""
        update monitor_metadata set is_active = {not state} where id = '{id}'
        """).collect()
    if not state:
        st.session_state['session'].sql(f"""
            alter task if exists task_{task} resume
            """).collect()
    else:
        st.session_state['session'].sql(f"""
            alter task if exists task_{task} suspend
            """).collect()
        
def edit_rule(id):
    print('change')

def delete_rule(id, task):
    st.session_state['session'].sql(f"""
        delete from monitor_metadata where id = '{id}'
        """).collect()
    st.session_state['session'].sql(f"""
        drop task if exists task_{task}
        """).collect()

def run_rule(task):
    st.session_state['session'].sql(f"""
        execute task task_{task}
        """).collect()

containerStyle = ["""{
    border: 1px solid #bdc4d5;
    border-radius: 0.5rem;
    padding: 8px;
    overflow: hidden;
}"""]

results = st.session_state['session'].sql(f"""SELECT * FROM dashboard_stats_view""").to_pandas()

for i in range(len(results)):
    cols = st.columns(len(results.columns))
    for j, column in enumerate(results.columns):
        with cols[j]:
            with stylable_container(key="containerStyle", css_styles=containerStyle):
                st.markdown(f'<h3>{column}</h3>', unsafe_allow_html=True)
                st.markdown(f'<h4>{str(results.iloc[i][column])}</h4>', unsafe_allow_html=True)

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
    'WAREHOUSE_NAME',
    'CREDIT_LIMIT', 
    'PERCENTAGE',
    'LOG_TIMES',
    'START_TIME',
    'END_TIME',
    'FREQUENCY_NAME',
    'TASK_NAME',
    'EMAIL_ID',
    'CREATED_BY']]

text_search = st.text_input("Search Monitor name, type, category, subcategory, actions, warehouse name, email_id and created by", value="", placeholder="Type and press enter")
search1 = display_df["MONITOR_NAME"].str.contains(text_search)
search2 = display_df["MONITOR_TYPE"].str.contains(text_search)
search3 = display_df["MONITOR_CATEGORY"].str.contains(text_search)
search4 = display_df["MONITOR_SUBCATEGORY"].str.contains(text_search)
search5 = display_df["MONITOR_ACTION"].str.contains(text_search)
search6 = display_df["WAREHOUSE_NAME"].str.contains(text_search)
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
# if len(event.selection.rows)>0 else [0]
row = data.iloc[checked]

try:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.toggle('Active', value=row['IS_ACTIVE'].values[0], key=str(row['ID'].values[0]) + ':active', on_change=active_rule, args=(str(row['ID'].values[0]), str(row['IS_ACTIVE'].values[0]), str(row['TASK_NAME'].values[0]), ), disabled=False if checked else True)
    with col2:
        st.button('Edit', key=str(row['ID'].values[0]) + ':edit', on_click=edit_rule, args=(str(row['ID'].values[0]), ), disabled=False if checked else True)
    with col3:
        st.button('Delete', key=str(row['ID'].values[0]) + ':delete', on_click=delete_rule, args=(str(row['ID'].values[0]), str(row['TASK_NAME'].values[0]), ), disabled=False if checked else True)
    with col4:
        st.button('Run', key=str(row['ID'].values[0]) + ':run', on_click=run_rule, args=(row['TASK_NAME'].values[0], ), disabled=False if checked else True)
    with st.expander("See results"):
        st.dataframe(st.session_state['session'].sql(f"""select * from result_table where id='{str(row['ID'].values[0])}'"""), hide_index=True, use_container_width=True)
        if st.button(label='', icon=':material/refresh:', key=str(row['ID'].values[0]) + ':refresh', disabled=False if checked else True):
            st.rerun()
except IndexError:
    st.write('Select any rule from above to continue')
