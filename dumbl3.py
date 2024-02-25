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
        st.text_area("", value=message["content"], key=f"assistant_{st.session_state.messages.index(message)}", height=100, disabled=True, background_color="#f0f2f6")

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

# Update this part within the button click handling
if st.button('Get Recommendation') and user_input:
    user_context = classify_and_update_context(user_input)
    add_message("user", user_input)

def get_workout_suggestion(prompt, user_context):
    model_ref = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'  # Ensure correct model reference
    
    # Enhance the prompt with contextual info
    enhanced_prompt = f"{prompt}Given the user's interest in {user_context}, provide a suitable workout suggestion.Stick to similar regions of the body and dont try to give too many exercises. only suggest 3-4 along with reps and sets.\n\n###\n\n"
    
    try:
        response_generator = replicate.run(model_ref, {
            "prompt": enhanced_prompt,
            "temperature": 0.7,
            "max_length": 200,
            "top_p": 0.95,
            "stop_sequences": ["###"]
        })
        
        # Concatenate text from generator
        response_text = "".join([text for text in response_generator])
        return response_text
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "I couldn't generate a workout suggestion at the moment. Please try again later."

# Within the button click handling, after updating context
if st.button('Get Recommendation') and user_input:
    # Context classification is already handled above
    recommendation = get_workout_suggestion(user_input, st.session_state.conversation_context)
    add_message("assistant", recommendation)
    st.session_state.user_input = ""  # Optionally clear input field