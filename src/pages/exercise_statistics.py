import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import vizro.models as vm
import vizro.plotly.express as px
from dash import Input, Output, State, callback, html
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


def create_stats_cards(n_sets, n_repetitions, n_weight, n_rest):
    # Format weight
    if isinstance(n_weight, (int, float)) and n_weight > 1000:
        weight_display = f"{round(n_weight / 1000, 1)} ton"
    else:
        weight_display = f"{n_weight} kg"

    stats_cards = dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H4("Lifetime Statistics", className="text-center mb-4"),
                                    dbc.Row(
                                        [
                                            # Sets Card
                                            dbc.Col(
                                                [
                                                    dbc.Card(
                                                        [
                                                            dbc.CardBody(
                                                                [
                                                                    html.I(className="fas fa-layer-group mb-2"),
                                                                    html.H6(
                                                                        "Total Sets",
                                                                        className="card-subtitle text-muted",
                                                                    ),
                                                                    html.H3(f"{n_sets}", className="mt-2"),
                                                                ],
                                                                className="text-center",
                                                            )
                                                        ],
                                                        className="h-100",
                                                    )
                                                ],
                                                width=6,
                                                lg=3,
                                                className="mb-3",
                                            ),
                                            # Repetitions Card
                                            dbc.Col(
                                                [
                                                    dbc.Card(
                                                        [
                                                            dbc.CardBody(
                                                                [
                                                                    html.I(className="fas fa-redo mb-2"),
                                                                    html.H6(
                                                                        "Total Repetitions",
                                                                        className="card-subtitle text-muted",
                                                                    ),
                                                                    html.H3(f"{n_repetitions}", className="mt-2"),
                                                                ],
                                                                className="text-center",
                                                            )
                                                        ],
                                                        className="h-100",
                                                    )
                                                ],
                                                width=6,
                                                lg=3,
                                                className="mb-3",
                                            ),
                                            # Weight Card
                                            dbc.Col(
                                                [
                                                    dbc.Card(
                                                        [
                                                            dbc.CardBody(
                                                                [
                                                                    html.I(className="fas fa-dumbbell mb-2"),
                                                                    html.H6(
                                                                        "Total Weight",
                                                                        className="card-subtitle text-muted",
                                                                    ),
                                                                    html.H3(weight_display, className="mt-2"),
                                                                ],
                                                                className="text-center",
                                                            )
                                                        ],
                                                        className="h-100",
                                                    )
                                                ],
                                                width=6,
                                                lg=3,
                                                className="mb-3",
                                            ),
                                            # Rest Time Card
                                            dbc.Col(
                                                [
                                                    dbc.Card(
                                                        [
                                                            dbc.CardBody(
                                                                [
                                                                    html.I(className="fas fa-clock mb-2"),
                                                                    html.H6(
                                                                        "Total Rest Time",
                                                                        className="card-subtitle text-muted",
                                                                    ),
                                                                    html.H3(f"{n_rest}", className="mt-2"),
                                                                ],
                                                                className="text-center",
                                                            )
                                                        ],
                                                        className="h-100",
                                                    )
                                                ],
                                                width=6,
                                                lg=3,
                                                className="mb-3",
                                            ),
                                        ]
                                    ),
                                ]
                            )
                        ],
                        className="shadow",
                    )
                ]
            )
        ]
    )

    return stats_cards


