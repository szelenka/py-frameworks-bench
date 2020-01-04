#!/bin/bash
#set -x

APP_ROOT_SRC=${APP_ROOT_SRC-/opt/app-root/src}
TEST_HTTP_SERVER=${TEST_HTTP_SERVER-127.0.0.1}
TEST_HTTP_PORT=${TEST_HTTP_PORT-5000}
DURATION=${DURATION-20}
CONNECTIONS=${CONNECTIONS-200}
THREADS=${THREADS-10}
TIMEOUT=${TIMEOUT-10}

my_dir="$(dirname "$0")"
source "$my_dir/methods.sh"

framework="${1}"

kill_and_wait_for_pid "${framework}"
echo ">>> marking as complete"
echo $(echo date +"%Y-%m-%dT%H-%M-%S") > "${framework}/last_run.txt"