import http.server
import http.client
import socketserver
import bs4
import re

from decouple import config


# Use 'config' to read values from the .env file
HOST = config('HOST', default='127.0.0.1')
PORT = config('PORT', default=8232, cast=int)
TARGET_HOST = config('TARGET_HOST')


class ProxyHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):

        client = http.client.HTTPSConnection(TARGET_HOST)
        client.request('GET', self.path)
        response = client.getresponse()

        # Get the page content as a string
        html = response.read().decode('utf-8')
        # Modify the HTML content
        modified_html = self.modify_html(html)


        # Send the status code
        self.send_response(response.status)
        # Add headers to the response
        for header in response.getheaders():
            self.send_header(*header)

        self.end_headers()
        self.wfile.write(modified_html.encode('utf-8'))

        client.close()

    @staticmethod
    def modify_html(html):
        """
        Modify the HTML content of the page.
        """
        soup = bs4.BeautifulSoup(html, 'lxml')

        try:
            # Find all <div> tags with class 'comment'
            comments = soup.find_all('div', {'class': 'comment'})

            pattern = r"(?:(?<=\s)|(?<=^))[a-zA-ZА-Яа-я-]{6}(?=\s|\,|\.|\:)"

            for comment in comments:
                print(comment.get_text())

                text = str(comment.get_text())
                modified_text = re.sub(pattern, r'\g<0>™', text)
                comment.string = modified_text

        except Exception as ex:
            print('No posts found on the page')
            print('Exception:', ex)

        return soup.prettify()


def run_proxy_server():
    with socketserver.TCPServer((HOST, PORT), ProxyHandler) as httpd:
        print('Server is running at', f'{HOST}:{PORT}')
        httpd.serve_forever()


if __name__ == '__main__':
    run_proxy_server()
