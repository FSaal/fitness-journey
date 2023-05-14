from dash import Dash, html, dcc, callback, Output, Input, dash_table
import dash_mantine_components as dmc
import plotly.express as px
import numpy as np
import csv
import re
import pandas as pd

import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from preprocessing import PreprocessClass

app = Dash(__name__)

progression_path = "2023-04-27 18 58 40.csv"
gymbook_path = "GymBook-Logs-2023-04-08.csv"
preprocess = PreprocessClass(gymbook_path, progression_path)
df = preprocess.main()


# All sets with comments
df_comments = df[df["Set Comment"].notna()]


app.layout = html.Div(
    children=[
        dcc.Graph(id="graph-weight-by-exercise"),
        dmc.Select(id="dropdown-exercise", data=sorted(list(set(df["Exercise Name"]))), searchable=True),
        dcc.Graph(
            figure=px.scatter_3d(
                df[df["Exercise Name"].isin(["Barbell Bench Press", "Barbell Squat", "Barbell Deadlift"])],
                x="Time",
                y="Exercise Name",
                z="Weight",
                color="Repetitions",
            )
        ),
        dcc.Graph(id="graph-volumne-by-exercise"),
        dcc.Graph(id="graph-1rm"),
        dcc.Graph(id="graph-day-by-exercise"),
        # dcc.Graph(
        #     figure=px.density_heatmap(
        #         df, x="Weekday", y=df["Time"].dt.hour, category_orders={"Weekday": list(weekday_map.values())}
        #     )
        # ),
        dash_table.DataTable(df_comments.to_dict("records")),
    ]
)


@callback(Output("graph-weight-by-exercise", "figure"), Input("dropdown-exercise", "value"))
def show(exercise: str):
    df_filtered_exercise = df[df["Exercise Name"] == exercise]
    return px.scatter(df_filtered_exercise, x="Time", y="Weight", color="Repetitions")


@callback(Output("graph-volumne-by-exercise", "figure"), Input("dropdown-exercise", "value"))
def show2(exercise: str):
    df_filtered_exercise = df[df["Exercise Name"] == exercise]
    grouped_by_date = df_filtered_exercise.groupby(df_filtered_exercise["Time"].dt.date)

    def calculate_volumne(group):
        return (group["Repetitions"] * group["Weight"]).sum()

    volumne = grouped_by_date.apply(calculate_volumne)
    fig = px.scatter(volumne)
    fig.update_layout(yaxis_title="Volumne [kg]")
    return fig


@callback(Output("graph-1rm", "figure"), Input("dropdown-exercise", "value"))
def show3(exercise: str):
    """Calculate estimated 1RM for each set of an specific exercise"""
    df_by_exercise = df[df["Exercise Name"] == exercise]
    one_rm = df_by_exercise["Weight"] / (1.0278 - (0.0278) * df_by_exercise["Repetitions"])
    return px.scatter(df_by_exercise, x="Time", y=one_rm)


@callback(Output("graph-day-by-exercise", "figure"), Input("dropdown-exercise", "value"))
def show(exercise: str):
    weekday_map = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }

    df_filtered_exercise = df[df["Exercise Name"] == exercise]
    figure = px.density_heatmap(
        df_filtered_exercise,
        x="Weekday",
        y=df_filtered_exercise["Time"].dt.hour,
        category_orders={"Weekday": list(weekday_map.values())},
    )
    return figure


if __name__ == "__main__":
    app.run_server(debug=True)
