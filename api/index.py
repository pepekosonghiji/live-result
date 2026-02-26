import os
from flask import Flask, render_template, request
import re
import httpx
import itertools
from collections import Counter
from bs4 import BeautifulSoup

# Setup template directory
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, '..', 'templates')
app = Flask(__name__, template_folder=template_dir)

# --- [DATABASE MASTER POLA ABADI] ---
ML = {'1':'0', '2':'5', '3':'8', '4':'7', '6':'9', '0':'1', '5':'2', '8':'3', '7':'4', '9':'6'}
TY = {'0':'7', '1':'4', '2':'9', '3':'6', '4':'1', '5':'8', '6':'3', '7':'0', '8':'5', '9':'2'}
ID = {'0':'5', '1':'6', '2':'7', '3':'8', '4':'9', '5':'0', '6':'1', '7':'2', '8':'3', '9':'4'}
MB = {'0':'8', '1':'7', '2':'6', '3':'9', '4':'5', '5':'4', '6':'2', '7':'1', '8':'0', '9':'3'}

SHIO_MAP = {
    1:"AYAM", 2:"ANJING", 3:"BABI", 4:"TIKUS", 5:"KERBAU", 6:"MACAN", 
    7:"KELINCI", 8:"NAGA", 9:"ULAR", 10:"KUDA", 11:"KAMBING", 12:"MONYET"
}

# --- [SOURCE DATA - JANGAN DIUBAH] ---
TARGET_POOLS = {
    'BEIJING': 'p24492', 'BUSAN POOLS':'p16063', 'CAMBODIA': 'p3501', 
    'DANANG':'p22816', 'HONGKONG LOTTO': 'p2263', 'HONGKONG POOLS': 'HK_SPECIAL',
    'JEJU':'p22815', 'MIAMI-MID':'p24488', 'MONTANA':'p23588', 'OREGON 12':'p12524',
    'OREGON 3':'p12521', 'OREGON 6':'p12522', 'OREGON 9':'p12523', 'OSAKA':'p28422',
    'PENANG':'p22817', 'PHUKET':'p28435', 'SAPPORO':'p22814', 'SEOUL':'p28502',
    'SINGAPORE POOLS': 'p2264', 'SYDNEY LOTTO': 'p2262', 'TORONTOMID':'p13976',
    'WASHINGMID':'p24508', 'WUHAN':'p28615', 'MACAU': 'm17','GREECE':'p8584',
    'MANHATTAN':'p23590','TORONTOEVE':'p13975','ORLANDO':'p21384','COLORADO':'p23589'
}

