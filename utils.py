from openai import OpenAI
import os
import base64
import streamlit as st
import json
from datetime import datetime

# Load OpenAI API key from Streamlit secrets
api_key = st.secrets["openai"]["api_key"]

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

def get_answer(messages,tools=None):
    system_message = [{"role": "system", "content": f"You are a Google Assistant helper. Execute the instructions the user gives you, you can guess preferences without asking the user. Just explain your choices after having finished. Current time: {datetime.now().strftime('%Y-%m-%d %H:%M')}"}]
    messages = system_message + messages
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools
    )

    for message in messages:
        print("List of messages: ")
        print(message)

    return response.choices[0].message

def execute_tool_calls(service,messages, tool_calls, function_dict):

    tool_results = []
    
    # Execute tools one by one
    for tool_call in tool_calls:

        # Get the name
        name_of_function_gpt_wants_to_call = tool_call.function.name

        # Get the arguments
        arguments = json.loads(tool_call.function.arguments)
        
        # Check if the function name exists
        if name_of_function_gpt_wants_to_call in function_dict:
            # Get the function
            function_to_call = function_dict[name_of_function_gpt_wants_to_call]
            
            # Call the function with the provided arguments
            result = function_to_call(service,**arguments)

            # Add the result to the list
            tool_results.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": 'tool',
                    "name": name_of_function_gpt_wants_to_call,
                    "content": str(result),
                }
            )
    return tool_results


def ask_chatgpt_with_tools(service,messages, function_dict, tools, verbose=False):

    # Get the answer from the model
    message = get_answer(messages, tools=tools)
    messages.append(message)
    
    # Execute the tools and get new reply while tools are requested
    while message.tool_calls:
        tool_calls = message.tool_calls
        if tool_calls:
            tool_results = execute_tool_calls(service,messages, tool_calls, function_dict)
            for tool_result in tool_results:
                messages.append(tool_result)

            # Get the new answer
            message = get_answer(messages, tools=tools)
            messages.append(message)
    
    if verbose:
        for message in messages:
            print(message)
            
    return message.content

def speech_to_text(audio_data):
    with open(audio_data, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            response_format="text",
            file=audio_file
        )
    return transcript

def text_to_speech(input_text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=input_text
    )
    webm_file_path = "temp_audio_play.mp3"
    with open(webm_file_path, "wb") as f:
        response.stream_to_file(webm_file_path)
    return webm_file_path

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    md = f"""
    <audio autoplay>
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)
