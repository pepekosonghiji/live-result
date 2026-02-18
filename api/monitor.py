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

def scrape_prize(url, proxy_config, headers):
    try:
        r = requests.get(url, headers=headers, proxies=proxy_config, timeout=12)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Mencari elemen 1st prize (biasanya ID prize1 atau class ballres)
        prize_section = soup.find('td', id='prize1')
        
        if prize_section:
            balls = [b.text.strip() for b in prize_section.find_all('span', class_='ball')]
            if not balls:
                return "PENDING", None
            return "SUCCESS", balls
        return "NOT_FOUND", None
    except Exception as e:
        return f"ERROR: {str(e)[:30]}", None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        proxies = get_proxies()
        selected_proxy = random.choice(proxies) if proxies else None
        proxy_config = {'http': selected_proxy, 'https': selected_proxy} if selected_proxy else {}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}

        # Ambil Data Busan
        status_busan, data_busan = scrape_prize("http://busanpools.asia/live.php?time=Result", proxy_config, headers)
        
        # Ambil Data Jeju
        status_jeju, data_jeju = scrape_prize("http://jejupools.asia/live.php?time=Pools", proxy_config, headers)

        def generate_ball_html(status, data):
            if status == "SUCCESS":
                ball_elements = "".join([f'<div class="ball">{num}</div>' for num in data])
                return f'<div class="balls-container">{ball_elements}</div>'
            elif status == "PENDING":
                return '<div class="status pending">WAITING RESULT...</div>'
            else:
                return f'<div class="status error">{status}</div>'

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html_content = f"""
        <!DOCTYPE html>
        <html lang="id">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Live Result Pools</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background-color: #0f0f0f;
                    color: white;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    padding: 20px;
                    margin: 0;
                }}
                .container {{ width: 100%; max-width: 500px; }}
                .card {{
                    background: linear-gradient(145deg, #1e1e1e, #252525);
                    margin-bottom: 20px;
                    padding: 20px;
                    border-radius: 20px;
                    box-shadow: 0 10px 20px rgba(0,0,0,0.5);
                    text-align: center;
                    border: 1px solid #333;
                }}
                .busan {{ border-top: 5px solid #ff4d4d; }}
                .jeju {{ border-top: 5px solid #00c3ff; }}
                h2 {{ margin: 0 0 10px 0; letter-spacing: 2px; font-size: 1.2rem; }}
                .busan h2 {{ color: #ff4d4d; }}
                .jeju h2 {{ color: #00c3ff; }}
                .balls-container {{
                    display: flex;
                    justify-content: center;
                    gap: 8px;
                    margin: 15px 0;
                }}
                .ball {{
                    width: 45px;
                    height: 45px;
                    background: radial-gradient(circle at 30% 30%, #ffffff, #dddddd);
                    border-radius: 50%;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    font-size: 1.4rem;
                    font-weight: bold;
                    color: #000;
                    box-shadow: inset -3px -3px 8px rgba(0,0,0,0.2), 0 5px 10px rgba(0,0,0,0.4);
                }}
                .busan .ball {{ background: radial-gradient(circle at 30% 30%, #ff5f6d, #7a0000); color: white; }}
                .jeju .ball {{ background: radial-gradient(circle at 30% 30%, #00c3ff, #004e66); color: white; }}
                .status {{ padding: 10px; border-radius: 8px; font-size: 0.9rem; }}
                .pending {{ color: #ffcc00; background: rgba(255,204,0,0.1); }}
                .error {{ color: #ff4d4d; background: rgba(255,77,77,0.1); font-size: 0.7rem; }}
                .refresh-box {{ text-align: center; margin-top: 10px; }}
                .btn-refresh {{
                    background: #333;
                    color: white;
                    border: none;
                    padding: 12px 30px;
                    border-radius: 50px;
                    cursor: pointer;
                    text-decoration: none;
                    font-weight: bold;
                    transition: 0.3s;
                }}
                .btn-refresh:hover {{ background: #555; transform: scale(1.05); }}
                .info {{ font-size: 0.65rem; color: #555; margin-top: 20px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="card busan">
                    <h2>BUSAN POOLS</h2>
                    <div style="font-size: 0.8rem; color: #666;">1st PRIZE RESULT</div>
                    {generate_ball_html(status_busan, data_busan)}
                </div>

                <div class="card jeju">
                    <h2>JEJU POOLS</h2>
                    <div style="font-size: 0.8rem; color: #666;">1st PRIZE RESULT</div>
                    {generate_ball_html(status_jeju, data_jeju)}
                </div>

                <div class="refresh-box">
                    <a href="javascript:location.reload()" class="btn-refresh">REFRESH DATA</a>
                </div>

                <div class="info">
                    Waktu Cek: {current_time}<br>
                    Proxy: {selected_proxy if selected_proxy else "None"}<br>
                    Status: Active
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
