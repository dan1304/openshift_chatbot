#!/bin/bash

export FLASK_APP=main.py
export FLASK_RUN_PORT=8080
# init db
flask db init
flask db migrate
flask db upgrade
# flask run --host=0.0.0.0
python main.py

