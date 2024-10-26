#Preliminary
import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.graph_objs as go
import pandas as pd
df = pd.read_csv('finaldf.csv')
df.dropna(inplace=True)
    ##Compared to use component replacement rate, we want to use the reverse so that the right-upper corner presents better outcomes.
for year in range(2016, 2022):
    df[f'components replacement-free rate {year}'] = 1 - df[f'component replacement rate {year}']
    ## Not all power plants starts from 2016.
for year in range(2016, 2022):
    df[f'Power Generation {year}(MWh)'].replace(0, None, inplace=True)
    df[f'component replacement rate {year}'].replace(0, None, inplace=True)

# Dashboard layout
app = dash.Dash(__name__)
filter_section = html.Div([
    dcc.Dropdown(
        id='city_dropdown',
        options=[{'label': city, 'value': city} for city in df['City'].unique()],
        placeholder="Select City",
        style={'margin-bottom': '10px'}
    ),
    dcc.RadioItems(
        id='project_type_radio',
        options=[{'label': pt, 'value': pt} for pt in df['Project Type'].unique()],
        labelStyle={'display': 'block', 'margin-bottom': '5px'},
        inputStyle={"margin-right": "10px"}
    ),
    dcc.Dropdown(
        id='station_dropdown',
        options=[],
        multi=True,
        placeholder="Select Power Stations",
        style={'margin-bottom': '10px'}
    ),
    dcc.Slider(
        id='year_slider',
        min=2016,
        max=2021,
        marks={str(year): str(year) for year in range(2016, 2022)},
        step=1,
        value=2021
    )
], style={
    'width': '25%', 'display': 'inline-block', 'vertical-align': 'top',
    'border': '2px solid #ccc', 'border-radius': '8px', 'padding': '15px',
    'background-color': '#f9f9f9', 'box-shadow': '2px 2px 10px rgba(0, 0, 0, 0.1)',
    'font-size': '12px'
})
graphs_section = html.Div([
    dcc.Graph(id='bubble_chart', style={'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.1)'}),
    dcc.Graph(id='line_chart_generation', style={'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.1)'}),
    dcc.Graph(id='line_chart_replacement_rate', style={'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.1)'})
], style={'width': '70%', 'display': 'inline-block', 'padding': '0 10px'})
app.layout = html.Div([
    html.H1("Power Plants", style={'text-align': 'center', 'font-size': '32px', 'color': '#2E86C1'}),
    html.Div([filter_section, graphs_section], style={'display': 'flex', 'flex-direction': 'row'})
])

# Dropdown
@app.callback(
    Output('station_dropdown', 'options'),
    [Input('city_dropdown', 'value'), Input('project_type_radio', 'value')]
)
def update_station_options(selected_city, selected_project_type):
    filtered_df = df
    if selected_city:
        filtered_df = filtered_df[filtered_df['City'] == selected_city]
    if selected_project_type:
        filtered_df = filtered_df[filtered_df['Project Type'] == selected_project_type]
    return [{'label': name, 'value': name} for name in filtered_df['Project Power Station Name'].unique()]

#bubble_chart
@app.callback(
    Output('bubble_chart', 'figure'),
    [Input('station_dropdown', 'value'), Input('year_slider', 'value')]
)
def update_bubble_chart(selected_stations, selected_year):
    if not selected_stations:  
        selected_stations = df['Project Power Station Name'].unique()[:20] 
    filtered_df = df[df['Project Power Station Name'].isin(selected_stations)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=filtered_df[f'component replacement rate {selected_year}'],
        y=filtered_df[f'Power Generation {selected_year}(MWh)'],
        text=filtered_df['Project Power Station Name'],
        mode='markers',
        marker=dict(size=filtered_df['Power Station Scale (MW)'] * 3, color='#48C9B0'), 
        hoverinfo='text+x+y'
    ))   
    fig.update_layout(
        title=dict(text=f'Component Replacement Rate vs Power Generation ({selected_year})',
                   font=dict(size=18, color="#2E86C1"), x=0.5, y=0.95),
        xaxis=dict(title=f'Component Replacement Rate {selected_year}', titlefont=dict(size=14, color='#2E86C1')),
        yaxis=dict(title=f'Power Generation {selected_year}(MWh)', titlefont=dict(size=14, color='#2E86C1')),
        plot_bgcolor="#f2f2f2",  
        paper_bgcolor="#ADD8E6",  
        font=dict(color="#333", size=12),  
        hovermode='closest'
    )
    return fig

# line_chart_generation
@app.callback(
    Output('line_chart_generation', 'figure'),
    [Input('station_dropdown', 'value'), Input('year_slider', 'value')]
)
def update_line_chart_generation(selected_stations, selected_year):
    if not selected_stations:  
        selected_stations = df['Project Power Station Name'].unique()[:2]  
    filtered_df = df[df['Project Power Station Name'].isin(selected_stations)]   
    fig = go.Figure()
    for station in selected_stations:
        station_data = filtered_df[filtered_df['Project Power Station Name'] == station]
        fig.add_trace(go.Scatter(
            x=list(range(2016, selected_year + 1)),
            y=station_data[[f'Power Generation {year}(MWh)' for year in range(2016, selected_year + 1)]].values[0],
            mode='lines+markers',
            name=station,  
            hoverinfo='text+x+y',
            text=[station] * (selected_year - 2016 + 1)
        ))

    fig.update_layout(
        title=dict(text='Power Generation Over Time', font=dict(size=18, color="#2E86C1"), x=0.5, y=0.95),
        xaxis=dict(title='Year', titlefont=dict(size=14, color='#2E86C1')),
        yaxis=dict(title='Power Generation (MWh)', titlefont=dict(size=14, color='#2E86C1')),  
        paper_bgcolor="#ADD8E6",  
        font=dict(color="#333", size=12),  
        hovermode='closest',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)    
    )
    return fig

# line chart replacement rate
@app.callback(
    Output('line_chart_replacement_rate', 'figure'),
    [Input('station_dropdown', 'value'), Input('year_slider', 'value')]
)
def update_line_chart_replacement_rate(selected_stations, selected_year):
    if not selected_stations:  
        selected_stations = df['Project Power Station Name'].unique()[:2]  
    filtered_df = df[df['Project Power Station Name'].isin(selected_stations)]  
    fig = go.Figure()
    for station in selected_stations:
        station_data = filtered_df[filtered_df['Project Power Station Name'] == station]
        fig.add_trace(go.Scatter(
            x=list(range(2016, selected_year + 1)),
            y=station_data[[f'component replacement rate {year}' for year in range(2016, selected_year + 1)]].values[0],
            mode='lines+markers',
            name=station,
            hoverinfo='text+x+y',
            text=[station] * (selected_year - 2016 + 1)
        ))
    fig.update_layout(
        title=dict(text='Component Replacement Rate Over Time', font=dict(size=18, color="#2E86C1"), x=0.5, y=0.95),  
        xaxis=dict(title='Year', titlefont=dict(size=14, color='#2E86C1')),  
        yaxis=dict(title='Component Replacement Rate', titlefont=dict(size=14, color='#2E86C1')),  
        hovermode='closest',
        paper_bgcolor="#ADD8E6",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)  
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
