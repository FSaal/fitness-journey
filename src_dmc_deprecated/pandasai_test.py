import os

from langchain_community.llms import Ollama
from pandasai import SmartDataframe, SmartDatalake

from preprocessing import PreprocessClass

llm = Ollama(model="mistral")


def load_data():
    """Load data and preprocess it"""
    progression_path = "data/2024-09-25 08:19:34.csv"
    gymbook_path = "data/GymBook-Logs-2023-04-08.csv"
    weight_myfitnesspal_path = "data/weight.csv"
    weight_eufy_path = "data/weight_Felix_1713633990.csv"
    preprocess = PreprocessClass(
        gymbook_path,
        progression_path,
        weight_myfitnesspal_path,
        weight_eufy_path,
    )
    df, df_weight = preprocess.main()
    # rename Time column to time_column
    df = df.rename(columns={"Time": "time_column"})
    df_weight = df_weight.rename(columns={"Weight": "Body weight"})
    return df, df_weight


os.environ["PANDASAI_API_KEY"] = "$2a$10$sQgAzi26CRgZy3pEDZVVQ.sZHGlLKmM9B9.iyLrrl.PKm6iBjZrEW"
os.environ["PANDASAI_WORKSPACE"] = "/Users/felix/Documents/coding/fitness-journey/fitness-journey/pandas-ai"
df_exercises, df_bodyweight = load_data()

df_smart = SmartDatalake([df_exercises, df_bodyweight])
response = df_smart.chat(
    # "What is the max weight for the exercise Squat and at what time?"
    """Create a creative plot that correlates all data. Keep in mind that bodyweight is not the same as weight. Try to incorporate some jokes."""
    # The x-axis is time    and the y-axis is weight. """
)
# response = df_smart.chat("When was I the strongest in squat relative to my bodyweight?")
# print(response)
