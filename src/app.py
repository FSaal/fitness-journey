import dash_mantine_components as dmc
from dash import Dash, Input, Output, State, _dash_renderer, callback, html
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from components.header import header
from components.sidebar import SIDEBAR_HIDDEN_STYLE, SIDEBAR_VISIBLE_STYLE, get_sidebar
from exercise_compendium import exercise_compendium
from pages import (
    ai_queries,
    exercise_statistics,
    general_statistics,
    playground,
    powerlifting_statistics,
    program_statistics,
)
from preprocessing import PreprocessClass

_dash_renderer._set_react_version("18.2.0")

# Constants
CONTENT_STYLE_COMPACT = {
    "transition": "margin-left .5s",
    "margin-left": "22rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    # "background-color": "#f8f9fa",
}

CONTENT_STYLE_FULL = {
    "transition": "margin-left .5s",
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    # "background-color": "#f8f9fa",
}


def load_data():
    """Load data and preprocess it"""
    # Training data of iOS fitness app: Gymbook
    ios_fitness_data_path = "data/GymBook-Logs-2023-04-08.csv"
    # Training data of Android fitness app: Progression
    android_fitness_data_path = "data/2024-09-25 08:19:34.csv"
    # Body weight measurements from myFitnessPal app
    body_weight_myfitnesspal_path = "data/weight.csv"
    # Body weight measurements from Eufy scale
    body_weight_eufy_path = "data/weight_Felix_1727247358.csv"
    preprocess = PreprocessClass(
        ios_fitness_data_path,
        android_fitness_data_path,
        body_weight_myfitnesspal_path,
        body_weight_eufy_path,
    )
    return preprocess.main()


def create_app():
    app = Dash(__name__)
    df, df_weight = load_data()

    content = html.Div(
        id="content",
        children=[
            dmc.Tabs(
                [
                    dmc.TabsList(
                        [
                            dmc.TabsTab("Exercise", value="exercise"),
                            dmc.TabsTab("Powerlifting Headquarter", value="powerlifting"),
                            dmc.TabsTab("Program Statistics", value="program"),
                            dmc.TabsTab("Timely", value="time"),
                            dmc.TabsTab("Data Playground", value="playground"),
                            dmc.TabsTab("Ai Playground", value="ai-playground"),
                        ],
                    ),
                    dmc.TabsPanel(exercise_statistics.exercise_layout(app, df, exercise_compendium), value="exercise"),
                    dmc.TabsPanel(powerlifting_statistics.powerlifting_layout(df, df_weight), value="powerlifting"),
                    dmc.TabsPanel(program_statistics.program_layout(app, df), value="program"),
                    dmc.TabsPanel(general_statistics.time_layout(df), value="time"),
                    dmc.TabsPanel(playground.playground_layout(df), value="playground"),
                    dmc.TabsPanel(ai_queries.ai_playground_layout(df), value="ai-playground"),
                ],
                id="tabs",
                value="exercise",
            ),
        ],
        style=CONTENT_STYLE_COMPACT,
    )

    app.layout = dmc.MantineProvider(
        dmc.AppShell(
            html.Div(
                id="div-app",
                children=[
                    header,
                    get_sidebar(df),
                    dmc.AppShellMain(content),
                ],
            ),
            header={"height": 50},
        ),
        id="mantine-provider",
        theme={"primaryColor": "violet", "components": {"Select": {"defaultProps": {"clearable": True}}}},
    )

    @callback(
        Output("sidebar", "style"),
        Output("content", "style"),
        Input("button-toggle-sidebar", "opened"),
    )
    def toggle_sidebar(opened: bool) -> tuple[dict, dict]:
        """Toggle the sidebar."""
        return (SIDEBAR_VISIBLE_STYLE, CONTENT_STYLE_COMPACT) if opened else (SIDEBAR_HIDDEN_STYLE, CONTENT_STYLE_FULL)

    @callback(Output("button-toggle-sidebar", "opened"), Input("tabs", "value"))
    def hide_sidebar(selected_tab):
        return selected_tab == "exercise"

    @callback(
        Output("mantine-provider", "forceColorScheme"),
        Input("color-scheme-toggle", "n_clicks"),
        State("mantine-provider", "forceColorScheme"),
        prevent_initial_call=True,
    )
    def switch_theme(_, theme):
        return "dark" if theme == "light" else "light"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run_server(debug=True)
    # app.run_server(host="0.0.0.0")
