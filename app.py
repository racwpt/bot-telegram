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

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)