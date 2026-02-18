import os, re, httpx, datetime
from flask import Flask, render_template, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__, template_folder='../templates')

# Daftar Pasaran
TARGET_POOLS = {
    'CAMBODIA': 'p3501', 'SYDNEY LOTTO': 'p2262', 'HONGKONG LOTTO': 'p2263', 
    'HONGKONG POOLS': 'HK_SPECIAL', 'SINGAPORE POOLS': 'p2264',
    'DANANG':'p22816', 'PENANG':'p22817', 'PHUKET':'p28435', 'MACAU 4D': 'm17'
}

def fetch_results(market_code):
    results = []
    
    # --- KHUSUS MACAU 4D (M17) ---
    if market_code == 'm17':
        url = "https://9yjus6z6kz.salamrupiah.com/history/result-mobile/m17-pool-1"
        try:
            with httpx.Client(timeout=20.0, verify=False) as client:
                r = client.get(url)
                soup = BeautifulSoup(r.text, 'html.parser')
                table = soup.find('table', class_='table-history')
                if table:
                    rows = table.find('tbody').find_all('tr')
                    for row in rows:
                        tds = row.find_all('td')
                        if len(tds) >= 3:
                            val = re.sub(r'\D', '', tds[2].text.strip())
                            if len(val) == 4: results.append(val)
            if results: return results
        except:
            return []
    # -----------------------------

    # Jalur khusus HK
    if market_code == "HK_SPECIAL":
        try:
            with httpx.Client(timeout=10.0, verify=False) as client:
                r = client.get("https://tabelsemalam.com/")
                soup = BeautifulSoup(r.text, 'html.parser')
                table = soup.find('table')
                if table:
                    for row in table.find('tbody').find_all('tr'):
                        tds = row.find_all('td')
                        if len(tds) >= 2:
                            val = tds[1].text.strip()
                            if val.isdigit() and len(val) == 4: results.append(val)
            if results: return results
        except: pass

    # Jalur umum
    urls = [
        f"https://dk9if7ik34.salamrupiah.com/history/result-mobile/{market_code}-pool-1", 
        f"https://dk9if7ik34.salamrupiah.com/history/result-mobile/kia_{market_code}"
    ]
    for url in urls:
        try:
            with httpx.Client(timeout=10.0, verify=False) as client:
                r = client.get(url)
                soup = BeautifulSoup(r.text, 'html.parser')
                table = soup.find('table', class_='table-history')
                if table:
                    for row in table.find('tbody').find_all('tr'):
                        tds = row.find_all('td')
                        if len(tds) >= 4:
                            val = re.sub(r'\D', '', tds[3].text.strip())
                            if len(val) == 4: results.append(val)
            if results: break
        except: continue
    return results

@app.route('/')
def index():
    # Tambahkan Tanggal, Bulan, Tahun dan Jam
    now = datetime.datetime.now()
    tgl_display = now.strftime("%d %B %Y | %H:%M:%S")
    
    final_data = []
    for name, code in TARGET_POOLS.items():
        res = fetch_results(code)
        last_val = res[0] if res else "----"
        final_data.append({"name": name, "result": last_val})
    return render_template('index.html', data=final_data, current_time=tgl_display)

# Agar Flask bisa berjalan di Vercel
app_handler = app
