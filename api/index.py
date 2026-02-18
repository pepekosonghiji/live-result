import os, re, httpx, datetime
from flask import Flask, render_template, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__, template_folder='../templates')

TARGET_POOLS = {
    'CAMBODIA': 'p3501', 'SYDNEY LOTTO': 'p2262', 'HONGKONG LOTTO': 'p2263', 
    'HONGKONG POOLS': 'HK_SPECIAL', 'SINGAPORE POOLS': 'p2264',
    'DANANG':'p22816', 'PENANG':'p22817', 'PHUKET':'p28435', 'MACAU 4D': 'm17'
}

def fetch_results(market_name, market_code):
    data_final = {"res": "----", "date": "-"}
    
    if market_code == "HK_SPECIAL":
        url = "https://tabelsemalam.com/"
    elif market_code == 'm17':
        url = "https://9yjus6z6kz.salamrupiah.com/history/result-mobile/m17-pool-1"
    else:
        url = f"https://dk9if7ik34.salamrupiah.com/history/result-mobile/{market_code}-pool-1"

    try:
        with httpx.Client(timeout=15.0, verify=False) as client:
            r = client.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            table = soup.find('table')
            if table:
                rows = table.find('tbody').find_all('tr')
                if rows:
                    tds = rows[0].find_all('td')
                    
                    # LOGIKA HK POOLS (Ambil Kolom Indeks 1 sesuai <th>HK)
                    if market_code == "HK_SPECIAL":
                        if len(tds) >= 2:
                            # Mengambil kolom HK (indeks 1)
                            res_val = tds[1].text.strip()
                            data_final["res"] = res_val if res_val != "-" else "WAIT"
                            data_final["date"] = tds[0].text.strip()
                    
                    # LOGIKA MACAU (Kolom 2)
                    elif market_code == 'm17':
                        if len(tds) >= 3:
                            data_final["res"] = re.sub(r'\D', '', tds[2].text.strip())
                            data_final["date"] = tds[0].text.strip()
                    
                    # LOGIKA UMUM (Kolom 3)
                    else:
                        if len(tds) >= 4:
                            data_final["res"] = re.sub(r'\D', '', tds[3].text.strip())
                            data_final["date"] = tds[0].text.strip()
    except:
        pass
    return data_final

@app.route('/')
def index():
    now = datetime.datetime.now()
    tgl_global = now.strftime("%d %B %Y | %H:%M:%S")
    
    final_results = []
    for name, code in TARGET_POOLS.items():
        data = fetch_results(name, code)
        final_results.append({
            "name": name, 
            "result": data["res"], 
            "date": data["date"]
        })
    
    return render_template('index.html', data=final_results, current_time=tgl_global)

app_handler = app
