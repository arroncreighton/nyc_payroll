import requests
import pandas as pd
import plotly
import dash
from dash import html
from dash import dcc

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
df.head(10)
