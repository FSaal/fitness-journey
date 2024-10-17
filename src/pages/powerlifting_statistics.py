from typing import Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
from dash import Input, Output, callback
from scipy.interpolate import interp1d
from statsmodels.nonparametric.smoothers_lowess import lowess
from vizro.models.types import capture

# Constants
POWERLIFTING_EXERCISES = ["Barbell Squat", "Barbell Bench Press", "Barbell Deadlift"]
MARKER_TYPES = ["circle", "square", "diamond"]
COLORS = ["#636EFB", "#19D3F3", "#AB63FA"]
WEIGHT_CLASSES = [66, 74]


@capture("graph")
def get_powerlifting_plot(
    data_frame: pd.DataFrame, first_date: pd.Timestamp, last_date: pd.Timestamp, metric: str = "Weight [kg]"
) -> go.Figure:
    """Plot weight of the powerlifting exercises (each exercise has a different marker symbol) as scatter plot,
    with time as x-axis and weight as y-axis. The y-axis metric can be changed. A trend line is added to every exercise. Sets with 8 or more reps are colored gray.
    """
    fig = go.Figure()

    for i, exercise in enumerate(data_frame["Exercise Name"].unique()):
        exercise_data = data_frame[data_frame["Exercise Name"] == exercise]
        add_exercise_traces(fig, exercise_data, exercise, i, metric)

    update_layout(fig, first_date, last_date, metric)
    return fig


def add_exercise_traces(fig: go.Figure, exercise_data: pd.DataFrame, exercise: str, index: int, metric: str) -> None:
    """Add traces for a single exercise to the figure."""
    reliable_data = exercise_data[exercise_data["Repetitions"] < 8]
    unreliable_data = exercise_data[exercise_data["Repetitions"] >= 8]

    add_reliable_data_trace(fig, reliable_data, exercise, index, metric)
    add_trend_line_trace(fig, reliable_data, exercise, index, metric)
    add_unreliable_data_trace(fig, unreliable_data, index, metric)


def add_reliable_data_trace(fig: go.Figure, data: pd.DataFrame, exercise: str, index: int, metric: str) -> None:
    """Add trace for reliable data points."""
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data[metric],
            mode="markers",
            name=exercise,
            legendgroup=exercise,
            marker=dict(symbol=MARKER_TYPES[index], color=COLORS[index], opacity=0.6),
            customdata=data[["Repetitions", "1RM", "Bodyweight [kg]", "Relative Strength"]],
            hovertemplate=(
                "Date: %{x}<br>"
                "Weight: %{y}<br>"
                "Repetitions: %{customdata[0]}<br>"
                "1RM: %{customdata[1]:.2f} kg<br>"
                "Bodyweight: %{customdata[2]:.1f} kg<br>"
                "Relative Strength: %{customdata[3]:.0%}<extra></extra>"
            ),
        )
    )


def add_trend_line_trace(fig: go.Figure, data: pd.DataFrame, exercise: str, index: int, metric: str) -> None:
    """Add trend line trace."""
    peak_moving_avg = data[metric].rolling(window="180D").max()
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=peak_moving_avg,
            mode="lines",
            name="Smoothed Trend",
            legendgroup=exercise,
            line=dict(color=COLORS[index], dash="dash", width=3),
        )
    )


def add_unreliable_data_trace(fig: go.Figure, data: pd.DataFrame, index: int, metric: str) -> None:
    """Add trace for unreliable data points (8+ repetitions)."""
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data[metric],
            mode="markers",
            name="8+ Repetitions",
            legendgroup="unreliable",
            marker=dict(color="gray", symbol=f"{MARKER_TYPES[index]}-open", opacity=0.3),
            showlegend=index == 0,
            legendrank=10000,
            customdata=data[["Repetitions", "Bodyweight [kg]", "High Rep Relative Volume"]],
            hovertemplate=(
                "Date: %{x}<br>"
                "Weight: %{y}<br>"
                "Repetitions: %{customdata[0]}<br>"
                "Bodyweight: %{customdata[1]:.1f} kg<br>"
                "High Rep Relative Volume: %{customdata[2]:.2f}<extra></extra>"
            ),
        )
    )


