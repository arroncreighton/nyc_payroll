import requests
import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc, Input, Output

# --- 1. Data Loading (Fix #1: Filtering by Fiscal Year) ---
# We filter for 2024 to ensure we get as many agencies as possible within the 50k limit.
api_url = "https://data.cityofnewyork.us/resource/k397-673e.json?fiscal_year=2025&$limit=70000"

print("Fetching 2024 Payroll Data...")
response = requests.get(api_url)
data = [] 

if response.status_code == 200:
    data = response.json()
    print(f"Success! Loaded {len(data)} records for FY2024.")
else:
    print(f"Request failed: {response.status_code}")
    
df = pd.DataFrame() 

if data:
    df = pd.DataFrame(data)

    # --- 2. Data Preparation ---
    # Convert 'regular_gross_paid' to numeric
    df['regular_gross_paid'] = pd.to_numeric(df['regular_gross_paid'], errors='coerce')
    
    # Drop rows missing essential data for our filters and charts
    df.dropna(subset=['regular_gross_paid', 'work_location_borough', 'title_description', 'agency_name'], inplace=True)
    
    # Standardize names for consistency in the dropdowns
    df['work_location_borough'] = df['work_location_borough'].str.upper().str.strip()
    df['agency_name'] = df['agency_name'].str.upper().str.strip()
    
    # Options for Borough Filter
    borough_options = [{'label': b, 'value': b} for b in sorted(df['work_location_borough'].unique())]
    borough_options.insert(0, {'label': 'All Boroughs', 'value': 'All'})

    # Options for Agency Filter (Should now show many more agencies)
    agency_options = [{'label': a, 'value': a} for a in sorted(df['agency_name'].unique())]
    agency_options.insert(0, {'label': 'All Agencies', 'value': 'All'})

    app = dash.Dash(__name__)

    # --- 3. Layout ---
    app.layout = html.Div([
        html.H1("NYC FY2025 Payroll Analytics", style={'textAlign': 'center', 'color': '#2c3e50', 'marginTop': '20px'}),
        html.P("Analyzing Gross Pay across City Agencies", style={'textAlign': 'center', 'color': '#7f8c8d'}),
        
        # Filter Section
        html.Div([
            html.Div([
                html.Label("Borough Selection:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(id='borough-dropdown', options=borough_options, value='All', clearable=False),
            ], style={'width': '45%', 'display': 'inline-block', 'padding': '10px'}),
            
            html.Div([
                html.Label("Agency Selection:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(id='agency-dropdown', options=agency_options, value='All', clearable=False),
            ], style={'width': '45%', 'display': 'inline-block', 'padding': '10px'}),
        ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'borderRadius': '10px', 'margin': '20px', 'boxShadow': '0px 2px 4px rgba(0,0,0,0.1)'}),
        
        # Metric Summary
        html.Div(id='metrics-container', style={'display': 'flex', 'justifyContent': 'space-around', 'margin': '20px'}),
        
        # Charts
        dcc.Loading(
            type="circle",
            children=[
                html.Div([
                    html.Div(dcc.Graph(id='avg-gross-chart'), style={'width': '50%', 'display': 'inline-block'}),
                    html.Div(dcc.Graph(id='headcount-chart'), style={'width': '50%', 'display': 'inline-block'}),
                ]),
                html.Div([
                    dcc.Graph(id='dist-chart')
                ], style={'padding': '10px'})
            ]
        )
    ], style={'fontFamily': 'Arial, sans-serif', 'padding': '10px'})

    # --- 4. Callback ---
    @app.callback(
        [Output('avg-gross-chart', 'figure'),
         Output('headcount-chart', 'figure'),
         Output('dist-chart', 'figure'),
         Output('metrics-container', 'children')],
        [Input('borough-dropdown', 'value'),
         Input('agency-dropdown', 'value')]
    )
    def update_dashboard(borough, agency):
        # Filtering logic
        dff = df.copy()
        if borough != 'All':
            dff = dff[dff['work_location_borough'] == borough]
        if agency != 'All':
            dff = dff[dff['agency_name'] == agency]

        if dff.empty:
            return {}, {}, {}, [html.H3("No results found for this selection.", style={'color': '#e74c3c'})]

        # Calculate Summary Metrics
        summary_stats = [
            ('Employees', f"{len(dff):,}"),
            ('Avg Gross', f"${dff['regular_gross_paid'].mean():,.0f}"),
            ('Median Gross', f"${dff['regular_gross_paid'].median():,.0f}"),
            ('Max Gross', f"${dff['regular_gross_paid'].max():,.0f}")
        ]
        
        metrics_html = [
            html.Div([
                html.Span(label, style={'color': '#95a5a6', 'fontSize': '14px', 'textTransform': 'uppercase'}),
                html.H2(val, style={'margin': '5px 0 0 0', 'color': '#2980b9'})
            ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '8px', 'boxShadow': '2px 2px 10px #eee', 'minWidth': '200px'})
            for label, val in summary_stats
        ]

        # Figure 1: Average Gross Pay by Title
        top_avg = dff.groupby('title_description')['regular_gross_paid'].mean().nlargest(10).reset_index()
        fig_avg = px.bar(top_avg, x='regular_gross_paid', y='title_description', orientation='h',
                         title="Highest Average Gross Pay by Title",
                         labels={'regular_gross_paid': 'Avg Gross Pay ($)', 'title_description': ''},
                         template='plotly_white', color_discrete_sequence=['#3498db'])
        fig_avg.update_layout(yaxis={'categoryorder':'total ascending'})

        # Figure 2: Headcount by Title
        top_count = dff.groupby('title_description').size().nlargest(10).reset_index(name='count')
        fig_count = px.bar(top_count, x='count', y='title_description', orientation='h',
                           title="Highest Headcount by Title",
                           labels={'count': 'Number of Employees', 'title_description': ''},
                           template='plotly_white', color_discrete_sequence=['#2ecc71'])
        fig_count.update_layout(yaxis={'categoryorder':'total ascending'})

        # Figure 3: Gross Pay Distribution
        fig_dist = px.histogram(dff, x='regular_gross_paid', nbins=50,
                                title="Gross Pay Distribution",
                                labels={'regular_gross_paid': 'Gross Pay ($)'},
                                template='plotly_white', color_discrete_sequence=['#9b59b6'])
        fig_dist.update_layout(bargap=0.1)

        return fig_avg, fig_count, fig_dist, metrics_html

    if __name__ == '__main__':
        app.run(debug=True)
else:
    print("Could not load data. Check the API URL or your connection.")