import os
import pandas as pd
import pymysql
from flask import Flask, request, render_template, send_file
from sshtunnel import SSHTunnelForwarder
from io import BytesIO

app = Flask(__name__)

# SSH and database credentials
SQL_HOST = ('176.74.219.82', 55567)
SERVER_USER = 'api.speedy.company'
PRIVATE_KEY = 'dimab_key'
SQL_USER = 'speedypaper'
DB_PASSWORD = '9MT8suTX8CB4q3E'
DB_NAME = 'speedypaper'

# Start the SSH tunnel
server = SSHTunnelForwarder(
    SQL_HOST,
    ssh_username=SERVER_USER,
    ssh_pkey=PRIVATE_KEY,
    remote_bind_address=('172.18.0.104', 3306)
)
server.start()

# Establish a MySQL connection
connection = pymysql.connect(
    host='127.0.0.1',
    user=SQL_USER,
    password=DB_PASSWORD,
    db=DB_NAME,
    port=server.local_bind_port
)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get the SQL query from the form
        sql_query = request.form.get("sql_query")

        try:
            # Execute the query and fetch the results
            df = pd.read_sql_query(sql_query, connection)

            # Save the results to an in-memory file
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Results")
            output.seek(0)

            # Send the file as a download
            return send_file(
                output,
                as_attachment=True,
                download_name="query_results.xlsx",
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            # Handle errors gracefully
            return f"Error: {str(e)}"

    # Render the input form
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
