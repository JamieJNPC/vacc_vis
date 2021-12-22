import dash
from dash import dcc, html
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Create Dataframe
df = pd.read_csv("data.csv", usecols=['Date', 'ConfirmedCovidCases', 'ConfirmedCovidDeaths', 'PartialPercent', 'FullyPercent', 'PerBoosterDose'])
df['AdjustedPartialPercent'] = df['PartialPercent'] - df['FullyPercent'].fillna(0)
df['AdjustedFullyPercent'] = df['FullyPercent'] - df['PerBoosterDose'].fillna(0)


# Create Figures
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Bar(x=df['Date'], y=df['ConfirmedCovidDeaths']), secondary_y=False)
fig.add_trace(go.Scatter(x=df['Date'], y=df['ConfirmedCovidCases'], mode='lines'), secondary_y=True)
fig.update_yaxes(rangemode='tozero', scaleanchor='y2', scaleratio=100, constraintoward='bottom', secondary_y=False)
fig.update_yaxes(rangemode='tozero', scaleanchor='y', scaleratio=0.01, constraintoward='bottom', secondary_y=True)
fig2 = px.area(df, x="Date", y=["AdjustedPartialPercent", "AdjustedFullyPercent", "PerBoosterDose"])
app.layout = html.Div(children=[
    html.H1(children='Vindicating the Vaccines', style={"textAlign": "center"}),
    dcc.Graph(
        id='example-graph',
        figure=fig
    ),
    dcc.Graph(
        id='example-graph2',
        figure=fig2
    )
])
if __name__ == '__main__':
    app.run_server(debug=True)