from datetime import datetime

import dash
import numpy as np
import pandas
from dash import dcc, html, Output, Input
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
df = pd.read_csv("data.csv", usecols=['Date', 'ConfirmedCovidCases', 'ConfirmedCovidDeaths', 'PartialPercent', 'FullyPercent', 'PerBoosterDose'])
df['AdjustedPartialPercent'] = df['PartialPercent'] - df['FullyPercent'].fillna(0)
df['AdjustedFullyPercent'] = df['FullyPercent'] - df['PerBoosterDose'].fillna(0)
df2 = df.iloc[179:, :]
# Create Weekly Deaths Dataframe
i, deaths, cases, output_dates, output_deaths, output_cases = 0, 0, 0, [], [], []
for case_count, death_count, date in zip(df['ConfirmedCovidCases'].fillna(0), df['ConfirmedCovidDeaths'].fillna(0), df['Date']):
    deaths += death_count
    cases += case_count
    if i == 7:
        output_dates.append(date)
        output_cases.append(cases)
        output_deaths.append(deaths)
        deaths = 0
        cases = 0
        i = 0
    i += 1
df_adjusted = pandas.DataFrame(zip(output_dates, output_cases, output_deaths), columns=["Date", "ConfirmedCovidCases","ConfirmedCovidDeaths"])

# Create Adjusted Deaths Dataframe
df_adjusted_deaths = df_adjusted.copy(deep=True)
df_adjusted_deaths['ConfirmedCovidDeaths'] = df_adjusted_deaths['ConfirmedCovidDeaths'].shift(-2)
df_adjusted_deaths['CaseDeathRatio'] = df_adjusted_deaths['ConfirmedCovidDeaths']/df_adjusted_deaths['ConfirmedCovidCases']
df_final = df_adjusted_deaths.iloc[25: , :]
app.layout = html.Div(children=[
    html.H1(children='Vindicating the Vaccines', style={"textAlign": "center"}),
    html.Div(children='Despite the scary headlines, the vaccines are helping to reduce the mortality rate of COVID-19', style={"textAlign": "center", "font-size": "14pt"}),
    html.Div(children=dcc.Graph(
        id='graph1',
    )),
    html.Div(id='description'),
    dcc.Checklist(id='graph-options', options=[],
    value=['CASES', 'DEATHS', 'CDR', 'VACC'],
    labelStyle={'display': 'inline-block'}
    ),
    dcc.Slider(
        id='progress-slider',
        min=0,
        max=4,
        value=0,
        marks={0: "Raw Data", 1: "Death Lag Adjusted", 2: "COVID Death Rate", 3: "Vaccinations and COVID Death Rate", 4: "Explore the Data Yourself"},
        step=None
    ),
])

@app.callback(
    Output('graph1', 'figure'),
    Output('description', 'children'),
    Output('graph-options', 'options'),
    Input('progress-slider', 'value'),
    Input('graph-options', 'value'))
