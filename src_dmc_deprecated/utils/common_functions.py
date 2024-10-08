def plot_placeholder(exercise: str) -> str:
    """Display an error message in the plot if no data is available."""
    if not exercise:
        error_message = "Select an exercise to visualize data"
    else:
        error_message = "No data found for the selected time frame"
    empty_message = {
        "layout": {
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
            "annotations": [
                {
                    "text": error_message,
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 28},
                }
            ],
        }
    }
    return empty_message
