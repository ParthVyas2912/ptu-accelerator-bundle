# Original frontend Dockerfile runtime stage, consuming the already-tested native production build.
FROM python:3.11-slim
ARG PIP_INDEX_URL=https://packagefeedproxy.microsoft.io/pypi/simple/
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY dist ./dist
COPY frontend_server.py .
EXPOSE 3000
CMD ["uvicorn", "frontend_server:app", "--host", "0.0.0.0", "--port", "3000"]
