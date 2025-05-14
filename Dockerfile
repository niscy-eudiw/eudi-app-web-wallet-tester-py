FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR .

COPY . .

RUN pip install --no-cache-dir -r wallet/requirements.txt

#CMD ["sh", "-c", "flask --app wallet run --debug --host=0.0.0.0 --cert=certs/cert.pem --key=certs/key.pem"]
CMD ["sh", "-c", "flask --app wallet run --debug --host=0.0.0.0"]
