import streamlit as st
import json
import pandas as pd


def defaultMonitors():
    st.markdown("<h2 style='text-align: left;'>Default Monitors</h2>", unsafe_allow_html=True)
    # DESC NOTIFICATION INTEGRATION EMAIL_NOTIFICATION_INT
    with open('data.json', 'r') as file:
        data = json.load(file)

    availableEmailIds = ['hariprasath.s@tigeranalytics.com', 'sruthi.sri@tigeranalytics.com']

    if 'data' not in st.session_state:
        st.session_state['data'] = pd.DataFrame(columns=['State', 'Monitor', 'Parameters', 'MonitorType', 'Category', 'SubCategory', 'Action', 'ActionEmail'])

    for i in range(len(data['defaults'])):
        default = data['defaults'][i]
        monitorName = default['name']
        monitorType = default['value']
        monitorUserInput = default['user_input']
        monitorUserInputType = default['input_type']
        categoryName = default['category']['value']
        subcategoryName = default['category']['sub_category']['value']
        actionName = default['category']['sub_category']['action']['value']
        st.session_state['data'].loc[i] = [False, monitorName, '', monitorType, categoryName, subcategoryName, actionName, availableEmailIds[0]]

    with st.expander("User Monitoring"):
        umData = st.data_editor(
            st.session_state['data'][st.session_state['data']['MonitorType'] == 'User Monitoring'][['State', 'Monitor', 'Parameters', 'Action', 'ActionEmail']],
            column_config={
                'State': st.column_config.CheckboxColumn(
                    'State',
                    help='Activate/Deactivate',
                    default=False
                ),
                'Parameters': st.column_config.TextColumn(
                    'Parameters',
                    help='Optional column'
                ),
                'ActionEmail': st.column_config.SelectboxColumn(
                    'ActionEmail',
                    options=availableEmailIds,
                    required=True
                )
            },
            hide_index=True,
            use_container_width=True,
            key='data_editor_um' 
        )
        for index, row in umData.iterrows():
            if row['State']:
                st.session_state['data'].loc[st.session_state['data']['Monitor'] == row['Monitor'], 'State'] = row['State']
                st.session_state['data'].loc[st.session_state['data']['Monitor'] == row['Monitor'], 'Parameters'] = row['Parameters']
                st.session_state['data'].loc[st.session_state['data']['Monitor'] == row['Monitor'], 'ActionEmail'] = row['ActionEmail']
    with st.expander("Warehouse Monitoring"):
        wmData = st.data_editor(
            st.session_state['data'][st.session_state['data']['MonitorType'] == 'Warehouse Monitoring'][['State', 'Monitor', 'Parameters', 'Action', 'ActionEmail']],
            column_config={
                'State': st.column_config.CheckboxColumn(
                    'State',
                    help='Activate/Deactivate',
                    default=False
                ),
                'ActionEmail': st.column_config.SelectboxColumn(
                    'ActionEmail',
                    options=availableEmailIds,
                    required=True
                )
            },
            hide_index=True,
            use_container_width=True,
            key='data_editor_wm'
        )
        for index, row in wmData.iterrows():
            if row['State']:
                st.session_state['data'].loc[st.session_state['data']['Monitor'] == row['Monitor'], 'State'] = row['State']
                st.session_state['data'].loc[st.session_state['data']['Monitor'] == row['Monitor'], 'ActionEmail'] = row['ActionEmail']
    with st.expander("Database Object Monitoring"):
        st.data_editor(
            st.session_state['data'][st.session_state['data']['MonitorType'] == 'Database Object Monitoring'][['State', 'Monitor', 'Parameters', 'Action', 'ActionEmail']],
            column_config={
                'State': st.column_config.CheckboxColumn(
                    'State',
                    help='Activate/Deactivate',
                    default=False
                ),
                'ActionEmail': st.column_config.SelectboxColumn(
                    'ActionEmail',
                    options=availableEmailIds,
                    required=True
                )
            },
            hide_index=True,
            use_container_width=True,
            key='data_editor_dom'
        )
    with st.expander("Query Monitoring"):
        st.data_editor(
            st.session_state['data'][st.session_state['data']['MonitorType'] == 'Query Monitoring'][['State', 'Monitor', 'Parameters', 'Action', 'ActionEmail']],
            column_config={
                'State': st.column_config.CheckboxColumn(
                    'State',
                    help='Activate/Deactivate',
                    default=False
                ),
                'ActionEmail': st.column_config.SelectboxColumn(
                    'ActionEmail',
                    options=availableEmailIds,
                    required=True
                )
            },
            hide_index=True,
            use_container_width=True,
            key='data_editor_qm'
        )

    st.dataframe(st.session_state['data'])
