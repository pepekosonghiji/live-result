import os, re, httpx
from flask import Flask, render_template, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)

# --- [DATA PASARAN - MONITORING ONLY] ---
TARGET_POOLS = {
    'CAMBODIA': 'p3501', 'SYDNEY LOTTO': 'p2262', 'HONGKONG LOTTO': 'p2263', 
    'HONGKONG POOLS': 'HK_SPECIAL', 'SINGAPORE POOLS': 'p2264', 'SYDNEY POOLS': 'sydney',
    'BUSAN POOLS':'p16063', 'OSAKA':'p28422', 'JEJU':'p22815', 'DANANG':'p22816',
    'PENANG':'p22817', 'SEOUL':'p28502', 'TORONTOMID':'p13976', 'SAPPORO':'p22814',
    'PHUKET':'p28435', 'WUHAN':'p28615', 'MACAU 4D': 'm17-pool-1'
}

# --- [SCRAPER ENGINE - VERSI OPTIMAL] ---
def fetch_results(market_code):
    results = []
    # Jalur Khusus HK Special
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
                            if val.isdigit() and len(val) == 4: 
                                results.append(val)
            if results: return results
        except: pass

    # Jalur Umum Pasaran Lain
    urls = [
        f"https://dk9if7ik34.salamrupiah.com/history/result-mobile/{market_code}-pool-1", 
        f"https://dk9if7ik34.salamrupiah.com/history/result-mobile/kia_{market_code}",
        f"https://9yjus6z6kz.salamrupiah.com/history/result-mobile/{market_code}" # Backup Link
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
                            if len(val) == 4: 
                                results.append(val)
            if results: break # Berhenti jika sudah dapat data
        except: continue
    return results

# --- [ROUTES API MONITOR] ---
@app.route('/api/results')
def get_all_monitor():
    """Mengambil semua hasil terakhir untuk dashboard utama"""
    monitor_data = {}
    for name, code in TARGET_POOLS.items():
        data = fetch_results(code)
        monitor_data[name] = data[0] if data else "PENDING"
    return jsonify(monitor_data)

@app.route('/api/last/<market>')
def get_single(market):
    """Cek last result pasaran tertentu secara cepat"""
    m_upper = market.upper()
    if m_upper in TARGET_POOLS:
        data = fetch_results(TARGET_POOLS[m_upper])
        return jsonify({
            "status": "success",
            "market": m_upper,
            "last": data[0] if data else "N/A"
        })
    return jsonify({"status": "error", "msg": "Pasaran tidak ada"}), 404

@app.route('/')
def dashboard():
    return render_template('index.html', markets=sorted(TARGET_POOLS.keys()))

if __name__ == '__main__':
    app.run(debug=True)
