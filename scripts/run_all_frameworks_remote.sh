#!/bin/bash
#set -x

APP_ROOT_SRC=${APP_ROOT_SRC-/opt/app-root/src}
TEST_HTTP_SERVER=${TEST_HTTP_SERVER-127.0.0.1}
APP_HTTP_PORT=${APP_HTTP_PORT-8001}
TEST_HTTP_PORT=${TEST_HTTP_PORT-5000}
DURATION=${DURATION-60}
CONNECTIONS=${CONNECTIONS-200}
THREADS=${THREADS-10}
TIMEOUT=${TIMEOUT-10}

my_dir="$(dirname "$0")"
source "$my_dir/methods.sh"

# add headers
echo "title,endpoint,latency.min,latency:percentile(50),latency:percentile(75),latency:percentile(90),latency:percentile(99),latency:percentile(99.9),latency.max,latency.mean,summary.duration,summary.requests,summary.errors.connect,summary.errors.read,summary.errors.write,summary.errors.status,summary.errors.timeout" > "${APP_ROOT_SRC}/reports/results.csv"

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

  # TODO: add logic to prevent multiple scripts from running at the same time


  {
    # wait for the API to start the server
    curl -X PUT "http://${TEST_HTTP_SERVER}:${APP_HTTP_PORT}/frameworks/${framework##*/}"
    echo ''
    wait_for_port "${framework##*/}" "${TEST_HTTP_SERVER}" "${TEST_HTTP_PORT}"

    # execute tests
    run_wrt_tests "${framework##*/}" "${TEST_HTTP_SERVER}" "${TEST_HTTP_PORT}" "${DURATION}" "${CONNECTIONS}" "${THREADS}" "${TIMEOUT}"

    # stop the remote server
    curl -X DELETE "http://${TEST_HTTP_SERVER}:${APP_HTTP_PORT}/frameworks/${framework##*/}"
    echo ''

    echo ">>> marking as complete"
    echo $(echo date +"%Y-%m-%dT%H-%M-%S") > "${framework}/last_run.txt"
  } || {
    echo run_wrt_tests">>> Unable to launch ${framework}"
  }
done