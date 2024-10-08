import pandas as pd
import vizro.models as vm
import vizro.plotly.express as px
from dash import Input, Output, callback


def get_exercise_distribution_page(df_fitness: pd.DataFrame):
    @callback(
        Output("exercise-sunburst", "figure", allow_duplicate=True),
        Input("dropdown-category", "value"),
        Input("dropdown-metric", "value"),
        prevent_initial_call=True,
    )
    def update_sunburst_chart(category, metric):
        # Create the path with the category as a list
        path = [category, "Exercise Name"]
        fig = px.sunburst(df_fitness, path=path, values=metric)
        return fig

    vm.Page.add_type("controls", vm.Dropdown)
    page = vm.Page(
        title="Exercise Distribution",
        components=[
            vm.Graph(
                id="exercise-sunburst",
                figure=px.sunburst(df_fitness, path=["Muscle Category", "Exercise Name"], values="Repetitions"),
            )
        ],
        controls=[
            vm.Dropdown(
                id="dropdown-category",
                options=["Muscle Category", "Exercise Type", "Weekday"],
                value="Muscle Category",
                title="Category",
                multi=False,
            ),
            vm.Dropdown(
                id="dropdown-metric",
                options=["Repetitions", "Volume", "Weight [kg]"],
                value="Repetitions",
                title="Metric",
                multi=False,
            ),
        ],
    )
    return page
