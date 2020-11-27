#!/bin/bash

function connect() {
  echo 'select 00:1B:DC:FB:3C:91' \
    && sleep 1 \
    && echo 'connect 0C:DD:24:6A:B0:ED' \
    && sleep 5 \
    && echo 'select 00:1B:DC:FA:C3:80' \
    && sleep 1 \
    && echo 'connect A8:66:7F:35:20:E0' \
    && sleep 5 \
    && echo 'quit'
}

sudo systemctl restart bluetooth
sleep 5
connect | bluetoothctl
sleep 1

cd `dirname $0`
python3 BluezAvrcpVolumeControl.py & python3 BTAggregationSystem.py
