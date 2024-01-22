import plotly.express as px
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import dcc


def powerlifting_content(df):
    """
    This function returns a Dash component containing a scatter plot of powerlifting exercises.
    """
    powerlifting_exercises = [
        "Barbell Squat",
        "Barbell Bench Press",
        "Barbell Deadlift",
    ]
    df_powerlifting = df[df["Exercise Name"].isin(powerlifting_exercises)]
    fig = px.scatter(
        df_powerlifting,
        y="Weight",
        color="Exercise Name",
        symbol="Exercise Name",
        hover_name="Repetitions",
    )
    fig.update_xaxes(title_text="Time")
    fig.update_yaxes(title_text="Weight [kg]")
    fig.update_layout(title_text="Powerlifting Exercises", title_x=0.5)

    strength_cards = []
    exercise_icons = []
    for exercise in powerlifting_exercises:
        df_exercise = df[df["Exercise Name"] == exercise]
        # Information about PR
        record_idx = df_exercise["Weight"].argmax()
        record_date = df_exercise.index[record_idx].strftime("%d.%m.%y")
        record = df_exercise["Weight"][record_idx]

        total_reps = df_exercise["Repetitions"].sum()
        # Total weight in tonnes
        total_weight = (df_exercise["Weight"] * df_exercise["Repetitions"]).sum() / 1000
        strength_cards.append(
            strength_card(
                exercise.split(" ")[1],
                record,
                record_date,
                total_reps,
                total_weight,
                "pajamas:weight",
            )
        )
    strength_cards = dmc.Group(strength_cards, spacing="md")

    return dmc.Paper([dcc.Graph(figure=fig), strength_cards])


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
                            dmc.Text(
                                children=date, color="dimmed", size="sm", align="right"
                            ),
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
