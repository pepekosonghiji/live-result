from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import random
import os

def load_proxies():
    proxies_list = []
    # Membaca proxy.txt yang ada di root folder
    try:
        path = os.path.join(os.getcwd(), 'proxy.txt')
        with open(path, 'r') as f:
            for line in f:
                proxy = line.strip()
                if proxy:
                    if proxy.startswith('socks5'):
                        proxy = proxy.replace('socks5', 'socks5h')
                    elif proxy.startswith('socks4'):
                        proxy = proxy.replace('socks4', 'socks4h')
                    proxies_list.append(proxy)
    except Exception:
        pass
    return proxies_list

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = "http://busanpools.asia/live.php?time=Result"
        proxies_pool = load_proxies()
        
        if not proxies_pool:
            result_text = "Error: No proxies in proxy.txt"
        else:
            selected_proxy = random.choice(proxies_pool)
            proxy_config = {'http': selected_proxy, 'https': selected_proxy}
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}

            try:
                response = requests.get(url, headers=headers, proxies=proxy_config, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    prize1_section = soup.find('td', id='prize1')
                    if prize1_section:
                        balls = prize1_section.find_all('span', class_='ball')
                        numbers = "".join([ball.text.strip() for ball in balls])
                        result_text = f"SUCCESS: 1st Prize {numbers} (via {selected_proxy})"
                    else:
                        result_text = "HTML Structure Changed"
                else:
                    result_text = f"HTTP Error {response.status_code}"
            except Exception as e:
                result_text = f"Failed via {selected_proxy}: {str(e)[:50]}"

        # Response untuk Vercel (dan Cron Job)
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(result_text.encode())
        return
