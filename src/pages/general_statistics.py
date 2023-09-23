from dash import dcc
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px


def timely_content(df):
    df["Week"] = df["Time"].dt.strftime("%Y-%U")
    df["Day"] = df["Time"].dt.day
    days_per_week = df.groupby("Week")["Day"].nunique().reset_index()
    days_per_week.columns = ["Week", "Days Trained"]
    days_per_week["Week"] = pd.to_datetime(days_per_week["Week"] + "-1", format="%Y-%U-%w")
    fig = px.bar(days_per_week, x="Week", y="Days Trained")
    fig.update_layout(
        xaxis=dict(tickformat="CW %W<br>%Y", title="Time"), yaxis_range=[0, 7], title="Days Trained per Week"
    )
    fig.update_layout(yaxis_range=[0, 7])
    return dmc.Paper(dcc.Graph(figure=fig))
