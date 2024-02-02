from typing import Any, Dict

import dash_mantine_components as dmc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html
from dash_iconify import DashIconify

from utils.common_functions import plot_placeholder


def exercise_content(app, df: pd.DataFrame) -> dmc.Stack:
    get_callbacks(app, df)
    layout = dmc.Stack(
        [
            generate_info_cards(),
            html.Br(),
            dmc.Grid(
                children=[
                    dmc.Col(
                        dmc.Paper(dcc.Graph(id="graph-weight-by-exercise"), shadow="md"),
                        span=12,
                    ),
                    dmc.Col(
                        dmc.Paper(dcc.Graph(id="graph-volume-by-exercise"), shadow="md"),
                        span=6,
                    ),
                    dmc.Col(
                        dmc.Paper(dcc.Graph(id="graph-1rm-by-exercise"), shadow="md"),
                        span=6,
                    ),
                    dmc.Col(
                        dmc.Paper(dcc.Graph(id="graph-day-by-exercise"), shadow="md"),
                        span=6,
                    ),
                    dmc.Col(
                        dmc.Paper(dcc.Graph(id="graph-days-trained-by-exercise"), shadow="md"),
                        span=6,
                    ),
                ],
                justify="flex-end",
            ),
        ]
    )
    return layout


def generate_info_cards() -> dmc.Group:
    """Display general statistics on info cards, stacked horizontally."""
    return dmc.Group(
        [
            info_card(
                "weight",
                "kg moved on average",
                "material-symbols:weight-outline",
            ),
            info_card(
                "sets",
                "sets performed on average",
                "material-symbols:reorder",
            ),
            info_card(
                "reps",
                "reps performed on average",
                "material-symbols:replay",
            ),
            info_card(
                "rest",
                "s rest time on average",
                "material-symbols:timer-outline",
            ),
        ]
    )


def info_card(
    category: str,
    description: str,
    icon: str,
    icon_size: int = 30,
) -> Dict[str, Any]:
    """Display a general statistic on an info card."""
    main_text_id = f"text-median-{category}-by-exercise"
    negative_text_id = f"badge-min-{category}-by-exercise"
    positive_text_id = f"badge-max-{category}-by-exercise"
    negative_tooltip_id = f"tooltip-min-{category}-by-exercise"
    positive_tooltip_id = f"tooltip-max-{category}-by-exercise"
    layout = dmc.Card(
        children=[
            dmc.Stack(
                [
                    dmc.Group(
                        [
                            dmc.Text(category.capitalize(), weight=500, size="md"),
                            DashIconify(icon=icon, width=icon_size),
                        ],
                        position="apart",
                    ),
                    dmc.Group(
                        [
                            dmc.Text(id=main_text_id, weight=700, size="xl"),
                            dmc.Text(children=description, color="dimmed", size="sm"),
                        ],
                        spacing="xs",
                    ),
                    dmc.Group(
                        [
                            dmc.Tooltip(
                                children=dmc.Badge(id=negative_text_id, color="red"),
                                id=negative_tooltip_id,
                                label="Min",
                                position="bottom",
                                transition="slide-down",
                            ),
                            dmc.Tooltip(
                                children=dmc.Badge(id=positive_text_id, color="green"),
                                id=positive_tooltip_id,
                                label="Max",
                                position="bottom",
                                transition="slide-down",
                            ),
                        ],
                        position="center",
                    ),
                ],
                spacing="sm",
            ),
        ],
        shadow="sm",
    )
    return layout


