# Notes for deploying to AWS

Whenever you install a new package into the virtualenv, update
`requirements.txt`:

    pip freeze | grep -v pkg-resources > requirements.txt

`git commit` to the state that you want to deploy, then `eb deploy`.

# Environment variables

These contain sensitive information. I've stored them in

    pass Servers/aws/blackjack-web-deb/env

You can view them with `eb printenv`

# PostgreSQL

The credentials are stored in pass.

Upon changing the models in the code, you need to update the schema in the
database. Create the migrations:

    flask db migrate -m "description of changes made"

To apply the migrations to the local test database, simply do:

    flask db upgrade

To apply the migrations to the real database:

    ./db-tunnel.sh &
    bash
    source bj-venv/bin/activate
    source <(pass Servers/aws/blackjack-web-dev/postgres-env)
    flask db upgrade
    exit
    kill %1
