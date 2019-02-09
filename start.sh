#!/bin/sh
/etc/init.d/rethinkdb start
nohup python3.7 vmemperor.py &
cd frontend
npm run start
