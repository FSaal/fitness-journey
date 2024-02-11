import dash_loading_spinners
import dash_mantine_components as dmc
from components.header import header
from components.sidebar import SIDEBAR_HIDDEN_STYLE, SIDEBAR_VISIBLE_STYLE, get_sidebar
from dash import Dash, Input, Output, State, callback, html
from dash.exceptions import PreventUpdate
from exercise_compendium import exercise_compendium
from pages.exercise_statistics import exercise_layout
from pages.general_statistics import time_layout
from pages.playground import playground_layout
from pages.powerlifting_statistics import powerlifting_layout
from pages.program_statistics import program_layout
from preprocessing import PreprocessClass

app = Dash(__name__)


def load_data():
    """Load data and preprocess it"""
    progression_path = r"data\2024-01-21 18 02 06.csv"
    gymbook_path = r"data\GymBook-Logs-2023-04-08.csv"
    weight_myfitnesspal_path = r"data\weight.csv"
    weight_eufy_path = r"data\weight_Felix_1707336212.csv"
    preprocess = PreprocessClass(
        gymbook_path,
        progression_path,
        weight_myfitnesspal_path,
        weight_eufy_path,
    )
    df, df_weight = preprocess.main()
    return df, df_weight


df, df_weight = load_data()


# the styles for the main content position is to the right of the sidebar and
# add some padding.
CONTENT_STYLE_COMPACT = {
    "transition": "margin-left .5s",
    "margin-left": "22rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE_FULL = {
    "transition": "margin-left .5s",
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

content = html.Div(
    id="content",
    children=[
        dmc.Tabs(
            [
                dmc.TabsList(
                    [
                        dmc.Tab("Exercise", value="exercise"),
                        dmc.Tab("Powerlifting Headquarter", value="powerlifting"),
                        dmc.Tab("Program Statistics", value="program"),
                        dmc.Tab("Timely", value="time"),
                        dmc.Tab("Data Playground", value="playground"),
                    ],
                ),
                dmc.TabsPanel(exercise_layout(app, df, exercise_compendium), value="exercise"),
                dmc.TabsPanel(powerlifting_layout(df, df_weight), value="powerlifting"),
                dmc.TabsPanel(program_layout(app, df), value="program"),
                dmc.TabsPanel(id="general-content", value="time"),
                dmc.TabsPanel(playground_layout(df), value="playground"),
            ],
            id="tabs",
            value="exercise",
            color="violet",
        ),
    ],
    style=CONTENT_STYLE_COMPACT,
)


app.layout = dmc.MantineProvider(
    theme={
        # "colorScheme": "dark",
    },
    children=[
        html.Div(id="div-loading", children=[dash_loading_spinners.Pacman(fullscreen=True, id="loading-whole-app")]),
        html.Div(id="div-app", children=[header, get_sidebar(df), html.Br(), content]),
    ],
)


@app.callback(
    Output("div-loading", "children"),
    [Input("div-app", "loading_state")],
    [
        State("div-loading", "children"),
    ],
)
def hide_loading_after_startup(loading_state, children):
    if children:
        print("remove loading spinner!")
        return None
    print("spinner already gone!")
    raise PreventUpdate


@callback(
    Output("sidebar", "style"),
    Output("content", "style"),
    Input("button-toggle-sidebar", "opened"),
)
def toggle_sidebar(opened: bool) -> tuple[dict, dict]:
    """Toggle the sidebar."""
    if opened:
        return SIDEBAR_VISIBLE_STYLE, CONTENT_STYLE_COMPACT
    return SIDEBAR_HIDDEN_STYLE, CONTENT_STYLE_FULL


# @callback(Output("button-toggle-sidebar", "opened"), Input("tabs", "value"))
# def hide_sidebar(selected_tab):
#     if selected_tab != "exercise":
#         return False
#     return True


if __name__ == "__main__":
    app.run_server(debug=True)
    # app.run_server(host="0.0.0.0")