def get_exercise_statistic_page(df_fitness: pd.DataFrame) -> vm.Page:
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
        Output("exercise-info-card", "children"),
        Output("card-exercise-info-weight", "children"),
        Output("card-exercise-info-all-time", "children"),
        Input("dropdown-exercise", "value"),
    )
    def update_exercise_info_card(exercise_name: str):
        exercise = exercises.get_exercise(exercise_name)
        similar_exercises = exercises.get_similar_exercises(exercise)

        text = f"""### {exercise.name}
        {exercise.description}
        """

        df_by_exercise = df_fitness[df_fitness["Exercise Name"] == exercise.name]
        max_weight = round(df_by_exercise["Weight [kg]"].max() / 2.5) * 2.5
        mean_weight = round(df_by_exercise["Weight [kg]"].mean() / 2.5) * 2.5
        mean_sets = round(df_by_exercise["Repetitions"].mean())
        # mean_rest = df_by_exercise["Set Time"].mean()
        mean_rest = "test"
        card_stats = f"""
        ### Weight Statistics

        **Max. Weight:** **{max_weight} kg**
        Mean. Weight: {mean_weight} kg
        Mean. Sets: {mean_sets}
        Mean. Rest Time: {mean_rest}
        """

        # all time stats
        n_repetitions = df_by_exercise["Repetitions"].sum()
        n_sets = df_by_exercise["Set Order"].count()
        n_weight = round(df_by_exercise["Weight [kg]"].sum() / 2.5) * 2.5
        # if n_weight is more than 1000 kg, display ton instead of kg
        if n_weight > 1000:
            n_weight = round(n_weight / 1000)
            n_weight = f"{n_weight} ton"
        else:
            n_weight = f"{n_weight} kg"
        # n_rest = df_by_exercise["Set Time"].sum()
        n_rest = "test"
        time_stats = f"""
        ### Total Statistics
        
        {n_sets} sets with a total of {n_repetitions} repetitions were performed.
        This amounts to **{n_weight} kg** moved weight in total.
        """

        return text, card_stats, time_stats

    @callback(
        Output("graph-exercise-volume", "figure", allow_duplicate=True),
        Output("graph-exercise-1rm", "figure", allow_duplicate=True),
        Input("dropdown-period", "value"),
        State("dropdown-exercise", "value"),
        prevent_initial_call=True,
    )
    def update_graph_exercise_1rm(period: str, exercise: str):
        fig_volume = plot_volume(df_fitness, period, exercise=exercise)
        fig_one_rm = plot_one_rm(df_fitness, period, exercise=exercise)
        return fig_volume, fig_one_rm

    @capture("graph")
    def plot_weight_bubbles(data_frame: pd.DataFrame, similar_exercises: list[str] = None, **kwargs) -> go.Figure:
        """Plot of weight over time. Different colors for different repetitions.
        Bubble size represents volume.
        """
        # data_frame = data_frame[data_frame["Exercise Name"] == exercise]
        if similar_exercises is not None:
            data_frame = data_frame[data_frame["Exercise Name"].isin(similar_exercises)]
        # Limit max color scale value to not dilute the colors
        if data_frame["Repetitions"].max() > 12:
            color_scale_range = [data_frame["Repetitions"].min(), 12]
        else:
            color_scale_range = [data_frame["Repetitions"].min(), data_frame["Repetitions"].max()]

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

        # Hoverup text
        figure_weight.update(
            data=[
                {
                    "customdata": data_frame["Set Comment"],
                    "hovertemplate": "Time: %{x}<br>Weight: %{y} kg<br>Repetitions: %{marker.color}<br>Volume: %{marker.size} kg<br>Set Comment: %{customdata}",
                }
            ]
        )

        # Move legend to bottom left corner and conditionally display
        if len(data_frame["Exercise Name"].unique()) > 2:
            figure_weight.update_layout(legend=dict(orientation="h"))
        else:
            figure_weight.update_layout(showlegend=False)

        return figure_weight

    @capture("graph")
    def plot_one_rm(
        data_frame: pd.DataFrame, period: str = "monthly", exercise: str = None, max_reps: int = 5
    ) -> go.Figure:
        """Plot estimated 1RM over time."""
        if exercise is not None:
            data_frame = data_frame[data_frame["Exercise Name"] == exercise]

        # 1RM calculation is only reliable up to about 5 reps - separate intto two dataFrames to distinguish
        df_reliable = data_frame[data_frame["Repetitions"] <= max_reps].copy()
        # 1RM for more than 20 reps is not reliable at all - ignore
        df_unreliable = data_frame[(data_frame["Repetitions"] > max_reps) & (data_frame["Repetitions"] < 20)].copy()

        df_reliable["1RM"] = df_reliable["Weight [kg]"] / (1.0278 - (0.0278) * df_reliable["Repetitions"])
        df_unreliable["1RM"] = df_unreliable["Weight [kg]"] / (1.0278 - (0.0278) * df_unreliable["Repetitions"])

        if period == "daily":
            pass
        # If a period is provided, group sets by that period
        else:
            if period == "monthly":
                date_format = "%Y-%m"
            elif period == "yearly":
                date_format = "%Y"

            df_reliable = (
                df_reliable.groupby(df_reliable.index.strftime(date_format))
                .agg(
                    {
                        "1RM": "max",
                        "Weight [kg]": "first",  # Keep original weight for hover data
                        "Repetitions": "first",  # Keep reps for hover data
                    }
                )
                .reset_index()
            )
            df_unreliable = (
                df_unreliable.groupby(df_unreliable.index.strftime(date_format))
                .agg({"1RM": "max", "Weight [kg]": "first", "Repetitions": "first"})
                .reset_index()
            )

        figure_1rm = px.scatter(df_reliable, x=df_reliable.index, y="1RM", color="Repetitions", template="plotly_dark")
        figure_1rm.update(
            data=[
                {
                    "customdata": df_reliable["Weight [kg]"],
                    "hovertemplate": "Time: %{x}<br>Weight: %{y:.2f} kg<br>Attempt: %{customdata} kg x %{marker.color}",
                }
            ]
        )
        figure_1rm.add_trace(
            go.Scatter(
                x=df_unreliable.index,
                y=df_unreliable["1RM"],
                mode="markers",
                # Make markers diamonds
                marker={"symbol": "diamond", "size": 5, "color": "gray"},
                # Add hoverup data with info about repetitions and weight
                hovertemplate="Time: %{x}<br>Weight: %{y:.2f} kg<br>Attempt: %{customdata[0]} kg x %{customdata[1]}",
                customdata=list(zip(df_unreliable["Weight [kg]"], df_unreliable["Repetitions"])),
                name="",
            )
        )
        # Do not show legend for the two traces
        figure_1rm.update_layout(showlegend=False, yaxis_title="Weight [kg]")
        return figure_1rm

    @capture("graph")
    def plot_volume(data_frame: pd.DataFrame, period: str = "monthly", exercise=None, **kwargs) -> go.Figure:
        """Plot training volume per day over time."""
        if exercise is not None:
            data_frame = data_frame[data_frame["Exercise Name"] == exercise]

        if period == "daily":
            grouped_by_time_frame = data_frame.groupby(data_frame.index.date, observed=True)
        elif period == "weekly":
            grouped_by_time_frame = data_frame.groupby(data_frame.index.strftime("%Y-%W"))
        elif period == "monthly":
            grouped_by_time_frame = data_frame.groupby(data_frame.index.strftime("%Y-%m"))
        elif period == "yearly":
            grouped_by_time_frame = data_frame.groupby(data_frame.index.strftime("%Y"))

        volume = grouped_by_time_frame.apply(lambda x: (x["Repetitions"] * x["Weight [kg]"]).sum())
        n_sets = grouped_by_time_frame["Set Order"].count()
        n_reps = grouped_by_time_frame["Repetitions"].sum()
        avg_weight = grouped_by_time_frame["Weight [kg]"].median()

        figure_volume = px.scatter(data_frame, x=volume.index, y=volume, template="plotly_dark", **kwargs)
        figure_volume.update_layout(xaxis_title="Time", yaxis_title="Volume [kg]")
        figure_volume.update(
            data=[
                {
                    "customdata": np.stack((n_reps, avg_weight, n_sets), axis=1),
                    "hovertemplate": "Time: %{x}<br>Volume: %{y} kg<br>Sets: %{customdata[2]}<br>Repetitions: %{customdata[0]}<br>Average weight: %{customdata[1]} kg",
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

    colorscales = px.colors.named_colorscales()
    first_page = vm.Page(
        title="Exercise Statistics",
        layout=vm.Layout(
            grid=[
                [0, 0, 0, 0, 1, 2],
                [3, 3, 3, 3, 3, 3],
                [3, 3, 3, 3, 3, 3],
                [4, 4, 4, 5, 5, 5],
                [4, 4, 4, 5, 5, 5],
            ],
            row_min_height="170px",
        ),
        components=[
            vm.Card(id="exercise-info-card", text="None"),
            vm.Card(id="card-exercise-info-weight", text="None"),
            vm.Card(id="card-exercise-info-all-time", text="None"),
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
                        title="Volume",
                        components=[
                            vm.Graph(
                                id="graph-exercise-volume",
                                figure=plot_volume(df_fitness),
                                title="Training Volume over Time",
                                header="What is the training volume over time?",
                            ),
                        ],
                    ),
                    vm.Container(
                        title="Strength",
                        components=[
                            vm.Graph(
                                id="graph-exercise-1rm",
                                figure=plot_one_rm(df_fitness),
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
                ]
            ),
            vm.Tabs(
                tabs=[
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
                    id="dropdown-exercise", value="Barbell Squat", multi=False, title="Select Exercise"
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
                options=["daily", "monthly", "yearly"],
                value="daily",
                title="Period (Volume & Strength)",
            ),
        ],
    )

    return first_page
