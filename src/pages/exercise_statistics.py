import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import dcc, html, Output, Input, callback
import plotly.express as px
import pandas as pd

from utils.common_functions import plot_placeholder


def exercise_content(app, df, df_weight):
    get_callbacks(app, df, df_weight)

    return dmc.Stack(
        [
            dmc.Group(
                [
                    info_card(
                        "Weight moved on average",
                        "text-median-weight-by-exercise",
                        "badge-min-weight-by-exercise",
                        "badge-max-weight-by-exercise",
                        "pajamas:weight",
                    ),
                    info_card(
                        "Reps performed on average",
                        "text-median-reps-by-exercise",
                        "badge-min-reps-by-exercise",
                        "badge-max-reps-by-exercise",
                        "pajamas:repeat",
                    ),
                    info_card(
                        "Rest time on average",
                        "text-median-rest-by-exercise",
                        "badge-min-rest-by-exercise",
                        "badge-max-rest-by-exercise",
                        "bi:stopwatch",
                    ),
                ]
            ),
            html.Br(),
            dmc.Grid(
                children=[
                    dmc.Col(dmc.Paper(dcc.Graph(id="graph-weight-by-exercise"), shadow="xs"), span=12),
                    dmc.Col(dmc.Paper(dcc.Graph(id="graph-volume-by-exercise"), shadow="xs"), span=6),
                    dmc.Col(dmc.Paper(dcc.Graph(id="graph-1rm-by-exercise"), shadow="xs"), span=6),
                    dmc.Col(dmc.Paper(dcc.Graph(id="graph-day-by-exercise"), shadow="xs"), span=6),
                    dmc.Col(dmc.Paper(dcc.Graph(id="graph-days-trained-by-exercise"), shadow="xs"), span=6),
                ],
                justify="flex-end",
            ),
            dcc.Graph(
                id="graph-bodyweight",
                figure=px.scatter(
                    df_weight,
                    y="Weight",
                    title="Bodyweight",
                    trendline="lowess",
                    trendline_options=dict(frac=0.1),
                ),
            ),
            # dash_table.DataTable(df_comments.to_dict("records")),
        ]
    )


def info_card(description_text, main_text_id, negative_text_id, positive_text_id, icon, icon_size=30):
    return dmc.Card(
        children=[
            dmc.Stack(
                [
                    dmc.Group(
                        [
                            dmc.Text(id=main_text_id, weight=700, size="xl"),
                            DashIconify(icon=icon, width=icon_size),
                        ],
                        position="apart",
                    ),
                    dmc.Text(children=description_text, color="dimmed", size="sm"),
                    dmc.Group(
                        [
                            dmc.Badge(id=negative_text_id, color="red"),
                            dmc.Badge(id=positive_text_id, color="green"),
                        ],
                        spacing="md",
                    ),
                ],
                spacing="sm",
            )
        ],
        shadow="sm",
    )


