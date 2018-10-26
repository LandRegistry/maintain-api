# Set the base image to the base image
FROM hmlandregistry/dev_base_python_flask:3

# ----
# Put your app-specific stuff here (extra yum installs etc).
# Any unique environment variables your config.py needs should also be added as ENV entries here

ENV APP_NAME="maintain-api" \
    MINT_API_URL="http://mint-api:8080/v1.0/records" \
    MINT_API_URL_ROOT="http://mint-api:8080" \
    SEARCH_API_URL="http://search-api:8080" \
    AUTHENTICATION_API_URL="http://authentication-api:8080/v2.0" \
    AUTHENTICATION_API_BASE_URL="http://authentication-api:8080" \
    SQL_HOST="postgres" \
    SQL_DATABASE="search_api_db" \
    SQL_PASSWORD="password" \
    APP_SQL_USERNAME="search_api_db_user" \
    ALEMBIC_SQL_USERNAME="alembic_user" \
    SQL_USE_ALEMBIC_USER="false" \
    STATUTORY_PROVISION_CACHE_TIMEOUT_MINUTES="240" \
    MAX_HEALTH_CASCADE=6 \
    SQLALCHEMY_POOL_RECYCLE="3300"

# ----

# The command to run the app is inherited from lr_base_python_flask

# Get the python environment ready.
# Have this at the end so if the files change, all the other steps don't need to be rerun. Same reason why _test is
# first. This ensures the container always has just what is in the requirements files as it will rerun this in a
# clean image.
ADD requirements_test.txt requirements_test.txt
ADD requirements.txt requirements.txt
RUN yum install -y postgresql-devel
RUN pip3 install -q -r requirements.txt && \
  pip3 install -q -r requirements_test.txt
