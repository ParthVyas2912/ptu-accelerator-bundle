FROM acrptubundle7d804f70.azurecr.io/conversation/api@sha256:baa11a820f821532ade2129fe5dd628764b9053778b3ef6d35e89fa2345ee8f8
COPY --chown=appuser:appuser ckm_serving.py ckm_serving_guard.py ckm_serving_probe.py ckm-serving-expected.json ckm_sql_identity.py /app/src/api/
RUN python -m py_compile /app/src/api/ckm_serving.py /app/src/api/ckm_serving_guard.py /app/src/api/ckm_serving_probe.py
CMD ["uvicorn", "src.api.ckm_serving:app", "--host", "0.0.0.0", "--port", "8000"]
