#!/bin/bash
set -x

APP_ROOT_SRC=${APP_ROOT_SRC-/opt/app-root/src}
TRY_LOOP=${TRY_LOOP-30}

wait_for_port() {
  local name="$1" host="$2" port="$3"
  local j=0
  while ! nc -z "${host}" "${port}" >/dev/null 2>&1 < /dev/null; do
    j=$((j+1))
    if [ $j -ge ${TRY_LOOP} ]; then
      echo >&2 "$(date) - ${host}:${port} still not reachable, giving up"
      exit 1
    fi
    echo "$(date) - waiting for ${name}... ${j}/${TRY_LOOP}"
    sleep 1
  done
}


kill_and_wait_for_pid() {
  local framework="${1}" j=0 pid="/tmp/${framework}.pid"
  $(kill `cat ${pid}`)
  echo ">>> wait for ${pid} to terminate"
  # TODO: wait for PID to terminate?
  while [ -f "${pid}" ]; do
    j=$((j+1))
    if [ $j -ge ${TRY_LOOP} ]; then
      echo >&2 "$(date) - $(cat ${pid}) still running, forcing kill..."
      kill -9 `cat ${pid}`
      exit 0
    fi
    echo "$(date) - waiting for $(cat ${pid}) to terminate... ${j}/${TRY_LOOP}"
    sleep 1
  done
  echo ">>> ${pid} terminated"

}


run_wsgi_service() {
  # default gunicorn options
  local framework="${1}" http_server="${2}" http_port="${3}"
  local pid="/tmp/${framework}.pid"
  local dir="${APP_ROOT_SRC}/frameworks/${framework}"
  local opts="--pid ${pid} --workers 2 --chdir=${dir} --bind=${http_server}:${http_port}"
  local cmd="${dir}/bin/gunicorn app:app ${opts}"
  local worker_class="meinheld.gmeinheld.MeinheldWorker"

  if [ "${framework}" = "tornado" ]; then
    worker_class="gunicorn.workers.gtornado.TornadoWorker"
  elif [ "${framework}" = "responder" ]; then
    worker_class="uvicorn.workers.UvicornWorker"
  elif [ "${framework}" = "twisted" ]; then
    opts="-pid &"
    continue
    # TODO: how to specify the PID for twisted?
    # ${framework}/bin/python ${framework}/app.py &
  elif [ "${framework}" = "weppy" ]; then
    rm -rf ${dir}/databases
  fi

  cmd="${cmd} --worker-class=${worker_class} --daemon"

  echo ">>> Starting ${framework} from: ${APP_ROOT_SRC}/frameworks/${framework}"
  echo ${cmd}
  eval ${cmd}
  wait_for_port "${framework}" "${http_server}" "${http_port}"
  echo ">>> ${framework} started in PID [$(cat ${pid})] ${pid}"
}

run_wrt_tests() {
  local framework="${1}" http_server="${2}" http_port="${3}" duration="${4}" connections="${5}" threads="${6}" timeout="${7}"
  declare -a endpoints=("json" "remote" "complete")
  for endpoint in "${endpoints[@]}"
  do
    echo ">>> /${endpoint}"
    OUTPUT_FILE="${APP_ROOT_SRC}/reports/results.csv" \
      TESTEE="${framework},/${endpoint}" \
      wrk \
        -d${duration}s \
        -c${connections} \
        -t${threads} \
        --timeout ${timeout}s \
        -s ${APP_ROOT_SRC}/scripts/cvs-report.lua \
        http://${http_server}:${http_port}/${endpoint}
  done
  echo ">>> endpoint tests complete!"
}