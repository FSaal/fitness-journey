from datetime import datetime

import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback, dcc, html

from preprocessing import PreprocessClass

app = Dash(__name__)

progression_path = r"data\2023-04-27 18 58 40.csv"
gymbook_path = r"data\GymBook-Logs-2023-04-08.csv"
preprocess = PreprocessClass(gymbook_path, progression_path)
df = preprocess.main()


# All sets with comments
df_comments = df[df["Set Comment"].notna()]


app.layout = html.Div(
    children=[
        dmc.Title("Plots by Exercise"),
        dmc.Text("Section exercise based plots"),
        dmc.Grid(
            children=[
                dmc.Col(
                    dmc.Select(
                        id="dropdown-muscle-group",
                        data=sorted(set(df["Bereich"])),
                        label="Muscle Group",
                        description="Filter exercises by muscle group",
                        searchable=True,
                    ),
                    span=3,
                ),
                # TODO add exercise type to each column in dataframe
                dmc.Col(
                    dmc.Select(
                        id="dropdown-exercise-type",
                        data=["Dumbbell", "Cable machine", "Barbell"],
                        label="Exercise Type",
                        description="Filter exercises by exercise type",
                        searchable=True,
                    ),
                    span=3,
                ),
                dmc.Col(
                    dmc.Select(
                        id="dropdown-exercise",
                        data=sorted(set(df["Exercise Name"])),
                        label="Exercise",
                        description="Plot",
                        searchable=True,
                    ),
                    span=3,
                ),
                dmc.Col(
                    dmc.DateRangePicker(
                        id="date-range-picker",
                        label="Timeframe",
                        description="Limit plots to a certain time frame.",
                        minDate=min(df["Time"]),
                    ),
                    span=2,
                ),
                dmc.Col(dmc.Paper(dcc.Graph(id="graph-weight-by-exercise"), shadow="xs"), span=6),
                dmc.Col(dmc.Paper(dcc.Graph(id="graph-volumne-by-exercise"), shadow="xs"), span=6),
                dmc.Col(dmc.Paper(dcc.Graph(id="graph-1rm-by-exercise"), shadow="xs"), span=6),
                dmc.Col(dmc.Paper(dcc.Graph(id="graph-days-trained-by-exercise"), shadow="xs"), span=6),
            ]
        ),
        dcc.Graph(
            figure=px.scatter_3d(
                df[df["Exercise Name"].isin(["Barbell Bench Press", "Barbell Squat", "Barbell Deadlift"])],
                x="Time",
                y="Exercise Name",
                z="Weight",
                color="Repetitions",
            )
        ),
        dcc.Graph(id="graph-day-by-exercise"),
        # dcc.Graph(
        #     figure=px.density_heatmap(
        #         df, x="Weekday", y=df["Time"].dt.hour, category_orders={"Weekday": list(weekday_map.values())}
        #     )
        # ),
        # dash_table.DataTable(df_comments.to_dict("records")),
    ]
)


@callback(Output("dropdown-exercise", "data"), Input("dropdown-muscle-group", "value"))
def filter_exercise_by_musclegroup(muscle_group):
    if not muscle_group:
        return sorted(set(df["Exercise Name"]))

    df_muscle_group_specific = df[df["Bereich"] == muscle_group]
    return sorted(set(df_muscle_group_specific["Exercise Name"]))


@callback(
    Output("graph-weight-by-exercise", "figure"),
    Output("graph-volumne-by-exercise", "figure"),
    Output("graph-1rm-by-exercise", "figure"),
    Output("graph-days-trained-by-exercise", "figure"),
    Input("dropdown-exercise", "value"),
    Input("date-range-picker", "value"),
)
def graph_by_exercise(exercise: str, date_range):
    """Plot the weight and volumne of an exercise over time"""
    df_filtered_exercise = df[df["Exercise Name"] == exercise]
    if date_range:
        # Convert date range to valid format
        start_date = datetime.strptime(date_range[0], "%Y-%m-%d")
        end_date = datetime.strptime(date_range[1], "%Y-%m-%d")
        df_filtered_exercise = df_filtered_exercise[
            (df_filtered_exercise["Time"] >= start_date) & (df_filtered_exercise["Time"] <= end_date)
        ]
    if df_filtered_exercise.empty:
        if not exercise:
            error_message = "Select an exercise to visualize data"
        else:
            error_message = "No data found for the selected time frame"
        empty_message = {
            "layout": {
                "xaxis": {"visible": False},
                "yaxis": {"visible": False},
                "annotations": [
                    {
                        "text": error_message,
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {"size": 28},
                    }
                ],
            }
        }
        return (empty_message,) * 4

    figure_weight = px.scatter(df_filtered_exercise, x="Time", y="Weight", color="Repetitions")
    figure_weight.update_layout(title="Weight Progression", yaxis_title="Weight [kg]")

    grouped_by_date = df_filtered_exercise.groupby(df_filtered_exercise["Time"].dt.date)

    def calculate_volumne(group):
        return (group["Repetitions"] * group["Weight"]).sum()

    volumne = grouped_by_date.apply(calculate_volumne)
    # TODO Fix wide ValueError
    figure_volumne = px.scatter(x=volumne.index, y=volumne)
    figure_volumne.update_layout(
        title="Volumne (Weight * Reps) Progression", xaxis_title="Time", yaxis_title="Volumne [kg]"
    )

    one_rm = df_filtered_exercise["Weight"] / (1.0278 - (0.0278) * df_filtered_exercise["Repetitions"])
    figure_1rm = px.scatter(
        df_filtered_exercise,
        x="Time",
        y=one_rm,
        color="Repetitions",
        title="Estimated 1RM (only accurate up to 5 reps)",
    )
    figure_1rm.update_layout(yaxis_title="Weight [kg]")

    weekdays = pd.Categorical(
        grouped_by_date["Weekday"].first(),
        categories=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    )
    figure_weekday = px.histogram(weekdays.sort_values(), title="Training Days")
    figure_weekday.update_layout(xaxis_title="Weekday", yaxis_title="Training Days", showlegend=False)

    return figure_weight, figure_volumne, figure_1rm, figure_weekday


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


# TODO: Add slider component, to limit x axis for all  plots


if __name__ == "__main__":
    app.run_server(debug=True)
    # app.run_server(host="0.0.0.0")
