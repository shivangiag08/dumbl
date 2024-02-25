import streamlit as st
import replicate
import pandas as pd
import os

# Set up the page.
st.set_page_config(page_title="Workout Recommender Chatbot")
st.title('💪 Workout Recommender Chatbot')

# Load the exercise data.
data = pd.read_json("exercises.json")
data = data.drop(columns=["images", "instructions", "mechanic", "id"])

# Sidebar for user preferences.
st.sidebar.header('Set Your Preferences')
level = st.sidebar.selectbox('Choose your current fitness level', ['beginner', 'intermediate', 'expert'])
equipment = st.sidebar.selectbox('Choose your preferred equipment', ['No equipment', 'Basic at-home equipment', 'Full gym access'])

# Mapping preferences to data.
level_mapping = {'beginner': 0, 'intermediate': 1, 'expert': 2}
equipment_mapping = {'No equipment': 0, 'Basic at-home equipment': 1, 'Full gym access': 2}
user_level = level_mapping[level]
user_equipment = equipment_mapping[equipment]

# Filter the data based on preferences.
filtered_exercises = data[(data['level'] == user_level) & (data['equipment'] <= user_equipment)]

# Initialize or load the Replicate API token.
if 'REPLICATE_API_TOKEN' in st.secrets:
    replicate_api = st.secrets['REPLICATE_API_TOKEN']
else:
    replicate_api = st.text_input('Enter Replicate API token:', type='password')

# Initialize session state for storing chat history and context.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Add a message to the chat history.
def add_message(author, text):
    st.session_state.messages.append({'author': author, 'text': text})

# Display the chat history.
for message in st.session_state.messages:
    if message['author'] == 'user':
        st.text_area('', value=message['text'], height=75, disabled=True)
    else:
        st.text_area('', value=message['text'], height=100, disabled=True)

# User input for chatbot.
user_input = st.text_input('Type your message here...', key='user_input')

# Function to get workout suggestions from LLaMA model.
def get_workout_suggestion(user_message):
    # Ensure the correct model reference.
    model_ref = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5' 
    
    # Construct the prompt.
    prompt = f"You are a fitness assistant. A user has the following preferences: level - {level}, equipment - {equipment}. They are asking: {user_message}"
    
    try:
        # Use the Replicate API to run the model.
        response = replicate.run(model_ref, {
            'prompt': prompt,
            'temperature': 0.5,
            'max_tokens': 150
        })

        # Assuming the generator yields a single item with the response.
        response_text = next(response)
        return response_text
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "I couldn't generate a workout suggestion at the moment. Please try again later."

# Handle button click to get recommendation.
if st.button('Get Recommendation') and user_input:
    # Add the user message to the chat history.
    add_message('user', user_input)
    
    # Get the workout suggestion.
    recommendation = get_workout_suggestion(user_input)
    
    # Add the assistant's response to the chat history.
    add_message('assistant', recommendation)
    
    # Clear the input box.
    st.session_state['user_input'] = ''

# Clear the chat history.
if st.sidebar.button('Clear Chat'):
    st.session_state.messages = []
