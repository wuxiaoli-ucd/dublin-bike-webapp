import os
from app import create_app
from app.services.db import get_db_settings


app = create_app()

if __name__ == "__main__":
    """
    Runs the Flask development server.

    Behaviour varies depending on DEPLOY_ENV:
    - local: runs on localhost with debug enabled
    - production (e.g. EC2): binds to all interfaces with debug disabled
    """
    deploy_env = os.getenv("DEPLOY_ENV", "local").lower()

    host = "127.0.0.1" if deploy_env == "local" else "0.0.0.0"
    port = int(os.getenv("PORT", "5001"))

    # when deployed in ec2, the debug is turned to false for information security
    debug = deploy_env == "local"
    db_settings = get_db_settings()

    print("Running on:", deploy_env)
    print("Host:", host)
    print("Port:", port)
    print("DB_HOST =", db_settings["host"])
    print("DB_NAME =", db_settings["db"])
 
    app.run(host=host, port=port, debug=debug)
