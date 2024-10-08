import os

import pandas as pd
import vizro.models as vm
from vizro.tables import dash_ag_grid

api_key = os.getenv("OPENAI_API_KEY")
print(api_key)


def get_playground_page(df_fitness: pd.DataFrame):
    page = vm.Page(title="Playground", components=[vm.AgGrid(figure=dash_ag_grid(df_fitness))])
    return page
