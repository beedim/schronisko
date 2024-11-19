rom flask import Flask, request, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import requests
import json
import zipfile
import os
from datetime import datetime
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

PROXY_HOST = 'res.proxy-seller.com'
PROXY_PORT = 10000
PROXY_USER = '41b0ad102cea9a8c'
PROXY_PASS = 'RNW78Fm5'


def generate_proxy_plugin(PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS):
    """Generates a Chrome extension for proxy authentication."""
    manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
    """

    background_js = f"""
    var config = {{
            mode: "fixed_servers",
            rules: {{
              singleProxy: {{
                scheme: "https",
                host: "{PROXY_HOST}",
                port: parseInt({PROXY_PORT})
              }},
              bypassList: ["foobar.com"]
            }}
          }};
    chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
    function callbackFn(details) {{
        return {{
            authCredentials: {{
                username: "{PROXY_USER}",
                password: "{PROXY_PASS}"
            }}
        }};
    }}
    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {{urls: ["<all_urls>"]}},
                ['blocking']
    );
    """

    pluginfile = 'proxy_auth_plugin.zip'

    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return pluginfile


@app.route('/')
def home():
    """Render the home page."""
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process_domains():
    """Process the domains based on the selected action."""
    try:
        domains = request.form.get('domains').splitlines()
        action = request.form.get('action')

        if action == "check_spam":
            spam = []

            for domain in domains:
                driver = generate_selenium_driver()
                url = f'https://mxtoolbox.com/SuperTool.aspx?action=blacklist%3a{domain}&run=toolpage'
                driver.get(url)

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'tool-result-body'))
                )

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                result_text = soup.find('div', class_='tool-result-body').get_text()
                listed_count = int(result_text.split('Listed ')[1].split(' ')[0])
                spam.append([domain, listed_count])

                driver.quit()

            # Save to Excel
            df = pd.DataFrame(spam, columns=['Domain', 'Listed_count'])
            df = df[df['Listed_count'] == 0].drop(columns=['Listed_count'])
            filename = save_to_excel(df, "mxtoolbox_result")

            return jsonify({"status": "success", "message": f"Results saved to {filename}."})

        elif action == "get_ahrefs_domains":
            all_refdomains = []

            api_url = "https://api.ahrefs.com/v3/site-explorer/linkeddomains"
            api_key = "MwW6L33A0px09aTjCRhUdgd0TuVZyQ3ag2HfeK43"

            for domain in domains:
                params = {
                    'target': domain,
                    'limit': 1000,
                    'output': 'json',
                    'select': 'domain,dofollow_refdomains'
                }

                response = requests.get(api_url, headers={'Authorization': f'Bearer {api_key}'}, params=params)
                data = response.json()
                linkeddomains = data.get('linkeddomains', [])
                domain_list = [[item['domain'], item['dofollow_refdomains'], domain] for item in linkeddomains]
                all_refdomains.extend(domain_list)

            # Save to Excel
            df = pd.DataFrame(all_refdomains, columns=['Domain', 'Dofollow Refdomains', 'Donor'])
            df = df[df['Dofollow Refdomains'] > 10].drop(columns=['Dofollow Refdomains', 'Donor'])
            filename = save_to_excel(df, "ahrefs_result")

            return jsonify({"status": "success", "message": f"Results saved to {filename}."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


def generate_selenium_driver():
    """Sets up and returns a Selenium WebDriver with proxy."""
    pluginfile = generate_proxy_plugin(PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)
    service = Service(ChromeDriverManager().install())

    options = webdriver.ChromeOptions()
    options.add_extension(pluginfile)
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def save_to_excel(df, prefix):
    """Save a DataFrame to an Excel file."""
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f'{prefix}_{current_time}.xlsx'
    df.to_excel(filename, index=False)
    return filename


if __name__ == '__main__':
    app.run(debug=True)
