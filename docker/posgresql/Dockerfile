# https://github.com/sclorg/postgresql-container
FROM centos/postgresql-10-centos7:latest

# post-start scripts
# https://github.com/sclorg/postgresql-container/blob/master/src/root/usr/bin/run-postgresql
COPY ./docker/postgres.sh ${APP_DATA}/src/postgresql-start/py_frameworks_bench.sh
COPY ./docker/dump.sql /tmp/dump.sql
