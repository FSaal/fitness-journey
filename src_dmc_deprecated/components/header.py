"""This module contains the header of the app, which is displayed at the top of the page."""

import dash_mantine_components as dmc
from dash_iconify import DashIconify

theme_toggle = dmc.ActionIcon(
    [
        dmc.Paper(DashIconify(icon="radix-icons:sun", width=25), darkHidden=True),
        dmc.Paper(DashIconify(icon="radix-icons:moon", width=25), lightHidden=True),
    ],
    variant="transparent",
    color="yellow",
    id="color-scheme-toggle",
    size="lg",
    ms="auto",
)
header = dmc.AppShellHeader(
    # height=50,
    # fixed=True,
    children=[
        dmc.Group(
            [dmc.Burger(id="button-toggle-sidebar", opened=True), dmc.Title("Fitness", td="center"), theme_toggle]
        )
    ],
)
