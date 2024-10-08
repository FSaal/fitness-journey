import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc
from dash_iconify import DashIconify
from scipy.interpolate import interp1d
from statsmodels.nonparametric.smoothers_lowess import lowess


def powerlifting_layout(df: pd.DataFrame, df_weight: pd.DataFrame) -> dmc.Stack:
    """
    This function returns a Dash component containing a scatter plot of powerlifting exercises.
    """
    powerlifting_exercises = [
        "Barbell Squat",
        "Barbell Bench Press",
        "Barbell Deadlift",
    ]
    df_powerlifting = df[df["Exercise Name"].isin(powerlifting_exercises)]
    fig = get_plot(df_powerlifting)

    strength_cards = get_card_overview(df, powerlifting_exercises)
    strength_cards = dmc.Group(strength_cards, gap="xl")

    figure_bodyweight = get_bodyweight_figure(df_weight)

    layout = dmc.Stack(
        [
            dmc.Center(strength_cards),
            dmc.Paper(dcc.Graph(figure=fig), shadow="md"),
            dmc.Paper(dcc.Graph(figure=figure_bodyweight), shadow="md"),
        ]
    )
    return layout


def get_card_overview(df, powerlifting_exercises):
    strength_cards = []
    exercise_icons = []
    powerlifting_total = 0
    for exercise in powerlifting_exercises:
        df_exercise = df[df["Exercise Name"] == exercise]
        # Information about PR
        record_idx = df_exercise["Weight"].argmax()
        record_date = df_exercise.index[record_idx].strftime("%d.%m.%y")
        record_weight = df_exercise["Weight"].iloc[record_idx]
        powerlifting_total += record_weight

        total_reps = df_exercise["Repetitions"].sum()
        # Total weight in tonnes
        total_weight = (df_exercise["Weight"] * df_exercise["Repetitions"]).sum() / 1000
        strength_cards.append(
            strength_card(
                exercise.split(" ")[1],
                record_weight,
                record_date,
                total_reps,
                total_weight,
                "pajamas:weight",
            )
        )

    powerlifting_total_lbs = powerlifting_total * 2.20462
    total_card = dmc.Card(
        children=[
            dmc.Group(
                [
                    dmc.Text("Total", fw=700, size="xl"),
                    dmc.Text(
                        f"{powerlifting_total:.0f} kg\n({powerlifting_total_lbs:.0f} lbs)",
                    ),
                ]
            )
        ]
    )
    strength_cards.append(total_card)

    return strength_cards


def get_plot(df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        df,
        x="Time",
        y="Weight",
        color="Exercise Name",
        symbol="Exercise Name",
    )
    fig.update_layout(yaxis_title="Weight [kg]", title_text="Powerlifting Exercises")
    fig.update(
        data=[
            {
                "customdata": df["Repetitions"],
                "hovertemplate": "Time: %{x}<br>Weight: %{y} kg<br>Repetitions: %{customdata}",
            }
        ]
    )
    return fig


def calculate_wilks_score():
    return None


def strength_card(exercise, weight, date, total_reps, total_weight, icon, icon_size=30):
    return dmc.Card(
        children=[
            dmc.Stack(
                [
                    dmc.Group(
                        [
                            dmc.Text(children=exercise, fw=700, size="xl"),
                            DashIconify(icon=icon, width=icon_size),
                        ],
                        justify="apart",
                    ),
                    dmc.Group(
                        [
                            dmc.Text(children=weight, fw=500, size="xl"),
                            dmc.Text(children=date, c="dimmed", size="sm", ta="right"),
                        ]
                    ),
                    dmc.Group(
                        [
                            dmc.Text(children=f"Reps: {total_reps}"),
                            dmc.Text(children=f"Weight: {total_weight:.0f} t"),
                        ]
                    ),
                ],
                gap="sm",
            )
        ],
        shadow="sm",
    )


def get_bodyweight_figure(df_weight: pd.DataFrame) -> go.Figure:
    # Create trendline
    time_num = df_weight["Time"].astype(int) / 10**9
    lowess_smoothed = lowess(df_weight["Weight"], time_num, frac=0.15)
    interp_func = interp1d(lowess_smoothed[:, 0], lowess_smoothed[:, 1], kind="cubic", fill_value="extrapolate")
    # Generate more frequent time points for a smoother curve (one per day)
    n_days = (df_weight["Time"].max() - df_weight["Time"].min()).days
    dense_time = pd.date_range(start=df_weight["Time"].min(), end=df_weight["Time"].max(), periods=n_days)
    dense_time_num = dense_time.astype(int) / 10**9

    # Create the figure
    fig = go.Figure()

    # Add scattered points
    fig.add_trace(
        go.Scatter(
            x=df_weight["Time"],
            y=df_weight["Weight"],
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
    )
    return fig


def add_weight_class_line(fig: go.Figure, weight_class: int) -> None:
    fig.add_hline(
        y=weight_class,
        line_dash="dash",
        line_width=0.5,
        annotation_text=f"{weight_class} kg Weight Class",
        annotation_position="bottom left",
    )
