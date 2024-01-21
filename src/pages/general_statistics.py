from dash import dcc
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px


def timely_content(df):
    training_days_per_week = training_days(df)
    training_time_per_day = training_time(df)
    moved_weight = lifted_weight(df)
    performed_reps = done_reps(df)
    return dmc.SimpleGrid(
        cols=2,
        children=[
            dmc.Paper(training_days_per_week, shadow="md"),
            dmc.Paper(training_time_per_day, shadow="md"),
            dmc.Paper(moved_weight, shadow="md"),
            dmc.Paper(performed_reps, shadow="md"),
        ],
    )


def training_days(df):
    """Calculate the number of training days per week."""
    df["Week"] = df.index.strftime("%Y-%U")
    df["Day"] = df.index.day
    days_per_week = df.groupby("Week")["Day"].nunique().reset_index()
    days_per_week.columns = ["Week", "Days"]
    days_per_week["Week"] = pd.to_datetime(
        days_per_week["Week"] + "-1", format="%Y-%U-%w"
    )
    fig = px.bar(days_per_week, x="Week", y="Days")
    fig.update_layout(
        xaxis=dict(tickformat="CW %W<br>%Y", title="Time"),
        yaxis_range=[0, 7],
        title="Days Trained per Week",
    )
    fig.update_layout(yaxis_range=[0, 7])
    return dcc.Graph(figure=fig)


def training_time(df):
    """Calculate the training time per day."""
    training_time_per_day = df.groupby(df.index.date)["Time"].apply(
        lambda x: (x.max() - x.min()).total_seconds() / 60
    )
    fig = px.histogram(
        training_time_per_day,
        x=training_time_per_day.values,
        nbins=int((training_time_per_day.max() + 10) / 10),
        range_x=(0, 150),
    )
    fig.update_layout(
        title="Training Time per Training Day",
        xaxis_title="Time (min)",
        yaxis_title="Sessions",
    )
    return dcc.Graph(figure=fig)


def lifted_weight(df):
    lifted_weight = (df["Weight"] * df["Repetitions"]).cumsum().rename("Weight")
    fig = px.area(lifted_weight, y="Weight")
    fig.update_layout(title="Lifted Weight cumulative sum", yaxis_title="Weight [kg]")
    return dcc.Graph(figure=fig)


def done_reps(df):
    done_reps = df["Repetitions"].cumsum()
    fig = px.area(done_reps, y="Repetitions")
    fig.update_layout(
        title="Performed Repetitions cumulative sum", yaxis_title="Repetitions"
    )
    return dcc.Graph(figure=fig)
