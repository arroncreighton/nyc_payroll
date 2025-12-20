📄 README.md Template: NYC 2025 Payroll Dashboard
# NYC 2025 Payroll Dashboard
This is an interactive web dashboard built using Dash (Plotly/Python) that provides real-time analytics and visualizations of the New York City Administration for Children's Services (ACS) payroll data. Users can filter data by borough to analyze salary distributions, average pay, and top-paid or most common job titles.

🚀 Features
Borough Filtering: Instantly filter all charts and metrics by selecting one of the five NYC boroughs or "All Boroughs."

Key Salary Metrics: Displays calculated metrics for the selected borough:

Total Employee Headcount

Average, Median, Minimum, and Maximum Base Salary

Top Titles by Average Salary: Horizontal bar chart showing the top 10 job titles ranked by average salary.

Top Titles by Headcount: Horizontal bar chart showing the top 10 job titles ranked by the number of employees.

Salary Distribution: Histogram visualizing the frequency distribution of salaries across the selected borough.

📚 Data Source
The data used for this dashboard is accessed directly from the official NYC Open Data API.

Dataset: NYC ACS Payroll Data

API Endpoint: https://data.cityofnewyork.us/resource/k397-673e.json

The script uses the requests library to fetch the latest payroll records upon startup.

🛠️ Code Structure
app.py: The main Python file containing the Dash application logic, API call, data preprocessing, layout definition, and callback functions for interactivity.

requirements.txt: List of all required Python libraries.

✨ Future Enhancements
Add a Salary Range Slider to filter data based on minimum and maximum pay.

Implement a Job Title Search Bar to quickly filter the titles displayed in the bar charts.

Add Data Cleaning steps for title standardization (e.g., mapping abbreviations) to improve aggregation quality.

Author: Arron Creighton 
