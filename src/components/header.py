"""This module contains the header of the app, which is displayed at the top of the page."""

import dash_mantine_components as dmc

header = dmc.Header(
    height=50,
    fixed=True,
    children=[
        dmc.Group(
            [
                dmc.Burger(id="button-toggle-sidebar", opened=True),
                dmc.Title("Fitness", align="center"),
            ]
        )
    ],
)
