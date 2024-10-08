import pandas as pd
import plotly.graph_objects as go
import vizro.models as vm

# import plotly.express as px
import vizro.plotly.express as px
from dash import Input, Output, callback, dcc
from vizro.models.types import capture
from wordcloud import WordCloud


def get_general_statistics_page(df_fitness: pd.DataFrame) -> vm.Page:
    @callback(
        Output("graph-cumulative", "figure", allow_duplicate=True),
        Input("dropdown-filter-exercise-type", "value"),
        Input("dropdown-filter-muscle-category", "value"),
        Input("dropdown-cumulative-metric", "value"),
        prevent_initial_call=True,
    )
    def plot_cumulative_stuff(exercise_type, muscle_category, metric):
        if exercise_type and "ALL" not in exercise_type:
            filtered_df = df_fitness[df_fitness["Exercise Type"].isin(exercise_type)]
        else:
            filtered_df = df_fitness

        if muscle_category and "ALL" not in muscle_category:
            filtered_df = filtered_df[filtered_df["Muscle Category"].isin(muscle_category)]
        else:
            filtered_df = filtered_df

        if metric == "Repetitions":
            cumulative_series = filtered_df["Repetitions"].cumsum()
        elif metric == "Sets":
            # Normal Set Order column can not be used, since it is not 1 per set
            filtered_df["Sets"] = 1
            cumulative_series = filtered_df["Sets"].cumsum()
        elif metric == "Weight [kg]":
            cumulative_series = (filtered_df["Weight [kg]"] * filtered_df["Repetitions"]).cumsum().rename("Weight [kg]")
        fig = px.area(cumulative_series, y=metric)
        return fig

    vm.Page.add_type("controls", vm.Dropdown)
    page = vm.Page(
        title="General Statistics",
        components=[
            vm.Graph(figure=training_days(df_fitness), title="Training Days per Week"),
            vm.Graph(figure=training_time(df_fitness), title="Training Duration per Session"),
            # Average rest time between sets per day
            # vm.Graph(figure=rest_time(df_fitness), title="Rest Time between Sets"),
            vm.Graph(id="graph-cumulative", figure=lifted_weight(df_fitness), title="Lifted Weight"),
        ],
        controls=[
            vm.Dropdown(
                id="dropdown-cumulative-metric",
                options=["Weight [kg]", "Repetitions", "Sets"],
                value="Repetitions",
                multi=False,
            ),
            vm.Dropdown(
                id="dropdown-filter-exercise-type",
                options=df_fitness["Exercise Type"].unique().tolist(),
                title="Filter by Exercise Type",
            ),
            vm.Dropdown(
                id="dropdown-filter-muscle-category",
                options=df_fitness["Muscle Category"].unique().tolist(),
                title="Filter by Muscle Category",
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
    fig.add_hline(y=mean_days, line_dash="dash", line_color="gray")
    return fig


@capture("graph")
def training_time(data_frame):
    """Calculate the training time per day."""
    training_time_per_day = data_frame.groupby(data_frame.index.date, observed=True)["Time"].apply(
        lambda x: (x.max() - x.min()).total_seconds() / 60
    )
    fig = px.histogram(
        training_time_per_day,
        x=training_time_per_day.values,
        nbins=int((training_time_per_day.max() + 10) / 10),
        range_x=(0, 150),
        template="plotly_dark",
    )
    fig.update_layout(
        xaxis_title="Time [min]",
        yaxis_title="Sessions",
    )
    return fig


@capture("graph")
def lifted_weight(data_frame):
    lifted_weight = (data_frame["Weight [kg]"] * data_frame["Repetitions"]).cumsum().rename("Weight [kg]")
    done_reps = data_frame["Repetitions"].cumsum()
    fig = px.area(lifted_weight, y="Weight [kg]", template="plotly_dark")
    fig.update_layout(title="Lifted Weight cumulative sum", yaxis_title="Weight [kg]")
    return fig
