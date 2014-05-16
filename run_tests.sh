#! /usr/bin/env sh

PYTHONPATH="$PYTHONPATH:src/"
sudo env PYTHONPATH=$PYTHONPATH py.test src/edeposit/amqp/ftp/tests