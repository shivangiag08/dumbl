import json

# Parse the exercises.json data
with open("exercises.json", "r") as f:
    exercises = json.load(f)

# Define attributes and their corresponding keys
attributes = {
    "difficulty level": "level",
    "muscles": "primaryMuscles",
    "equipment": "equipment",
    "category": "category",
}

# Create the dataset
dataset = []

# Loop through each exercise
for exercise in exercises:
    for attribute, key in attributes.items():
        prompt = f"what {attribute} does {exercise['name']} work on?"
        completion = exercise.get(key, None)  # Handle missing values
        dataset.append({"prompt": prompt, "completion": completion})

# Save the dataset
with open("workout_data.json", "w") as f:
    json.dump(dataset, f, indent=4)