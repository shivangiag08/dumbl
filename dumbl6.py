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
# function to generate workout suggestion
# Adjusted function to generate workout suggestion using replicate.run
def generate_workout_suggestion(prompt_input, relevant_exercises):
    # Assuming llm variable is set based on user's model selection as in the chatbot example
    model_ref = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
    
    # Construct the prompt with detailed information
    string_dialogue = "You are a fitness assistant. Recommend the ideal workout based on the following criteria:\n\n"
    string_dialogue += f"User Input: {prompt_input}\n\n"
    string_dialogue += "Available exercises:\n" + relevant_exercises.to_string(index=False) + "\n\n"
    
    # Parameters for the model call, adjust based on your requirements
    temperature = 0.5  # Adjust this value as necessary
    top_p = 0.9  # Adjust this value as necessary
    max_length = 120  # Adjust this value as necessary
    
    try:
        response_generator = replicate.run(model_ref, input={
            "prompt": string_dialogue,
            "temperature": temperature,
            "top_p": top_p,
            "max_length": max_length,
            "repetition_penalty": 1
        })

        for item in response_generator:
            st.write("Yielded item:", item)
    except Exception as e:
        st.error(f"An error occurred while iterating over the generator: {str(e)}")



# getting the user input
prompt_input = f"I am a {level} and I have {equipment}. I want a workout routine for 3 days this week.Pick out of these exercises and focus on similar regions of the body for each session. Dont try to include everything, pick out a few good exercises and curate the routine with reps and sets mentioned."
if replicate_api and st.button("Suggest Workout"):
    workout_suggestion = generate_workout_suggestion(prompt_input, relevant_exercises)
    st.write("**Workout Suggestion:**", workout_suggestion)