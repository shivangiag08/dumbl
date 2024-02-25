import streamlit as st
import replicate
import pandas as pd
import os

st.set_page_config(page_title="💪🏼 Workout Recommender")

# Assuming exercises.json is correctly formatted and in the same directory
data = pd.read_json("exercises.json")
data = data.drop(columns=["images", "instructions", "mechanic", "id"])

st.title('💪🏼 Workout Recommender')

if 'REPLICATE_API_TOKEN' in st.secrets:
    replicate_api = st.secrets['REPLICATE_API_TOKEN']
else:
    replicate_api = st.text_input('Enter Replicate API token:', type='password')

if replicate_api:
    os.environ['REPLICATE_API_TOKEN'] = replicate_api

# mapping the equipment and level to numerical values
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

# getting the user input
level = st.selectbox('Choose your current fitness level', ['beginner', 'intermediate', 'expert'])

equipment = st.selectbox('Choose your preferred equipment', ['No equipment','Basic at-home equipment','Full gym access'])

equipment_mapping = {
    "No equipment":0,
    "Basic at-home equipment":1,
    "Full gym access":2,
}

equipment = equipment_mapping[equipment]

# filtering the data based on the user input
relevant_exercises = data[(data["level"] == level_mapping[level]) & (data["equipment"] <= equipment)]
relevant_exercises = relevant_exercises[["name","primaryMuscles","category"]]

if 'REPLICATE_API_TOKEN' in st.secrets:
    replicate_api = st.secrets['REPLICATE_API_TOKEN']
else:
    replicate_api = st.text_input('Enter Replicate API token:', type='password')

if replicate_api:
    os.environ['REPLICATE_API_TOKEN'] = replicate_api

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm your fitness buddy. How can I assist you today?"}]
if "conversation_context" not in st.session_state:
    st.session_state.conversation_context = "general"

# Function to add messages to chat
def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.text_area("", value=message["content"], key=f"user_{st.session_state.messages.index(message)}", height=75, disabled=True)
    else:  # Assistant's messages
        st.text_area("", value=message["content"], key=f"assistant_{st.session_state.messages.index(message)}", height=100, disabled=True)

# User input for the chatbot
user_input = st.text_input("Type your message here...", key="user_input")

# Function to classify user queries and update context
def classify_and_update_context(user_input):
    # Example: simple keyword-based classification
    context_keywords = {
        "cardio": ["run", "cardio", "jog"],
        "strength": ["lift", "strength", "weight"],
        "flexibility": ["stretch", "flexibility", "yoga"]
    }
    for context, keywords in context_keywords.items():
        if any(keyword in user_input.lower() for keyword in keywords):
            st.session_state.conversation_context = context
            return context
    return "general"
# Function to generate workout suggestions based on the conversation
def get_workout_suggestion(prompt, user_context):
    model_ref = 'a16z-infra/llama13b-v2-chat:latest'  # Replace with the correct LLaMA model reference
    
    # Construct the full prompt with the user context and conversation history
    full_prompt = f"You are a fitness assistant. {prompt} Given the user's interest in {user_context}, provide a suitable workout suggestion. Stick to similar regions of the body and don't try to give too many exercises. Only suggest 3-4 exercises along with reps and sets.\n\n###\n\n"
    
    # Iterate over the messages to add to the prompt
    for msg in st.session_state.messages:
        full_prompt += f"{msg['role'].capitalize()}: {msg['content']}\n\n"
    
    # Add stopping sequence to end the generation
    full_prompt += "###"
    
    try:
        # Call the Replicate API
        response = replicate.run(model_ref, {
            "prompt": full_prompt,
            "temperature": 0.7,
            "max_tokens": 150,
            "top_p": 0.95,
            "stop_sequences": ["###"]
        })
        
        # Assuming the response is a list and the first item is the text
        response_text = response[0] if response else "No response generated."
        return response_text
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "I couldn't generate a workout suggestion at the moment. Please try again later."

# Handle button click to get recommendation
if st.button('Get Recommendation') and user_input:
    # Obtain the context from the user's input message
    user_context = classify_and_update_context(user_input)
    
    # Add the user's message to the chat
    add_message("user", user_input)
    
    # Generate the workout suggestion
    recommendation = get_workout_suggestion(user_input, user_context)
    
    # Add the assistant's response to the chat
    add_message("assistant", recommendation)
    
    # Clear the user input
    st.session_state.user_input = ""
