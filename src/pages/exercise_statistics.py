from typing import Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
import vizro.plotly.express as px
from dash import Input, Output, callback
from vizro.models.types import capture

from components.modified_components import kpi_card, kpi_card_reference
from exercise_compendium import create_exercise_library

exercises = create_exercise_library()
default_exercise = "Barbell Squat"
default_period = "monthly"


weekday_map = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}

# Add components to the controls sidebar, to be able to use them there
vm.Page.add_type("controls", vm.Dropdown)
vm.Page.add_type("controls", vm.RadioItems)


def get_exercise_statistic_page(df_fitness: pd.DataFrame) -> vm.Page:
    @callback(
        Output("exercise-info-card", "children"),
        Input("dropdown-exercise", "value"),
    )
    def update_exercise_info_card(exercise_name: str) -> str:
        """Generate exercise information card with statistics."""
        exercise = exercises.get_exercise(exercise_name)
        similar_exercises = exercises.get_similar_exercises(exercise)
        df_by_exercise = df_fitness[df_fitness["Exercise Name"] == exercise.name]
        n_repetitions = df_by_exercise["Repetitions"].sum()
        n_sets = df_by_exercise["Set Order"].count()
        total_weight = df_by_exercise["Weight [kg]"].sum()
        total_weight = f"{total_weight:.1f} kg" if total_weight < 1000 else f"{total_weight / 1000:.2f} t"

        # exercise_info_and_stats = f"""
        exercise_info_and_stats = f"""### {exercise.name}
                {exercise.description}         
* * *           
Lifetime Statistics: **Sets:** {n_sets:,} | **Repetitions:** {n_repetitions:,} | **Total Weight:** {total_weight}"""

        return exercise_info_and_stats

    @callback(
        Output("graph-exercise-progression", "figure", allow_duplicate=True),
        Input("switch-show-variations", "value"),
        Input("dropdown-exercise", "value"),
        Input("range-slider-repetitions", "value"),
        prevent_initial_call=True,
    )
    def update_graph_exercise_progression(show_variations: bool, exercise_name: str, _):
        if show_variations:
            similar_exercises = exercises.get_similar_exercises(exercise_name)
            similar_exercise_names = [exercise.name for exercise in similar_exercises]
        else:
            similar_exercise_names = [exercise_name]
        fig = plot_weight_progression(df_fitness, similar_exercises=similar_exercise_names)
        return fig

    @callback(
        Output("graph-exercise-volume", "figure", allow_duplicate=True),
        Output("graph-exercise-1rm", "figure", allow_duplicate=True),
        Input("dropdown-period", "value"),
        Input("dropdown-exercise", "value"),
        prevent_initial_call=True,
    )
    def update_graph_exercise_1rm(period: str, exercise: str):
        fig_volume = plot_volume(df_fitness, exercise, period)
        fig_one_rm = plot_one_rm(df_fitness, exercise, period)
        return fig_volume, fig_one_rm

    @capture("graph")
    def plot_weight_progression(
        data_frame: pd.DataFrame, similar_exercises: Optional[list[str]] = None, **kwargs
    ) -> go.Figure:
        """Plot weight per set as a bubble chart, with time as x-axis, weight as y-axis, repetitions as color and volume as size.

        The method is affected by the following sidebar controls:
        - exercise (Filter): The name of the exercise
        - Filter by repetitions (Filter): Range slider for the number of repetitions
        - Show Variations (Parameter): Boolean Switch, if true, also plot variations of the selected exercise
        """
        # Number of repetitions, up to which the color scale will generate new colors
        MAX_REPETITIONS = 12

        # Also show similar exercises if the switch is set (additional to the selected exercise)
        if similar_exercises:
            data_frame = data_frame.loc[data_frame["Exercise Name"].isin(similar_exercises)]

        # Limit max color scale value to not dilute the colors
        min_reps = data_frame["Repetitions"].min()
        max_reps = min(data_frame["Repetitions"].max(), MAX_REPETITIONS)
        color_scale_range = [min_reps, max_reps]

        fig = px.scatter(
            data_frame,
            x=data_frame.index,
            y="Weight [kg]",
            color="Repetitions",
            range_color=color_scale_range,
            color_continuous_scale="plasma",
            size="Volume",
            symbol="Exercise Name",
            **kwargs,
        )
        fig.update_layout(xaxis_title=None, yaxis_title="Weight")
        fig.update_yaxes(ticksuffix=" kg")

        hover_data = {
            "customdata": data_frame["Set Comment"],
            "hovertemplate": (
                "Date: %{x}<br>"
                "Weight: %{y}<br>"
                "Repetitions: %{marker.color}<br>"
                "Volume: %{marker.size} kg<br>"
                "Set Comment: %{customdata}"
            ),
        }
        fig.update(data=[hover_data])

        # Show legend if more than one exercise is displayed
        legend_config = (
            {"showlegend": False}
            if len(data_frame["Exercise Name"].unique()) == 1
            else {"legend": dict(orientation="h")}
        )
        fig.update_layout(**legend_config)
        return fig

    @capture("graph")
    def plot_one_rm(
        data_frame: pd.DataFrame, exercise: str = None, period: str = default_period, rolling_avg_window_size: int = 90
    ):
        """Plot 1RM trend as line chart, with time as x-axis and 1RM as y-axis.
        Only the max 1RM for each period is shown.

        The method is affected by the following sidebar controls:
        - exercise (Filter): The name of the exercise
        - period (Parameter): Time frame for grouping the data (weekly, monthly or yearly, default: monthly)
        """
        # Number of repetitions, up to which the 1RM formula will be applied
        RELIABLE_REPETITIONS = 7
        # Filter data for the specific exercise
        if data_frame["Exercise Name"].nunique() > 1:
            data_frame = data_frame[data_frame["Exercise Name"] == exercise]

        # Remove sets with too many repetitions (not reliable for the 1RM calculation)
        exercise_data = data_frame.copy()
        exercise_data = exercise_data[exercise_data["Repetitions"] <= RELIABLE_REPETITIONS]

        # Set up period grouper
        if period == "weekly":
            rolling_avg_window_size = 7 * 5
            exercise_data["period"] = exercise_data.index.to_period("W").start_time
        elif period == "monthly":
            rolling_avg_window_size = 30 * 5
            exercise_data["period"] = exercise_data.index.to_period("M").start_time
        elif period == "yearly":
            rolling_avg_window_size = 365
            exercise_data["period"] = exercise_data.index.to_period("Y").start_time

        # Reset index, to make sure to only get entry for each period, because it could be that two sets have the same timestamp
        original_index = exercise_data.index
        exercise_data = exercise_data.reset_index()
        # Filter by period - only the max 1RM for each period is extracted
        max_indices = exercise_data.groupby("period")["1RM"].idxmax().values
        exercise_data = exercise_data.loc[max_indices]
        exercise_data.index = original_index[exercise_data.index]

        # Smooth 1RM by using a peak moving average
        peak_moving_avg = exercise_data["1RM"].rolling(window=f"{rolling_avg_window_size}D", min_periods=1).max()

        fig = go.Figure()
        # Add estimated 1RM data points
        fig.add_trace(
            go.Scatter(
                # x=exercise_data["period"],
                x=exercise_data.index,
                y=exercise_data["1RM"],
                mode="markers",
                name="1RM (≤5 reps)",
                line=dict(color="#636EFB"),
                hovertemplate="Date: %{x}<br>1RM: %{y:.2f} kg<br>Attempt: %{customdata[0]} kg x %{customdata[1]}",
                customdata=exercise_data[["Weight [kg]", "Repetitions"]],
            )
        )
        # Add peak moving average
        fig.add_trace(
            go.Scatter(
                x=peak_moving_avg.index,
                y=peak_moving_avg,
                mode="lines",
                name=f"{rolling_avg_window_size}-day Peak Moving Average",
                line=dict(color="#6544CA", dash="dashdot", width=3),
            )
        )
        fig.update_layout(
            yaxis_title="Estimated 1RM",
            legend_title="Legend",
            legend=dict(yanchor="top", y=0.1, xanchor="right", x=0.99),
        )
        fig.update_yaxes(ticksuffix=" kg")
        fig.update_layout(
            xaxis=dict(showgrid=True, gridcolor="rgba(255, 255, 255, 0.01)"),  # Subtle vertical grid lines
            yaxis=dict(showgrid=True, gridcolor="rgba(255, 255, 255, 0.05)"),  # Subtle horizontal grid lines
        )
        return fig

    @capture("graph")
    def plot_volume(
        data_frame: pd.DataFrame, exercise: str = None, period: str = default_period, **kwargs
    ) -> go.Figure:
        """Plot training volume per time frame (period) as area chart, with time as x-axis and volume as y-axis.

        The method is affected by the following sidebar controls:
        - exercise (Filter): The name of the exercise
        - period (Parameter): Time frame for grouping the data (weekly, monthly or yearly, default: monthly)
        """
        if data_frame["Exercise Name"].nunique() > 1:
            data_frame = data_frame[data_frame["Exercise Name"] == exercise]

        if period == "weekly":
            grouped_by_time_frame = data_frame.groupby(data_frame.index.strftime("%Y-%W"), observed=True)
        elif period == "monthly":
            grouped_by_time_frame = data_frame.groupby(data_frame.index.strftime("%Y-%m"), observed=True)
        elif period == "yearly":
            grouped_by_time_frame = data_frame.groupby(data_frame.index.strftime("%Y"), observed=True)

        # Volume = Repetitions * Weight
        volume = grouped_by_time_frame.apply(lambda x: (x["Repetitions"] * x["Weight [kg]"]).sum())
        n_sets = grouped_by_time_frame["Set Order"].count()
        n_reps = grouped_by_time_frame["Repetitions"].sum()
        avg_weight = grouped_by_time_frame["Weight [kg]"].median()

        # TODO: Find root cause of this error, for now catch it
        try:
            plot_data = pd.DataFrame(
                {"Volume": volume, "Sets": n_sets, "Repetitions": n_reps, "Average Weight": avg_weight}
            )
        except ValueError:
            return go.Figure()

        fig = px.area(plot_data, x=plot_data.index, y="Volume", template="plotly_dark", **kwargs)
        fig.update_layout(xaxis_title=None, yaxis_title="Volume [kg]")
        hover_data = {
            "customdata": np.stack((n_sets, n_reps, avg_weight), axis=1),
            "hovertemplate": (
                "Date: %{x}<br>"
                "Volume: %{y} kg<br>"
                "Sets: %{customdata[0]}<br>"
                "Repetitions: %{customdata[1]}<br>"
                "Average weight: %{customdata[2]} kg"
            ),
        }
        fig.update(data=[hover_data])
        return fig

    @capture("graph")
    def plot_frequent_day(data_frame: pd.DataFrame) -> go.Figure:
        """Plot favorite training day using a histogram, with weekday as x-axis and number of training days as y-axis.
        Days where at least one set of the exercise was performed counts as training day.

        The method is affected by the following sidebar controls:
        - exercise (Filter): The name of the exercise
        """
        grouped_by_date = data_frame.groupby(data_frame.index.date, observed=True)
        # Sum training days per day
        weekday_counts = pd.Categorical(
            grouped_by_date["Weekday"].first(), categories=list(weekday_map.values())
        ).sort_values()

        fig = px.histogram(weekday_counts, template="plotly_dark")
        fig.update_layout(xaxis_title=None, yaxis_title="Number of training days", showlegend=False)
        fig.update(data=[{"hovertemplate": "Weekday: %{x}<br>Number of days trained: %{y}"}])
        return fig

    @capture("graph")
    def plot_frequent_time(data_frame: pd.DataFrame) -> go.Figure:
        """Plot favorite training time using a heatmap, with weekday as x-axis and hour as y-axis and number of sets as z-axis.
        Each performed set inside a 1 hour block increases the counter.

        The method is affected by the following sidebar controls:
        - exercise (Filter): The name of the exercise
        """
        # TODO: Fix hour cell size issue for low set exercises
        fig = px.density_heatmap(
            data_frame,
            x="Weekday",
            y=data_frame.index.hour,
            category_orders={"Weekday": list(weekday_map.values())},
            template="plotly_dark",
        )
        fig.update_layout(xaxis_title=None, yaxis_title="Hour of Day", coloraxis_colorbar={"title": "Sets"})
        # Reverse the y-axis order
        fig.update_yaxes(autorange="reversed", tickmode="linear", tick0=0, dtick=1, tickformat="%H:00")
        # fig.update_yaxes(autorange="reversed")
        fig.update(data=[{"hovertemplate": "Weekday: %{x}<br>Hour: %{y}:00 - %{y}:59<br>Number of Sets: %{z}"}])
        return fig

    def compare_exercise_metric_periods(
        df: pd.DataFrame, column: str, agg_func: str, today, days: int = 30
    ) -> pd.Series:
        """Calculate progression for a given exercise over specified days."""
        reference_period = (df.index <= today - pd.Timedelta(days=days)) & (
            df.index > today - pd.Timedelta(days=days * 2)
        )
        current_period = df.index > today - pd.Timedelta(days=days)

        return pd.Series(
            {
                "reference": getattr(df.loc[reference_period, column], agg_func)(),
                "value": getattr(df.loc[current_period, column], agg_func)(),
            }
        )

    def calculate_exercise_metrics_over_time(
        df: pd.DataFrame, column: str, agg_func: str, days: int = 30
    ) -> pd.DataFrame:
        """Apply progression calculation to all exercises in the dataframe."""
        today = df.index.max()
        return (
            df.groupby("Exercise Name", observed=True)
            .apply(lambda x: compare_exercise_metric_periods(x, column, agg_func, today, days))
            .reset_index()
            .rename(columns={"level_1": "metric"})
        )

    volume_data = calculate_exercise_metrics_over_time(df_fitness, column="Volume", agg_func="sum")
    weight_data = calculate_exercise_metrics_over_time(df_fitness, column="Weight [kg]", agg_func="mean")

    page = vm.Page(
        title="Exercise Statistics",
        layout=vm.Layout(
            grid=[
                [0, 0, 0, 1, 2, 3],  # Exercise info, 3 stat cards
                [4, 4, 4, 4, 4, 4],  # Weight progression graph
                [4, 4, 4, 4, 4, 4],
                [4, 4, 4, 4, 4, 4],
                [5, 5, 5, 5, 5, 5],  # Other plots in Tabs
                [5, 5, 5, 5, 5, 5],
                [5, 5, 5, 5, 5, 5],
            ],
            row_min_height="170px",
        ),
        components=[
            vm.Card(id="exercise-info-card", text="Placeholder"),
            vm.Figure(
                figure=kpi_card(
                    df_fitness,
                    "Weight [kg]",
                    value_format="{value:,.0f} kg",
                    agg_func="max",
                    title="Personal Best",
                    icon="trophy",
                )
            ),
            vm.Figure(
                figure=kpi_card_reference(
                    data_frame=weight_data,
                    value_column="value",
                    reference_column="reference",
                    value_format="{value:,.0f} kg",  # Format as integer with comma separators
                    reference_format="{delta_relative:+.1%} vs. previous 30 days ({reference:,.0f} kg)",
                    icon="fitness_center",
                    title="Avg Weight",
                ),
            ),
            vm.Figure(
                figure=kpi_card_reference(
                    data_frame=volume_data,
                    value_column="value",
                    reference_column="reference",
                    value_format="{formatted_value}",  # Format as integer with comma separators
                    reference_format="{delta_relative:+.1%} vs. previous 30 days ({formatted_reference})",
                    icon="show_chart",
                    title="Avg Volume",
                ),
            ),
            vm.Graph(
                id="graph-exercise-progression",
                figure=plot_weight_progression(df_fitness),
                title="Weight progression",
                header="""
                Visualizes weight progression over time for the selected exercise.
                Bubbles represent training sets, with color showing repetitions and size reflecting volume.
                Filter by rep range and view similar exercises in the sidebar for a comprehensive strength development overview.""",
            ),
            vm.Tabs(
                tabs=[
                    vm.Container(
                        title="Strength",
                        components=[
                            vm.Graph(
                                id="graph-exercise-1rm",
                                figure=plot_one_rm(df_fitness, default_exercise),
                                title="Estimated One-Rep Max (1RM)",
                                header="""
                                Tracks estimated One-Rep Max (1RM) over time for the chosen exercise, showing individual data points and a peak moving average trend.
                                Excludes sets with more than 7 reps for accuracy.
                                Adjust data grouping period in the sidebar to customize strength progression views.""",
                            ),
                        ],
                    ),
                    vm.Container(
                        title="Volume",
                        components=[
                            vm.Graph(
                                id="graph-exercise-volume",
                                figure=plot_volume(df_fitness, default_exercise),
                                title="Training Volume over Time",
                                header="""
                                Illustrates training volume fluctuations over time for the selected exercise, providing insights into workout intensity and consistency.
                                Volume calculated as weight multiplied by repetitions.
                                Adjust time period grouping in the sidebar to analyze volume trends across different timescales.""",
                            ),
                        ],
                    ),
                    vm.Container(
                        title="Favorite Training Day",
                        components=[
                            vm.Graph(
                                id="graph-exercise-favorite-day",
                                figure=plot_frequent_day(df_fitness),
                                title="Frequency of Exercise Performance by Weekday",
                                header="""
                                Highlights weekly training patterns for the selected exercise by showing performance frequency across weekdays.
                                Each day with at least one set counts as a training day.""",
                            ),
                        ],
                    ),
                    vm.Container(
                        title="Favorite Training Time",
                        components=[
                            vm.Graph(
                                id="graph-exercise-favorite-time",
                                figure=plot_frequent_time(df_fitness),
                                title="Training Hours",
                                header="""
                                Reveals preferred training times for the selected exercise through workout hour distribution across the week.
                                Color intensity represents sets performed at each hour.""",
                            )
                        ],
                    ),
                ]
            ),
        ],
        controls=[
            vm.Filter(
                column="Exercise Name",
                selector=vm.Dropdown(
                    id="dropdown-exercise", value=default_exercise, multi=False, title="Select Exercise"
                ),
            ),
            vm.Filter(
                column="Repetitions",
                targets=["graph-exercise-progression"],
                selector=vm.RangeSlider(
                    id="range-slider-repetitions",
                    title="Filter by repetitions",
                    min=1,
                    max=50,
                    step=1,
                    marks={1: "1", 5: "5", 12: "12"},
                ),
            ),
            vm.RadioItems(
                id="switch-show-variations",
                options=[{"label": "Exercise only", "value": False}, {"label": "Show variations", "value": True}],
                title="Show variations",
            ),
            vm.RadioItems(
                id="dropdown-period",
                options=["weekly", "monthly", "yearly"],
                value=default_period,
                title="Time Period (affects Strength & Volume)",
            ),
        ],
    )

    return page
