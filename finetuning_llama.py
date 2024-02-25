import replicate

training = replicate.trainings.create(
  version="meta/llama-2-7b:73001d654114dad81ec65da3b834e2f691af1e1526453189b7bf36fb3f32d0f9",
  input={
    "train_data": "https://github.com/shivangiag08/dumbl/blob/main/workout_data.json",
    "num_train_epochs": 3,
  },
  destination="shivangiag08/llama2-gymbro"
)

print(training)