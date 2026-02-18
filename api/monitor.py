import os, re, httpx, random
from flask import Flask, render_template, jsonify
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__, template_folder='.')

# --- [TARGET POOLS CONFIG] ---
TARGET_POOLS = {
    'BUSAN POOLS':'p16063', 
    'JEJU':'p22815',
    'CAMBODIA': 'p3501', 
    'SYDNEY LOTTO': 'p2262', 
    'HONGKONG LOTTO': 'p2263', 
    'HONGKONG POOLS': 'HK_SPECIAL', 
    'SINGAPORE POOLS': 'p2264', 
    'SYDNEY POOLS': 'sydney',
    'OSAKA':'p28422', 
    'DANANG':'p22816',
    'PENANG':'p22817', 
    'SEOUL':'p28502', 
    'TORONTOMID':'p13976', 
    'SAPPORO':'p22814',
    'PHUKET':'p28435', 
    'WUHAN':'p28615', 
    'MACAU 4D': 'm17-pool-1'
}

def get_proxies():
    path = os.path.join(os.getcwd(), 'proxy.txt')
    if not os.path.exists(path): return []
    with open(path, 'r', encoding='utf-8') as f:
        return [p.strip().replace('socks5', 'socks5h').replace('socks4', 'socks4h') for p in f if p.strip()]

def fetch_last_result(market_name, proxy=None):
    market_code = TARGET_POOLS.get(market_name)
    p_config = {'http://': proxy, 'https://': proxy} if proxy else None
    
    # Khusus Hongkong Pools
    if market_name == "HONGKONG POOLS":
        try:
            with httpx.Client(timeout=10.0, verify=False, proxies=p_config) as client:
                r = client.get("https://tabelsemalam.com/")
                soup = BeautifulSoup(r.text, 'html.parser')
                table = soup.find('table')
                if table:
                    val = table.find('tbody').find_all('tr')[0].find_all('td')[1].text.strip()
                    return list(val) if len(val) == 4 else ["-","-","-","-"]
        except: return ["E","R","R","!"]

    # Scraper Standar (Busan, Jeju, dll)
    urls = [
        f"https://dk9if7ik34.salamrupiah.com/history/result-mobile/{market_code}",
        f"https://9yjus6z6kz.salamrupiah.com/history/result-mobile/{market_code}"
    ]

    for url in urls:
        try:
            with httpx.Client(timeout=10.0, verify=False, proxies=p_config) as client:
                r = client.get(url)
                soup = BeautifulSoup(r.text, 'html.parser')
                table = soup.find('table', class_='table-history')
                if table:
                    first_row = table.find('tbody').find_all('tr')[0]
                    tds = first_row.find_all('td')
                    val = re.sub(r'\D', '', tds[-1].text.strip())
                    if len(val) >= 4: return list(val[-4:]) # Ambil 4 angka terakhir
        except: continue
    
    return ["N","A","N","A"]

@app.route('/')
def index():
    proxies = get_proxies()
    proxy = random.choice(proxies) if proxies else None
    
    # Ambil data utama untuk dashboard
    busan_res = fetch_last_result('BUSAN POOLS', proxy)
    jeju_res = fetch_last_result('JEJU', proxy)
    
    # Data tambahan untuk info di footer
    check_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return render_template('index.html', 
                           busan=busan_res, 
                           jeju=jeju_res, 
                           proxy_used=proxy if proxy else "DIRECT",
                           time_now=check_time)

# Helper route jika ingin cek via JSON
@app.route('/api/monitor')
def monitor_all():
    summary = {m: "".join(fetch_last_result(m)) for m in TARGET_POOLS.keys()}
    return jsonify(summary)

# Penting agar Vercel bisa membaca app Flask
def handler(request):
    return app(request)
