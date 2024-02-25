import streamlit as st
import replicate

# Initialize the chatbot UI
st.set_page_config(page_title="Fitness Buddy Chatbot")
st.title('🏋️ Fitness Buddy Chatbot')

# Initialize session state for storing chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm your fitness buddy. How can I assist you today?"}]

# Function to add messages to chat
def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.text_area("", value=message["content"], key=f"user_{st.session_state.messages.index(message)}", height=75, disabled=True)
    else:  # Assistant's messages
        st.text_area("", value=message["content"], key=f"assistant_{st.session_state.messages.index(message)}", height=100, disabled=True, background_color="#f0f2f6")

# User input
user_input = st.text_input("Type your message here...", key="user_input")

def get_workout_suggestion(user_query):
    # Example model reference, replace with the specific LLaMA model you're using
    model_ref = 'a16z-infra/llama13b-v2-chat:latest'
    
    # Construct the prompt
    prompt = f"{user_query}\n\n###\n\n"
    for msg in st.session_state.messages:
        prompt += f"{msg['role'].capitalize()}: {msg['content']}\n\n"
    
    # Call the Replicate API
    try:
        response = replicate.predictions.create(model_ref, {
            "prompt": prompt,
            "temperature": 0.7,
            "max_tokens": 150,
            "top_p": 0.95,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "stop_sequences": ["###"]
        })
        
        # Assuming the response structure matches expected format
        return response[0]['text']
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "I couldn't generate a workout suggestion at the moment. Please try again later."

# Handle button click to get recommendation
if st.button('Get Recommendation') and user_input:
    add_message("user", user_input)
    recommendation = get_workout_suggestion(user_input)
    add_message("assistant", recommendation)
    st.session_state.user_input = ""  # Clear input field
