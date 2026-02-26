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
    QUANTUM HYPER-DIMENSION V23.0
    Fokus: Anti-Cluster Shield, Triple-Digit Resonance, & Matrix Positioning.
    """
    last_p1 = all_res_data[0][0]  
    p1_list = [d[0] for d in all_res_data] 
    p2_last = all_res_data[0][1] if len(all_res_data[0]) > 1 and all_res_data[0][1] else "0000"
    p3_last = all_res_data[0][2] if len(all_res_data[0]) > 2 and all_res_data[0][2] else "0000"

    # --- 1. CLUSTER DETECTION (ANTI-ANOMALI) ---
    # Melacak angka yang mendominasi P1, P2, P3 (seperti angka 1 di result 1181)
    all_p_data = last_p1 + p2_last + p3_last
    cluster_map = Counter(all_p_data)
    # Angka yang muncul > 2x dalam satu putaran dianggap 'Cluster'
    hot_clusters = [num for num, count in cluster_map.items() if count >= 2]
    
    # Deteksi Pola Sandwich & Twin Depan/Belakang
    is_sandwich = last_p1[0] == last_p1[3]
    is_twin_front = last_p1[0] == last_p1[1]
    is_twin_back = last_p1[2] == last_p1[3]
    
    # --- 2. ADVANCED SCORING (DIMENSION SHIFT) ---
    all_7d = "".join(p1_list[:7])
    counts_7d = Counter(all_7d)
    
    scores = {str(i): 0 for i in range(10)}
    for d in scores:
        # A. Cluster Bonus: Jika angka muncul kuat di P2/P3, dia wajib masuk radar
        if d in hot_clusters: scores[d] += 180
        # B. Shadow Resonance: Indeks & Mistik dari P2/P3 (Bukan cuma P1)
        if d in [ID.get(x) for x in (p2_last + p3_last)]: scores[d] += 70
        # C. Missing Gap: Angka yang benar-benar hilang dalam 10 hari terakhir
        if counts_7d[d] == 0: scores[d] += 200
        # D. Taysen Shift: Mencari angka 'lompatan'
        if d in [TY.get(x) for x in last_p1]: scores[d] += 50

    top_digits = "".join([x[0] for x in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:6]])

    # --- 3. BIJI HYPER (Multi-Layer Sum) ---
    biji_hist = [(sum(int(d) for d in res) % 9 or 9) for res in p1_list[:20]]
    # Menghindari Biji yang baru keluar & memprioritaskan Biji yang sedang 'Haus' (Jarang muncul)
    biji_target = [b for b, c in Counter(biji_hist).most_common()[-4:]]

    # --- 4. FILTRASI BRUTAL (7 DIMENSI) ---
    raw_2d = [''.join(p) for p in itertools.product(top_digits, repeat=2)]
    hyper_2d = []
    seen = set()

    for line in raw_2d:
        if line in seen: continue
        h, t = line[0], line[1]
        b_line = (int(h) + int(t)) % 9 or 9
        score_2d = 0

        # GERBANG 1: Biji Hyper (Wajib lolos)
        if b_line not in biji_target: continue

        # GERBANG 2: Cluster Connection
        if any(d in hot_clusters for d in [h, t]): score_2d += 250
        
        # GERBANG 3: Polarity Logic (Odd-Even Balance)
        if (int(h) % 2) != (int(t) % 2): score_2d += 120
        
        # GERBANG 4: High-Low Split
        if (int(h) >= 5 and int(t) < 5) or (int(h) < 5 and int(t) >= 5): score_2d += 100

        # GERBANG 5: Anti-Zonk (Buang angka yang sama persis dengan 2D terakhir)
        if line == last_p1[2:]: continue

        # GERBANG 6: Twin Shield 3.0 (Deteksi Twin Balasan)
        if h == t:
            # Jika kemarin Twin (1181), hari ini Twin hanya boleh muncul jika skor sangat tinggi
            if is_twin_front or is_twin_back: score_2d += 150
            elif any(d in hot_clusters for d in h): score_2d += 200
            else: continue # Buang twin tanpa dasar cluster

        hyper_2d.append((line, score_2d))
        seen.add(line)

    # SORTING TOP 5 (Sangat Selektif)
    top2 = [x[0] for x in sorted(hyper_2d, key=lambda x: x[1], reverse=True)[:5]]

    # --- 5. HYPER 3D/4D (MATRIX POSITIONING) ---
    top3, top4 = [], []
    for i, l2 in enumerate(top2):
        try:
            # Menggunakan kombinasi Mistik Baru & Taysen silang antara P2 dan P3
            # As diambil dari Mistik Prize 2, Kop diambil dari Taysen Prize 3
            asn = MB.get(p2_last[i % 4], last_p1[0])
            kop = TY.get(p3_last[i % 4], last_p1[1])
            
            # Jika ada cluster, paksa angka cluster masuk ke struktur 4D
            if hot_clusters and i == 0: 
                asn = hot_clusters[0]

            top3.append(f"{kop}{l2}")
            top4.append(f"{asn}{kop}{l2}")
        except: pass

    return {
        'version': 'V23.0 [HYPER-DIMENSION]',
        'market': market_name,
        'last_res': last_p1, 'p2_last': p2_last, 'p3_last': p3_last,
        'am': top_digits[:4], 'ai': top_digits[4:6],
        'bbfs': top_digits,
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
