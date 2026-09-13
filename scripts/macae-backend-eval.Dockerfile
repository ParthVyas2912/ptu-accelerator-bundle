ARG BASE_IMAGE=ptu-macae-backend:8ac703a7
FROM ${BASE_IMAGE}
COPY macae_model_guard.py macae_cosmos_budget.py macae_cloud_run.py /eval/
COPY macae_cloud_test.py /eval/
COPY macae_cloud_ingest.py /eval/
COPY --from=hrpack hr.json /eval/hr.json
COPY --from=indexscripts index_datasets.py /eval/index_datasets.py
COPY --from=testdata ptu-macae-rfp.txt ptu-macae-contract.txt /eval/data/
ENV MACAE_LIVE_REQUESTS_ENABLED=false
CMD ["/app/.venv/bin/python", "/eval/macae_cloud_run.py"]
