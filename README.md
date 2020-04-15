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
