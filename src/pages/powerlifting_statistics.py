import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc
from dash_iconify import DashIconify


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
    strength_cards = dmc.Group(strength_cards, spacing="xl")

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
                    dmc.Text("Total", weight=700, size="xl"),
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
                            dmc.Text(children=exercise, weight=700, size="xl"),
                            DashIconify(icon=icon, width=icon_size),
                        ],
                        position="apart",
                    ),
                    dmc.Group(
                        [
                            dmc.Text(children=weight, weight=500, size="xl"),
                            dmc.Text(children=date, color="dimmed", size="sm", align="right"),
                        ]
                    ),
                    dmc.Group(
                        [
                            dmc.Text(children=f"Reps: {total_reps}"),
                            dmc.Text(children=f"Weight: {total_weight:.0f} t"),
                        ]
                    ),
                ],
                spacing="sm",
            )
        ],
        shadow="sm",
    )


def get_bodyweight_figure(df_weight):
    # TODO: All
    fig = px.scatter(
        df_weight,
        x="Time",
        y="Weight",
        title="Bodyweight",
        trendline="lowess",
        trendline_options={"frac": 0.1},
    )
    fig.add_hline(
        y=66,
        line_dash="dash",
        line_width=0.5,
        annotation_text="66 kg Weight Class",
        annotation_position="bottom left",
    )
    fig.add_hline(
        y=74,
        line_dash="dot",
        annotation_text="74 kg Weight Class",
        annotation_position="bottom left",
    )
    return fig
