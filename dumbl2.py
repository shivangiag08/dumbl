import streamlit as st
import replicate
import os
import pandas as pd

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
level = 'intermediate'
equip = 1

relevant_exercises = data[(data["level"] == level) & (data["equipment"] == equip)]


def generate_workout_suggestion(prompt_input):
    llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'

    
    string_dialogue = f"You are a fitness assistant. Recommend the ideal workout based on the following:\n"
    string_dialogue += f"- User Input: {prompt_input}\n"

    # Add exercise data to context (similar to chatbot approach)
    string_dialogue += f"\nAvailable exercises: {relevant_exercises.to_string()}"

    output = replicate.run(llm, 
                           input={"prompt": string_dialogue,
                                   "temperature":temperature, "top_p":top_p, "max_length":max_length, "repetition_penalty":1})
    return output

# ... (Remove chatbot UI code) ...

prompt_input = st.text_input("Enter your workout request (e.g., I want a full-body workout for beginners):")

# Run prompt generation in the background
if st.button("Suggest Workout"):
    with st.spinner("Finding the perfect workout..."):
        workout_suggestion = generate_workout_suggestion(prompt_input)

    # Display workout suggestion
    st.write("**Workout Suggestion:**")
    st.text(workout_suggestion)