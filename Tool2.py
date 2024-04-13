from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import psycopg2
import pandas as pd
import dask.dataframe as dd
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

    # Perform necessary data processing and plotting here
    # Example:
    # df['date_time'] = pd.to_datetime(df['date_time'])
    # ...

    # Save the plots as a PDF file with the district name
    output_file = f"{selected_district.lower()}_crime_distribution.pdf"
    plt.savefig(output_file)
    plt.close()
    return output_file

@app.route('/download/<district>', methods=['GET'])
def download_pdf(district):
    output_file = generate_plots(district)
    if output_file:
        return send_file(output_file, as_attachment=True, download_name=f"{district}_crime_distribution.pdf")
    else:
        return jsonify({"error": "No data available or invalid district"}), 404
