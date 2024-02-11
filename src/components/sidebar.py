"""This module contains the sidebar of the app, which is displayed at the left of the page.
By default, the sidebar is only visible in the exercise tab."""

import dash_mantine_components as dmc
from dash_iconify import DashIconify
from pandas import DataFrame


def get_sidebar(df: DataFrame) -> dmc.Aside:
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
                dmc.Switch(id="switch-show-variations", label="Also show similar exercises"),
            ]
        ),
        style=SIDEBAR_VISIBLE_STYLE,
    )
    return sidebar


# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_VISIBLE_STYLE = {
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

SIDEBAR_HIDDEN_STYLE = {
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
