import os
from dotenv import load_dotenv
from app import create_app

load_dotenv()
app = create_app()

if __name__ == "__main__":
    deploy_env = os.getenv("DEPLOY_ENV", "local").lower()

    host = "127.0.0.1" if deploy_env == "local" else "0.0.0.0"
    port = int(os.getenv("PORT", "5001"))

    # when deployed in ec2, the debug turned to false for information securuty
    debug = deploy_env == "local"

    print("Running in:", deploy_env)
    print("Host:", host)
    print("Port:", port)
    print("DB_HOST =", app.config.get("DB_HOST"))
    print("DB_NAME =", app.config.get("DB_NAME"))
 
    app.run(host=host, port=port, debug=debug)
