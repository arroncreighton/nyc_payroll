import requests
import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc, Input, Output

# The URL of the API endpoint you want to access
api_url = "https://data.cityofnewyork.us/resource/k397-673e.json"

# Make the GET request
response = requests.get(api_url)
if response.status_code == 200:
    print("Request successful!")
else:
    print(f"Request failed with status code: {response.status_code}")
if response.status_code == 200:
    # Convert JSON response into a Python dictionary/list
    data = response.json()
    
    # You can now work with the data like any other Python structure
    print(data)
df = pd.DataFrame(data)

# Ensure the 'Salary' column is numeric and handle potential missing values
df['base_salary'] = pd.to_numeric(df['base_salary'], errors='coerce')
df.dropna(subset=['base_salary', 'work_location_borough', 'title_description'], inplace=True)

# Get the unique borough names for the dropdown
borough_options = [{'label': b, 'value': b} for b in sorted(df['work_location_borough'].unique())]
borough_options.insert(0, {'label': 'All Boroughs', 'value': 'All'}) # Add an option to view all

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("NYC ACS Payroll Dashboard"),
    
    # Dropdown for Borough Selection
    html.Div([
        html.Label("Select Borough:"),
        dcc.Dropdown(
            id='borough-dropdown',
            options=borough_options,
            value='All', # Default selected value
            clearable=False
        ),
    ], style={'width': '50%', 'padding': '10px'}),
    
    html.Hr(),
    
    # Graph to display the average salary chart
    dcc.Graph(id='average-salary-chart')
])

@app.callback(
    Output('average-salary-chart', 'figure'),
    [Input('borough-dropdown', 'value')]
)
def update_chart(selected_borough):
    # Step 1: Filter the DataFrame based on the selected borough
    if selected_borough == 'All':
        filtered_df = df
    else:
        filtered_df = df[df['work_location_borough'] == selected_borough]
        
    # Step 2: Calculate the average salary per job title for the filtered data
    avg_salary_df = filtered_df.groupby('title_description')['base_salary'].mean().reset_index(name='Average Salary')
    
    # Step 3: Sort the data (e.g., top 10 highest paid titles) and create the plot
    # You might want to filter for the top N titles or titles with many employees for clarity
    avg_salary_df = avg_salary_df.sort_values(by='Average Salary', ascending=False).head(10)
    
    # Create the Plotly Express bar chart
    fig = px.bar(
        avg_salary_df, 
        x='Average Salary', 
        y='title_description',
        orientation='h',
        title=f'Top 10 Average Salaries per Job Title in {selected_borough}',
        labels={'Average Salary': 'Average Annual Salary', 'title_description': 'title_description'}
    )
    
    # Customize layout for better readability
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
