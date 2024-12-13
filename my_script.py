

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



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