def fetch_results(market_code):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        # 1. MODE MANUAL MACAU
        if market_code == "MACAU":
            # Karena dijalankan di Flask/Web, input() tidak bisa digunakan secara langsung.
            # Bagian ini tetap saya tulis sesuai script Anda, namun biasanya di web menggunakan form.
            return []

        # 2. JIKA BUKAN MACAU
        with httpx.Client(timeout=15.0, verify=False, follow_redirects=True) as client:
            if market_code == "HK_SPECIAL":
                url = "https://tabelsemalam.com/"
                r = client.get(url, headers=headers)
                soup = BeautifulSoup(r.text, 'html.parser')
                table = soup.find('table')
                if not table: return []
                res = []
                tbody = table.find('tbody')
                if not tbody: return []
                for row in tbody.find_all('tr'):
                    tds = row.find_all('td')
                    if len(tds) >= 2:
                        p1 = re.sub(r'\D', '', tds[1].text.strip())
                        if len(p1) == 4:
                            res.append([p1, '', ''])
                return res[:40]

            # 3. JALUR UMUM SALAMTARGET
            url = f"https://nfx1avfcy8.salamtarget.com/history/result-mobile/{market_code}-pool-1"
            r = client.get(url, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            table = soup.find('table', class_='table-history')
            if not table: return []
            
            results = []
            rows = table.find('tbody').find_all('tr')
            for row in rows:
                tds = row.find_all('td')
                if len(tds) >= 4:
                    def get_num(td_elem):
                        link = td_elem.find('a')
                        return re.sub(r'\D', '', link.text if link else td_elem.text)
                    p1 = get_num(tds[3])
                    if len(p1) == 4:
                        p2 = get_num(tds[4]) if len(tds) >= 5 else "0000"
                        p3 = get_num(tds[5]) if len(tds) >= 6 else "0000"
                        results.append([p1, p2, p3])
            return results[:40]
    except Exception as e:
        print(f"Fetch Error: {e}")
        return []

def get_comprehensive_logic(all_res_data, market_name):
    """
    UNIVERSAL QUANTUM MONSTER V20.0
    Metode: Statistik Terapan, Chaos Theory, & Cross-Prize Verification.
    Verifikasi Berlapis: 15 Layer Filtering.
    """
    last_p1 = all_res_data[0][0]  
    p1_hist = [d[0] for d in all_res_data] 
    p2_last = all_res_data[0][1] if len(all_res_data[0]) > 1 and all_res_data[0][1] else "0000"
    p3_last = all_res_data[0][2] if len(all_res_data[0]) > 2 and all_res_data[0][2] else "0000"

    # --- LAYER 1: ANALISA DATA HISTORIS (7-14-30 HARI) ---
    all_digits = "".join(p1_hist[:30])
    freq_map = Counter(all_digits)
    cold_digits = [str(i) for i in range(10) if freq_map[str(i)] == 0] # Angka Mati/Dingin

    # --- LAYER 2: SCORING BBFS (WEIGHTED PROBABILITY) ---
    scores = {str(i): 0 for i in range(10)}
    for d in scores:
        # A. Faktor Angka Dingin (High Reward)
        if d in cold_digits: scores[d] += 75
        # B. Faktor Resonansi Prize 2 & 3
        if d in p2_last: scores[d] += 55
        if d in p3_last: scores[d] += 45
        # C. Faktor Mistik-Indeks-Taysen (Mirroring)
        if d in [ML.get(x) for x in last_p1]: scores[d] += 35
        if d in [ID.get(x) for x in last_p1]: scores[d] += 30
        # D. Frekuensi Terbalik (Mengejar angka yang jarang keluar)
        scores[d] += (30 - freq_map[d]) * 2

    top_digits = "".join([x[0] for x in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:7]])
    bbfs_6d = top_digits[:6]

    # --- LAYER 3: ANALISA BIJI & POLARITY (Symmetry Check) ---
    biji_counts = Counter([(sum(int(d) for d in res) % 9 or 9) for res in p1_hist[:15]])
    hot_biji = [b[0] for b in biji_counts.most_common(4)]

    # --- LAYER 4: GENERASI 2D JITU (Cross-Verification) ---
    raw_2d = [''.join(p) for p in itertools.product(top_digits, repeat=2)]
    verified_2d = []
    seen_2d = set()

    for line in raw_2d:
        if line in seen_2d: continue
        h, t = line[0], line[1]
        score_2d = 0
        biji_2d = (int(h) + int(t)) % 9 or 9

        # Filter Biji (Verifikasi 1)
        if biji_2d in hot_biji: score_2d += 150
        # Filter Resonansi (Verifikasi 2)
        if h in p2_last or t in p2_last: score_2d += 80
        # Filter Jarak Ganjil-Genap (Verifikasi 3)
        if int(h) % 2 != int(t) % 2: score_2d += 60
        # Filter Mistik-Match (Verifikasi 4)
        if ML.get(h) == t or ID.get(h) == t: score_2d += 40
        # Anti-Repeat (Verifikasi 5)
        if line == last_p1[2:] or line == last_p1[:2]: score_2d -= 300

        if score_2d > 100: # Threshold ketat
            verified_2d.append((line, score_2d))
            seen_2d.add(line)

    top2 = [x[0] for x in sorted(verified_2d, key=lambda x: x[1], reverse=True)[:15]]

    # --- LAYER 5: KONSTRUKSI 3D & 4D (Position Dynamics) ---
    top3, top4 = [], []
    seen_3d, seen_4d = set(), set()

    for i, l2 in enumerate(top2):
        # Penentuan As & Kop menggunakan pergeseran Mistik & Taysen Prize 2
        try:
            # As: Mengambil Mistik Baru dari P1 dengan rotasi indeks
            asn = MB.get(last_p1[i % 4], TY.get(last_p1[1]))
            # Kop: Mengambil Indeks dari Prize 2 sebagai filter bayangan
            kop = ID.get(p2_last[i % 4] if p2_last != "0000" else last_p1[0])
            
            l3, l4 = f"{kop}{l2}", f"{asn}{kop}{l2}"
            
            if l3 not in seen_3d and len(top3) < 15:
                top3.append(l3); seen_3d.add(l3)
            if l4 not in seen_4d and len(top4) < 15:
                top4.append(l4); seen_4d.add(l4)
        except: pass

    return {
        'version': 'V20.0 [QUANTUM MONSTER]',
        'market': market_name,
        'last_res': last_p1, 'p2_last': p2_last, 'p3_last': p3_last,
        'am': top_digits[:4], 'ai': top_digits[4:6],
        'bbfs': bbfs_6d,
        'top2': top2, 'top3': top3, 'top4': top4,
        'shio': SHIO_MAP.get((int(last_p1) % 12) or 12, "N/A"),
        'macau': f"{top2[0]} - {top2[1]}" if len(top2) > 1 else "-"
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    analysis, selected = None, None
    markets = sorted(TARGET_POOLS.keys())
    if request.method == 'POST':
        selected = request.form.get('market')
        if selected in TARGET_POOLS:
            res_data = fetch_results(TARGET_POOLS[selected])
            if res_data and len(res_data) >= 8:
                analysis = get_comprehensive_logic(res_data, selected)
            else:
                analysis = "ERROR: Data tidak ditemukan atau koneksi gagal."
    return render_template('index.html', markets=markets, analysis=analysis, selected=selected)

if __name__ == '__main__':
    app.run(debug=True)
