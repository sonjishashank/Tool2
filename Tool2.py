from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Connect to PostgreSQL database
def connect_to_postgresql():
    connection = psycopg2.connect(
        host="dpg-cobrpren7f5s73ftpqrg-a.oregon-postgres.render.com",
        database="sheshank_sonji",
        user="sheshank_sonji_user",
        password="Lo2Ze5zVZSRPGxDLCg5WAKUXUfxo7rrZ"
    )
    return connection

# Function to generate plots and save them to a PDF file
def generate_plots(selected_district):
    # Connect to PostgreSQL
    conn = connect_to_postgresql()

    # Query data from PostgreSQL
    query = f"SELECT * FROM tool2 WHERE district_name = '{selected_district}';"
    df = pd.read_sql_query(query, conn)

    # Close the connection
    conn.close()

    if df.empty:
        return None  # No data available

    # Filter the DataFrame based on the selected district
    df_selected_district = df[df['District_Name'] == selected_district]

    # Check if the selected district has any data
    if len(df_selected_district.index) == 0:
        return {"error": "No data available for the selected district"}

    # Group the filtered DataFrame by 'UnitName' and 'beat' and calculate the size of each group
    df_crime = df_selected_district.groupby(['UnitName', 'beat']).size().reset_index().rename(columns={0: 'crime_count'}).compute()

    # List of unit names to plot
    unit_names_to_plot = df_crime['UnitName'].unique()

    # Create subplots for each unit name
    num_rows = len(unit_names_to_plot)
    fig, axes = plt.subplots(num_rows, 1, figsize=(10, num_rows*5))

    # Iterate over each unit name and plot beat-wise crime distribution
    for i, unit_name in enumerate(unit_names_to_plot):
        # Filter data for the current unit name
        data_unit = df_crime[df_crime['UnitName'] == unit_name]
        
        # Extract beat and crime count data
        x = data_unit['beat']
        y = data_unit['crime_count']

        # Plot beat-wise crime distribution for the current unit name
        axes[i].bar(x, y)
        axes[i].set_title(unit_name)  # Set subplot title as unit name
        axes[i].set_xlabel('Beat')
        axes[i].set_ylabel('Number of Crimes')
        axes[i].tick_params(axis='x', rotation=90)  
        axes[i].grid(which='both', linestyle=':')

    # Adjust layout
    plt.tight_layout()

    # Save the plot to a PDF file with the district name
    output_dir = 'static'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file = os.path.join(output_dir, f"{selected_district.lower()}_crime_distribution.pdf")
    plt.savefig(output_file)
    plt.close()

    return output_file

# Route for downloading the PDF file
@app.route('/download/<district>', methods=['GET'])
def download_pdf(district):
    output_file = generate_plots(district)
    if output_file:
        return send_file(output_file, as_attachment=True, download_name=f"{district}_crime_distribution.pdf")
    else:
        return jsonify({"error": "No data available or invalid district"}), 404


