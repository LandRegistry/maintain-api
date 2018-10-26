# Maintain API

This is the repository for the maintain API used by the Maintain LLC application.

### Local Quick Start (Outside Docker)

```shell
# For Flask CLI
export FLASK_APP=maintain_api/main.py
export FLASK_DEBUG=1
# For Python
export PYTHONUNBUFFERED=yes
# For gunicorn
export PORT=9998
# For app's config.py
export FLASK_LOG_LEVEL=DEBUG
export COMMIT=LOCAL
export APP_NAME=maintain-api

# Run the app
flask run
```

### Documentation

The API has been documented using swagger YAML files. 

The swagger files can be found under the [documentation](maintain_api/documentation) directory.

At present the documentation is not hooked into any viewer within the dev environment. To edit or view the documentation open the YAML file in swagger.io <http://editor.swagger.io>

### Unit tests

To run the unit tests if you are using the common dev-env use the following command:
```
docker-compose exec maintain-api make unittest
or (using the alias)
unit-test maintain-api
```

### Linting

Linting is performed with [Flake8](http://flake8.pycqa.org/en/latest/).

To run linting:
```
docker-compose exec maintain-api make lint
or
exec maintain-api make lint
```
