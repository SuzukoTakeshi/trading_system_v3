#
# auditor/api.py
#
# Auditor API
#
# 役割:
#   ・Auditor状態を外部へ提供
#

from fastapi import FastAPI

from auditor.auditor_client import AuditorClient


app = FastAPI(
    title="Trading System V3 Auditor"
)


auditor = AuditorClient()


@app.get("/auditor")
def get_auditor():

    return auditor.data