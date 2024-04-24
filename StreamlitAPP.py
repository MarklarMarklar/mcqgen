import os
import json
import traceback
import pandas as pd
import io
import base64
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file,get_table_data
import streamlit as st
from langchain_community.callbacks import get_openai_callback
from src.mcqgenerator.MCQGenerator import generate_evaluate_chain
from src.mcqgenerator.logger import logging

with open('/home/marklar/mcqgen/Response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)
    
st.title("MCQ creator app 🌈")

with st.form("user_inputs"):
    uploaded_files=st.file_uploader("upload a pdf or txt file")
                                    
    mcq_count=st.number_input("No. of MCQs", min_value=3, max_value=50)

    subject=st.text_input("Insert Subject", max_chars=20)

    tone=st.text_input("Complexity level of questions")

    button=st.form_submit_button("Create MCQs")

    #Check if the button is clicked and all fields have input

    if button and uploaded_files is not None and mcq_count and subject and tone:
        with st.spinner("loading..."):
            try:
                text=read_file(uploaded_files)
                #Count tokens and the cost of API call
                with get_openai_callback() as cb:
                    response=generate_evaluate_chain(
                        {
                            "text": text,
                            "number": mcq_count,
                            "subject": subject,
                            "tone": tone,
                            "response_json": json.dumps(RESPONSE_JSON)
                        }
                    )
                #st.write(response)
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Error")
            else:
                print(f"Total tokens:{cb.total_tokens}")
                print(f"Prompt tokens:{cb.prompt_tokens}")
                print(f"Completion tokens:{cb.completion_tokens}")
                print(f"total cost:{cb.total_cost}")
                if isinstance(response, dict):
                    #extract the quiz data from the response
                    quiz=response.get("quiz", None)
                    if quiz is not None:
                        table_data=get_table_data(quiz)
                        if table_data is not None:
                            df=pd.DataFrame(table_data)
                            df.index=df.index+1
                            st.table(df)
                            #Display the review in a text box as well
                            st.text_area(label="Review", value=response["review"])
                            
                        else:
                            st.error("Error in the table data")
                else:
                    st.write(response)

            
        