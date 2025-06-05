import streamlit as st
import json
import pandas as pd


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
    umData = st.dataframe(
        st.session_state['data'][st.session_state['data']['MonitorType'] == 'User Monitoring'][['State', 'Monitor', 'Parameters', 'Action', 'ActionEmail']],
        hide_index=True,
        use_container_width=True,
        selection_mode=["single-row"], 
        on_select='rerun',
        key='data_editor_um' 
    )
    checked = umData.selection.rows 
    row = st.session_state['data'].iloc[checked]
    try:
        col1, col3, col4 = st.columns(3)
        with col1:
            st.toggle('Active', value=row['State'].values[0], key=row['Monitor'].values[0] + ':active', on_change=active_rule, args=(row['ID'].values[0], row['IS_ACTIVE'].values[0], row['TASK_NAME'].values[0], ), disabled=False if checked else True)
        # with col4:
        #     st.button('Run', key=row['ID'].values[0] + ':run', on_click=run_rule, args=(row['TASK_NAME'].values[0], ), disabled=False if checked else True)
        # with st.expander("See results"):
        #     st.dataframe(st.session_state['session'].sql(f"""select * from monitoring_results where rule_id='{row['ID'].values[0]}'"""), hide_index=True, use_container_width=True)
        #     if st.button(label='', icon=':material/refresh:', key=row['ID'].values[0] + ':refresh', disabled=False if checked else True):
        #         st.rerun()
    except IndexError:
        st.write('Select any rule from above to continue')
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
        key='data_editor_wm',
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

# with st.expander("User Monitoring"):
#     umData = st.data_editor(
#         st.session_state['data'][st.session_state['data']['MonitorType'] == 'User Monitoring'][['State', 'Monitor', 'Parameters', 'Action', 'ActionEmail']],
#         column_config={
#             'State': st.column_config.CheckboxColumn(
#                 'State',
#                 help='Activate/Deactivate',
#                 default=False
#             ),
#             'Parameters': st.column_config.TextColumn(
#                 'Parameters',
#                 help='Optional column'
#             ),
#             'ActionEmail': st.column_config.SelectboxColumn(
#                 'ActionEmail',
#                 options=availableEmailIds,
#                 required=True
#             )
#         },
#         hide_index=True,
#         use_container_width=True,
#         key='data_editor_um' 
#     )
#     for index, row in umData.iterrows():
#         if row['State']:
#             st.session_state['data'].loc[st.session_state['data']['Monitor'] == row['Monitor'], 'State'] = row['State']
#             st.session_state['data'].loc[st.session_state['data']['Monitor'] == row['Monitor'], 'Parameters'] = row['Parameters']
#             st.session_state['data'].loc[st.session_state['data']['Monitor'] == row['Monitor'], 'ActionEmail'] = row['ActionEmail']
#             selectedData = st.session_state['data'].loc[st.session_state['data']['Monitor'] == row['Monitor']].to_dict()
#             st.write(selectedData)
# with st.expander("Warehouse Monitoring"):
#     wmData = st.data_editor(
#         st.session_state['data'][st.session_state['data']['MonitorType'] == 'Warehouse Monitoring'][['State', 'Monitor', 'Parameters', 'Action', 'ActionEmail']],
#         column_config={
#             'State': st.column_config.CheckboxColumn(
#                 'State',
#                 help='Activate/Deactivate',
#                 default=False
#             ),
#             'ActionEmail': st.column_config.SelectboxColumn(
#                 'ActionEmail',
#                 options=availableEmailIds,
#                 required=True
#             )
#         },
#         hide_index=True,
#         use_container_width=True,
#         key='data_editor_wm',
#     )
#     for index, row in wmData.iterrows():
#         if row['State']:
#             st.session_state['data'].loc[st.session_state['data']['Monitor'] == row['Monitor'], 'State'] = row['State']
#             st.session_state['data'].loc[st.session_state['data']['Monitor'] == row['Monitor'], 'ActionEmail'] = row['ActionEmail']
# with st.expander("Database Object Monitoring"):
#     st.data_editor(
#         st.session_state['data'][st.session_state['data']['MonitorType'] == 'Database Object Monitoring'][['State', 'Monitor', 'Parameters', 'Action', 'ActionEmail']],
#         column_config={
#             'State': st.column_config.CheckboxColumn(
#                 'State',
#                 help='Activate/Deactivate',
#                 default=False
#             ),
#             'ActionEmail': st.column_config.SelectboxColumn(
#                 'ActionEmail',
#                 options=availableEmailIds,
#                 required=True
#             )
#         },
#         hide_index=True,
#         use_container_width=True,
#         key='data_editor_dom'
#     )
# with st.expander("Query Monitoring"):
#     st.data_editor(
#         st.session_state['data'][st.session_state['data']['MonitorType'] == 'Query Monitoring'][['State', 'Monitor', 'Parameters', 'Action', 'ActionEmail']],
#         column_config={
#             'State': st.column_config.CheckboxColumn(
#                 'State',
#                 help='Activate/Deactivate',
#                 default=False
#             ),
#             'ActionEmail': st.column_config.SelectboxColumn(
#                 'ActionEmail',
#                 options=availableEmailIds,
#                 required=True
#             )
#         },
#         hide_index=True,
#         use_container_width=True,
#         key='data_editor_qm'
#     )

st.dataframe(st.session_state['data'])
