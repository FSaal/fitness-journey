import pandas as pd
import vizro.models as vm
from vizro.tables import dash_ag_grid


def get_playground_page(df_fitness: pd.DataFrame):
    df_fitness["Date"] = df_fitness.index.date
    df_fitness["Time"] = df_fitness.index.time

    # Round the 1RM column to 0 decimal places
    df_fitness["1RM"] = df_fitness["1RM"].round(0)

    # Define the desired column order
    column_order = [
        "Date",
        "Time",
        "Workout Name",
        "Exercise Name",
        "Set Order",
        "Weight [kg]",
        "Repetitions",
        "Volume",
        "1RM",
        "Distance",
        "Set Comment",
        "Session Duration [s]",
        "MuscleCategory",
        "Equipment",
        "Mechanic",
        "Force",
        "Weekday",
        "Session Comment",
    ]

    # Reorder the columns
    df_fitness = df_fitness[column_order]

    # Create the AG Grid configuration
    ag_grid_config = {
        "columnDefs": [
            {
                "field": col,
                "autoSize": True,  # This will adjust column width to fit content
                "sortable": True,
                "filter": True,
            }
            for col in df_fitness.columns
        ],
        "rowData": df_fitness.to_dict("records"),
        "defaultColDef": {"resizable": True, "sortable": True, "filter": True},
    }

    page = vm.Page(
        title="Playground",
        components=[
            vm.AgGrid(
                figure=dash_ag_grid(
                    df_fitness, columnDefs=ag_grid_config["columnDefs"], defaultColDef=ag_grid_config["defaultColDef"]
                )
            )
        ],
    )
    return page
