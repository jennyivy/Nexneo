#!/bin/bash

ROOT_DIR='root.Nexneo.app'
echo "starting sanic service"
START="nohup python -m sanic app.app.app --host=0.0.0.0 --port=8000 --workers=6 >log/test1.log 2>&1"
eval $START
echo "done."
