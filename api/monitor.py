from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import random
import os
from datetime import datetime

def get_proxies():
    proxies_list = []
    path = os.path.join(os.getcwd(), 'proxy.txt')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                p = line.strip()
                if p:
                    if p.startswith('socks5'): p = p.replace('socks5', 'socks5h')
                    elif p.startswith('socks4'): p = p.replace('socks4', 'socks4h')
                    proxies_list.append(p)
    return proxies_list

def scrape_data(url, proxy_config, headers):
    try:
        r = requests.get(url, headers=headers, proxies=proxy_config, timeout=12)
        soup = BeautifulSoup(r.text, 'html.parser')
        prize_section = soup.find('td', id='prize1')
        
        if prize_section:
            # Mengambil semua span di dalam prize1
            spans = prize_section.find_all('span')
            # Filter hanya yang ada teks angkanya
            balls = [s.text.strip() for s in spans if s.text.strip().isdigit()]
            
            if not balls:
                return "PENDING", None
            return "SUCCESS", balls
        return "NOT_FOUND", None
    except Exception as e:
        return f"TIMEOUT/ERROR", None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        proxies = get_proxies()
        selected_proxy = random.choice(proxies) if proxies else None
        proxy_config = {'http': selected_proxy, 'https': selected_proxy} if selected_proxy else {}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}

        # Scrape Busan & Jeju
        st_busan, data_busan = scrape_data("http://busanpools.asia/live.php?time=Result", proxy_config, headers)
        st_jeju, data_jeju = scrape_data("http://jejupools.asia/live.php?time=Pools", proxy_config, headers)

        def make_balls(status, data, pool_type):
            if status == "SUCCESS":
                return "".join([f'<div class="ball {pool_type}">{n}</div>' for n in data])
            return f'<div class="status">-- {status} --</div>'

        now = datetime.now().strftime("%d %b %Y | %H:%M:%S")

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Pools Monitor</title>
            <style>
                body {{ background: #0a0a0a; color: #eee; font-family: sans-serif; display: flex; justify-content: center; padding: 20px; }}
                .wrapper {{ width: 100%; max-width: 400px; }}
                .card {{ background: #1a1a1a; border-radius: 15px; padding: 20px; margin-bottom: 20px; text-align: center; box-shadow: 0 8px 16px rgba(0,0,0,0.5); border: 1px solid #333; }}
                h2 {{ margin: 0; font-size: 1.4rem; letter-spacing: 2px; }}
                .busan-title {{ color: #ff4d4d; }}
                .jeju-title {{ color: #ffd51d; }}
                .balls-row {{ display: flex; justify-content: center; gap: 10px; margin: 20px 0; min-height: 50px; align-items: center; }}
                .ball {{ 
                    width: 45px; height: 45px; border-radius: 50%; display: flex; justify-content: center; 
                    align-items: center; font-size: 1.3rem; font-weight: bold; color: #fff;
                    box-shadow: inset -3px -3px 6px rgba(0,0,0,0.4), 0 4px 8px rgba(0,0,0,0.4);
                }}
                .b-ball {{ background: radial-gradient(circle at 30% 30%, #ff5f6d, #7a0000); border: 2px solid #ff4d4d; }}
                .j-ball {{ background: radial-gradient(circle at 30% 30%, #205da8, #102e52); border: 2px solid #ffd51d; color: #ffd51d; }}
                .status {{ color: #666; font-style: italic; font-size: 0.9rem; }}
                .refresh {{ display: block; width: 100%; padding: 12px; background: #333; color: #fff; text-decoration: none; border-radius: 10px; font-weight: bold; transition: 0.3s; }}
                .refresh:hover {{ background: #444; }}
                .footer {{ text-align: center; font-size: 0.7rem; color: #444; margin-top: 15px; line-height: 1.5; }}
            </style>
        </head>
        <body>
            <div class="wrapper">
                <div class="card">
                    <h2 class="busan-title">BUSAN POOLS</h2>
                    <div class="balls-row">{make_balls(st_busan, data_busan, 'b-ball')}</div>
                </div>

                <div class="card">
                    <h2 class="jeju-title">JEJU POOLS</h2>
                    <div class="balls-row">{make_balls(st_jeju, data_jeju, 'j-ball')}</div>
                </div>

                <a href="javascript:location.reload()" class="refresh">REFRESH RESULT</a>
                
                <div class="footer">
                    CHECKED AT: {now}<br>
                    PROXY: {selected_proxy if selected_proxy else 'DIRECT'}<br>
                    SERVER: VERCEL SERVERLESS
                </div>
            </div>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
