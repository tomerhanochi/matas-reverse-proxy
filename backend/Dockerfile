FROM python:3.12-alpine3.19

WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["/usr/local/bin/python", "main.py"]