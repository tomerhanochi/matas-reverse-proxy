import cgi
from dataclasses import dataclass
from http.server import HTTPServer, BaseHTTPRequestHandler

import requests


@dataclass(slots=True)
class CachedResponse:
    status_code: int
    content_length: str
    content_type: str
    content: bytes


INDEX = 0
CACHE: dict[str, CachedResponse] = {}


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def backend(self) -> str:
        global INDEX
        hosts = ["http://localhost:3000"]
        host = hosts[INDEX]
        INDEX = (INDEX + 1) % len(hosts)
        return host

    def do_GET(self):
        global CACHE
        cached_response = CACHE.get(self.path)
        if cached_response is None:
            response = requests.get(f"{self.backend()}{self.path}")
            cached_response = CachedResponse(
                response.status_code,
                response.headers.get("Content-Length"),
                response.headers.get("Content-Type"),
                response.content,
            )
            CACHE[self.path] = cached_response

        self.send_response(cached_response.status_code)
        self.send_header("Content-Length", cached_response.content_length)
        self.send_header("Content-Type", cached_response.content_type)
        self.end_headers()
        self.wfile.write(cached_response.content)

    def do_POST(self):
        form = cgi.FieldStorage(
            self.rfile,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers.get("Content-Type"),
                "CONTENT_LENGTH": self.headers.get("Content-Length"),
            }
        )
        field_storage = form.list[0]
        while True:
            chunk = field_storage.file.read(1024)
            response = requests.post(
                url=f"{self.backend()}/upload-large/{field_storage.filename}",
                files={"file": (field_storage.filename, chunk, field_storage.type)},
            )
            # If the chunk was smaller than 1024, then it was the last chunk
            # And if there was an error, we want to return it to the user
            if len(chunk) < 1024 or response.status_code != 200:
                break
        self.send_response(response.status_code)
        self.send_header("Content-Length", response.headers.get("Content-Length"))
        self.send_header("Content-Type", response.headers.get("Content-Type"))
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
