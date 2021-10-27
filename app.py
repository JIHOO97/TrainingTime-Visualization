import dash # initialize your application
import dash_core_components as dcc # allows you to create interactive components like graphs, dropdowns, or date ranges
import dash_html_components as html # access HTML tags
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import json # unnecessary library now

from datetime import datetime
from dash.dependencies import Output, Input


# Import data

data = pd.read_csv("Swim_dataset.csv") # read csv file

# filter the unnecessary columns
unnec_cols = data.columns[10:]
data = data.drop(columns=unnec_cols)

# rename "Unnamed: 0" column name to "Date"
data = data.rename(columns={"Unnamed: 0":"Date"})

# convert the contents in the date column into a datetime format
data["Date"] = pd.to_datetime(data["Date"], format="%Y-%m-%d") # convert the date into a date format

# set Date as an index 
# data = data.set_index('Date')

# convert nan to 0
data = data.fillna(0)

# remove all zeros
column_list = data.columns[1:]
data = data[(data[column_list].T != 0.0).any()]


# Import competition data

# convert measured time to seconds (utility function)
def convertToSec(s):
    if s != 0:
        minute = int(s[:2])
        second = int(s[3:5])
        millisecond = int(s[6:])
        return minute*60 + second + millisecond/100
    return 0

competition_data = pd.read_csv("Swim_progress.csv") # read csv file

# fill NaN with zeros
competition_data = competition_data.fillna(0)

# drop all zero rows
competition_data = competition_data.loc[(competition_data!=0).any(axis=1)]
competition_data = competition_data.reset_index(drop=True)

# change date format
for i in range(len(competition_data)):
    competition_data.at[i, 'Date'] = datetime.strptime(competition_data.Date[i], '%d/%m/%Y').date()

# convert Date column as an index
competition_data['Date'] = pd.to_datetime(competition_data['Date'])
competition_data.set_index('Date', inplace=True)

# convert str to time
cols = competition_data.columns[:-1]
isNotEric = False
for i in range(len(competition_data)):
    if isNotEric:
        break
    for col in cols:
        if competition_data["Name"][i] != "오승현":
            isNotEric = True
            break
        if competition_data.iloc[i][col] != 0:
            competition_data.iloc[i, competition_data.columns.get_loc(col)] = convertToSec(competition_data.iloc[i][col])

competition_option_list = []
for column in competition_data.columns[:-1]:
    tmp_dict = {}
    tmp_dict["label"] = column
    tmp_dict["value"] = column
    competition_option_list.append(tmp_dict)


# Initialize application

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server
app.title = "Swimming Training Time Analysis"


graph_bgcolor = "#0A165A"
font_color = "#FFFFFF"


