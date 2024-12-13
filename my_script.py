

from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sshtunnel import SSHTunnelForwarder
import pymysql


app = Flask(__name__)


scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name({
  "type": "service_account",
  "project_id": "pythontest-349818",
  "private_key_id": "22361a42675ad9a7eb77942430753cfb40950d5d",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDavEJZY0bj8jsr\nC/v+qJ9e79pFYL0kVsxKAn8InUCMn3VxGN1IBSUYye/1+z3l1EOocgtBJ5Qohu1f\naYvI+HyyrRj89G6gMVOa6SNYf9CMN0kibYU3JMKKx4dpXJK3mIOu6ALs2ytnP7w8\nz2b4OWQmxd6Zm0kcnDdvA6sacBY6VfxpsfTW5BW3ZhlIVSAu9R6+DPCoFH9LkSIG\ntLYDvT3ZcpFl84FkXfcNiY/W8HdR/pZHT5lcc67mYtBcm8e+Jai2VCMCSLUSuPr8\nh1plsrDzLMFHDgLW4+8OUXAXqPEN3Ax2W9J7/StNslEhTy4j6pPjkPc5ctCm0a7Q\nB8l9D9hPAgMBAAECggEALk3TF9whyihhqSOw1UB5+F17DdvEPniXZ4VuwfKUExDA\nilASq+fW6g/5mc91U31jUznNMx4/SXMCtgOAYWtk7mghVY8jCgtXIQCAiIAKNFyR\nwVWA8WL5QeqqOj4sGuyQ18pqsBxXbFR8Mz1OlXaEwoZ5sHfEeueA/qG+q2qV8gQU\njFjBCNCJcIOViouw+ducbZzAMydAjpKV76i8IfIkr5E/DmTjStGX/jb0nlNylWwq\nH2++lQSeukynnZElVGIycTwpQ7Qw0ZjZD16F24Fk9AzlglcEIes3bFMVa3+t0FbL\nrvVVofam5OdWhvgY3VddweOAvEcVVRh88R25qGRcMQKBgQDhdDXnLJuvuxTO7i0O\ntnw2SYTdJf6AKtho4Sgyk3WuZagYUU9LVLLPKVtR5RHBb6ScuThNtz2kw24HQQ0F\ngYmTKw0TVvCRer5BIMbsPzN8YtbimvioOkv+3QQ9G71PqVXMiSn5aaEknqo154g2\nzG2ndmhLqeQzL0MEkyLqnL+oPwKBgQD4XwSMXhwbmlWpo2F5MN2wpEPEyrJ6in9h\n0OLKq8GCmKai06JvsZAujAZn/iO+JOCOkN7bvFQJ6qaV71c8u5b3gTW5oyScM+ih\nZ6gWWmYjcOLRVgCWE24XTUHDa0d0CUZpvovuXD8+MAmjoTXJEGxhDOWaOo8qqW2n\nIsyXY6hL8QKBgBRmWYJDbQrnmKhosLcGGBMpb9Y6295pAg/rX6HD6gAPvrgEk3Iz\nhcJs8ZBlc8fW/EQaFlgh3ngMHuaVIkJ/SB2C5bn8QeRIAPMPrjAuP9BfeSYj85/1\nNm8nPHzzB5wvrE3Hk3636hbQLIKYIqEiukFO230NMFLZUe0WCzDDYiwtAoGAYCKv\nKQHYUVrYo3PI69bdSF0cmhR3JvVqvtrSne4DVeBuR4IxUphhHZM3e5MkFJpDjQtI\nJ7dqs/fuiQR+ONTHZ3/M4tDh/9Ab0DXGGvjcpgUw1iQ6z9wvdbeCp/hjTOe2KIIH\nubhdBl4jrQFeRzgjKyGJ0buu5K118waGOGbropECgYAe9JjoEXdMSwIvzzy/j0kG\n60EY4xedLKtOvhc3ktmy0IqcZu/foVm2p+geFbD2cvbeILg+Gmq9w6DCr+cI62Oi\ngc/bmbxPdl5cM7HjV5Fp0F6A3dqAhsDeqs2ZNx7cxn0qf25KOJS6ud8f4HmC8TLC\nkNQy1UpAnc8c9GSoCtEAkA==\n-----END PRIVATE KEY-----\n",
  "client_email": "vidpravkatest@pythontest-349818.iam.gserviceaccount.com",
  "client_id": "113201679112522439937",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/vidpravkatest%40pythontest-349818.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}, scope)
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

