from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def index():
    conn = sqlite3.connect("pelanggan.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pelanggan")
    data = cursor.fetchall()
    return render_template("index.html", data=data)

from flask import send_file
import pandas as pd

@app.route("/export")
def export():
    conn = get_db()  # atau psycopg2 kalau pakai PostgreSQL

    df = pd.read_sql("SELECT * FROM pelanggan", conn)

    file_path = "data_pelanggan.xlsx"
    df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