def update_figure(mode, options):
    if mode == 0:
        fig = make_subplots()
        fig.add_trace(go.Bar(x=df_adjusted['Date'], y=df_adjusted['ConfirmedCovidDeaths'], yaxis='y', name="Covid Deaths", marker_color="rgb(255,0,0)"))
        fig.add_trace(go.Scatter(x=df['Date'], y=df['ConfirmedCovidCases'], mode='lines', yaxis='y2', name="Covid Cases", line_color="rgb(209,181,21)"))
        fig.update_layout(xaxis1={'title': 'Date'},
                          yaxis={'title': 'Weekly Deaths', 'range':[0,500], 'rangemode': 'tozero', 'side': 'right', 'showgrid': True, 'showticklabels': True},
                          yaxis2={'title': 'Daily Cases', 'range':[0,10000], 'rangemode': 'tozero', 'anchor': 'x', 'overlaying': 'y', 'side': 'left', 'showgrid': True, 'showticklabels': True},
                          xaxis2={'anchor': 'y', 'overlaying': 'x', 'side': 'top', 'showgrid': False, 'showticklabels': False},
                          legend={'x': 0, 'y': 1, 'traceorder': 'normal'})
        fig.update_xaxes(nticks=10)
        fig.data[1].update(xaxis='x2')

        description = "It feels like every day we're being bombarded with scary stories about how many fully vaccinated people are catching COVID. This may lead some people to believe that these vaccines were all a giant waste of time. However when you take a step back and actually look at the data you can really appreciate just how consequential these vaccines really are. The graph above shows us the number of daily COVID cases and weekly COVID deaths in Ireland. Considering the fact that (until recently) we have had very few COVID restrictions in place, these case numbers are already likely far lower than they would have been without the vaccines. However, they have other benefits beyond this."
        graph_options = []
    if mode == 1:
        fig = make_subplots()
        fig.add_trace(go.Bar(x=df_final['Date'], y=df_final['ConfirmedCovidDeaths'], yaxis='y', name="Covid Deaths", marker_color="rgb(255,0,0)"))
        fig.add_trace(go.Scatter(x=df_final['Date'], y=df_final['ConfirmedCovidCases'], yaxis='y2', mode='lines', name="Covid Cases", line_color="rgb(209,181,21)"))
        fig.update_layout(xaxis1={'title': 'Date'},
                          yaxis={'title': 'Weekly Deaths', 'range':[0,500], 'rangemode': 'tozero', 'side': 'right', 'showgrid': True, 'showticklabels': True},
                          yaxis2={'title': 'Weekly Cases', 'range':[0,50000], 'rangemode': 'tozero', 'anchor': 'x', 'overlaying': 'y', 'side': 'left', 'showgrid': True, 'showticklabels': True},
                          legend={'x':0, 'y':1, 'traceorder':'normal'})
        fig.update_xaxes(nticks=10)

        description = "We need to make a few changes to the data in order to make it useful. I have removed the first few months of data since COVID testing was not done at nearly the same sort of scale we are today, dramatically skewing the figures. Also, people don't catch COVID and instantly either die from or survive it. Most people who are killed by COVID die roughly 2 weeks after showing symptoms. Some people may be quicker or slower at getting tested than others but shifting our data by 2 weeks helps to make our case and death numbers more aligned. Finally I have changed the case numbers to be weekly averages like the death numbers."
        graph_options = []
    if mode == 2:
        fig = make_subplots()
        fig.add_trace(go.Bar(x=df_final['Date'], y=df_final['ConfirmedCovidDeaths'], yaxis='y', name="Covid Deaths", marker_color="rgb(255,0,0)"))
        fig.add_trace(go.Scatter(x=df_final['Date'], y=df_final['ConfirmedCovidCases'], yaxis='y2', mode='lines', name="Covid Cases", line_color="rgb(209,181,21)"))
        fig.add_trace(go.Scatter(x=df_final['Date'], y=df_final['CaseDeathRatio'], yaxis='y3', mode='lines', name="Case-Death Ratio", line_color="rgb(0,0,255)"))
        fig.update_layout(xaxis1={'title': 'Date'},
                          yaxis1={'rangemode': 'tozero', 'range':[0,500], 'showgrid': False, 'showticklabels': False},
                          yaxis2={'rangemode': 'tozero', 'range':[0,50000], 'anchor': 'free', 'overlaying': 'y', 'side': 'left', 'showgrid': False,'showticklabels': False},
                          yaxis3={'title': 'Covid Deaths/ Case', 'range':[0,0.05], 'rangemode': 'tozero', 'anchor': 'x', 'overlaying': 'y', 'side': 'left', 'showgrid': True, 'showticklabels': True},
                          legend={'x': 0, 'y': 1, 'traceorder': 'normal'})
        fig.update_xaxes(nticks=10)

        description = "Ipsum Lorem"
        graph_options = []
    if mode == 3:
        fig = make_subplots()
        fig.add_trace(go.Scatter(x=df2['Date'], y=df2["AdjustedPartialPercent"], mode='lines', stackgroup="one", name="Partially Vaccinated", fillcolor="rgba(55,255,0,0.5)", line_color="rgba(55,255,0,1)"))
        fig.add_trace(go.Scatter(x=df2['Date'], y=df2["AdjustedFullyPercent"], mode='lines', stackgroup="one", name="Fully Vaccinated", fillcolor="rgba(36,168,0,0.5)", line_color="rgba(36,168,0,1)"))
        fig.add_trace(go.Scatter(x=df2['Date'], y=df2["PerBoosterDose"], mode='lines', stackgroup="one", name="Fully Vaccinated with Booster", fillcolor="rgba(19,89,0,0.5)", line_color="rgba(19,89,0,1)"))
        fig.add_trace(go.Scatter(x=df_final['Date'], y=df_final['CaseDeathRatio'], yaxis='y2', mode='lines', name="Case-Death Ratio", line_color="rgb(0,0,255)"))
        fig.update_layout(xaxis1={'title': 'Date'},
                          xaxis2={'anchor': 'y', 'overlaying': 'x', 'side': 'top', 'showgrid': False, 'showticklabels': False},
                          yaxis1={'title': 'Vaccination Percent', 'range':[0,100], 'rangemode': 'tozero', 'side': 'right', 'showgrid': True,'showticklabels': True},
                          yaxis2={'title': 'Covid Deaths/ Case', 'range': [0,0.05], 'rangemode': 'tozero', 'anchor': 'free', 'overlaying': 'y', 'side': 'left', 'showgrid': True,'showticklabels': True},
                          legend={'x': 0, 'y': 1, 'traceorder': 'normal'})
        fig.update_xaxes(nticks=10)

        description = "Ipsum Lorem"
        graph_options = []
    if mode == 4:
        fig = make_subplots()
        if 'VACC' in options:
            fig.add_trace(go.Scatter(x=df2['Date'], y=df2["AdjustedPartialPercent"], xaxis='x2', yaxis='y4', mode='lines', stackgroup="one", name="Partially Vaccinated", fillcolor="rgba(55,255,0,0.5)", line_color="rgba(55,255,0,1)"))
            fig.add_trace(go.Scatter(x=df2['Date'], y=df2["AdjustedFullyPercent"], xaxis='x2', yaxis='y4', mode='lines', stackgroup="one", name="Fully Vaccinated", fillcolor="rgba(36,168,0,0.5)", line_color="rgba(36,168,0,1)"))
            fig.add_trace(go.Scatter(x=df2['Date'], y=df2["PerBoosterDose"], xaxis='x2', yaxis='y4', mode='lines', stackgroup="one", name="Fully Vaccinated with Booster", fillcolor="rgba(19,89,0,0.5)", line_color="rgba(19,89,0,1)"))
        if 'DEATHS' in options:
            fig.add_trace(go.Bar(x=df_final['Date'], y=df_final['ConfirmedCovidDeaths'], yaxis='y', name="Covid Deaths", marker_color="rgb(255,0,0)"))
        if 'CASES' in options:
            fig.add_trace(go.Scatter(x=df_final['Date'], y=df_final['ConfirmedCovidCases'], yaxis='y2', mode='lines', name="Covid Cases", line_color="rgb(209,181,21)"))
        if 'CDR' in options:
            fig.add_trace(go.Scatter(x=df_final['Date'], y=df_final['CaseDeathRatio'], yaxis='y3', mode='lines', name="Case-Death Ratio", line_color="rgb(0,0,255)"))

        if 'DEATHS' in options:
            fig.update_layout(xaxis1={'title': 'Date', 'domain':[0.05,0.95]},
                              xaxis2={'domain': [0.05, 0.95], 'anchor': 'y', 'overlaying': 'x', 'side': 'top', 'showgrid': False, 'showticklabels': False},
                              yaxis1={'title': 'Weekly Deaths', 'range': [0, 500], 'rangemode': 'tozero', 'side': 'right', 'showgrid': True, 'showticklabels': True},
                              yaxis2={'title': 'Weekly Cases', 'range': [0, 50000], 'rangemode': 'tozero', 'overlaying': 'y', 'anchor': 'x', 'side': 'left', 'showgrid': True, 'showticklabels': True},
                              yaxis3={'title': 'Covid Deaths/ Case', 'range': [0, 0.05], 'rangemode': 'tozero', 'overlaying': 'y','side': 'left', 'position':0, 'showgrid': True, 'showticklabels': True},
                              yaxis4={'title': 'Vaccination Percent', 'range':[0,100], 'rangemode': 'tozero',  'overlaying': 'y', 'side': 'right', 'position':1, 'showgrid': True,'showticklabels': True},
                              legend={'x': 0.1, 'y': 1, 'traceorder': 'normal'})
        elif 'CASES' in options:
            fig.update_layout(xaxis1={'title': 'Date', 'domain':[0.05,0.95]},
                              xaxis2={'domain': [0.05, 0.95], 'anchor': 'y', 'overlaying': 'x', 'side': 'top', 'showgrid': False, 'showticklabels': False},
                              yaxis2={'title': 'Weekly Cases', 'range': [0, 50000], 'rangemode': 'tozero', 'anchor': 'x', 'side': 'left', 'showgrid': True, 'showticklabels': True},
                              yaxis3={'title': 'Covid Deaths/ Case', 'range': [0, 0.05], 'rangemode': 'tozero', 'overlaying': 'y2','side': 'left', 'position':0, 'showgrid': True, 'showticklabels': True},
                              yaxis4={'title': 'Vaccination Percent', 'range':[0,100], 'rangemode': 'tozero',  'overlaying': 'y2', 'side': 'right', 'position':1, 'showgrid': True,'showticklabels': True},
                              legend={'x': 0.1, 'y': 1, 'traceorder': 'normal'})
        elif 'CDR' in options:
            fig.update_layout(xaxis1={'title': 'Date', 'domain':[0.05,0.95]},
                              xaxis2={'domain': [0.05, 0.95], 'anchor': 'y', 'overlaying': 'x', 'side': 'top', 'showgrid': False, 'showticklabels': False},
                              yaxis3={'title': 'Covid Deaths/ Case', 'range': [0, 0.05], 'rangemode': 'tozero', 'side': 'left', 'position':0, 'showgrid': True, 'showticklabels': True},
                              yaxis4={'title': 'Vaccination Percent', 'range':[0,100], 'rangemode': 'tozero',  'overlaying': 'y3', 'side': 'right', 'position':1, 'showgrid': True,'showticklabels': True},
                              legend={'x': 0.1, 'y': 1, 'traceorder': 'normal'})
        else:
            fig.update_layout(xaxis1={'title': 'Date', 'domain':[0.05,0.95]},
                              xaxis2={'domain': [0.05, 0.95], 'anchor': 'y', 'overlaying': 'x', 'side': 'bottom', 'showgrid': False, 'showticklabels': True},
                              yaxis4={'title': 'Vaccination Percent', 'range':[0,100], 'rangemode': 'tozero', 'side': 'right', 'position':1, 'showgrid': True,'showticklabels': True},
                              legend={'x': 0.1, 'y': 1, 'traceorder': 'normal'})
        fig.update_xaxes(nticks=10)

        description = "Lorem ipsum"
        graph_options = [{'label': 'Cases', 'value': 'CASES'},
        {'label': 'Deaths', 'value': 'DEATHS'},
        {'label': 'Case-Death Ratio', 'value': 'CDR'},
        {'label': 'Vaccinations', 'value': 'VACC'}]
    return fig, description, graph_options

if __name__ == '__main__':
    app.run_server(debug=True)