def update_layout(fig: go.Figure, first_date: pd.Timestamp, last_date: pd.Timestamp, metric: str) -> None:
    """Update the layout of the figure."""
    fig.update_layout(
        xaxis_range=[first_date, last_date],
        xaxis_title=None,
        template="plotly_dark",
        showlegend=True,
    )
    if metric == "Weight [kg]":
        fig.update_layout(yaxis_title="Weight")
        fig.update_yaxes(ticksuffix=" kg")
    elif metric == "1RM":
        fig.update_layout(yaxis_title="1RM")
        fig.update_yaxes(ticksuffix=" kg")
        # limit y axis to 0 to 250 - necessary due to outliers
        fig.update_yaxes(range=[0, 250])
    elif metric == "Relative Strength":
        fig.update_layout(yaxis_title="Relative Strength")
        fig.update_yaxes(tickformat=".0%")


@capture("graph")
def get_bodyweight_figure(
    data_frame: pd.DataFrame, df_bodyweight_smoothed: pd.DataFrame, first_date: pd.Timestamp, last_date: pd.Timestamp
) -> go.Figure:
    """Plot bodyweight as scatter plot with time as x-axis and weight as y-axis. A trend line is added to the figure using LOWESS smoothing."""
    fig = go.Figure()
    add_bodyweight_traces(fig, data_frame, df_bodyweight_smoothed)
    add_weight_class_lines(fig)
    update_bodyweight_layout(fig, first_date, last_date)
    return fig


