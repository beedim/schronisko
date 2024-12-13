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











from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sshtunnel import SSHTunnelForwarder
import pymysql


app = Flask(__name__)


scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
client = gspread.authorize(credentials)
sheet = client.open_by_key("1u7GAOMMJxajJF3v81E2Vn327UF6_7Q-Pu6lBnOfZwtc").worksheet("1")
data = pd.DataFrame(sheet.get_all_records())

sheet2 = client.open_by_key("1u7GAOMMJxajJF3v81E2Vn327UF6_7Q-Pu6lBnOfZwtc").worksheet("2")
data2 = pd.DataFrame(sheet2.get_all_records())

sheet3 = client.open_by_key("1u7GAOMMJxajJF3v81E2Vn327UF6_7Q-Pu6lBnOfZwtc").worksheet("3")
data3 = pd.DataFrame(sheet3.get_all_records())


SQL_HOST = ('176.74.219.82', 55567)
SERVER_USER = 'api.speedy.company'
PRIVATE_KEY = 'dimab_key'
SQL_USER = 'speedypaper'
server = SSHTunnelForwarder(
    SQL_HOST,
    ssh_username=SERVER_USER,
    ssh_pkey=PRIVATE_KEY,
    remote_bind_address=('172.18.0.104', 3306)
)
server.start()
connection = pymysql.connect(
    host='127.0.0.1',
    user=SQL_USER,
    password='9MT8suTX8CB4q3E',
    db='speedypaper',
    port=server.local_bind_port
)
Cursor = connection.cursor()

user_state = {}

@app.route('/')
def index():
    return render_template('index.html')  # HTML form to enter username

@app.route('/process_username', methods=['POST'])
def process_username():
    username = request.form.get('username').strip()
    if not username:
        return jsonify({"error": "Введіть ім'я користувача."}), 400

    filtered_values = data3[data3["A"] == username]["B"].tolist()
    if not filtered_values:
        return jsonify({"error": "Користувача не знайдено."}), 404

    user_state[username] = {
        "username": username,
        "filtered_values": filtered_values[0],
        "algorithm_type": None
    }

    return render_template('choose_algorithm.html', username=username)  # Page to choose algorithm

@app.route('/select_algorithm', methods=['POST'])
def select_algorithm():
    username = request.form.get('username')
    algorithm_type = request.form.get('algorithm_type')

    if username not in user_state:
        return jsonify({"error": "Invalid user session."}), 400

    user_state[username]["algorithm_type"] = algorithm_type

    if algorithm_type == "direct_algorithm":
        filtered_values2 = data[data["A"] == username]["B"].tolist()
        return render_template('select_package.html', username=username, options=filtered_values2)  # Page to select package
    elif algorithm_type == "custom_function":
        return render_template('sql_interface.html', username=username)  # Page for SQL query
    else:
        return jsonify({"error": "Invalid algorithm type."}), 400

@app.route('/run_direct_algorithm', methods=['POST'])
def run_direct_algorithm():
    username = request.form.get('username')
    selected_value = request.form.get('selected_value')

    if username not in user_state:
        return jsonify({"error": "Invalid user session."}), 400

    try:
        filtered_valuess = data2[data2["B"] == selected_value]["C"].tolist()[0]
        exec(filtered_valuess, globals())
        # Save the result as an Excel file
        file_path = f"{username}_result.xlsx"
        k1.to_excel(file_path, index=False)
        return jsonify({"message": f"Забери результат у файлі {file_path}."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/run_custom', methods=['POST'])
def run_custom():
    username = request.form.get('username')
    sql_query = request.form.get('query').strip()

    if user_state[username]["filtered_values"] != 2:
        return jsonify({"error": "Не маєш прав."}), 403

    try:
        Cursor.execute(sql_query)
        k1 = pd.read_sql_query(sql_query, connection)
        file_path = f"{username}_custom_query.xlsx"
        k1.to_excel(file_path, index=False)
        return jsonify({"message": f"Забери результат у файлі {file_path}."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

