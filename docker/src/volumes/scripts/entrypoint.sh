#!/bin/bash


cmd="python3 -m fileagent"

if [ -n "$PORT" ]; then
    cmd+=" --port $PORT"
fi

if [ -n "$HOST" ]; then
    cmd+=" --host $HOST"
fi

if [ -n "$DIRECTORY" ]; then
    cmd+=" --directory $DIRECTORY"
fi

if [ -n "$FILE" ]; then
    cmd+=" --file $FILE"
fi

eval "$cmd"
