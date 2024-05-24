from http.server import HTTPServer, BaseHTTPRequestHandler

import requests

INDEX = 0
CACHE = {}


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def backend(self) -> str:
        global INDEX
        hosts = ["http://localhost:3000"]
        host = hosts[INDEX]
        INDEX = (INDEX + 1) % len(hosts)
        return host

    def do_GET(self):
        response = requests.get(f"{self.backend()}{self.path}")
        self.send_response(response.status_code)
        self.send_header("Content-Length", response.headers.get('Content-Length'))
        self.send_header("Content-Type", response.headers.get('Content-Type'))
        self.end_headers()
        self.wfile.write(response.content)

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
        except (ValueError, KeyError):
            self.send_response(400, "Missing Content-Length")
            self.end_headers()
            return

        response = requests.post(
            url=f"{self.backend()}{self.path}",
            data=self.rfile.read(content_length),
            headers={
                "Content-Length": str(content_length),
                "Content-Type": self.headers.get('Content-Type')
            }
        )
        self.send_response(response.status_code)
        self.send_header("Content-Length", response.headers.get('Content-Length'))
        self.send_header("Content-Type", response.headers.get('Content-Type'))
        self.end_headers()
        self.wfile.write(response.content)


# class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
#     def do_GET(self):
#         body = b"Hello, World!"
#         self.send_response(200)
#         self.send_header("Content-Length", len(body))
#         self.send_header("Content-Type", "text/plain")
#         self.end_headers()
#         self.wfile.write(body)


def main(host: str, port: int):
    with HTTPServer((host, port), MyHTTPRequestHandler) as httpd:
        httpd.serve_forever()


if __name__ == '__main__':
    main("0.0.0.0", 8080)