def get_callbacks(app, df, df_weight):
    @app.callback(
        Output("dropdown-exercise", "data"),
        Input("dropdown-muscle-group", "value"),
        Input("dropdown-exercise-type", "value"),
    )
    def filter_exercise_by_musclegroup(muscle_group, exercise_type):
        """Update selectable exercises dependent on selected exercise type and muscle category."""
        if not muscle_group and not exercise_type:
            return sorted(set(df["Exercise Name"]))

        if muscle_group and exercise_type:
            df_filtered = df[(df["Muscle Category"] == muscle_group) & (df["Exercise Type"] == exercise_type)]
        elif muscle_group:
            df_filtered = df[df["Muscle Category"] == muscle_group]
        elif exercise_type:
            df_filtered = df[df["Exercise Type"] == exercise_type]
        return sorted(set(df_filtered["Exercise Name"]))

    def filter_exercise_data(df, exercise, date_range, show_only_comment_sets):
        """Filter exercise data based on selected exercise, date range, and show only comment sets."""
        df_filtered_exercise = df[df["Exercise Name"] == exercise]
        if date_range:
            start_date, end_date = pd.to_datetime(date_range)
            df_filtered_exercise = df_filtered_exercise[
                (df_filtered_exercise.index >= start_date) & (df_filtered_exercise.index <= end_date)
            ]
        if show_only_comment_sets:
            df_filtered_exercise = df_filtered_exercise[df_filtered_exercise["Set Comment"].notna()]
        return df_filtered_exercise

    @callback(
        Output("graph-weight-by-exercise", "figure"),
        Output("graph-volume-by-exercise", "figure"),
        Output("graph-1rm-by-exercise", "figure"),
        Output("graph-day-by-exercise", "figure"),
        Output("graph-days-trained-by-exercise", "figure"),
        Input("dropdown-exercise", "value"),
        Input("date-range-picker", "value"),
        Input("switch-show-comments", "checked"),
    )
    def graph_by_exercise(exercise: str, date_range: list[str], show_only_comment_sets: bool):
        """Different exercise specific plots over time. Such as weight, volume or 1rm."""
        df_filtered_exercise = filter_exercise_data(df, exercise, date_range, show_only_comment_sets)

        if df_filtered_exercise.empty:
            empty_message = plot_placeholder(exercise)
            return (empty_message,) * 5

        # Limit max color scale value to not dilute the colors
        if df_filtered_exercise["Repetitions"].max() > 12:
            color_scale_range = [df_filtered_exercise["Repetitions"].min(), 12]
        else:
            color_scale_range = [df_filtered_exercise["Repetitions"].min(), df_filtered_exercise["Repetitions"].max()]

        # Plot - Weight over time
        figure_weight = px.scatter(
            df_filtered_exercise,
            y="Weight",
            color="Repetitions",
            range_color=color_scale_range,
            size="Volume",
            hover_data=["Set Comment"],
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
            y=one_rm,
            color="Repetitions",
            range_color=color_scale_range,
            title="Estimated 1RM (only accurate up to 5 reps)",
        )
        figure_1rm.update_layout(yaxis_title="Weight [kg]")

        # Plot - Volume per training day over time
        grouped_by_date = df_filtered_exercise.groupby(df_filtered_exercise.index.date)
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
            y=df_filtered_exercise.index.hour,
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

    @callback(
        [Output(f"badge-min-{category}-by-exercise", "children") for category in ["weight", "reps", "rest"]],
        [Output(f"badge-max-{category}-by-exercise", "children") for category in ["weight", "reps", "rest"]],
        [Output(f"text-median-{category}-by-exercise", "children") for category in ["weight", "reps", "rest"]],
        Input("dropdown-exercise", "value"),
    )
    def stats_by_exercise(exercise: str) -> tuple([str] * 9):
        """Display statistics for the selected exercise."""
        df_filtered_exercise = df[df["Exercise Name"] == exercise]
        if df_filtered_exercise.empty:
            return ("",) * 9

        weight_statistics = df_filtered_exercise["Weight"].agg(["min", "max", "median"])
        reps_statistics = df_filtered_exercise["Repetitions"].agg(["min", "max", "median"])

        # Calculate median rest time between sets
        # TODO: Logic Flaw - this is not the rest time, but the rest time + exercise time
        stats_per_date = df_filtered_exercise.groupby(df_filtered_exercise.index.date)["Time"].agg(
            ["min", "max", "count"]
        )
        time_difference = (stats_per_date["max"] - stats_per_date["min"]).dt.total_seconds()
        # Remove days with zero rest time, either due to only one set that day or data added after training
        stats_per_date = stats_per_date[time_difference > 0]
        avg_set_time_per_date = time_difference / stats_per_date["count"]
        set_time_statistics = avg_set_time_per_date.agg(["min", "max", "median"])

        # Format the statistics
        weight_min, weight_max, weight_median = (
            weight_statistics["min"],
            weight_statistics["max"],
            weight_statistics["median"],
        )
        reps_min, reps_max, reps_median = (
            reps_statistics["min"],
            reps_statistics["max"],
            round(reps_statistics["median"]),
        )
        set_time_min, set_time_max, set_time_median = (
            round(set_time_statistics["min"]),
            round(set_time_statistics["max"]),
            round(set_time_statistics["median"]),
        )

        # Return the formatted statistics
        return (
            f"{weight_min} kg",
            reps_min,
            f"{set_time_max} s",
            f"{weight_max} kg",
            reps_max,
            f"{set_time_min} s",
            f"{weight_median} kg",
            f"{reps_median} reps",
            f"{set_time_median} s",
        )
