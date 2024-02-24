#import numpy as np
#import sklearn as sk
import pandas as pd
#import tensorflow as tf

data = pd.read_json("exercises.json")
data = data.drop(columns=["images","instructions","mechanic"])
print(data)

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

import pathlib
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

genai.configure(api_key="AIzaSyCLNphKj4p1sSVILlDCyNv93sjMDYZ9oWY")

model = genai.GenerativeModel('gemini-pro')

prompt = relevant_exercises.to_string + "\n\ngive me a one hour workout routine from these set of exercises. stick to similar regions of the body and make sure to include a warmup and cooldown."
response = model.generate_content("What is the meaning of life?")