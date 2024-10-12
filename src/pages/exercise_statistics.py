from typing import Optional

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import vizro.models as vm
import vizro.plotly.express as px
from dash import Input, Output, State, callback, html
from vizro.figures import kpi_card, kpi_card_reference
from vizro.models.types import capture

from exercise_compendium import (
    Equipment,
    Exercise,
    ExerciseLibrary,
    ExerciseSearchCriteria,
    Force,
    Mechanic,
    Muscle,
    create_exercise_library,
)

exercises = create_exercise_library()
default_exercise = "Barbell Squat"
default_period = "monthly"

pio.templates.default = "plotly_dark"
weekday_map = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}


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

        exercise_info_and_stats = f"""## {exercise.name}
                {exercise.description}         
* * *           
### All Time Statistics
- **Sets:** {n_sets:,}
- **Repetitions:** {n_repetitions:,}
- **Total Weight:** {total_weight}"""

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
        fig = plot_weight_bubbles(df_fitness, similar_exercises=similar_exercise_names)
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
    def plot_weight_bubbles(
        data_frame: pd.DataFrame, similar_exercises: Optional[list[str]] = None, **kwargs
    ) -> go.Figure:
        """Plot of weight over time. Different colors for different repetitions. Bubble size represents volume."""
        # Number of repetitions, up to which the color scale will generate new colors
        MAX_REPETITIONS = 12

        if similar_exercises:
            data_frame = data_frame.loc[data_frame["Exercise Name"].isin(similar_exercises)]

        # Limit max color scale value to not dilute the colors
        min_reps = data_frame["Repetitions"].min()
        max_reps = min(data_frame["Repetitions"].max(), MAX_REPETITIONS)
        color_scale_range = [min_reps, max_reps]

        # Plot - Weight over time
        figure_weight = px.scatter(
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
        figure_weight.update_layout(xaxis_title=None)

        hover_data = {
            "customdata": data_frame["Set Comment"],
            "hovertemplate": (
                "Time: %{x}<br>"
                "Weight: %{y} kg<br>"
                "Repetitions: %{marker.color}<br>"
                "Volume: %{marker.size} kg<br>"
                "Set Comment: %{customdata}"
                "<extra></extra>"
            ),
        }
        figure_weight.update(data=[hover_data])

        # Show legend if more than one exercise is displayed
        legend_config = (
            {"showlegend": False}
            if len(data_frame["Exercise Name"].unique()) == 1
            else {"legend": dict(orientation="h")}
        )
        figure_weight.update_layout(**legend_config)

        return figure_weight

    @capture("graph")
    def plot_one_rm(
        data_frame: pd.DataFrame, exercise: str = None, period: str = default_period, initial_window: int = 90
    ):
        """Plot 1RM trend for a specific exercise over time."""
        if exercise is not None:
            data_frame = data_frame[data_frame["Exercise Name"] == exercise]

        # Filter data for the specific exercise and remove sets with more than 20 reps (unreliable for 1RM calculation)
        exercise_data = data_frame[(data_frame["Exercise Name"] == exercise) & (data_frame["Repetitions"] <= 20)].copy()

        # Set up period grouper
        if period == "weekly":
            exercise_data["period"] = exercise_data.index.to_period("W").start_time
        elif period == "monthly":
            exercise_data["period"] = exercise_data.index.to_period("M").start_time
        elif period == "yearly":
            initial_window = 500
            exercise_data["period"] = exercise_data.index.to_period("Y").start_time

        # Function to get max 1RM for each period and rep range
        def get_max_1rm(data, max_reps):
            return data[data["Repetitions"] <= max_reps].loc[
                data[data["Repetitions"] <= max_reps].groupby("period")["1RM"].idxmax()
            ]

        # Get max 1RM for ≤5 reps and >5 reps
        reliable_data = get_max_1rm(exercise_data, 7)
        less_reliable_data = get_max_1rm(exercise_data[exercise_data["Repetitions"] > 7], 20)

        # Convert period to datetime for consistent comparison
        reliable_data["period"] = pd.to_datetime(reliable_data["period"])
        less_reliable_data["period"] = pd.to_datetime(less_reliable_data["period"])

        # Create a mask for filtering less_reliable_data
        mask = ~less_reliable_data["period"].isin(reliable_data["period"])
        for period in less_reliable_data["period"]:
            if period in reliable_data["period"].values:
                reliable_1rm = reliable_data.loc[reliable_data["period"] == period, "1RM"].values[0]
                less_reliable_1rm = less_reliable_data.loc[less_reliable_data["period"] == period, "1RM"].values[0]
                mask |= (less_reliable_data["period"] == period) & (less_reliable_1rm > reliable_1rm)
        # Apply the mask to filter less_reliable_data
        less_reliable_data = less_reliable_data[mask]

        # Initial calculations
        peak_moving_avg = (
            reliable_data.set_index("period")["1RM"].rolling(window=f"{initial_window}D", min_periods=1).max()
        )

        # Create the plot
        fig = go.Figure()
        # Add reliable data points (≤5 reps)
        fig.add_trace(
            go.Scatter(
                x=reliable_data["period"],
                y=reliable_data["1RM"],
                mode="lines+markers",
                name="1RM (≤5 reps)",
                hovertemplate="Date: %{x|%Y-%m-%d}<br>1RM: %{y:.2f} kg<br>Attempt: %{customdata[0]} kg x %{customdata[1]}<extra></extra>",
                customdata=reliable_data[["Weight [kg]", "Repetitions"]],
            )
        )

        # Add peak moving average
        peak_trace = go.Scatter(
            x=peak_moving_avg.index,
            y=peak_moving_avg,
            mode="lines",
            name=f"{initial_window}-day Peak Moving Average",
            line=dict(color="red", dash="dash"),
            hovertemplate="Date: %{x|%Y-%m-%d}<br>Peak Avg 1RM: %{y:.2f} kg<extra></extra>",
        )
        fig.add_trace(peak_trace)

        fig.update_layout(
            yaxis_title="Estimated 1RM [kg]",
            legend_title="Legend",
            legend=dict(yanchor="top", y=0.1, xanchor="right", x=0.99),
        )

        return fig

    @capture("graph")
    def plot_volume(
        data_frame: pd.DataFrame, exercise: str = None, period: str = default_period, **kwargs
    ) -> go.Figure:
        """Plot training volume per time frame (period) over time."""
        if exercise is not None:
            data_frame = data_frame[data_frame["Exercise Name"] == exercise]

        if period == "weekly":
            grouped_by_time_frame = data_frame.groupby(data_frame.index.strftime("%Y-%W"), observed=True)
        elif period == "monthly":
            grouped_by_time_frame = data_frame.groupby(data_frame.index.strftime("%Y-%m"), observed=True)
        elif period == "yearly":
            grouped_by_time_frame = data_frame.groupby(data_frame.index.strftime("%Y"), observed=True)

        volume = grouped_by_time_frame.apply(lambda x: (x["Repetitions"] * x["Weight [kg]"]).sum())
        n_sets = grouped_by_time_frame["Set Order"].count()
        n_reps = grouped_by_time_frame["Repetitions"].sum()
        avg_weight = grouped_by_time_frame["Weight [kg]"].median()

        try:
            plot_data = pd.DataFrame(
                {"Volume": volume, "Sets": n_sets, "Repetitions": n_reps, "Average Weight": avg_weight}
            )
        except ValueError:
            return go.Figure()

        figure_volume = px.area(plot_data, x=plot_data.index, y="Volume", template="plotly_dark", **kwargs)
        figure_volume.update_layout(xaxis_title=None, yaxis_title="Volume [kg]")
        figure_volume.update(
            data=[
                {
                    "customdata": np.stack((n_sets, n_reps, avg_weight), axis=1),
                    "hovertemplate": "Time: %{x}<br>Volume: %{y} kg<br>Sets: %{customdata[0]}<br>Repetitions: %{customdata[1]}<br>Average weight: %{customdata[2]} kg",
                }
            ]
        )
        return figure_volume

    @capture("graph")
    def plot_frequent_day(data_frame: pd.DataFrame) -> go.Figure:
        """Plot favorite training day.
        Days where at least one set of the exercise was performed count as training day.
        """
        grouped_by_date = data_frame.groupby(data_frame.index.date, observed=True)
        # Sum training days per day
        weekdays = pd.Categorical(
            grouped_by_date["Weekday"].first(), categories=list(weekday_map.values())
        ).sort_values()

        figure_weekday = px.histogram(weekdays, template="plotly_dark")
        figure_weekday.update_layout(xaxis_title="Weekday", yaxis_title="Days", showlegend=False)
        figure_weekday.update(data=[{"hovertemplate": "Weekday: %{x}<br>Days: %{y}"}])
        return figure_weekday

    @capture("graph")
    def plot_frequent_time(data_frame: pd.DataFrame) -> go.Figure:
        """Plot favorite training time.
        Each performed set in a 1 hour block increases the counter.
        """
        figure_time_heatmap = px.density_heatmap(
            data_frame,
            x="Weekday",
            y=data_frame.index.hour,
            category_orders={"Weekday": list(weekday_map.values())},
            template="plotly_dark",
        )
        figure_time_heatmap.update_layout(yaxis_title="Hour")
        # Reverse the y-axis order
        figure_time_heatmap.update_yaxes(autorange="reversed")
        figure_time_heatmap.update(data=[{"hovertemplate": "Weekday: %{x}<br>Hour: %{y}<br>Performed sets: %{z}"}])
        figure_time_heatmap.update_layout(coloraxis_colorbar={"title": "Sets"})
        return figure_time_heatmap

    # KPI card component
    def calculate_exercise_volume_progression(df: pd.DataFrame, today, days: int = 30) -> pd.Series:
        """Calculate volume progression for a given exercise over specified days."""
        return pd.Series(
            {
                "reference": df[
                    (df.index <= today - pd.Timedelta(days=days)) & (df.index > today - pd.Timedelta(days=days * 2))
                ]["Volume"].sum(),
                "value": df[df.index > today - pd.Timedelta(days=days)]["Volume"].sum(),
            }
        )

    def apply_to_all_exercises(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
        """Apply volume progression calculation to all exercises in the dataframe."""
        today = df.index.max()
        return (
            df.groupby("Exercise Name")
            .apply(lambda x: calculate_exercise_volume_progression(x, today, days))
            .reset_index()
            .rename(columns={"level_1": "metric"})
        )

    # Assuming df_fitness is your original DataFrame
    volume_data = apply_to_all_exercises(df_fitness)

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
            row_min_height="155px",
        ),
        components=[
            vm.Card(id="exercise-info-card", text="Placeholder"),
            vm.Figure(
                figure=kpi_card(
                    df_fitness,
                    "Weight [kg]",
                    value_format="{value} kg",
                    agg_func="max",
                    title="Personal Best",
                    icon="fitness_center",
                )
            ),
            vm.Figure(
                figure=kpi_card(
                    df_fitness,
                    "Repetitions",
                    value_format="{value:,.0f}",
                    agg_func="mean",
                    title="Mean Reps",
                    icon="repeat",
                )
            ),
            vm.Figure(
                id="card-exercise-kpi",
                figure=kpi_card_reference(
                    data_frame=volume_data,
                    value_column="value",
                    reference_column="reference",
                    value_format="{value:,.0f} kg",  # Format as integer with comma separators
                    reference_format="{delta_relative:+.1%} vs. last 30 days ({reference:,.0f})",
                    icon="show_chart",
                    title="Volume",
                ),
            ),
            vm.Graph(
                id="graph-exercise-progression",
                figure=plot_weight_bubbles(df_fitness),
                title="Weight progression",
                header="""
                Each bubble in the graph represents a training set.
                The color of the bubble indicates the number of sets performed.
                The size of the bubble indicates the volume (weight times repetitions) of the set.""",
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
                                What is the estimated 1RM for each set?
                                When a period filter is applied, the max 1RM of the period is shown.
                                Note, that the formula used is only accurate up to 5 reps.
                                Estimates based on more than 5 reps are colored gray.
                                """,
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
                                header="What is the training volume over time?",
                            ),
                        ],
                    ),
                    vm.Container(
                        title="Favorite Training Day",
                        components=[
                            vm.Graph(
                                id="graph-exercise-favorite-day",
                                figure=plot_frequent_day(df_fitness),
                                title="Training Days",
                                header="On which day was this exercise performed most often?",
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
                                header="On which time of the day was this exercise performed most often (by sets)?",
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
                title="Period (Volume & Strength)",
            ),
        ],
    )

    return page