def get_callbacks(app, df):
    @app.callback(
        Output("dropdown-exercise", "data"),
        Input("dropdown-muscle-group", "value"),
        Input("dropdown-exercise-type", "value"),
    )
    def filter_exercise_by_musclegroup(muscle_group: str, exercise_type: str) -> list[str]:
        """Update selectable exercises in sidebar,
        dependent on selected exercise type and muscle category."""
        # Do not filter, if no exercise type or muscle group is selected
        if not muscle_group and not exercise_type:
            return sorted(set(df["Exercise Name"]))

        df_filtered = df
        if muscle_group:
            df_filtered = df_filtered[df_filtered["Muscle Category"] == muscle_group]
        if exercise_type:
            df_filtered = df_filtered[df_filtered["Exercise Type"] == exercise_type]
        return sorted(set(df_filtered["Exercise Name"]))

    def filter_exercise_data(
        df: pd.DataFrame,
        exercise: str,
        date_range: None | list[str],
        show_only_commented_sets: bool,
    ) -> pd.DataFrame:
        """Filter exercise data based on selection in sidebar.
        Includes selected exercise, date range and show only comment sets."""
        df_filtered_exercise = df[df["Exercise Name"] == exercise]
        if date_range:
            start_date, end_date = pd.to_datetime(date_range)
            df_filtered_exercise = df_filtered_exercise[
                (df_filtered_exercise.index >= start_date) & (df_filtered_exercise.index <= end_date)
            ]
        if show_only_commented_sets:
            df_filtered_exercise = df_filtered_exercise[df_filtered_exercise["Set Comment"] != "None"]
        return df_filtered_exercise

    @callback(
        [Output(f"badge-min-{category}-by-exercise", "children") for category in ["weight", "sets", "reps", "rest"]],
        [Output(f"badge-max-{category}-by-exercise", "children") for category in ["weight", "sets", "reps", "rest"]],
        [Output(f"text-median-{category}-by-exercise", "children") for category in ["weight", "sets", "reps", "rest"]],
        [Output(f"tooltip-min-{category}-by-exercise", "label") for category in ["weight", "sets", "reps", "rest"]],
        [Output(f"tooltip-max-{category}-by-exercise", "label") for category in ["weight", "sets", "reps", "rest"]],
        Input("dropdown-exercise", "value"),
    )
    def stats_by_exercise(exercise: str) -> tuple([str] * 12):
        """Display statistics for the selected exercise."""
        df_filtered_exercise = df[df["Exercise Name"] == exercise]
        if df_filtered_exercise.empty:
            return ("",) * 12

        # Calculate median rest time between sets
        avg_set_time_per_date = calculate_avg_set_time(df_filtered_exercise)

        columns = ["Weight", "Set Order", "Repetitions"]
        number_statistics = df_filtered_exercise.agg({key: ["min", "max", "median"] for key in columns})
        # Set Time must be calculated separately, because it is grouped by date
        # and thus not the same length as the original dataframe
        number_statistics["Set Time"] = avg_set_time_per_date.agg(["min", "max", "median"]).astype(int)

        # Calculate the Time when the min or max values where observed
        time_statistics = {}
        for column in columns:
            time_statistics[column] = df_filtered_exercise[column].agg(["idxmin", "idxmax"])
        time_statistics["Set Time"] = avg_set_time_per_date.agg(["idxmin", "idxmax"])
        time_statistics = pd.DataFrame(time_statistics)

        return (
            *tuple(number_statistics.loc["min"]),
            *tuple(number_statistics.loc["max"]),
            *tuple(number_statistics.loc["median"]),
            *tuple(time_statistics.loc["idxmin"]),
            *tuple(time_statistics.loc["idxmax"]),
        )

    def calculate_avg_set_time(df: pd.DataFrame) -> pd.Series:
        """Calculate the average time between sets for each date."""
        # TODO: Logic Flaw - this is not the rest time, but the rest time + exercise time
        stats_per_date = df.groupby(df.index.date)["Time"].agg(["min", "max", "count"])
        time_difference = (stats_per_date["max"] - stats_per_date["min"]).dt.total_seconds()
        # Remove days with zero rest time, either due to only one set that day or data added after training
        stats_per_date = stats_per_date[time_difference > 0]
        avg_set_time_per_date = time_difference / stats_per_date["count"]
        return round(avg_set_time_per_date)

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
    def graph_by_exercise(exercise: str, date_range: None | list[str], show_only_comment_sets: bool):
        """Different exercise specific plots over time. Such as weight, volume or 1rm."""
        df_filtered_exercise = filter_exercise_data(df, exercise, date_range, show_only_comment_sets)

        if df_filtered_exercise.empty:
            empty_message = plot_placeholder(exercise)
            return (empty_message,) * 5

        figure_weight = plot_weight_bubbles(df_filtered_exercise)
        figure_1rm = plot_one_rm(df_filtered_exercise)
        figure_volume = plot_volume(df_filtered_exercise)

        # Plot - Most trained day and time
        figure_time_heatmap, figure_weekday = plots_time_things(df_filtered_exercise)
        # TODO: Change Hoverup text (remove variable=0)

        return (
            figure_weight,
            figure_volume,
            figure_1rm,
            figure_time_heatmap,
            figure_weekday,
        )

    def plot_weight_bubbles(df: pd.DataFrame) -> go.Figure():
        """Plot of weight over time. Different colors for different repetitions.
        Bubble size represents volume."""
        # Limit max color scale value to not dilute the colors
        if df["Repetitions"].max() > 12:
            color_scale_range = [df["Repetitions"].min(), 12]
        else:
            color_scale_range = [
                df["Repetitions"].min(),
                df["Repetitions"].max(),
            ]

        # Plot - Weight over time
        figure_weight = px.scatter(
            df,
            x="Time",
            y="Weight",
            color="Repetitions",
            range_color=color_scale_range,
            size="Volume",
            title="Weight Progression",
        )
        figure_weight.update_layout(yaxis_title="Weight [kg]")
        # Hoverup text
        figure_weight.update(
            data=[
                {
                    "customdata": df["Set Comment"],
                    "hovertemplate": "Time: %{x}<br>Weight: %{y} kg<br>Repetitions: %{marker.color}<br>Volume: %{marker.size} kg<br>Set Comment: %{customdata}",
                }
            ]
        )

        return figure_weight

    def plot_one_rm(df: pd.DataFrame, max_reps: int = 5) -> go.Figure():
        """Plot predicting 1RM over time."""
        # 1RM calculation is only reliable up to about 5 reps
        df_reliable = df[df["Repetitions"] <= max_reps]
        # 1RM for more than 20 reps is not reliable at all - ignore
        df_unreliable = df[(df["Repetitions"] > max_reps) & (df["Repetitions"] < 20)]
        one_rm = df_reliable["Weight"] / (1.0278 - (0.0278) * df_reliable["Repetitions"])
        one_rm_unreliable = df_unreliable["Weight"] / (1.0278 - (0.0278) * df_unreliable["Repetitions"])
        figure_1rm = px.scatter(
            df_reliable,
            x="Time",
            y=one_rm,
            color="Repetitions",
            title="Estimated 1RM (only accurate up to 5 reps)",
        )
        figure_1rm.update(
            data=[
                {
                    "hovertemplate": "Time: %{x}<br>Weight: %{y:.2f} kg<br>Repetitions: %{marker.color}",
                }
            ]
        )
        figure_1rm.add_trace(
            go.Scatter(
                x=df_unreliable["Time"],
                y=one_rm_unreliable,
                mode="markers",
                # Make markers diamonds
                marker={"symbol": "diamond", "size": 5, "color": "gray"},
                # Add hoverup data with info about repetitions and weight
                hovertemplate="Time: %{x}<br>Weight: %{y:.2f} kg<br>Repetitions:%{text}",
                text=df_unreliable["Repetitions"],
            )
        )
        # Do not show legend for the two traces
        figure_1rm.update_layout(showlegend=False, yaxis_title="Weight [kg]")
        return figure_1rm

    def plot_volume(df: pd.DataFrame) -> go.Figure():
        """Plot training volume per day over time."""
        grouped_by_date = df.groupby(df.index.date)
        volume = grouped_by_date.apply(lambda x: (x["Repetitions"] * x["Weight"]).sum())
        n_sets = grouped_by_date["Set Order"].count()
        n_reps = grouped_by_date["Repetitions"].sum()
        avg_weight = grouped_by_date["Weight"].median()

        figure_volume = px.scatter(
            x=volume.index,
            y=volume,
            color=n_sets,
            title="Training volume per day",
        )
        figure_volume.update_yaxes(tickformat=",")
        figure_volume.update_layout(
            xaxis_title="Time",
            yaxis_title="Volume [kg]",
            separators="* .*",
            coloraxis_colorbar_title_text="Sets",
        )
        figure_volume.update(
            data=[
                {
                    "customdata": np.stack((n_reps, avg_weight), axis=1),
                    "hovertemplate": "Time: %{x}<br>Volume: %{y} kg<br>Repetitions: %{customdata[0]}<br>Average weight: %{customdata[1]} kg",
                }
            ]
        )
        return figure_volume

    def plots_time_things(
        df_filtered_exercise: pd.DataFrame,
    ) -> tuple[go.Figure, go.Figure]:
        """Plot time heatmap and favorite training day."""
        weekday_map = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
        }

        figure_time_heatmap = plot_frequent_time(df_filtered_exercise, weekday_map)
        figure_weekday = plot_frequent_day(df_filtered_exercise, weekday_map)
        return figure_time_heatmap, figure_weekday

    def plot_frequent_day(df: pd.DataFrame, weekday_map: dict[int, str]) -> go.Figure():
        """Plot favorite training day.
        Days where at least one set of the exercise was performed count as training day.
        """
        grouped_by_date = df.groupby(df.index.date)
        # Sum training days per day
        weekdays = pd.Categorical(
            grouped_by_date["Weekday"].first(),
            categories=list(weekday_map.values()),
        )
        figure_weekday = px.histogram(weekdays.sort_values(), title="Training Days")
        figure_weekday.update_layout(xaxis_title="Weekday", yaxis_title="Training Days", showlegend=False)
        return figure_weekday

    def plot_frequent_time(df: pd.DataFrame, weekday_map: dict[int, str]) -> go.Figure():
        """Plot favorite training time.
        Each performed set in a 1 hour block increases the counter."""
        figure_time_heatmap = px.density_heatmap(
            df,
            x="Weekday",
            y=df.index.hour,
            category_orders={"Weekday": list(weekday_map.values())},
            title="Favorite Set Time",
        )
        figure_time_heatmap.update_layout(yaxis_title="Hour")
        # Reverse the y-axis order
        figure_time_heatmap.update_yaxes(autorange="reversed")
        figure_time_heatmap.update(
            data=[
                {
                    "hovertemplate": "Weekday: %{x}<br>Hour: %{y}<br>Performed sets: %{z}",
                }
            ]
        )
        return figure_time_heatmap
