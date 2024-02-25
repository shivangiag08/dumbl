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

# function to generate workout suggestion
def generate_workout_suggestion(prompt_input, relevant_exercises):
    # Assuming the correct model reference; replace with your actual model
    model_ref = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    
    string_dialogue = f"You are a fitness assistant. Recommend the ideal workout based on the following:\n- User Input: {prompt_input}\n\nAvailable exercises: {relevant_exercises.to_string(index=False)}"
    
    # Assuming 'replicate.predictions.create' is the correct method based on your package version and documentation
    output = replicate.predictions.create(model_ref, input={"prompt": string_dialogue, "temperature": 0.5, "max_tokens": 150})
    return output['choices'][0]['text'] if output else "No suggestion could be made."


# getting the user input
prompt_input = f"I am a {level} and I have {equipment}. I want a workout routine for 3 days this week.Pick out of these exercises and focus on similar regions of the body for each session. Dont try to include everything, pick out a few good exercises and curate the routine with reps and sets mentioned."
if replicate_api and st.button("Suggest Workout"):
    workout_suggestion = generate_workout_suggestion(prompt_input, relevant_exercises)
    st.write("**Workout Suggestion:**", workout_suggestion)