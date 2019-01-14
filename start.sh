#!/bin/sh
/etc/init.d/rethinkdb start
nohup python3 vmemperor.py &
cd new-frontend
npm run start