def add_bodyweight_traces(fig: go.Figure, data_frame: pd.DataFrame, df_bodyweight_smoothed: pd.DataFrame) -> None:
    """Add raw and smoothed bodyweight traces to the figure."""
    fig.add_trace(
        go.Scatter(
            x=data_frame.index,
            y=data_frame["Weight [kg]"],
            mode="markers",
            name="Bodyweight",
            marker=dict(color="#636EFB"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_bodyweight_smoothed.index,
            y=df_bodyweight_smoothed["Bodyweight [kg]"],
            mode="lines",
            name="Smoothed Trend",
            line=dict(color="#AB63FA"),
        )
    )


def add_weight_class_lines(fig: go.Figure) -> None:
    """Add horizontal lines for weight classes."""
    for weight_class in WEIGHT_CLASSES:
        fig.add_hline(
            y=weight_class,
            line_dash="dash",
            line_color="gray",
            line_width=0.5,
            annotation_text=f"{weight_class} kg Weight Class",
            annotation_position="bottom left",
        )


def update_bodyweight_layout(fig: go.Figure, first_date: pd.Timestamp, last_date: pd.Timestamp) -> None:
    """Update the layout of the bodyweight figure."""
    fig.update_layout(
        xaxis_title=None, yaxis_title="Weight", xaxis_range=[first_date, last_date], template="plotly_dark"
    )
    fig.update_yaxes(ticksuffix=" kg")


def interpolate_data(data_frame: pd.DataFrame, frac: float = 0.15) -> pd.DataFrame:
    """Interpolate bodyweight data using LOWESS smoothing."""
    data_frame = data_frame.copy()
    data_frame.index = pd.to_datetime(data_frame.index.date)
    # Remove duplicates (use first measurement), such that there is only one entry per day (necessary for interpolation)
    data_frame = data_frame.groupby(data_frame.index).first()

    # Converting datetime to int results in nanoseconds --> scale to get seconds
    time_numeric = data_frame.index.astype(int) / 1e9

    # Perform LOWESS (https://en.wikipedia.org/wiki/Local_regression) smoothing
    lowess_smoothed = lowess(data_frame["Weight [kg]"], time_numeric, frac=frac)
    interp_func = interp1d(lowess_smoothed[:, 0], lowess_smoothed[:, 1], kind="cubic", fill_value="extrapolate")

    # Generate more frequent time points for a smoother curve (one data point per day)
    daily_range = pd.date_range(start=data_frame.index.min(), end=data_frame.index.max(), freq="D")
    daily_range_numeric = daily_range.astype(int) / 1e9

    # Apply interpolation
    interpolated_weights = interp_func(daily_range_numeric)
    return pd.DataFrame({"Bodyweight [kg]": interpolated_weights}, index=daily_range)


def combine_exercise_and_bodyweight(exercise_df: pd.DataFrame, bodyweight_df: pd.DataFrame) -> pd.DataFrame:
    """Combine exercise data with interpolated bodyweight data and calculate relative strength."""
    exercise_df = exercise_df.copy()
    exercise_df["Date"] = pd.to_datetime(exercise_df.index.date)

    combined_df = pd.merge(exercise_df, bodyweight_df, left_on="Date", right_index=True, how="left")

    combined_df["Relative Strength"] = np.where(
        combined_df["Repetitions"] <= 8, combined_df["Weight [kg]"] / combined_df["Bodyweight [kg]"], np.nan
    )

    # 1RM estimate is not reliable for high rep sets --> use different strength metric
    combined_df["High Rep Relative Volume"] = np.where(
        combined_df["Repetitions"] > 8,
        (combined_df["Weight [kg]"] * combined_df["Repetitions"]) / combined_df["Bodyweight [kg]"],
        np.nan,
    )

    return combined_df.set_index(exercise_df.index)


def get_date_range(df1: pd.DataFrame, df2: pd.DataFrame) -> Tuple[pd.Timestamp, pd.Timestamp]:
    """Get the common date range for two dataframes."""
    first_date = min(df1.index.min(), df2.index.min())
    last_date = max(df1.index.max(), df2.index.max())
    return first_date, last_date


def get_powerlifting_statistic_page(df_fitness: pd.DataFrame, df_bodyweight: pd.DataFrame) -> vm.Page:
    """
    Create the powerlifting statistics page.

    Args:
        df_fitness (pd.DataFrame): The dataframe containing fitness data.
        df_bodyweight (pd.DataFrame): The dataframe containing bodyweight data.

    Returns:
        vm.Page: A Vizro page object.
    """
    df_powerlifting = df_fitness[df_fitness["Exercise Name"].isin(POWERLIFTING_EXERCISES)]
    df_bodyweight_smoothed = interpolate_data(df_bodyweight)
    df_merged = combine_exercise_and_bodyweight(df_powerlifting, df_bodyweight_smoothed)

    first_date, last_date = get_date_range(df_powerlifting, df_bodyweight)

    @callback(
        Output("graph-powerlifting-exercises", "figure", allow_duplicate=True),
        Input("switch-powerlifting-y-axis", "value"),
        prevent_initial_call=True,
    )
    def sort_y_axis_by_metric(metric):
        return get_powerlifting_plot(df_merged, first_date, last_date, metric)

    vm.Page.add_type("controls", vm.RadioItems)
    vm.Page.add_type("controls", vm.Card)
    page = vm.Page(
        title="Powerlifting Statistics",
        components=[
            vm.Graph(
                id="graph-powerlifting-exercises",
                figure=get_powerlifting_plot(df_merged, first_date, last_date),
                title="Powerlifting Exercises Weight Progression",
                # header="Each point in the graph represents a performed set. Only sets with less than 8 reps are colored. The smoothed trend line was calculated using a peak moving average filter.",
                header="""
                Visualizes weight progression over time for key powerlifting exercises.
                Each point represents a set, with color and marker type distinguishing between the exercises.
                Trend lines use peak moving average for clearer progression tracking.
                Filter by repetitions and adjust y-axis to show Weight, estimated 1RM, or Relative Strength in the sidebar.""",
            ),
            vm.Graph(
                figure=get_bodyweight_figure(df_bodyweight, df_bodyweight_smoothed, first_date, last_date),
                title="Bodyweight",
                header="""
                Tracks bodyweight changes over time, with each point representing a measurement.
                The smoothed trend line, calculated using a LOWESS algorithm, helps visualize overall weight progression.
                Weight class lines provide context for powerlifting classifications.
                Complements the strength progression chart above for a comprehensive view of physical development.""",
                # header="Each point in the graph represents a body weight measurement. The smoothed trend line was calculated using a LOWESS smoothing algorithm.",
            ),
        ],
        controls=[
            vm.Filter(
                column="Repetitions",
                targets=["graph-powerlifting-exercises"],
                selector=vm.RangeSlider(
                    title="Filter by Repetitions",
                    min=1,
                    max=20,
                    step=1,
                    marks={1: "1", 5: "5", 20: "20"},
                ),
            ),
            vm.RadioItems(
                id="switch-powerlifting-y-axis",
                options=["Weight [kg]", "1RM", "Relative Strength"],
                value="Weight [kg]",
                title="Y-axis Metric",
            ),
        ],
    )
    return page
