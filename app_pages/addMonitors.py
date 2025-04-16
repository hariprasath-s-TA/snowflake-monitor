from streamlit_extras.stylable_container import stylable_container

import json
import streamlit as st
import pandas as pd
import uuid


st.header("Create Monitors")
containerStyle = ["""{
    border: 2px solid #bdc4d5;
    border-radius: 0.2rem;
    padding: 8px;
    overflow: hidden;
}"""]

with st.session_state['session'].file.get_stream('@"SNOWFLAKE_MONITORING"."PUBLIC"."SNOWFLAKE_MONITORING_APP_STAGE"/data.json') as file:
    data = json.load(file)

categories = ['Select Category']
sub_categories = ['Select SubCategory']
actions = ['Select Action']
monitors = ['Select Monitor']

# Session variables init
if 'no_actions' not in st.session_state:
	st.session_state['no_actions'] = 1
if 'data_dict' not in st.session_state:
    st.session_state['data_dict'] = dict()
if 'df' not in st.session_state:
    st.session_state['df'] = pd.DataFrame()
if 'reset' not in st.session_state:
    st.session_state['reset'] = True

for type in data['monitoring_type']:
    monitors.append(type['value'])

typeSelector = st.selectbox(
        "Select Monitoring Type",
        set(monitors),
        index=None,
        placeholder="Monitoring Type",
    )

categories_dict = {}
if typeSelector:
    for type in data['monitoring_type']:
        if type['value'] == typeSelector:
            categories_dict = type['category']
            for cat in categories_dict:
                categories.append(cat['value'])
    st.session_state['reset'] = True

monitor_name = st.text_input(label="Monitor Name", placeholder="Monitor name")

categorySelector = st.selectbox(
    "Category",
    set(categories),
    index=None,
    placeholder="Select category",
)

sub_categories_dict = {}
categories_input_type = ''
if categorySelector:
    for cat in categories_dict:
        if cat['value'] == categorySelector:
            if cat['user_input']:
                categories_input_type = cat['input_type']
            sub_categories_dict = cat['sub_category']
            for subcat in sub_categories_dict:
                sub_categories.append(subcat['value'])
    st.session_state['reset'] = True

start_timestamp = "NULL"
end_timestamp = "NULL"
warehouse = "NULL"

if categories_input_type == 'start/end time':
    col1,col2 = st.columns(2)
    with col1:
        date1 = st.date_input("Start Date",value = None)
    with col2:
        time1 = st.time_input("Start Time",value = None)
    col3,col4 = st.columns(2)
    with col3:
        date2 = st.date_input("End Date",value = None)
    with col4:
        time2 = st.time_input("End Time",value = None)
    if date1 and time1:
        start_timestamp = f"'{date1} {time1}'"  

    if date2 and time2:
        end_timestamp = f"'{date2} {time2}'" 
elif categories_input_type == 'warehouse':
    warehouse_data = st.session_state['session'].sql("""SELECT DISTINCT WAREHOUSE_NAME AS WAREHOUSES FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY""").to_pandas()
    warehouse = st.selectbox("Warehouse", warehouse_data['WAREHOUSES'].to_list(), index=None, key='warehouseSelector')

