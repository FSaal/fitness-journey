import os

import dash_mantine_components as dmc
from dash import Input, Output, State, callback, html
from dash.exceptions import PreventUpdate
from langchain_community.llms import Ollama
from pandasai import SmartDataframe, SmartDatalake
from pandasai.responses.response_parser import ResponseParser

llm = Ollama(model="mistral")


def ai_playground_layout(df):
    """Layout for AI Playground"""
    get_callbacks(df)
    return dmc.Group(
        [
            dmc.Text("AI Playground", size="xl"),
            dmc.Textarea(id="textarea-ai-query", label="Input:", autosize=True, minRows=4, maxRows=20),
            dmc.Button("Submit", id="submit-ai-query"),
            html.Div(id="output-ai-query"),
        ]
    )


def get_callbacks(df):
    @callback(
        Output("output-ai-query", "children"), Input("submit-ai-query", "n_clicks"), State("textarea-ai-query", "value")
    )
    def ai_callbacks(n_clicks, query):
        if n_clicks is None:
            raise PreventUpdate
        if query is None:
            raise PreventUpdate
        output = ai_query(df, query)
        print(type(output))
        if isinstance(output, str):
            return output
        return output


def ai_query(df, query):
    df_smart = SmartDataframe(df)
    response = df_smart.chat(query)
    return response


os.environ["PANDASAI_API_KEY"] = "$2a$10$sQgAzi26CRgZy3pEDZVVQ.sZHGlLKmM9B9.iyLrrl.PKm6iBjZrEW"
os.environ["PANDASAI_WORKSPACE"] = "/Users/felix/Documents/coding/fitness-journey/fitness-journey/pandas-ai"
# df_exercises, df_bodyweight = load_data()

# df_smart = SmartDatalake([df_exercises, df_bodyweight])
# response = df_smart.chat(
#     # "What is the max weight for the exercise Squat and at what time?"
#     """Plot the weight of squats over time as scatter plot.
#     The color is the number of repetitions.
#     Sets with more than 10 reps should be orange, the rest should be green.""",
#     # The x-axis is time and the y-axis is weight. """
# )
# response = df_smart.chat("When was I the strongest in squat relative to my bodyweight?")
# print(response)
