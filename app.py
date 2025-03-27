# https://fifa-world-cup-winners.onrender.com/

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Step 1: Create dataset
def create_worldcup_dataset():
    # Data from Wikipedia
    data = {
        'Year': [1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974, 
                 1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022],
        'Winner': ['Uruguay', 'Italy', 'Italy', 'Uruguay', 'West Germany', 'Brazil', 
                   'Brazil', 'England', 'Brazil', 'West Germany', 'Argentina', 
                   'Italy', 'Argentina', 'West Germany', 'Brazil', 'France', 
                   'Brazil', 'Italy', 'Spain', 'Germany', 'France', 'Argentina'],
        'Runner-up': ['Argentina', 'Czechoslovakia', 'Hungary', 'Brazil', 'Hungary', 
                      'Sweden', 'Czechoslovakia', 'West Germany', 'Italy', 'Netherlands', 
                      'Netherlands', 'West Germany', 'West Germany', 'Argentina', 
                      'Italy', 'Brazil', 'Germany', 'France', 'Netherlands', 
                      'Argentina', 'Croatia', 'France'],
        'Score': ['4-2', '2-1 (a.e.t.)', '4-2', '2-1', '3-2', '5-2', '3-1', '4-2 (a.e.t.)', 
                  '4-1', '2-1', '3-1 (a.e.t.)', '3-1', '3-2', '1-0', '0-0 (a.e.t.) (3-2 p)', 
                  '3-0', '2-0', '1-1 (a.e.t.) (5-3 p)', '1-0 (a.e.t.)', '1-0 (a.e.t.)', 
                  '4-2', '3-3 (a.e.t.) (4-2 p)'],
        'Host': ['Uruguay', 'Italy', 'France', 'Brazil', 'Switzerland', 'Sweden', 
                 'Chile', 'England', 'Mexico', 'West Germany', 'Argentina', 
                 'Spain', 'Mexico', 'Italy', 'United States', 'France', 
                 'South Korea/Japan', 'Germany', 'South Africa', 'Brazil', 'Russia', 'Qatar']
    }
    
    df = pd.DataFrame(data)
    
    # Clean country names for consistency
    df['Winner'] = df['Winner'].replace({'West Germany': 'Germany'})
    df['Runner-up'] = df['Runner-up'].replace({'West Germany': 'Germany', 'Czechoslovakia': 'Czech Republic'})
    
    return df

# Create the dataset
worldcup_df = create_worldcup_dataset()

# Prepare data for choropleth maps
def prepare_choropleth_data(df):
    # Count wins by country
    winners = df['Winner'].value_counts().reset_index()
    winners.columns = ['Country', 'Wins']
    
    # Count runner-ups by country
    runners = df['Runner-up'].value_counts().reset_index()
    runners.columns = ['Country', 'Runner-ups']
    
    # Merge data
    merged = pd.merge(winners, runners, on='Country', how='outer').fillna(0)
    merged['Total Finals'] = merged['Wins'] + merged['Runner-ups']
    
    return merged

choropleth_data = prepare_choropleth_data(worldcup_df)

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Define app layout
app.layout = dbc.Container([
    html.H1("FIFA World Cup Winners Dashboard", className="mb-4 text-center"),
    
    dbc.Row([
        dbc.Col([
            html.H3("World Cup Winners Choropleth Map", className="text-center"),
            dcc.Dropdown(
                id='map-type-dropdown',
                options=[
                    {'label': 'Total Wins', 'value': 'Wins'},
                    {'label': 'Total Runner-ups', 'value': 'Runner-ups'},
                    {'label': 'Total Finals Appearances', 'value': 'Total Finals'}
                ],
                value='Wins',
                clearable=False,
                className="mb-3"
            ),
            dcc.Graph(id='world-map')
        ], width=12, lg=6),
        
        dbc.Col([
            html.H3("World Cup Statistics", className="text-center"),
            dcc.Tabs(id='tabs', value='tab-1', children=[
                dcc.Tab(label='Winners', value='tab-1'),
                dcc.Tab(label='Year Selection', value='tab-2'),
            ]),
            html.Div(id='tabs-content')
        ], width=12, lg=6)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.H4("World Cup Winners Timeline", className="text-center mt-4"),
            dcc.Graph(
                figure=px.bar(
                    worldcup_df, 
                    x='Year', 
                    y=[1]*len(worldcup_df), 
                    color='Winner',
                    title='World Cup Winners by Year',
                    labels={'Winner': 'Country'},
                    height=400
                ).update_layout(showlegend=True, yaxis_visible=False)
            )
        ], width=12)
    ])
], fluid=True)