time, credits, percentage, email = '', '', '', ''
st.session_state['data_dict'][categorySelector] = []
with stylable_container(key="containerStyle", css_styles=containerStyle):
    st.subheader('Add Upto 3 Rules')
    for i in range(0, st.session_state['no_actions']):
        st.markdown(f'<h5>Rule {str(i+1)}:</h1>', unsafe_allow_html=True)
        cols = st.columns(2)
        with cols[0]:
            subcategorySelector = st.selectbox(
                "Sub Category",
                set(sub_categories),
                index=None,
                placeholder="Select subcategory",
                key="subcat"+str(i),
                disabled=False
            )
            actions_dict = {}
            sub_categories_input_type = ''
            if subcategorySelector:
                for subcat in sub_categories_dict:
                    if subcat['value'] == subcategorySelector:
                        if subcat['user_input']:
                            sub_categories_input_type = subcat['input_type']
                        else:
                            time = 1
                        actions_dict = subcat['action']
                        for act in actions_dict:
                            actions.append(act['value'])
                st.session_state['reset'] = False
        with cols[1]:
            if sub_categories_input_type == 'time':
                time = st.number_input("Number of times",value = None, key="time"+str(i))
            elif sub_categories_input_type == 'number':
                credits = st.number_input("Credit Limit to be Checked",value=None,key="num"+str(i))
            elif sub_categories_input_type == 'credits/percentage':
                credits = st.text_input("Enter Credit Limit",value=None,key="text"+str(i))
                percentage = st.number_input("Percentage to be Checked",value=None,key="num1"+str(i))
            elif sub_categories_input_type == 'credits':
                credits = st.text_input("Enter Credit Limit",value=None,key="text1"+str(i))
            else:
                dummy = st.text_input("Enter value", disabled=True, key="dummy"+str(i), value=None)
        
        with cols[0]:
            actionSelector = st.selectbox(
                "Actions",
                set(actions),
                index=None,
                placeholder="Select actions",
                key="act"+str(i)
            )

            actions_input_type = ''
            if actionSelector:
                for act in actions_dict:
                    if act['value'] == actionSelector:
                        if act['user_input']:
                            actions_input_type = act['input_type']
        
        with cols[1]:
            subcols = st.columns(2)
            with subcols[0]:
                email = st.text_input("Email id",value=None,key="email"+str(i), disabled=True if not actionSelector else False)
            with subcols[1]:
                frequency_data  = st.session_state['session'].sql("""SELECT * FROM SNOWFLAKE_MONITORING.PUBLIC.FREQUENCY_REGISTRY""").to_pandas()
                frequency = st.selectbox("Frequency", frequency_data['FREQUENCY_NAME'].to_list(), index=None, placeholder="Every Monday 00:00 AM UTC", key="freq"+str(i))
            
        if frequency or email or time or credits or percentage or actionSelector or subcategorySelector:
            try:
                if time:
                    st.session_state['data_dict'][categorySelector].append({subcategorySelector: {'time': time, "action": {"name": actionSelector, "value": email}, "frequency": frequency_data['FREQUENCY_VALUE'].to_list()[frequency_data['FREQUENCY_NAME'].to_list().index(frequency) - 1]}})
                elif credits:
                    st.session_state['data_dict'][categorySelector].append({subcategorySelector: {'credits': credits, "action": {"name": actionSelector, "value": email}, "frequency": frequency_data['FREQUENCY_VALUE'].to_list()[frequency_data['FREQUENCY_NAME'].to_list().index(frequency) - 1]}})
                elif percentage:
                    st.session_state['data_dict'][categorySelector].append({subcategorySelector: {'credits': credits, "percentage": percentage, "action": {"name": actionSelector, "value": email}, "frequency": frequency_data['FREQUENCY_VALUE'].to_list()[frequency_data['FREQUENCY_NAME'].to_list().index(frequency) - 1]}})
                else:
                    st.session_state['data_dict'][categorySelector].append({subcategorySelector: {"action": {"name": actionSelector, "value": email}, "frequency": frequency_data['FREQUENCY_VALUE'].to_list()[frequency_data['FREQUENCY_NAME'].to_list().index(frequency) - 1]}})
            except Exception as e:
                print(e, "Select frequency")
        st.divider()

    if None in st.session_state['data_dict'].keys():
        st.session_state['data_dict'].pop(None)

    category_list, subcategory_list, time_list, credits_list, percentage_list, action_name_list, action_value_list, frequency_list = [], [], [], [], [], [], [], []
    for data in st.session_state['data_dict']:
        for cat in st.session_state['data_dict'][data]:
            category_list.append(data)
            subcategory_list.append(list(cat.keys())[0])
            keys = cat[list(cat.keys())[0]].keys()        
            if 'time' in keys:
                time_list.append(cat[list(cat.keys())[0]]['time'])
            else:
                time_list.append('NULL')
            if 'credits' in keys:
                credits_list.append(cat[list(cat.keys())[0]]['credits']) 
            else:
                credits_list.append('NULL')
            if 'percentage' in keys:
                percentage_list.append(cat[list(cat.keys())[0]]['percentage'])
            else:
                percentage_list.append('NULL')
            action_name_list.append(cat[list(cat.keys())[0]]['action']['name'])
            action_value_list.append(cat[list(cat.keys())[0]]['action']['value'])
            frequency_list.append(cat[list(cat.keys())[0]]['frequency'])

    st.session_state['df'] = pd.DataFrame({
        "Category": category_list,
        "SubCategory": subcategory_list,
        "Time": time_list,
        "Credits": credits_list,
        "Percentage": percentage_list,
        "Action_Name": action_name_list,
        "Action_Value": action_value_list,
        "Frequency": frequency_list
    })

    btn_cols = st.columns(2)
    with btn_cols[0]:
        if st.button("Add New", key="add", disabled = False if not st.session_state['no_actions'] == 3 else True):
            if st.session_state['no_actions'] <= 2:
                st.session_state['no_actions'] += 1
            st.rerun()
    with btn_cols[1]:
        if st.button("Remove", key="remove", disabled = True if not st.session_state['no_actions'] > 1 else False):
            if st.session_state['no_actions'] > 1:
                st.session_state['no_actions'] -= 1
            st.rerun()
    if st.session_state['reset']:
        st.session_state['df'] = pd.DataFrame()
        st.session_state['data_dict'] = dict()
    if not st.session_state['df'].empty:
        st.dataframe(st.session_state['df'], hide_index=True, use_container_width=True)

