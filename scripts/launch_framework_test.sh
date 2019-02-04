#!/bin/bash

my_dir="$(dirname "$0")"
source "$my_dir/methods.sh"

APP_ROOT_SRC=${APP_ROOT_SRC-/opt/app-root/src}
TEST_HTTP_SERVER=${TEST_HTTP_SERVER-127.0.0.1}
TEST_HTTP_PORT=${TEST_HTTP_PORT-5000}
DURATION=${DURATION-20}
CONNECTIONS=${CONNECTIONS-200}
THREADS=${THREADS-10}
TIMEOUT=${TIMEOUT-10}


for framework in ${APP_ROOT_SRC}/frameworks/*;
do
  framework=${framework%*/}
  if [ ! -d "${framework}" ]; then
    continue;
  fi
  if [ "${framework##*/}" = "aiohttp" ] || [ "${framework##*/}" = "klein" ] || [ "${framework##*/}" = "muffin" ] || [ "${framework##*/}" = "twisted" ]; then
    # these fail with python 3.7
    echo ">>> Skipping over ${framework##*/} ..."
    continue;
  fi
  echo ">>> Starting ${framework##*/} from: ${framework}"

  # specify the process identifier so we can terminate it after the test is over
  PID="/tmp/${framework##*/}.pid"

  # TODO: add logic to prevent multiple scripts from running at the same time

  {
    run_wsgi_service "${framework##*/}" "${TEST_HTTP_SERVER}" "${TEST_HTTP_PORT}" "${PID}"
    run_wrt_tests "${framework##*/}" "${TEST_HTTP_SERVER}" "${TEST_HTTP_PORT}" "${DURATION}" "${CONNECTIONS}" "${THREADS}" "${TIMEOUT}"
    kill_and_wait_for_pid "${PID}"
    echo ">>> marking as complete"
    echo $(echo date +"%Y-%m-%dT%H-%M-%S") > "${framework}/last_run.txt"
  } || {
    echo run_wrt_tests">>> Unable to launch ${framework}"
  }
done