# Callback for tabs
@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value')
)
def render_tab_content(tab):
    if tab == 'tab-1':
        return dbc.Card([
            dbc.CardBody([
                html.H4("View World Cup Winners", className="card-title"),
                dcc.Dropdown(
                    id='country-dropdown',
                    options=[{'label': country, 'value': country} 
                             for country in sorted(worldcup_df['Winner'].unique())],
                    placeholder="Select a country...",
                    className="mb-3"
                ),
                html.Div(id='country-stats-output')
            ])
        ])
    elif tab == 'tab-2':
        return dbc.Card([
            dbc.CardBody([
                html.H4("View World Cup by Year", className="card-title"),
                dcc.Dropdown(
                    id='year-dropdown',
                    options=[{'label': year, 'value': year} 
                             for year in sorted(worldcup_df['Year'], reverse=True)],
                    placeholder="Select a year...",
                    className="mb-3"
                ),
                html.Div(id='year-stats-output')
            ])
        ])

# Callback for choropleth map
@app.callback(
    Output('world-map', 'figure'),
    Input('map-type-dropdown', 'value')
)
def update_choropleth(map_type):
    fig = px.choropleth(
        choropleth_data,
        locations="Country",
        locationmode="country names",
        color=map_type,
        hover_name="Country",
        hover_data={"Wins": True, "Runner-ups": True, "Total Finals": True},
        color_continuous_scale=px.colors.sequential.Plasma,
        title=f"World Cup {map_type} by Country"
    )
    
    fig.update_layout(
        margin={"r":0,"t":30,"l":0,"b":0},
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular'
        )
    )
    
    return fig

# Callback for country stats
@app.callback(
    Output('country-stats-output', 'children'),
    Input('country-dropdown', 'value')
)
def update_country_stats(country):
    if not country:
        return html.P("Select a country to see its World Cup winning statistics.")
    
    wins = worldcup_df[worldcup_df['Winner'] == country]
    runners = worldcup_df[worldcup_df['Runner-up'] == country]
    
    win_years = ", ".join(map(str, sorted(wins['Year'].tolist())))
    runner_years = ", ".join(map(str, sorted(runners['Year'].tolist()))) if not runners.empty else "None"
    
    return dbc.ListGroup([
        dbc.ListGroupItem(f"Total Wins: {len(wins)}"),
        dbc.ListGroupItem(f"Years Won: {win_years}"),
        dbc.ListGroupItem(f"Total Runner-ups: {len(runners)}"),
        dbc.ListGroupItem(f"Years as Runner-up: {runner_years}"),
        dbc.ListGroupItem(f"Total Finals: {len(wins) + len(runners)}")
    ])

# Callback for year stats
@app.callback(
    Output('year-stats-output', 'children'),
    Input('year-dropdown', 'value')
)
def update_year_stats(year):
    if not year:
        return html.P("Select a year to see the World Cup results for that year.")
    
    data = worldcup_df[worldcup_df['Year'] == year].iloc[0]
    
    return dbc.ListGroup([
        dbc.ListGroupItem(f"Year: {year}"),
        dbc.ListGroupItem(f"Host Country: {data['Host']}"),
        dbc.ListGroupItem(f"Winner: {data['Winner']}"),
        dbc.ListGroupItem(f"Runner-up: {data['Runner-up']}"),
        dbc.ListGroupItem(f"Final Score: {data['Score']}")
    ])

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