app.layout = html.Div(
    children=[
        
        # heading
        html.Div(
            children=[
                html.P(
                    children="🏊‍♂️", className="header-emoji"
                ),
                html.H1(
                    children="Swimming Training Analysis", className="header-title"
                ),
                html.P(
                    children="Analyze the how the training time affects the result",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        
        # Graph part
        html.Div(
            children=[
                
                # Competition graph
                html.Div(
                    children=[
                        
                        # title
                        html.Div(children='Competition Graph', className='competition-title'),
                        
                        # menu
                        html.Div(
                            children=[
                                
                                # name selector
                                dcc.Dropdown(
                                    id='competition-name-selector',
                                    options=[
                                        {'label': '오승현', 'value': '오승현'},
                                        {'label': '이호은', 'value': '이호은'},
                                        {'label': '변현준', 'value': '변현준'},
                                        {'label': '고준호', 'value': '고준호'},
                                        {'label': '우성홍', 'value': '우성홍'},
                                        {'label': '곽송현', 'value': '곽송현'},
                                        {'label': '정민서', 'value': '정민서'},
                                        {'label': '고관혁', 'value': '고관혁'},
                                        {'label': '김은호', 'value': '김은호'},
                                        {'label': '곽민지', 'value': '곽민지'},
                                        {'label': '안현정', 'value': '안현정'},
                                    ],
                                    value='오승현',
                                    style={"min-width": "150px"},
                                ),
                                
                                # event selector
                                dcc.Dropdown(
                                    id='competition-event-selector',
                                    options=competition_option_list,
                                    value='50 Free',
                                    style={"min-width": "200px"},
                                ),
                                
                                # average-total selection
                                dcc.RadioItems(
                                    id='competition-avg-date-selector',
                                    options=[
                                        {'label': 'Monthly Average', 'value': 'monthly-avg'},
                                        {'label': 'To-the-date', 'value': 'to-the-date'},
                                    ],
                                    value='monthly-avg',
                                    labelStyle={
                                        'display': 'flex',
                                        'margin-bottom': '5px',
                                        'font-weight': 300,
                                        'color': '#FFFFFF',
                                    },
                                ),
                            ],
                            className='menu'
                        ),
                        
                        # graph
                        dcc.Graph(
                            id='competition-graph-id',
                            className='competition-graph',
                            figure={
                                "layout": {
                                    "paper_bgcolor": graph_bgcolor,
                                    "plot_bgcolor": graph_bgcolor,
                                    "font": {
                                        "color": "#FFFFFF"
                                    }
                                },
                            },
                        ),
                    ],
                    className='competition-graph-container'
                ),
                
                
                # Training graph
                html.Div(
                    children=[
                        
                        # categorical bar plot
                        html.Div(
                            children=[
                                # title
                                html.Div(
                                    children=[
                                        html.Div(children='Categorical Graph', className='categorical-graph-title'),
                                    ], 
                                    className='category-title-container',
                                ),

                                # menu
                                html.Div(
                                    children=[
                                        # average-total selection
                                        dcc.RadioItems(
                                            id='category-avg-total-selector',
                                            options=[
                                                {'label': 'Average', 'value': 'avg'},
                                                {'label': 'Total', 'value': 'total'},
                                            ],
                                            value='avg',
                                            labelStyle={
                                                'display': 'flex',
                                                'margin-bottom': '5px',
                                                'font-weight': 300,
                                                'color': '#FFFFFF',
                                            },
                                        ),

                                        # category selector
                                        dcc.Dropdown(
                                            id='category-category-selector',
                                            options=[
                                                {'label': 'Warm Up', 'value': 'Warm Up'},
                                                {'label': 'Kick', 'value': 'Kick'},
                                                {'label': 'Pull', 'value': 'Pull'},
                                                {'label': 'Swim', 'value': 'Swim'},
                                                {'label': 'Drill', 'value': 'Drill'},
                                                {'label': 'Main Set', 'value': 'Main Set'},
                                                {'label': 'Post Set', 'value': 'Post Set'},
                                                {'label': 'Cool Down', 'value': 'Cool Down'},
                                            ],
                                            value=["Warm Up","Swim","Main Set"],
                                            multi=True,
                                            style={"min-width": "150px"},
                                        ),
                                    ],
                                    className='train-menu',
                                ),

                                # bar plot
                                html.Div(
                                    children=dcc.Graph(
                                        id='categorical-bar-chart',
                                        style={"height": "100%"},
                                        config={"displayModeBar": True},
                                        figure={
                                            "layout": {
                                                "paper_bgcolor": graph_bgcolor,
                                                "plot_bgcolor": graph_bgcolor,
                                                "font": {
                                                    "color": "#FFFFFF"
                                                }
                                            },
                                        },
                                    ),
                                    className='bar-categorical-graph'
                                ),
                            ],
                            className='bar-categorical-graph-container'
                        ),
                        
                        # Categorical line plot
                        html.Div(
                            children=[
                                # title
                                html.Div(
                                    children=[
                                        html.Div(children='Time Series Graph', className='time-graph-title'),
                                        html.Div(
                                            children=[
                                                html.Button('D', id='daily-button', className='time-series-button', n_clicks=0),
                                                html.Button('W', id='weekly-button', className='time-series-button', n_clicks=0),
                                                html.Button('M', id='monthly-button', className='time-series-button', n_clicks=0),
                                            ],
                                        ),
                                    ], 
                                    className='time-title-container',
                                ),

                                # menu
                                html.Div(
                                    children=[
                                        # average-total selection
                                        dcc.DatePickerRange(
                                            id='time-date-picker',
                                            min_date_allowed=data.Date.min().date(),
                                            max_date_allowed=data.Date.max().date(),
                                            start_date=data.Date.min().date(),
                                            end_date=data.Date.max().date(),
                                            with_portal=True,
                                            style={'display': 'inline-block'},
                                            display_format='DD-MMM-YY',
                                            className='datepicker',
                                        ),

                                        # category selector
                                        dcc.Dropdown(
                                            id='time-category-selector',
                                            options=[
                                                {'label': 'Warm Up', 'value': 'Warm Up'},
                                                {'label': 'Kick', 'value': 'Kick'},
                                                {'label': 'Pull', 'value': 'Pull'},
                                                {'label': 'Swim', 'value': 'Swim'},
                                                {'label': 'Drill', 'value': 'Drill'},
                                                {'label': 'Main Set', 'value': 'Main Set'},
                                                {'label': 'Post Set', 'value': 'Post Set'},
                                                {'label': 'Cool Down', 'value': 'Cool Down'},
                                            ],
                                            value=["Warm Up"],
                                            multi=True,
                                            style={"min-width": "150px"},
                                        ),
                                    ],
                                    className='train-menu'
                                ),

                                # line plot
                                html.Div(
                                    children=dcc.Graph(
                                        id='timeseries-line-chart',
                                        style={"height": "100%"},
                                        config={"displayModeBar": True},
                                        figure={
                                            "layout": {
                                                "paper_bgcolor": graph_bgcolor,
                                                "plot_bgcolor": graph_bgcolor,
                                                "font": {
                                                    "color": "#FFFFFF"
                                                }
                                            },
                                        },
                                    ),
                                    className='time-series-graph'
                                ),
                            ],
                            className='time-series-graph-container',
                        ),
                    ],
                    className='training-graph-container',
                ),
            ],
            className='graph-container'
        ),
        
        # space
        html.Div(style={"height": 80}),
    ],
    className='app-container'
)


# # Monthly data
# monthly_competition_data = competition_data.copy()
# monthly_competition_data = monthly_competition_data.astype('float16') # should match the datatype
# monthly_competition_data = monthly_competition_data.resample('1M').mean()
# monthly_competition_data = monthly_competition_data.fillna(0)

# # drop rows with all zeros
# compeition_column_list = monthly_competition_data.columns
# monthly_competition_data = monthly_competition_data[(monthly_competition_data[compeition_column_list].T != 0.0).any()]


def convertAverageMonthly(name, event_name):
    tmp_competition_data = competition_data.loc[competition_data['Name'] == name]
    tmp_competition_data = tmp_competition_data[event_name].to_frame()
    tmp_competition_data = tmp_competition_data[(tmp_competition_data.T != 0.0).any()]
    tmp_competition_data = tmp_competition_data.astype('float16').resample('1M').mean().fillna(0)
    return tmp_competition_data


@app.callback(
    Output("competition-graph-id", "figure"),
    [
        Input("competition-name-selector", "value"),
        Input("competition-event-selector", "value"),
        Input("competition-avg-date-selector", "value"),
    ],
)
def update_competition_chart(name, event_name, avg_or_date):
    # TODO
    '''
        filter by name is to be implemented
    '''
    
    # data according to avg_or_date selection
    competition_callback_data = None
    if avg_or_date == 'monthly-avg':
        competition_callback_data = convertAverageMonthly(name, event_name)
    else:
        competition_callback_data = competition_data.loc[competition_data['Name'] == name]
        competition_callback_data = competition_callback_data[event_name].to_frame()
        competition_callback_data = competition_callback_data[(competition_callback_data.T != 0.0).any()]
    
    if len(competition_callback_data) == 0:
        fig = px.line()
    else:
        fig = px.line(
            x=competition_callback_data.index, y=competition_callback_data[event_name]
        )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    
    fig.update_layout(
        {
            'clickmode': 'event+select',
            'plot_bgcolor': graph_bgcolor,
            'paper_bgcolor': graph_bgcolor,
            'xaxis_title': "Competition Date",
            'yaxis_title': "meter",
            'font': dict(
                family="Lato, sans-serif",
                size=18,
                color="#FFFFFF"
            ),
        }
    )
    
    return fig


@app.callback(
    Output("categorical-bar-chart", "figure"),
    [
        Input("category-avg-total-selector", "value"),
        Input("category-category-selector", "value"),
        Input("competition-graph-id", "clickData"),
    ],
)
def update_categorical_bar_chart(avg_or_total, categories, clickData):
    if clickData == None:
        startDate = data.Date.min()
        endDate = data.Date.max()
    # get the startDate from the clicked date
    else:
        startDate = clickData["points"][0]["x"]
        # get the endDate
        competition_data_mask = (competition_data.index > startDate)
        filtered_competition_data = competition_data.loc[competition_data_mask, :]
        if filtered_competition_data.empty:
            endDate = data.Date.max()
        else:
            endDate = filtered_competition_data.iloc[0].to_frame().columns[0].strftime("%Y-%m-%d")

    categorical_data_mask = (
        (data.Date >= startDate)
        & (data.Date <= endDate)
    )
    filtered_categorical_data = data.loc[categorical_data_mask, :]

    # filter by categories
    filtered_categorical_data = filtered_categorical_data[categories]
    # if new_data is in the form
    if isinstance(filtered_categorical_data, pd.Series):
        filtered_categorical_data = filtered_categorical_data.to_frame()

    # get avg or total data
    total_data = []
    if type(categories) == str:
        category_list = list(filtered_categorical_data[categories])
        total_value = sum(category_list)
        total_data.append(total_value)
    else:
        for category in categories:
            category_list = list(filtered_categorical_data[category])
            total_value = sum(category_list)
            total_data.append(total_value)

    if sum(total_data) != 0 and avg_or_total == 'avg':
        for i in range(len(total_data)):
            total_data[i] /= filtered_categorical_data.shape[0]

    bar_chart_figure = {
        "data": [
            {
                "x": categories,
                "y": total_data,
                "type": "bar",
                "hovertemplate": "%{y:.2f}M<extra></extra>",
            },
        ],
        "layout": {
            "paper_bgcolor": graph_bgcolor,
            "plot_bgcolor": graph_bgcolor,
            "font": {
                "color": "#FFFFFF"
            }
        },
    }

    return bar_chart_figure


'''
    Average data
'''
# Monthly data
monthly_avg_data = data.copy()
monthly_avg_data.set_index('Date', inplace=True)
monthly_avg_data = monthly_avg_data.resample('1M').mean()
monthly_avg_data = monthly_avg_data.fillna(0)

column_list = monthly_avg_data.columns[1:]
monthly_avg_data = monthly_avg_data[(monthly_avg_data[column_list].T != 0.0).any()]

# Weekly data
weekly_avg_data = data.copy()
weekly_avg_data.set_index('Date', inplace=True)
weekly_avg_data = weekly_avg_data.resample('1W').mean()
weekly_avg_data = weekly_avg_data.fillna(0)

column_list = weekly_avg_data.columns[1:]
weekly_avg_data = weekly_avg_data[(weekly_avg_data[column_list].T != 0.0).any()]

# Daily data
daily_avg_data = data.copy()
daily_avg_data.set_index('Date', inplace=True)


@app.callback(
    Output("timeseries-line-chart", "figure"),
    [
        Input("time-date-picker", "start_date"),
        Input("time-date-picker", "end_date"),
        Input("time-category-selector", "value"),
        Input("daily-button", "n_clicks"),
        Input("weekly-button", "n_clicks"),
        Input("monthly-button", "n_clicks"),
    ],
)
def update_categorical_line_chart(start_date, end_date, categories, daily_btn, weekly_btn, monthly_btn):
    # filter by daily/weekly/monthly
    changed_type = [p['prop_id'] for p in dash.callback_context.triggered][0]
    
    line_data = None
    
    if 'daily-button' in changed_type:
        line_data = daily_avg_data
    elif 'weekly-button' in changed_type:
        line_data = weekly_avg_data
    else:
        line_data = monthly_avg_data
        
    # filter by dates
    line_mask = (
        (line_data.index >= start_date)
        & (line_data.index <= end_date)
    )

    line_data = line_data.loc[line_mask, :]
    line_data

    # filter by categories
    line_data = line_data[categories]
    # if new_data is in the form
    if isinstance(line_data, pd.Series):
        line_data = line_data.to_frame()

    # data
    data_list = []
    if type(categories) == str:
        data_dict = {
            "x": line_data.index,
            "y": line_data[categories],
            "type": "lines",
        }
    else:
        for category in categories:
            data_dict = {
                "x": line_data.index,
                "y": line_data[category],
                "type": "lines",
                "name": category,
            }
            data_list.append(data_dict)
    
    line_chart_figure = {
        "data": data_list,
        "layout": {
            "paper_bgcolor": graph_bgcolor,
            "plot_bgcolor": graph_bgcolor,
            "font": {
                "color": "#FFFFFF"
            }
        },
    }
    
    return line_chart_figure


if __name__ == "__main__":
    app.run_server(debug=False)