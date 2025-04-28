from typing import Dict, List, Optional, Tuple
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.exceptions import SnowparkSQLException

import json
import time
import _snowflake
import pandas as pd
import streamlit as st
import tempfile
import os
import yaml


session = get_active_session()

SEMANTIC_MODEL_PATH = "SNOWFLAKE_MONITORING.PUBLIC.SNOWFLAKE_MONITORING_APP_STAGE/result_semantic_model/result_analysis_semantic_model.yaml"
API_ENDPOINT = "/api/v2/cortex/analyst/message"
API_TIMEOUT = 50000


def reset_session_state():
    st.session_state.messages = [] 
    st.session_state.active_suggestion = None 
    st.session_state.active_prompt = None 

def show_header_and_sidebar():
    st.markdown("<h2 style='text-align: left;'>Result Analysis</h2>", unsafe_allow_html=True)
    st.dataframe(st.session_state['session'].sql("SELECT * FROM SNOWFLAKE_MONITORING.PUBLIC.MONITORING_RESULTS"), hide_index=True, use_container_width=True)
    with st.sidebar:
        _, btn_container, _ = st.columns([2, 6, 2])
        if btn_container.button("Clear Chat History", use_container_width=True):
            reset_session_state()

def handle_user_inputs():
    user_input = st.chat_input("What is your question?")
    if user_input:
        st.session_state.active_prompt = user_input
        process_user_input(user_input)
    elif st.session_state.active_suggestion is not None:
        suggestion = st.session_state.active_suggestion
        st.session_state.active_prompt = suggestion
        st.session_state.active_suggestion = None
        process_user_input(suggestion)
    
def handle_error_notifications():
    if st.session_state.get("fire_API_error_notify"):
        st.toast("An API error has occured!", icon=":rotating_light:")
        st.session_state["fire_API_error_notify"] = False

def process_user_input(prompt: str):
    new_user_message = {
        "role": "user",
        "content": [{"type": "text", "text": prompt}],
    }
    st.session_state.messages.append(new_user_message)
    with st.chat_message("user"):
        user_msg_index = len(st.session_state.messages) - 1
        display_message(new_user_message["content"], user_msg_index)
    with st.chat_message("analyst"):
        with st.spinner("Waiting for Analyst's response..."):
            time.sleep(1)
            response, error_msg = get_analyst_response(st.session_state.messages)
            if error_msg is None:
                analyst_message = {
                    "role": "analyst",
                    "content": response["message"]["content"],
                    "request_id": response["request_id"],
                }
            else:
                analyst_message = {
                    "role": "analyst",
                    "content": [{"type": "text", "text": error_msg}],
                    "request_id": response["request_id"],
                }
                st.session_state["fire_API_error_notify"] = True
            st.session_state.messages.append(analyst_message)
            st.rerun()

def get_analyst_response(messages: List[Dict]) -> Tuple[Dict, Optional[str]]:
    request_body = {
        "messages": messages,
        "semantic_model_file": f"@{SEMANTIC_MODEL_PATH}",
    }
    resp = _snowflake.send_snow_api_request(
        "POST",
        API_ENDPOINT, 
        {}, 
        {}, 
        request_body, 
        None, 
        API_TIMEOUT, 
    )
    parsed_content = json.loads(resp["content"])
    if resp["status"] < 400:
        return parsed_content, None
    else:
        error_msg = f"""
:rotating_light: An Analyst API error has occurred :rotating_light:
* response code: `{resp['status']}`
* request-id: `{parsed_content['request_id']}`
* error code: `{parsed_content['error_code']}`
Message:
```
{parsed_content['message']}
```
        """
        return parsed_content, error_msg

def display_conversation():
    for idx, message in enumerate(st.session_state.messages):
        role = message["role"]
        content = message["content"]
        with st.chat_message(role):
            display_message(content, idx)

def display_message(content: List[Dict[str, str]], message_index: int):
    for item in content:
        if item["type"] == "text":
            st.markdown(item["text"])
        elif item["type"] == "suggestions":
            for suggestion_index, suggestion in enumerate(item["suggestions"]):
                if st.button(
                    suggestion, key=f"suggestion_{message_index}_{suggestion_index}"
                ):
                    st.session_state.active_suggestion = suggestion
        elif item["type"] == "sql":
            display_sql_query(item["statement"], message_index)
        else:
            pass

@st.cache_data(show_spinner=False)
def get_query_exec_result(query: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    global session
    try:
        df = session.sql(query).to_pandas()
        return df, None
    except SnowparkSQLException as e:
        return None, str(e)

def display_sql_query(sql: str, message_index: int):
    with st.expander("SQL Query", expanded=False):
        st.code(sql, language="sql")
        if st.button('Add to verified queries', key=f'verified_queries_{message_index}'):
            yaml_file = SEMANTIC_MODEL_PATH
            stage_name, file_name = yaml_file.split('/')[0], yaml_file.split('/')[-1]
            verified_at = str(int(time.time()))
            verified_query = {
                'name': f'Verified query for {st.session_state.active_prompt}', 
                'question': st.session_state.active_prompt, 
                'sql': sql, 
                'verified_at': verified_at
            }
            file = session.file.get_stream(f"@{yaml_file}")
            yml_data = yaml.safe_load(file.read())

            if 'verified_queries' in yml_data.keys():
                yml_data['verified_queries'].append(verified_query)
            else:
                yml_data['verified_queries'] = [verified_query]
            
            with tempfile.TemporaryDirectory() as temp_dir:
                tmp_file_path = os.path.join(temp_dir, file_name)

                with open(tmp_file_path, "w", encoding="utf-8") as temp_file:
                    yaml.safe_dump(yml_data, temp_file, sort_keys=False)

                session.file.put(
                    tmp_file_path,
                    f"@{stage_name}",
                    auto_compress=False,
                    overwrite=True,
                )
            st.success('Success')


    with st.expander("Results", expanded=True):
        with st.spinner("Running SQL..."):
            df, err_msg = get_query_exec_result(sql)
            if df is None:
                st.error(f"Could not execute generated SQL query. Error: {err_msg}")
                return
            if df.empty:
                st.write("Query returned no data")
                return
            data_tab, chart_tab = st.tabs(["Data :page_facing_up:", "Chart :chart_with_upwards_trend: "])
            with data_tab:
                st.dataframe(df, use_container_width=True,hide_index=True)
            with chart_tab:
                display_charts_tab(df, message_index)

def display_charts_tab(df: pd.DataFrame, message_index: int) -> None:
    if len(df.columns) >= 2:
        all_cols_set = set(df.columns)
        col1, col2 = st.columns(2)
        x_col = col1.selectbox(
            "X axis", all_cols_set, key=f"x_col_select_{message_index}"
        )
        y_col = col2.selectbox(
            "Y axis",
            all_cols_set.difference({x_col}),
            key=f"y_col_select_{message_index}",
        )
        chart_type = st.selectbox(
            "Select chart type",
            options=["Line Chart", "Bar Chart"],
            key=f"chart_type_{message_index}",
        )
        if chart_type == "Line Chart":
            st.line_chart(df.set_index(x_col)[y_col])
        elif chart_type == "Bar Chart":
            st.bar_chart(df.set_index(x_col)[y_col])
    else:
        st.write("At least 2 columns are required")


if "messages" not in st.session_state:
    reset_session_state()
show_header_and_sidebar()
if len(st.session_state.messages) == 0:
    process_user_input("Tell me about the data")
display_conversation()
handle_user_inputs()
handle_error_notifications()
