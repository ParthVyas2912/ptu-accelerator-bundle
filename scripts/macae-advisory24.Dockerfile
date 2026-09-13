FROM acrptubundle7d804f70.azurecr.io/macae/backend@sha256:dc067468acd805293835c42c27969d46c301d88799ee297239eebf4140222781
COPY macae_model_guard.py macae_cosmos_budget.py macae_advisory.py /eval/
COPY advisory-team.json advisory-request.txt /eval/
ENV MACAE_LIVE_REQUESTS_ENABLED=false
CMD ["/app/.venv/bin/python", "/eval/macae_cloud_run.py"]
