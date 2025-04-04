import streamlit as st
import pandas as pd


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
    pass

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

data = st.session_state['session'].sql("""
    select 
        mm.id,
        mm.is_active,
        mm.monitor_name,
        mr.name as Monitor_Type,
        cr.name as Monitor_Category,
        scr.name as Monitor_SubCategory,
        ar.name as Monitor_Action,
        mm.warehouse_name,
        mm.credit_limit, 
        mm.percentage,
        mm.log_times,
        mm.start_time,
        mm.end_time,
        fr.frequency_name,
        mm.task_name,
        mm.email_id,
        mm.created_by
    from monitor_metadata mm
    join monitor_registry mr on mm.monitor_id = mr.id
    join category_registry cr on mm.category_id = cr.id
    join sub_category_registry scr on mm.sub_category_id = scr.id
    join actions_registry ar on mm.action_id = ar.id
    join frequency_registry fr on mm.frequency = fr.frequency_value""").to_pandas()

for index, row in data.iterrows():
    st.write(f'Rule {index + 1}:')
    with st.container(key=row['ID']+':rule_container'):
        st.dataframe(pd.DataFrame.from_dict({
            # 'ID': [row['ID']], 
            'MONITOR_NAME': [row['MONITOR_NAME']],
            'MONITOR_TYPE': [row['MONITOR_TYPE']],
            'MONITOR_CATEGORY': [row['MONITOR_CATEGORY']],
            'MONITOR_SUBCATEGORY': [row['MONITOR_SUBCATEGORY']],
            'MONITOR_ACTION': [row['MONITOR_ACTION']],
            'WAREHOUSE_NAME': [row['WAREHOUSE_NAME']],
            'CREDIT_LIMIT': [row['CREDIT_LIMIT']],
            'PERCENTAGE': [row['PERCENTAGE']],
            'LOG_TIMES': [row['LOG_TIMES']],
            'START_TIME': [row['START_TIME']],
            'END_TIME': [row['END_TIME']],
            'FREQUENCY_NAME': [row['FREQUENCY_NAME']],
            'TASK_NAME': [row['TASK_NAME']],
            'EMAIL_ID': [row['EMAIL_ID']],
            'CREATED_BY': [row['CREATED_BY']]
            }), hide_index=True, use_container_width=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.toggle('Active', value=row['IS_ACTIVE'], key=row['ID']+':active', on_change=active_rule, args=(row['ID'], row['IS_ACTIVE'], row['TASK_NAME'], ))
        with col2:
            st.button('Edit', key=row['ID']+':edit', on_click=edit_rule, args=(row['ID'], ))
        with col3:
            st.button('Delete', key=row['ID']+':delete', on_click=delete_rule, args=(row['ID'], row['TASK_NAME'], ))
        with col4:
            st.button('Run', key=row['ID']+':run', on_click=run_rule, args=(row['TASK_NAME'], ))
        with st.expander("See results"):
            st.dataframe(st.session_state['session'].sql(f"""select * from result_table where id='{row['ID']}'"""), hide_index=True, use_container_width=True)
            if st.button(label='', icon=':material/refresh:', key=row['ID']+ ':refresh'):
                st.rerun()
    st.divider()

# st.title('Warehouse result Table')
# st.dataframe(st.session_state['session'].sql("""select * from snowflake_monitoring.public.warehouse_result""").to_pandas())

