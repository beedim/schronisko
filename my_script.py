

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import request, send_file
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sshtunnel import SSHTunnelForwarder
import pymysql
from io import BytesIO

app = Flask(__name__)


ss = {'A': ['bee_dmy', 'bee_dmy' ], 'B': ['one', 'two']}
data = pd.DataFrame(ss)

ss2 = {'B': ['one', 'two' ], 'C': ["scripts/one.txt", "scripts/fiction.txt"]}
data2 = pd.DataFrame(ss2)
                                   
ss3 = {'A': ['bee_dmy'  ], 'B': [2]}
data3 = pd.DataFrame(ss3)    


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
    qq = request.form.get('var_value')
  
    if qq and qq.strip():
      pairs = qq.split(';')

      for pair in pairs:
          var_name, var_val = pair.strip().split('=')
          var_name = var_name.strip() 
          var_val = var_val.strip()

      if var_val.isdigit():  
          var_val = int(var_val)
      elif var_val.startswith("'") and var_val.endswith("'"):
          var_val = var_val[1:-1]

      globals()[var_name] = var_val


  

    if username not in user_state:
        return jsonify({"error": "Invalid user session."}), 400

    try:
        filtered_valuess = data2[data2["B"] == selected_value]["C"].tolist()[0]


        filename = filtered_valuess
        with open(filename, 'r') as file:
            script_content = file.read()
        exec(script_content,globals())
      
        #exec(filtered_valuess, globals())
        # Save the result as an Excel file
        file_path = f"{username}_result.xlsx"
        k1.to_excel(file_path, index=False)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
              k1.to_excel(writer, index=False, sheet_name="Results")
        output.seek(0)
            # Send the file as a download
        return send_file(
                output,
                as_attachment=True,
                download_name=file_path,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/run_custom', methods=['POST'])
def run_custom():
    username = request.form.get('username')
    sql_query = request.form.get('query').strip()
    base_name = request.form.get('selected_base')

    if user_state[username]["filtered_values"] != 2:
        return jsonify({"error": "Не маєш прав."}), 403

    try:
        if base_name == 'MySQL':
          
            Cursor.execute(sql_query)
            k1 = pd.read_sql_query(sql_query, connection)
            file_path = f"{username}_custom_query.xlsx"
            k1.to_excel(file_path, index=False)
        else:
            from clickhouse_driver import Client
            host = '5.43.226.89'
            port = 9000
            database='statistic'
            client = Client(host, port, database)
          
            result,columns = client.execute(sql_query, with_column_types = True)
            col = []
            for desc in columns:
                col.append(desc[0])
            k1 = pd.DataFrame(result, columns = col)
            file_path = f"{username}_custom_query.xlsx"
            k1.to_excel(file_path, index=False)
        


        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
              k1.to_excel(writer, index=False, sheet_name="Results")
        output.seek(0)
            # Send the file as a download
        return send_file(
                output,
                as_attachment=True,
                download_name=file_path,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