def create_task(frequency, task_name, procedure):
    task = f"""
        CREATE OR REPLACE TASK task_{task_name}
        WAREHOUSE = dwhbi_developer_wh
        SCHEDULE = 'USING CRON {frequency}'
        AS
        {procedure}"""
    resume_task = f"""ALTER TASK IF EXISTS task_{task_name} RESUME"""
    st.session_state['session'].sql(task).collect()
    st.session_state['session'].sql(resume_task).collect()


def coreProc(monitorName, monitorType, category, subcategory, action, startTimestamp, endTimestamp, credits, warehouseName, percentage, logTime, createdBy, frequency, email_id, createdAt):
    id = uuid.uuid1().hex
    monitorId = str(st.session_state['session'].sql(f"""SELECT * FROM SNOWFLAKE_MONITORING.PUBLIC.MONITOR_REGISTRY WHERE NAME = '{monitorType}'""").to_pandas()['ID'].values[0])
    categoryId = str(st.session_state['session'].sql(f"""SELECT * FROM SNOWFLAKE_MONITORING.PUBLIC.CATEGORY_REGISTRY WHERE NAME = '{category}'""").to_pandas()['ID'].values[0])
    subCategoryId = str(st.session_state['session'].sql(f"""SELECT * FROM SNOWFLAKE_MONITORING.PUBLIC.SUB_CATEGORY_REGISTRY WHERE NAME = '{subcategory}'""").to_pandas()['ID'].values[0])
    actionId = str(st.session_state['session'].sql(f"""SELECT * FROM SNOWFLAKE_MONITORING.PUBLIC.ACTIONS_REGISTRY WHERE NAME = '{action}'""").to_pandas()['ID'].values[0])
    isActive = True
    taskName = monitorName
    procedureId = str(st.session_state['session'].sql(f"""SELECT * FROM SNOWFLAKE_MONITORING.PUBLIC.PROCEDURE_REGISTRY WHERE SUBCATEGORY_ID = '{subCategoryId}'""").to_pandas()['ID'].values[0])
    procedure = str(st.session_state['session'].sql(f"""SELECT * FROM SNOWFLAKE_MONITORING.PUBLIC.PROCEDURE_REGISTRY WHERE ID = '{procedureId}'""").to_pandas()['PROCEDURE_NAME'].values[0])
    insertQuery = f"""INSERT INTO SNOWFLAKE_MONITORING.PUBLIC.MONITOR_METADATA VALUES('{id}', '{monitorName}', '{monitorId}', '{categoryId}', '{subCategoryId}', '{actionId}', '{warehouseName}', '{credits}', '{percentage}', '{logTime}', '{startTimestamp}', '{endTimestamp}', '{frequency}', '{isActive}', '{taskName}', '{email_id}', '{createdBy}', '{createdAt}')"""
    st.session_state['session'].sql(insertQuery).collect()
    create_task(frequency, taskName, f"call {procedure}('{id}')")

Button = st.button("Save and Monitor", disabled = st.session_state['df'].empty)
if Button:
    createdBy = st.session_state['session'].sql(f"""SELECT CURRENT_USER()""").to_pandas().iloc[0, 0]
    for index, row in st.session_state['df'].iterrows():
        coreProc(monitor_name, typeSelector, categorySelector, subcategorySelector, actionSelector, start_timestamp, end_timestamp, row['Credits'], warehouse, row['Percentage'], row['Time'], createdBy, row['Frequency'], row['Action_Value'], st.session_state['session'].sql('select current_timestamp() as TIMESTAMP').to_pandas()['TIMESTAMP'].values[0])
    st.write('Updated')
    st.session_state['reset'] = True
    st.rerun()
    