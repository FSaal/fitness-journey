from datetime import datetime

import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback, dcc, html

from preprocessing import PreprocessClass

app = Dash(__name__)

progression_path = r"data\2023-09-16 17 16 38.csv"
gymbook_path = r"data\GymBook-Logs-2023-04-08.csv"
weight1_path = r"data\weight.csv"
weight2_path = r"data\weight_Felix_1694877519.csv"
preprocess = PreprocessClass(gymbook_path, progression_path, weight1_path, weight2_path)
df, df_weight = preprocess.main()


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
                        maxDate=max(df["Time"]),
                    ),
                    span=2,
                ),
                dmc.Col(dmc.Paper(dcc.Graph(id="graph-weight-by-exercise"), shadow="xs"), span=12),
                dmc.Col(dmc.Paper(dcc.Graph(id="graph-volume-by-exercise"), shadow="xs"), span=6),
                dmc.Col(dmc.Paper(dcc.Graph(id="graph-1rm-by-exercise"), shadow="xs"), span=6),
                dmc.Col(dmc.Paper(dcc.Graph(id="graph-day-by-exercise"), shadow="xs"), span=6),
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
                size="Volume",
            )
        ),
        dcc.Graph(
            id="graph-bodyweight",
            figure=px.scatter(
                df_weight,
                x="Time",
                y="Weight",
                title="Bodyweight",
                trendline="lowess",
                trendline_options=dict(frac=0.1),
            ),
        ),
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
    Output("graph-volume-by-exercise", "figure"),
    Output("graph-1rm-by-exercise", "figure"),
    Output("graph-day-by-exercise", "figure"),
    Output("graph-days-trained-by-exercise", "figure"),
    Input("dropdown-exercise", "value"),
    Input("date-range-picker", "value"),
)
def graph_by_exercise(exercise: str, date_range: list[str]):
    """Different exercise specific plots over time. Such as weight, volume or 1rm."""
    df_filtered_exercise = df[df["Exercise Name"] == exercise]
    if date_range:
        # Convert date range to valid format
        start_date = datetime.strptime(date_range[0], "%Y-%m-%d")
        end_date = datetime.strptime(date_range[1], "%Y-%m-%d")
        df_filtered_exercise = df_filtered_exercise[
            (df_filtered_exercise["Time"] >= start_date) & (df_filtered_exercise["Time"] <= end_date)
        ]

    if df_filtered_exercise.empty:
        empty_message = plot_placeholder(exercise)
        return (empty_message,) * 5

    # Plot - Weight over time
    figure_weight = px.scatter(
        df_filtered_exercise,
        x="Time",
        y="Weight",
        color="Repetitions",
        size="Volume",
        title="Weight Progression",
    )
    figure_weight.update_layout(yaxis_title="Weight [kg]")

    # Plot - Estimated 1RM over time
    # 1RM Formula is only accurate up to about 12 reps
    max_reps = 12
    df_filtered_exercise_reps = df_filtered_exercise[df_filtered_exercise["Repetitions"] < max_reps]
    one_rm = df_filtered_exercise_reps["Weight"] / (1.0278 - (0.0278) * df_filtered_exercise_reps["Repetitions"])
    figure_1rm = px.scatter(
        df_filtered_exercise_reps,
        x="Time",
        y=one_rm,
        color="Repetitions",
        title="Estimated 1RM (only accurate up to 5 reps)",
    )
    figure_1rm.update_layout(yaxis_title="Weight [kg]")

    # Plot - Volume per training day over time
    grouped_by_date = df_filtered_exercise.groupby(df_filtered_exercise["Time"].dt.date)
    volume = grouped_by_date.apply(lambda x: (x["Repetitions"] * x["Weight"]).sum())
    n_sets = grouped_by_date.apply(lambda x: x["Set Order"].count())
    figure_volume = px.scatter(
        x=volume.index, y=volume, color=n_sets, title="Volume (Weight * Reps) Progression per Training Day"
    )
    figure_volume.update_layout(xaxis_title="Time", yaxis_title="Volume [kg]", coloraxis_colorbar_title_text="Sets")

    # Plot - Most trained day and time
    weekday_map = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }

    figure_time_heatmap = px.density_heatmap(
        df_filtered_exercise,
        x="Weekday",
        y=df_filtered_exercise["Time"].dt.hour,
        category_orders={"Weekday": list(weekday_map.values())},
        title="Favorite Set Time",
    )
    figure_time_heatmap.update_layout(yaxis_title="Hour")

    # Plot - Most trained day
    weekdays = pd.Categorical(
        grouped_by_date["Weekday"].first(),
        categories=list(weekday_map.values()),
    )
    figure_weekday = px.histogram(weekdays.sort_values(), title="Training Days")
    figure_weekday.update_layout(xaxis_title="Weekday", yaxis_title="Training Days", showlegend=False)

    return figure_weight, figure_volume, figure_1rm, figure_time_heatmap, figure_weekday


def plot_placeholder(exercise: str) -> str:
    """Display an error message in the plot if no data is available."""
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
    return empty_message


if __name__ == "__main__":
    app.run_server(debug=True)
    # app.run_server(host="0.0.0.0")
