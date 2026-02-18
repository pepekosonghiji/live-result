import os, re, httpx
from flask import Flask, render_template, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), '../templates'))

# --- [DATABASE PASARAN] ---
TARGET_POOLS = {
    'CAMBODIA': 'p3501', 'SYDNEY LOTTO': 'p2262', 'HONGKONG LOTTO': 'p2263', 
    'HONGKONG POOLS': 'HK_SPECIAL', 'SINGAPORE POOLS': 'p2264', 'SYDNEY POOLS': 'sydney',
    'DANANG':'p22816', 'PENANG':'p22817', 'PHUKET':'p28435', 'MACAU 4D': 'm17-pool-1'
}

# --- [SCRAPER ENGINE] ---
def fetch_results(market_code):
    results = []
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

# --- [ROUTES] ---
@app.route('/')
def index():
    # Mengambil data untuk semua pasaran saat halaman dibuka
    final_data = []
    for name, code in TARGET_POOLS.items():
        res = fetch_results(code)
        last = res[0] if res else "----"
        final_data.append({"name": name, "result": last})
    
    return render_template('index.html', data=final_data)

@app.route('/api/last')
def api_last():
    # Endpoint JSON jika ingin dipakai aplikasi lain
    monitor = {name: (fetch_results(code)[0] if fetch_results(code) else "----") 
               for name, code in TARGET_POOLS.items()}
    return jsonify(monitor)

# Penting untuk Vercel
def handler(request):
    return app(request)
