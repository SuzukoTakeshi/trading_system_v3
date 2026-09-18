#
# auditor/main.py
#
# Auditor Main
#
# 役割:
#   ・Auditor起動
#   ・Auditor APIサーバー起動
#
#	python -m auditor.main
#

import uvicorn

from core.config_loader import Config


def main():

    config = Config.instance().data

    server = config.get("server", {})
    auditor_port = server.get("auditor_port", 8508)

    uvicorn.run(
        "auditor.api:app",
        host="0.0.0.0",
        port=auditor_port,
        access_log=False,
    )


if __name__ == "__main__":
    main()