from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import random
import os

def get_proxies():
    proxies_list = []
    path = os.path.join(os.path.dirname(__file__), '..', 'proxy.txt')
    if os.path.exists(path):
        with open(path, 'r') as f:
            for line in f:
                p = line.strip()
                if p:
                    # Otomatis ubah ke h-protocol untuk bypass DNS
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

        try:
            r = requests.get(url, headers=headers, proxies=proxy_config, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            prize_section = soup.find('td', id='prize1')
            
            if prize_section:
                balls = "".join([b.text.strip() for b in prize_section.find_all('span', class_='ball')])
                output = f"1st PRIZE: {balls if balls else 'PENDING'}"
            else:
                output = "Error: Elemen tidak ditemukan. Struktur web mungkin berubah."
        except Exception as e:
            output = f"Error: {str(e)}"

        # Mengirim response ke browser
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(output.encode('utf-8'))
        return
