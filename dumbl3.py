import streamlit as st
import replicate
import pandas as pd
import os

# App title
st.set_page_config(page_title="Workout Recommender")

data = pd.read_json("exercises.json")
data = data.drop(columns=["images","instructions","mechanic"])

equipment_mapping = {
    "machine":2,
    "cable":2,
    "e-z curl bar":2,
    "barbell":2,
    "other":2,

    "dumbbell":1,
    "kettlebells":1,
    "medicine ball":1,
    "bands":1,
    "exercise ball":1,
    "foam roll":1,

    "body only":0,
}

level_mapping = {
    "beginner":0,
    "intermediate":1,
    "expert":2,
}

data["equipment"] = data["equipment"].map(equipment_mapping)
data["level"] = data["level"].map(level_mapping)

equipment_mapping = {
    "No equipment":0,
    "Basic at-home equipment":1,
    "Access to a Gym":2,
}
# Replicate Credentials
with st.sidebar:
    st.title('💪\n Workout Recommender')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')
    os.environ['REPLICATE_API_TOKEN'] = replicate_api

    st.subheader('Select your Parameters')
    level = st.sidebar.selectbox('Choose your current fitness level', ['beginner', 'intermediate', 'expert'])
    equipment = st.sidebar.selectbox('Choose your preferred equipment', ['No equipment', 'Basic at-home equipment', 'Access to a Gym'])
    st.markdown('🫂 Recommend us to your friends!')

relevant_exercises = data[(data["level"] == level) & (data["equipment"] <= equipment_mapping[equipment])]
# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "What can I help you with today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "What can I help you with today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating LLaMA2 response. Refactored from https://github.com/a16z-infra/llama2-chatbot
def generate_llama2_response(prompt_input):
    string_dialogue = f"You are a gym trainer. You only respond once as 'Gym Trainer'. You have to suggest a well balanced workout plan to the user based on their request. Dont ask too many questions and keep answers to the point. Give workout routines as a list of 3-5 exercises and include the number of sets and reps for each exercise.The user is a {level} and has {equipment}. Do not ask too many questions."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                  "temperature":0.2, "top_p":0.9, "max_length":600, "repetition_penalty":1})
    return output

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Curating your Workout..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)