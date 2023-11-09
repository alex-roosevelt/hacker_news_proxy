from http.server import HTTPServer, BaseHTTPRequestHandler
from bs4 import BeautifulSoup
import http.client
import re

from decouple import config

HOST = config('HOST', default='127.0.0.1')
PORT = config('PORT', default=8232, cast=int)


class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Определить целевой хост и порт
        target_host = "news.ycombinator.com"
        target_port = 443

        # Подключиться к целевому серверу
        conn = http.client.HTTPSConnection(target_host, target_port)
        conn.request("GET", self.path)

        # Получить ответ от целевого сервера
        response = conn.getresponse()
        response_data = response.read()

        # Анализировать HTML-код с помощью BeautifulSoup
        soup = BeautifulSoup(response_data, 'html.parser')

        # Заменить каждое слово из шести букв значком "™" в текстовом содержимом
        for tag in soup.find_all(text=True):
            if tag.parent.name not in ['style', 'script']:
                tag.replace_with(self.modify_html(tag))

        modified_response = str(soup)

        # Отправить модифицированный ответ клиенту
        self.send_response(response.status)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(modified_response.encode("utf-8"))

    @staticmethod
    def modify_html(content):
        # Шаблон для слов из шести букв
        pattern = r'\b\w{6}\b'

        # Заменить каждое слово из шести букв значком "™"
        modified_content = re.sub(pattern, lambda match: match.group() + '™', content)

        return modified_content


if __name__ == "__main__":
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, ProxyHandler)
    print('Server is running at', f'{HOST}:{PORT}')
    httpd.serve_forever()
