from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm
import vizro.plotly.express as px
from dash import dcc
from vizro.models.types import capture
from wordcloud import WordCloud


def get_general_statistics_page(df_fitness: pd.DataFrame) -> vm.Page:
    vm.Page.add_type("controls", vm.Dropdown)
    page = vm.Page(
        title="General Statistics",
        layout=vm.Layout(grid=[[0, 1], [0, 1], [2, 2], [2, 2]]),
        components=[
            vm.Graph(
                figure=training_days(df_fitness),
                title="Training Days per Week",
                header="""
                     Visualizes the consistency of training frequency over time. Each bar represents a week, with its height showing the number of training days that week.
                     The dashed line indicates the average training days per week, helping identify periods of high and low training frequency.""",
            ),
            vm.Graph(
                figure=training_time(df_fitness),
                title="Training Duration per Session",
                header="""
                     Displays the distribution of workout durations across all training sessions.
                     The x-axis shows time intervals in minutes, while the y-axis represents the number of sessions falling within each duration range.
                     Useful for understanding typical workout lengths and identifying outliers.""",
            ),
            vm.Graph(
                figure=create_heatmap_calendar(df_fitness),
                title="Training Volume Heatmap Calendar",
                header="""
                     Animates training volume patterns over the years in a calendar format.
                     Each cell represents a day, with color intensity indicating the training volume.
                     The animation progresses through weeks and years, revealing seasonal trends and long-term changes in training habits.
                     Use the play/pause button to control the animation.""",
            ),
        ],
    )
    return page


def generate_wordcloud(df: pd.DataFrame):
    # filter None comments
    set_comments = df[df["Set Comment"] != "None"]["Set Comment"]

    text = " ".join(set_comments)

    wordcloud = WordCloud(
        background_color="white",
        width=1600,
        height=800,
        max_words=100,
    ).generate(text)

    fig = go.Figure()
    fig.add_trace(go.Image(z=wordcloud.to_array(), hoverinfo="none"))
    fig.update_layout(
        width=wordcloud.width,
        height=wordcloud.height,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=10, r=10, t=10, b=10),
    )

    return dcc.Graph(figure=fig)


@capture("graph")
def training_days(data_frame):
    """Calculate the number of training days per week."""
    data_frame["Week"] = data_frame.index.strftime("%Y-%U")
    data_frame["Day"] = data_frame.index.day
    days_per_week = data_frame.groupby("Week", observed=True)["Day"].nunique().reset_index()
    days_per_week.columns = ["Week", "Days"]
    days_per_week["Week"] = pd.to_datetime(days_per_week["Week"] + "-1", format="%Y-%U-%w")
    fig = px.bar(days_per_week, x="Week", y="Days", template="plotly_dark")
    fig.update_layout(xaxis=dict(tickformat="CW %W<br>%Y", title="Week"), yaxis_range=[0, 7])
    mean_days = days_per_week["Days"].mean()
    fig.add_hline(y=mean_days, name=f"Mean: {int(mean_days)}", line_dash="dash", line_color="gray")
    return fig


@capture("graph")
def training_time(data_frame):
    """Calculate the training time per day."""
    training_time_per_day = data_frame.groupby(data_frame.index.date, observed=True).apply(
        lambda group: (group.index.max() - group.index.min()).total_seconds() / 60
    )
    fig = px.histogram(
        training_time_per_day,
        x=training_time_per_day.values,
        nbins=int((training_time_per_day.max() + 10) / 10),
        range_x=(0, 150),
        template="plotly_dark",
    )
    fig.update_layout(xaxis_title="Time [min]", yaxis_title="Sessions")
    return fig


@capture("graph")
def create_heatmap_calendar(data_frame: pd.DataFrame) -> go.Figure:
    """Create an animated heatmap calendar view of training volume across years."""
    # Get the range of years in the dataset
    years = data_frame.index.year.unique()

    # Calculate the maximum volume across all years
    max_volume = data_frame.groupby(data_frame.index.date)["Volume"].sum().max()

    # Create frames for each year
    frames = []
    for year in years:
        year_data = data_frame[data_frame.index.year == year]

        # Create a date range for the entire year
        date_range = pd.date_range(start=f"{year}-01-01", end=f"{year}-12-31", freq="D")

        # Create a DataFrame with all days of the year
        all_days = pd.DataFrame(index=date_range)
        all_days["day"] = all_days.index.dayofweek
        all_days["week"] = all_days.index.isocalendar().week
        all_days["month"] = all_days.index.month

        # Group by date and sum the volume
        daily_volume = year_data.groupby(year_data.index.date)["Volume"].sum()

        # Merge with the all_days DataFrame
        merged = all_days.merge(daily_volume, left_index=True, right_index=True, how="left")

        # Group by day and week, summing the volume
        grouped = merged.groupby(["day", "week"])["Volume"].sum().reset_index()

        # Create the pivot table
        pivot = grouped.pivot(index="day", columns="week", values="Volume")

        # Create the heatmap trace for this year
        heatmap = go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            colorscale="Plasma",
            colorbar=dict(title="Volume"),
            zmin=0,
            zmax=max_volume,
            hovertemplate="CW: %{x}<br>Day: %{y}<br>Volume: %{z:.0f} kg",
        )

        frames.append(go.Frame(data=[heatmap], name=str(year)))

    # Create the initial heatmap (using the first year)
    initial_year = years[0]
    initial_heatmap = frames[0].data[0]

    # Create the figure
    fig = go.Figure(
        data=[initial_heatmap],
        layout=go.Layout(
            updatemenus=[
                dict(
                    type="buttons",
                    buttons=[
                        dict(
                            label="Play",
                            method="animate",
                            args=[None, {"frame": {"duration": 1000, "redraw": True}, "fromcurrent": True}],
                        ),
                        dict(
                            label="Pause",
                            method="animate",
                            args=[
                                [None],
                                {
                                    "frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate",
                                    "transition": {"duration": 0},
                                },
                            ],
                        ),
                    ],
                    font=dict(color="black"),
                    bgcolor="white",
                )
            ],
            sliders=[
                dict(
                    steps=[
                        dict(
                            method="animate",
                            args=[
                                [str(year)],
                                dict(
                                    mode="immediate",
                                    frame=dict(duration=300, redraw=True),
                                    transition=dict(duration=300),
                                ),
                            ],
                            label=str(year),
                        )
                        for year in years
                    ],
                    transition=dict(duration=300),
                    x=0,
                    y=0,
                    len=1.0,
                )
            ],
            xaxis=dict(title="Week of Year"),
            yaxis=dict(title="Day of Week", dtick=1, tickvals=[0, 1, 2, 3, 4, 5, 6]),
        ),
        frames=frames,
    )

    # Add month separators (for the initial year)
    for month in range(1, 13):
        first_day = datetime(initial_year, month, 1)
        week_num = first_day.isocalendar()[1]
        fig.add_vline(x=week_num - 0.5, line_width=1, line_dash="dash", line_color="white")
        fig.add_annotation(x=week_num, y=7, text=first_day.strftime("%b"), showarrow=False, yshift=10)
    fig.update_layout(
        template="plotly_dark",
    )
    return fig
