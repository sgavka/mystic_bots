#!/bin/bash

export PATH="/opt/venv/bin:$PATH"

echo "Running command '$*'"
exec /bin/bash -c "$*"
