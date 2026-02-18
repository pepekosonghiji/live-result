from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import random
import os

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

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = "http://busanpools.asia/live.php?time=Result"
        proxies = get_proxies()
        selected_proxy = random.choice(proxies) if proxies else None
        proxy_config = {'http': selected_proxy, 'https': selected_proxy} if selected_proxy else {}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}

        result_html = ""
        try:
            r = requests.get(url, headers=headers, proxies=proxy_config, timeout=12)
            soup = BeautifulSoup(r.text, 'html.parser')
            prize_section = soup.find('td', id='prize1')
            
            if prize_section:
                balls = [b.text.strip() for b in prize_section.find_all('span', class_='ball')]
                if not balls:
                    result_html = '<div class="pending">PENDING</div>'
                else:
                    # Membuat tampilan bola-bola angka
                    ball_elements = "".join([f'<div class="ball">{num}</div>' for num in balls])
                    result_html = f'<div class="balls-container">{ball_elements}</div>'
            else:
                result_html = '<div class="error">Data tidak ditemukan. Struktur web berubah.</div>'
        except Exception as e:
            result_html = f'<div class="error">Koneksi Gagal: {str(e)}</div>'

        # Template HTML + CSS
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Busan Pools Live Result</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #1a1a1a;
                    color: white;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }}
                .card {{
                    background: #2d2d2d;
                    padding: 2rem;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                    text-align: center;
                    width: 90%;
                    max-width: 400px;
                    border: 2px solid #7a0000;
                }}
                h1 {{ color: #ff4d4d; margin-bottom: 0.5rem; font-size: 1.5rem; }}
                p {{ color: #aaa; margin-bottom: 1.5rem; font-size: 0.9rem; }}
                .balls-container {{
                    display: flex;
                    justify-content: center;
                    gap: 10px;
                    margin: 20px 0;
                }}
                .ball {{
                    width: 50px;
                    height: 50px;
                    background: radial-gradient(circle at 30% 30%, #ff5f6d, #7a0000);
                    border-radius: 50%;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    font-size: 1.5rem;
                    font-weight: bold;
                    color: white;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
                    border: 2px solid white;
                }}
                .pending {{ font-size: 1.2rem; color: #ffcc00; font-weight: bold; }}
                .error {{ font-size: 0.8rem; color: #ff4d4d; background: #441111; padding: 10px; border-radius: 5px; }}
                .footer {{ margin-top: 20px; font-size: 0.7rem; color: #666; }}
                .btn-refresh {{
                    margin-top: 15px;
                    background: #7a0000;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 5px;
                    cursor: pointer;
                    text-decoration: none;
                    display: inline-block;
                }}
                .btn-refresh:hover {{ background: #990000; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>BUSAN POOLS</h1>
                <p>LIVE RESULT 1st PRIZE</p>
                {result_html}
                <a href="javascript:location.reload()" class="btn-refresh">Refresh Result</a>
                <div class="footer">
                    Proxy: {selected_proxy if selected_proxy else "Direct"}<br>
                    Last Check: {os.popen('date').read()}
                </div>
            </div>
        </body>
        </html>
        """

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
        return
