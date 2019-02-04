FROM python:3.6-slim-stretch

ENV APP_ROOT_SRC="/opt/app-root/src"

COPY ./docker/py-frameworks-bench/requirements.txt /tmp/requirements.txt
COPY ./docker/py-frameworks-bench/requirements-apt.txt /tmp/requirements-apt.txt

# install python packages
RUN set -ex \
    && buildDeps=' \
      build-essential \
      gcc \
      gfortran \
      python3-dev \
      pax-utils \
    ' \
    && apt-get update -yqq \
    && apt-get upgrade -yqq \
    && apt-get install -yqq --no-install-recommends $buildDeps wrk curl netcat \
    && cat /tmp/requirements-apt.txt | egrep -v "^\s*(#|$)" | xargs apt-get install -yqq \
    && CFLAGS="-Os -g0 -Wl,--strip-all" /usr/local/bin/pip install \
        --no-cache-dir \
        --compile \
        --global-option=build_ext \
        --global-option="-I/usr/include:/usr/local/include" \
        --global-option="-L/usr/lib:/usr/local/lib" \
        --global-option="-j 4" \
        -r /tmp/requirements.txt \
    && runDeps="$( \
        scanelf --needed --nobanner --recursive /usr/local \
              | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
              | sort -u | cut -c4- \
              | xargs dpkg --search \
              | cut -d ':' -f 1 | sort -u \
      )" \
    && apt-get install -yqq --no-install-recommends $runDeps \
    && apt-get purge --auto-remove -yqq $buildDeps \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base

COPY ./docker/py-frameworks-bench/gunicorn.conf ${APP_ROOT_SRC}/gunicorn.conf
COPY ./docker/py-frameworks-bench/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN ln -s /usr/local/bin/docker-entrypoint.sh / \
  && mkdir -p ${APP_ROOT_SRC}/reports \
  && chgrp -R 0 \
    /usr/local/bin/docker-entrypoint.sh \
    /etc/passwd \
    ${APP_ROOT_SRC} \
  && chmod -R g+rwX \
    /usr/local/bin/docker-entrypoint.sh \
    /etc/passwd \
    ${APP_ROOT_SRC} \
  && chmod 770 \
    /usr/local/bin/docker-entrypoint.sh \
    /etc/passwd \
    ${APP_ROOT_SRC}/scripts/launch_framework_test.sh

WORKDIR ${APP_ROOT_SRC}
EXPOSE 8080
ENTRYPOINT ["docker-entrypoint.sh"]