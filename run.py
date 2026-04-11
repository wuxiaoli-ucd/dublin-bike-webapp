import os
from app import create_app
from app.services.db import get_db_settings


app = create_app()

if __name__ == "__main__":
    deploy_env = os.getenv("DEPLOY_ENV", "local").lower()

    host = "127.0.0.1" if deploy_env == "local" else "0.0.0.0" # is 0.0.0.0 okay for final product?
    port = int(os.getenv("PORT", "5001"))

    # when deployed in ec2, the debug turned to false for information securuty
    debug = deploy_env == "local"
    db_settings = get_db_settings()

    print("Running on:", deploy_env)
    print("Host:", host)
    print("Port:", port)
    print("DB_HOST =", db_settings["host"])
    print("DB_NAME =", db_settings["db"])
 
    app.run(host=host, port=port, debug=debug)
