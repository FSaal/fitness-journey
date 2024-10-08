import dash_ag_grid as dag
from dash import html


def playground_layout(df):
    row_data = df.to_dict("records")
    text_columns = [
        "Workout Name",
        "Exercise Name",
        "Set Comment",
        "Session Comment",
        "Muscle Category",
        "Exercise Type",
        "Weekday",
    ]
    number_columns = ["Set Order", "Weight", "Repetitions", "Session Duration (s)"]
    date_columns = ["Time"]
    text_column_defs = [{"field": col, "filter": "agTextColumnFilter", "sortable": True} for col in text_columns]
    number_column_defs = [{"field": col, "filter": "agNumberColumnFilter", "sortable": True} for col in number_columns]
    date_column_defs = [{"field": col, "filter": "agDateColumnFilter", "sortable": True} for col in date_columns]
    column_defs = text_column_defs + number_column_defs + date_column_defs
    # column_defs = [
    #     {"field": "Repetitions", "filter": "agNumberColumnFilter", "sortable": True},
    #     {"field": "Repetitions", "filter": "agNumberColumnFilter", "sortable": True},
    #     {"field": "Time", "filter": "agDateColumnFilter"},
    # ]
    grid = dag.AgGrid(
        id="ag-grid",
        columnDefs=column_defs,
        rowData=row_data,
        dashGridOptions={"supressRowTransform": True},
    )
    return html.Div(grid)
