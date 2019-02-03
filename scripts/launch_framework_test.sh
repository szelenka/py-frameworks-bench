#!/bin/bash

declare -a endpoints=("json" "remote" "complete")

for framework in ${APP_ROOT_SRC}/frameworks/*;
do
  framework=${framework%*/}
  if [ ! -d "${framework}" ]; then
    continue;
  fi
  echo ">>> Starting ${framework##*/} from: ${framework}"

  # specify the process identifier so we can terminate it after the test is over
  PID="/tmp/${framework##*/}.pid"

  # TODO: add logic to prevent multiple scripts from running at the same time

  # default gunicorn options
  OPTS="-p ${PID} -D -w 2"

  if [ "${framework##*/}" = "muffin" ]; then
    OPTS="--daemon --pid ${PID} --workers 2"
    ${framework}/bin/gunicorn app run ${OPTS} --bind 127.0.0.1:5000
  elif [ "${framework##*/}" = "tornado" ]; then
    ${framework}/bin/gunicorn app:app ${OPTS} \
	    --worker-class=gunicorn.workers.gtornado.TornadoWorker --bind=127.0.0.1:5000 \
	    --chdir=${framework}
  elif [ "${framework##*/}" = "twisted" ]; then
    OPTS="-pid &"
    continue
    # TODO: how to specify the PID for twisted?
    # ${framework}/bin/python ${framework}/app.py &
  else
    ${framework}/bin/gunicorn app:app ${OPTS} \
      -k meinheld.gmeinheld.MeinheldWorker --bind=127.0.0.1:5000 \
      --chdir=${framework}
  fi

  echo ">>> wait for ${framework##*/} to startup"
  # TODO: use 'wait' function on port 5000
  sleep 5

  for endpoint in "${endpoints[@]}"
  do
    echo ">>> /${endpoint}"
    OUTPUT_FILE="${APP_ROOT_SRC}/reports/results.csv" TESTEE="${framework##*/}:/${endpoint}" wrk -d${DURATION-20}s -c${CONNECTIONS-200} -t${THREADS-10} --timeout ${TIMEOUT-10}s -s ${APP_ROOT_SRC}/scripts/cvs-report.lua http://127.0.0.1:5000/${endpoint}
  done
  echo ">>> endpoint tests complete!"

  echo ">>> terminate ${framework##*/} for this framework"
  kill `cat ${PID}`

  echo ">>> wait for ${framework##*/} to terminate"
  sleep 5

  echo ">>> marking as complete"
  echo date +"%Y-%m-%dT%H-%M-%S" > "${framework}/last_run.txt"

done