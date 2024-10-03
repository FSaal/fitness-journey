import dash_mantine_components as dmc
import plotly.express as px
from dash import Input, Output, State, dcc
from dash.exceptions import PreventUpdate

from src.components.custom_elements import segmented_control


def program_layout(app, df):
    get_callbacks(app, df)
    # fig_exercise_sunburst = plot_exercise_sunburst(df)
    layout = dmc.Grid(
        [
            dmc.GridCol(
                dmc.Stack(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Text("Pie chart (Left)"),
                                        dmc.Select(
                                            id="dropdown-names",
                                            data=["Muscle Category", "Exercise Type"],
                                            value="Muscle Category",
                                            label="Category",
                                            description="Splits the chart into different categories",
                                        ),
                                        dmc.Select(
                                            id="dropdown-values",
                                            data=["Repetitions", "Weight", "Volume"],
                                            value="Repetitions",
                                            label="Muscle Group",
                                            description="Size the pieces",
                                        ),
                                    ]
                                )
                            ],
                            withBorder=True,
                        ),
                        dmc.Card(
                            dmc.Stack(
                                [
                                    segmented_control(
                                        title="Primary Group",
                                        description="First-level chart organization",
                                        id="segment-sunburst-first-path",
                                        data=[
                                            {"value": "Muscle Category", "label": "Muscle"},
                                            {"value": "Exercise Type", "label": "Equipment"},
                                        ],
                                        value="Muscle Category",
                                    ),
                                    segmented_control(
                                        title="Display metric",
                                        description="Data shown in segment",
                                        id="segment-sunburst-value",
                                        data=["Repetitions", "Volume", "Weight"],
                                        value="Repetitions",
                                    ),
                                ]
                            ),
                            withBorder=True,
                        ),
                    ]
                ),
                span=2,
            ),
            dmc.GridCol(dmc.Stack([dmc.Paper(dcc.Graph(id="exercise-pie"), shadow="md")]), span=5),
            dmc.GridCol(dmc.Stack([dmc.Paper(dcc.Graph(id="exercise-sunburst"), shadow="md")]), span=5),
        ]
    )
    return layout


def get_callbacks(app, df):
    @app.callback(
        Output("exercise-pie", "figure"),
        Input("dropdown-names", "value"),
        Input("dropdown-values", "value"),
        Input("tabs", "value"),
    )
    def update_pie_chart(names, values, tab):
        if tab != "program":
            raise PreventUpdate
        fig = px.pie(df, values=values, names=names, hole=0.2, title=f"{values} by {names}")
        return fig

    @app.callback(
        Output("exercise-sunburst", "figure"),
        Input("segment-sunburst-first-path", "value"),
        Input("segment-sunburst-value", "value"),
    )
    def update_sunburst_chart(first_path, values):
        fig = px.sunburst(
            df,
            path=[first_path, "Exercise Name"],
            values=values,
            title=f"{values} by Exercise, categorized in {first_path}",
        )
        return fig
