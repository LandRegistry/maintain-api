from flask_script import Manager
from maintain_api.main import app
import os

manager = Manager(app)


@manager.command
def runserver(port=9998):
    """Run the app using flask server"""

    os.environ["PYTHONUNBUFFERED"] = "yes"
    os.environ["FLASK_LOG_LEVEL"] = "DEBUG"
    os.environ["COMMIT"] = "LOCAL"
    os.environ["APP_NAME"] = "maintain-api"

    app.run(debug=True, port=int(port))


if __name__ == "__main__":
    manager.run()
