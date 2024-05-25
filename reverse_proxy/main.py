import cgi
from dataclasses import dataclass
from http.server import HTTPServer, BaseHTTPRequestHandler
from http.client import HTTPConnection


@dataclass(slots=True)
class CachedResponse:
    status_code: int
    reason: str
    content_length: str
    content_type: str
    content: bytes


INDEX = 0
CACHE: dict[str, CachedResponse] = {}


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def backend(self) -> str:
        global INDEX
        hosts = ["localhost:3000"]
        host = hosts[INDEX]
        INDEX = (INDEX + 1) % len(hosts)
        return host

    def do_GET(self):
        global CACHE
        cached_response = CACHE.get(self.path)
        if cached_response is None:
            con = HTTPConnection(self.backend())
            con.request("GET", self.path)
            res = con.getresponse()
            cached_response = CachedResponse(
                res.status,
                res.reason,
                res.getheader("content-length"),
                res.getheader("content-type"),
                res.read(),
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
            chunk_size = len(chunk)
            con = HTTPConnection(self.backend())
            con.request(
                "POST",
                f"upload-large/{field_storage.filename}",
                headers={
                    "content-length": chunk_size,
                    "content-type": "application/octet-stream",
                },
                body=chunk
            )
            res = con.getresponse()
            if chunk_size < 1024 or res.status != 200:
                break
        self.send_response(res.status, res.reason)
        self.end_headers()


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
