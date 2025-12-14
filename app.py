import requests
import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc, Input, Output
import numpy as np # Needed for histogram binning/range

# --- Data Loading ---
api_url = "https://data.cityofnewyork.us/resource/k397-673e.json"
response = requests.get(api_url)
data = [] 

if response.status_code == 200:
    print("Request successful!")
    data = response.json()
    print(f"Loaded {len(data)} records.")
else:
    print(f"Request failed with status code: {response.status_code}")
    
df = pd.DataFrame() 

if data:
    df = pd.DataFrame(data)

    # Data Preparation: Using Correct API Column Names
    df['base_salary'] = pd.to_numeric(df['base_salary'], errors='coerce')
    df.dropna(subset=['base_salary', 'work_location_borough', 'title_description'], inplace=True)
    
    # Get the unique borough names for the dropdown
    borough_options = [{'label': b, 'value': b} for b in sorted(df['work_location_borough'].unique())]
    borough_options.insert(0, {'label': 'All Boroughs', 'value': 'All'})

    app = dash.Dash(__name__)

    # --- 2. Define the Layout with All Metrics and Charts ---
    app.layout = html.Div([
        html.H1("NYC ACS Payroll Dashboard"),
        
        # Dropdown for Borough Selection
        html.Div([
            html.Label("Select Borough:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='borough-dropdown',
                options=borough_options,
                value='All',
                clearable=False
            ),
        ], style={'width': '50%', 'padding': '10px'}),
        
        html.Hr(),

        # Container for Metrics (5 Boxes)
        html.Div(id='metrics-container', children=[
            # 1. Total Employee Count (Headcount)
            html.Div(
                id='total-headcount-metric', 
                style={'border': '1px solid #ccc', 'padding': '10px', 'margin': '5px', 'flex': 1}
            ),
            # 2. Average Salary
            html.Div(
                id='avg-salary-metric', 
                style={'border': '1px solid #ccc', 'padding': '10px', 'margin': '5px', 'flex': 1}
            ),
            # 3. Median Salary
            html.Div(
                id='median-salary-metric', 
                style={'border': '1px solid #ccc', 'padding': '10px', 'margin': '5px', 'flex': 1}
            ),
            # 4. Minimum Salary
            html.Div(
                id='min-salary-metric',
                style={'border': '1px solid #ccc', 'padding': '10px', 'margin': '5px', 'flex': 1}
            ),
            # 5. Maximum Salary
            html.Div(
                id='max-salary-metric',
                style={'border': '1px solid #ccc', 'padding': '10px', 'margin': '5px', 'flex': 1}
            ),
        ], style={'display': 'flex', 'flexDirection': 'row', 'marginBottom': '20px'}),
        
        html.Hr(),

        # Container for Charts (2 Charts arranged side-by-side)
        html.Div(children=[
            # Chart 1: Average Salary per Title
            html.Div(dcc.Graph(id='average-salary-chart'), style={'flex': 1, 'padding': '10px'}),
            
            # Chart 2: Top Titles by Headcount (Headcount Distribution)
            html.Div(dcc.Graph(id='headcount-distribution-chart'), style={'flex': 1, 'padding': '10px'}),
        ], style={'display': 'flex', 'flexDirection': 'row', 'marginBottom': '20px'}),

        # Chart 3: Salary Distribution (Histogram)
        html.Div(dcc.Graph(id='salary-distribution-chart')),
    ])

    # --- 3. The Central Callback Function ---
    @app.callback(
        # 3 Chart Outputs
        Output('average-salary-chart', 'figure'),
        Output('headcount-distribution-chart', 'figure'),
        Output('salary-distribution-chart', 'figure'),
        # 5 Metric Outputs
        Output('total-headcount-metric', 'children'),
        Output('avg-salary-metric', 'children'),
        Output('median-salary-metric', 'children'),
        Output('min-salary-metric', 'children'),
        Output('max-salary-metric', 'children'),
        [Input('borough-dropdown', 'value')]
    )
    def update_dashboard(selected_borough):
        
        # --- Step 1: Filter Data ---
        if selected_borough == 'All':
            filtered_df = df
            borough_label = 'All Boroughs'
        else:
            filtered_df = df[df['work_location_borough'] == selected_borough]
            borough_label = selected_borough

        # --- Step 2: Calculate Metrics ---
        headcount = len(filtered_df)
        avg_salary = filtered_df['base_salary'].mean()
        median_salary = filtered_df['base_salary'].median()
        min_salary = filtered_df['base_salary'].min()
        max_salary = filtered_df['base_salary'].max()

        # Format metrics for display
        headcount_text = [
            html.H3("Total Employees", style={'textAlign': 'center'}),
            html.P(f"{headcount:,.0f}", style={'fontSize': '24px', 'fontWeight': 'bold', 'textAlign': 'center'})
        ]
        avg_text = [
            html.H3("Average Salary", style={'textAlign': 'center'}),
            html.P(f"${avg_salary:,.2f}", style={'fontSize': '24px', 'fontWeight': 'bold', 'textAlign': 'center'})
        ]
        median_text = [
            html.H3("Median Salary", style={'textAlign': 'center'}),
            html.P(f"${median_salary:,.2f}", style={'fontSize': '24px', 'fontWeight': 'bold', 'textAlign': 'center'})
        ]
        min_text = [
            html.H3("Minimum Salary", style={'textAlign': 'center'}),
            html.P(f"${min_salary:,.2f}", style={'fontSize': '24px', 'fontWeight': 'bold', 'textAlign': 'center'})
        ]
        max_text = [
            html.H3("Maximum Salary", style={'textAlign': 'center'}),
            html.P(f"${max_salary:,.2f}", style={'fontSize': '24px', 'fontWeight': 'bold', 'textAlign': 'center'})
        ]

        # --- Step 3: Create Charts ---

        # CHART 1: Average Salary per Title (Your original chart)
        avg_salary_df = filtered_df.groupby('title_description')['base_salary'].mean().reset_index(name='Average Salary')
        avg_salary_df = avg_salary_df.sort_values(by='Average Salary', ascending=False).head(10)
        
        fig_avg_salary = px.bar(
            avg_salary_df, 
            x='Average Salary', y='title_description', 
            orientation='h',
            title=f'Top 10 Average Salaries per Job Title in {borough_label}',
            labels={'Average Salary': 'Average Annual Salary', 'title_description': 'Job Title'}
        )
        fig_avg_salary.update_layout(yaxis={'categoryorder':'total ascending'})

        # CHART 2: Headcount Distribution (Top 10 Titles by Employee Count)
        headcount_df = filtered_df.groupby('title_description').size().reset_index(name='Employee Count')
        headcount_df = headcount_df.sort_values(by='Employee Count', ascending=False).head(10)

        fig_headcount = px.bar(
            headcount_df, 
            x='Employee Count', y='title_description', 
            orientation='h',
            title=f'Top 10 Titles by Employee Count in {borough_label}',
            labels={'Employee Count': 'Total Employees', 'title_description': 'Job Title'},
            color_discrete_sequence=px.colors.qualitative.Safe # Use a different color set
        )
        fig_headcount.update_layout(yaxis={'categoryorder':'total ascending'})

        # CHART 3: Salary Distribution (Histogram)
        # Use bins based on the full data range for consistent comparison across boroughs
        min_full_salary = df['base_salary'].min()
        max_full_salary = df['base_salary'].max()
        salary_range = max_full_salary - min_full_salary
        # Set bin size to 10k for reasonable granularity
        n_bins = int(salary_range / 10000) 
        
        fig_hist = px.histogram(
            filtered_df, 
            x='base_salary',
            nbins=n_bins,
            range_x=[min_full_salary, max_full_salary], # Keep the x-axis consistent
            title=f'Salary Distribution in {borough_label}',
            labels={'base_salary': 'Base Salary', 'count': 'Number of Employees'}
        )
        fig_hist.update_traces(marker_line_width=1, marker_line_color='white')
        
        # --- Step 4: Return all 8 outputs (3 figures, 5 metric texts) ---
        return (
            fig_avg_salary, 
            fig_headcount, 
            fig_hist,
            headcount_text, 
            avg_text, 
            median_text, 
            min_text, 
            max_text
        )

    # Run the app
    if __name__ == '__main__':
        app.run(debug=True)
else:
    print("Cannot run the Dash application because data could not be loaded from the API.")