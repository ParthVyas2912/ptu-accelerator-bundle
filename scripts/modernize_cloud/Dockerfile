FROM python:3.11-slim
ARG PIP_INDEX_URL=https://packagefeedproxy.microsoft.io/pypi/simple/
# Same official backend dependency/runtime steps, with the approved evaluation overlay.
RUN apt-get update && \
    apt-get install -y libicu-dev && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x /app/sql_agents/tools/linux-x64/tsqlParser
ENV APP_ENV=prod AZURE_BASIC_LOGGING_LEVEL=WARNING AZURE_PACKAGE_LOGGING_LEVEL=WARNING
EXPOSE 8000
CMD ["uvicorn", "cloud_app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
