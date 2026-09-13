FROM acrptubundle7d804f70.azurecr.io/macae/backend@sha256:ef9b436b6bee78259d00180899a86f3724adb385843c54245e79893eb691386d
COPY connection_config.py /app/orchestration/connection_config.py
COPY macae_model_guard.py macae_cosmos_budget.py macae_cloud_run.py /eval/
COPY macae_second_pass_admin.py /eval/
ENV MACAE_LIVE_REQUESTS_ENABLED=false
CMD ["/app/.venv/bin/python", "/eval/macae_cloud_run.py"]
