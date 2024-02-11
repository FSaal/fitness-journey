import dash_mantine_components as dmc
import plotly.express as px
from dash import Input, Output, State, dcc
from dash.exceptions import PreventUpdate


def program_layout(app, df):
    get_callbacks(app, df)
    # fig_exercise_sunburst = plot_exercise_sunburst(df)
    layout = dmc.Stack(
        [
            # dmc.Paper(dcc.Graph(figure=fig_exercise_sunburst), shadow="md"),
            dmc.Select(
                id="dropdown-names",
                data=["Muscle Category", "Exercise Type", "Exercise Name"],
                value="Muscle Category",
                # label="Muscle Group",
                # description="Filter exercises by muscle group",
            ),
            dmc.Select(
                id="dropdown-values",
                data=["Repetitions", "Weight", "Volume"],
                value="Repetitions",
                # label="Muscle Group",
                # description="Filter exercises by muscle group",
            ),
            dmc.Select(
                id="dropdown-sunburst",
                data=["Repetitions", "Weight", "Volume"],
                value="Repetitions",
                # label="Muscle Group",
                # description="Filter exercises by muscle group",
            ),
            dmc.Paper(dcc.Graph(id="exercise-pie"), shadow="md"),
            dmc.Paper(dcc.Graph(id="exercise-sunburst"), shadow="md"),
        ]
    )

    return layout


def get_callbacks(app, df):
    @app.callback(
        Output("exercise-sunburst", "figure"),
        Input("dropdown-names", "value"),
        Input("dropdown-values", "value"),
        Input("tabs", "value"),
    )
    def udpate_sth(names, values, tab):
        if tab != "program":
            raise PreventUpdate
        fig = px.pie(df, values=values, names=names, hole=0.2, title=f"{values} by {names}")
        return fig

    @app.callback(
        Output("exercise-pie", "figure"),
        Input("dropdown-sunburst", "value"),
    )
    def udpate_sth(values):
        fig = px.sunburst(df, path=["Muscle Category", "Exercise Name"], values=values, title=f"{values} by Exercise")
        return fig


def plot_trained_bodypart(df):
    # Generate a pie chart, where each section is a body part (column Muscle category)
    px.pie(df, values="Repetitions", names="Muscle Category", title="Exercises")
