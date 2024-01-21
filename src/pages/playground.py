import dash_ag_grid as dag
from dash import html


def playground(df):
    row_data = df.to_dict("records")
    column_defs = [{"field": col, "filter": True, "sortable": True} for col in df.columns]
    # column_defs = [
    #     {"field": "Repetitions", "filter": "agNumberColumnFilter"},
    #     {"field": "Time", "filter": "agDateColumnFilter"},
    # ]
    grid = dag.AgGrid(
        id="ag-grid", columnDefs=column_defs, rowData=row_data, dashGridOptions={"supressRowTransform": True}
    )
    return html.Div(grid)
