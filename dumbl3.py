import streamlit as st
import replicate
import pandas as pd
import os

st.set_page_config(page_title="💪🏼 Workout Recommender")

# loading the exercise data
data = pd.read_json("exercises.json")
data = data.drop(columns=["images","instructions","mechanic","id"])

st.title('💪🏼 Workout Recommender')
if 'REPLICATE_API_TOKEN' in st.secrets:
    replicate_api = st.secrets['REPLICATE_API_TOKEN']
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
    llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'


    string_dialogue = f"You are a fitness assistant. Recommend the ideal workout based on the following:\n"
    string_dialogue += f"- User Input: {prompt_input}\n"

    # Add exercise data to context (similar to chatbot approach)
    string_dialogue += f"\nAvailable exercises: {relevant_exercises.to_string()}"

    output = replicate.run(llm, 
                           input={"prompt": string_dialogue,
                                   "temperature":2.0, "top_p":0.8, "max_length":500, "repetition_penalty":1})
    return output

# getting the user input
prompt_input = f"I am a {level} and I have {equipment}. I want a workout routine for 3 days this week.Pick out of these exercises and focus on similar regions of the body for each session. Dont try to include everything, pick out a few good exercises and curate the routine with reps and sets mentioned."

# generating the workout suggestion
workout_suggestion = generate_workout_suggestion(prompt_input, relevant_exercises)

# displaying the workout suggestion
st.write("**Workout Suggestion:**")
st.text(workout_suggestion)