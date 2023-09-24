import dash_mantine_components as dmc
from dash import Dash, Input, Output, State, callback, dash_table, dcc, html
from dash_iconify import DashIconify

from pages.exercise_statistics import exercise_content
from pages.general_statistics import timely_content
from pages.powerlifting_statistics import powerlifting_content
from preprocessing import PreprocessClass

app = Dash(__name__)

progression_path = r"data\2023-09-16 17 16 38.csv"
gymbook_path = r"data\GymBook-Logs-2023-04-08.csv"
weight1_path = r"data\weight.csv"
weight2_path = r"data\weight_Felix_1694877519.csv"
preprocess = PreprocessClass(gymbook_path, progression_path, weight1_path, weight2_path)
df, df_weight = preprocess.main()


header = dmc.Header(
    height=50,
    fixed=True,
    children=[dmc.Group([dmc.Burger(id="button-toggle-sidebar", opened=True), dmc.Title("Fitness", align="center")])],
)

sidebar = dmc.Aside(
    id="sidebar",
    children=dmc.Stack(
        [
            dmc.Title("Plots by Exercise", color="white"),
            dmc.Text("Section exercise based plots", color="white"),
            dmc.Select(
                id="dropdown-muscle-group",
                data=sorted(set(df["Muscle Category"])),
                label="Muscle Group",
                description="Filter exercises by muscle group",
                clearable=True,
                icon=DashIconify(icon="icon-park-outline:muscle", color="blue"),
            ),
            dmc.Select(
                id="dropdown-exercise-type",
                data=sorted(set(df["Exercise Type"])),
                label="Exercise Type",
                clearable=True,
                icon=DashIconify(icon="material-symbols:exercise-outline", color="blue", width=17),
                description="Filter exercises by exercise type",
            ),
            dmc.Select(
                id="dropdown-exercise",
                data=sorted(set(df["Exercise Name"])),
                label="Exercise",
                value="Barbell Squat",
                icon=DashIconify(icon="healthicons:exercise-weights", color="blue", width=20),
                nothingFound="Exercise not found",
                description="Plot",
                placeholder="Enter or select an exercise",
                searchable=True,
                clearable=True,
            ),
            dmc.DateRangePicker(
                id="date-range-picker",
                label="Timeframe",
                icon=DashIconify(icon="clarity:date-line"),
                description="Limit plots to a certain time frame.",
                minDate=min(df.index),
                maxDate=max(df.index),
            ),
            dmc.Switch(id="switch-show-comments", label="Show only commented sets"),
        ]
    ),
)

content = html.Div(
    id="content",
    children=[
        dmc.Tabs(
            [
                dmc.TabsList(
                    [
                        dmc.Tab("Exercise", value="exercise"),
                        dmc.Tab("Powerlifting Headquarter", value="powerlifting"),
                        dmc.Tab("Timely", value="settings"),
                    ],
                ),
                dmc.TabsPanel(exercise_content(app, df, df_weight), value="exercise"),
                dmc.TabsPanel(powerlifting_content(df), value="powerlifting"),
                dmc.TabsPanel(timely_content(df), value="settings"),
            ],
            value="exercise",
            color="violet",
        ),
    ],
)


app.layout = dmc.MantineProvider(
    theme={
        # "colorScheme": "dark",
    },
    children=[html.Div(children=[header, sidebar, html.Br(), content])],
)


@callback(
    Output("sidebar", "style"),
    Output("content", "style"),
    Input("button-toggle-sidebar", "opened"),
)
def toggle_sidebar(opened: bool) -> tuple([dict, dict]):
    """Toggle the sidebar."""
    if opened:
        return SIDEBAR_STYLE, CONTENT_STYLE_COMPACT
    return SIDEBAR_HIDDEN, CONTENT_STYLE_FULL


# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 62.5,
    "left": 0,
    "bottom": 0,
    "width": "22rem",
    "height": "100%",
    "z-index": 1,
    "overflow-x": "hidden",
    "transition": "all 0.5s",
    "padding": "0.5rem 1rem",
    # "background-image": "linear-gradient(90deg, rgba(0, 0, 0, 0) 50%, rgba(0, 0, 0, 0.5) 100%)"
    # "background-color": "#845ef7",
}

SIDEBAR_HIDDEN = {
    "position": "fixed",
    "top": 62.5,
    "left": "-22rem",
    "bottom": 0,
    "width": "22rem",
    "height": "100%",
    "z-index": 1,
    "overflow-x": "hidden",
    "transition": "all 0.5s",
    "padding": "0rem 0rem",
    # "background-color": "#845ef7",
}

# the styles for the main content position it to the right of the sidebar and
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


if __name__ == "__main__":
    app.run_server(debug=True)
    # app.run_server(host="0.0.0.0")
