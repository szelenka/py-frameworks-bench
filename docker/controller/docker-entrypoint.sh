#!/bin/bash

set -e

# if the running user is an Arbitrary User ID which is not present in whoami
if ! whoami &> /dev/null; then
  # make sure we have read/write access to /etc/passwd
  if [ -w /etc/passwd ]; then
    # write a line in /etc/passwd for the Arbitrary User ID in the 'root' group
    echo "${USER_NAME:-default}:x:$(id -u):0:${USER_NAME:-default} user:${HOME}:/sbin/nologin" >> /etc/passwd
  else
    echo "read-write access denied for USER_ID:$(id -u) on /etc/passwd"
    exit 1
  fi
fi


# launch gunicorn
exec gunicorn app:app \
  -c ${APP_ROOT_SRC}/gunicorn.conf \
  -p /tmp/webapp.pid \
  --bind=0.0.0.0:8002 \
  --chdir=${APP_ROOT_SRC}/webapp-controller
