"""This module contains the sidebar of the app, which is displayed at the left of the page.
By default, the sidebar is only visible in the exercise tab."""

import dash_mantine_components as dmc
from dash_iconify import DashIconify
from pandas import DataFrame

from components.custom_elements import create_switch_card


def get_sidebar(df: DataFrame) -> dmc.AppShellAside:
    sidebar = dmc.AppShellAside(
        id="sidebar",
        children=dmc.Stack(
            [
                dmc.Title("Plots by Exercise", c="white"),
                dmc.Text("Section exercise based plots", c="white"),
                dmc.Select(
                    id="dropdown-muscle-group",
                    data=sorted(set(df["Muscle Category"])),
                    label="Muscle Group",
                    description="Filter exercises by muscle group",
                    clearable=True,
                    leftSection=DashIconify(icon="icon-park-outline:muscle", color="blue"),
                ),
                dmc.Select(
                    id="dropdown-exercise-type",
                    data=sorted(set(df["Exercise Type"])),
                    label="Exercise Type",
                    clearable=True,
                    leftSection=DashIconify(icon="material-symbols:exercise-outline", color="blue", width=17),
                    description="Filter exercises by exercise type",
                ),
                dmc.Select(
                    id="dropdown-exercise",
                    data=sorted(set(df["Exercise Name"])),
                    label="Exercise",
                    value="Barbell Squat",
                    leftSection=DashIconify(icon="healthicons:exercise-weights", color="blue", width=20),
                    nothingFoundMessage="Exercise not found",
                    description="Plot",
                    placeholder="Enter or select an exercise",
                    searchable=True,
                    clearable=True,
                ),
                dmc.DateTimePicker(
                    id="date-range-picker",
                    label="Timeframe",
                    leftSection=DashIconify(icon="clarity:date-line"),
                    description="Limit plots to a certain time frame.",
                    minDate=min(df.index),
                    maxDate=max(df.index),
                ),
                create_switch_card("switch-show-comments", "Show comments", "Show only commented sets"),
                create_switch_card("switch-show-variations", "Show variations", "Also show similar exercises"),
                dmc.Card(
                    [
                        dmc.Text("Filter by Repetitions"),
                        dmc.RangeSlider(
                            id="slider-repetitions",
                            min=1,
                            max=50,
                            step=1,
                            value=(1, 50),
                            minRange=1,
                            mb=35,
                            marks=[
                                {"value": 1, "label": "1"},
                                {"value": 50, "label": "50"},
                            ],
                        ),
                    ],
                    withBorder=True,
                ),
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
