from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import random
import os
from datetime import datetime

def get_proxies():
    path = os.path.join(os.getcwd(), 'proxy.txt')
    if not os.path.exists(path): return []
    with open(path, 'r', encoding='utf-8') as f:
        return [p.strip().replace('socks5', 'socks5h').replace('socks4', 'socks4h') for p in f if p.strip()]

def scrape_data(url, proxy, headers):
    try:
        p_config = {'http': proxy, 'https': proxy} if proxy else {}
        r = requests.get(url, headers=headers, proxies=p_config, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        p_section = soup.find('td', id='prize1')
        
        if p_section:
            # Ambil angka dari span (berlaku untuk Busan & Jeju)
            balls = [s.text.strip() for s in p_section.find_all('span') if s.text.strip().isdigit()]
            return ("SUCCESS", balls) if balls else ("PENDING", None)
        return ("NOT_FOUND", None)
    except Exception as e:
        return (f"ERROR: {str(e)[:20]}", None)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Setup Request
        proxies = get_proxies()
        selected_proxy = random.choice(proxies) if proxies else None
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}

        # 2. Ambil Data
        res_busan = scrape_data("http://busanpools.asia/live.php?time=Result", selected_proxy, headers)
        res_jeju = scrape_data("http://jejupools.asia/live.php?time=Pools", selected_proxy, headers)

        # 3. Helper untuk render bola
        def render_balls(res_tuple, css_class):
            status, data = res_tuple
            if status == "SUCCESS":
                return "".join([f'<div class="ball {css_class}">{n}</div>' for n in data])
            return f'<div class="status">-- {status} --</div>'

        # 4. Baca Template HTML
        template_path = os.path.join(os.path.dirname(__file__), 'index.html')
        with open(template_path, 'r') as f:
            content = f.read()

        # 5. Inject Data ke HTML
        content = content.replace('{{BUSAN_RESULT}}', render_balls(res_busan, 'b-ball'))
        content = content.replace('{{JEJU_RESULT}}', render_balls(res_jeju, 'j-ball'))
        content = content.replace('{{TIME}}', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        content = content.replace('{{PROXY}}', selected_proxy if selected_proxy else "DIRECT")

        # 6. Kirim Response
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))
