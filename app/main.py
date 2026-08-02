#
# app/main.py
#
# Application Entry Point
#
# 役割:
#   ・Trading System V2 起動
#   ・APIサーバー常駐
#
#


import uvicorn



def main():

    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=8000,
        access_log=False,
    )



if __name__ == "__main__":

    main()