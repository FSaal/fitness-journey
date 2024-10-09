import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import vizro.models as vm

# import vizro.plotly.express as px
from scipy.interpolate import interp1d
from statsmodels.nonparametric.smoothers_lowess import lowess
from vizro.models.types import capture


@capture("graph")
def get_plot(data_frame: pd.DataFrame, first_date: pd.Timestamp, last_date: pd.Timestamp) -> go.Figure:
    fig = px.scatter(
        data_frame,
        x=data_frame.index,
        y="Weight [kg]",
        color="Exercise Name",
        symbol="Exercise Name",
        template="plotly_dark",
    )
    fig.update_layout(xaxis_range=[first_date, last_date])
    fig.update(
        data=[
            {
                "customdata": data_frame["Repetitions"],
                "hovertemplate": "Time: %{x}<br>Weight: %{y} kg<br>Repetitions: %{customdata}",
            }
        ]
    )
    return fig


def get_powerlifting_statistic_page(df_fitness: pd.DataFrame, df_bodyweight: pd.DataFrame) -> dmc.Stack:
    powerlifting_exercises = [
        "Barbell Squat",
        "Barbell Bench Press",
        "Barbell Deadlift",
    ]
    df_powerlifting = df_fitness[df_fitness["Exercise Name"].isin(powerlifting_exercises)]

    # Get first date between the two dataframes, to have same x axis (time scale)
    first_date = min(df_powerlifting.index.min(), df_bodyweight.index.min())
    last_date = max(df_powerlifting.index.max(), df_bodyweight.index.max())

    page = vm.Page(
        title="PowerLifting Statistics",
        components=[
            vm.Graph(figure=get_plot(df_powerlifting, first_date, last_date)),
            vm.Graph(figure=get_bodyweight_figure(df_bodyweight, first_date, last_date)),
        ],
    )
    return page


def calculate_wilks_score():
    return None


@capture("graph")
def get_bodyweight_figure(data_frame: pd.DataFrame, first_date: pd.Timestamp, last_date: pd.Timestamp) -> go.Figure:
    # Create trendline
    time_num = data_frame.index.astype(int) / 10**9
    lowess_smoothed = lowess(data_frame["Weight [kg]"], time_num, frac=0.15)
    interp_func = interp1d(lowess_smoothed[:, 0], lowess_smoothed[:, 1], kind="cubic", fill_value="extrapolate")
    # Generate more frequent time points for a smoother curve (one per day)
    n_days = (data_frame.index.max() - data_frame.index.min()).days
    dense_time = pd.date_range(start=data_frame.index.min(), end=data_frame.index.max(), periods=n_days)
    dense_time_num = dense_time.astype(int) / 10**9

    # Create the figure
    fig = go.Figure()

    # Add scattered points
    fig.add_trace(
        go.Scatter(
            x=data_frame.index,
            y=data_frame["Weight [kg]"],
            mode="markers",
            name="Measured Weight",
        )
    )

    # Add smoothed line
    fig.add_trace(
        go.Scatter(
            x=dense_time,
            y=interp_func(dense_time_num),
            mode="lines",
            name="Smoothed Trend",
        )
    )

    # Add horizontal lines for weight classes
    add_weight_class_line(fig, 66)
    add_weight_class_line(fig, 74)

    # Update layout
    fig.update_layout(
        title="Bodyweight",
        xaxis_title="Time",
        yaxis_title="Weight [kg]",
        xaxis_range=[first_date, last_date],
        template="plotly_dark",
    )
    return fig


def add_weight_class_line(fig: go.Figure, weight_class: int) -> None:
    fig.add_hline(
        y=weight_class,
        line_dash="dash",
        line_color="gray",
        line_width=0.5,
        annotation_text=f"{weight_class} kg Weight Class",
        annotation_position="bottom left",
    )
