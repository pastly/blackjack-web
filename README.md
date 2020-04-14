# Notes for deploying to AWS

In a fresh virtualenv,
install latest flask and gunicorn.

Update `requirements.txt`:

    pip freeze | grep -v pkg-resources > requirements.txt

`git commit` to the state that you want to deploy, then `eb deploy`.
