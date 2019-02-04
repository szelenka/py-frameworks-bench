FROM python:3.6-slim-stretch

ENV APP_ROOT_SRC="/opt/app-root/src"
ENV GUNICORN_VERSION="19.9.0"

COPY ./docker/frameworks/requirements.txt /tmp/requirements.txt
COPY ./docker/frameworks/requirements-apt.txt /tmp/requirements-apt.txt

# add source code and execution file
COPY ./frameworks/ ${APP_ROOT_SRC}/frameworks/

WORKDIR ${APP_ROOT_SRC}

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
    && echo "execute virtualenv pip install for each framework ..." \
    && chgrp -R 0 ${APP_ROOT_SRC} \
    && chmod -R g+rwX ${APP_ROOT_SRC} \
    && for framework in ${APP_ROOT_SRC}/frameworks/*; \
      do \
        framework=${framework%*/} \
        && if [ ! -d "${framework}" ]; then continue; fi \
        && echo ">>> Installing ${framework##*/}" \
        && virtualenv ${framework} --python=python3 --system-site-packages \
#        && source ${framework}/bin/activate \
        && CFLAGS="-Os -g0 -Wl,--strip-all" ${framework}/bin/pip install \
          --no-cache-dir \
          --compile \
          --global-option=build_ext \
          --global-option="-I/usr/include:/usr/local/include" \
          --global-option="-L/usr/lib:/usr/local/lib" \
          --global-option="-j 4" \
          -r ${framework}/requirements.txt \
        # gunicorn needs to be installed in EACH virtualenv...
        && ${framework}/bin/pip install -I gunicorn==${GUNICORN_VERSION} \
#        && deactivate \
        ; \
      done \
    # environment for the basic webapp
    && virtualenv webapp-frameworks --python=python3 --system-site-packages \
    && ${APP_ROOT_SRC}/webapp-frameworks/bin/pip install -I flask gunicorn==${GUNICORN_VERSION} \
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

#RUN apt-get update && apt-get install -yqq procps vim

COPY ./webapp-frameworks/ ${APP_ROOT_SRC}/webapp-frameworks/
COPY ./scripts/ ${APP_ROOT_SRC}/scripts/
COPY ./docker/frameworks/gunicorn.conf ${APP_ROOT_SRC}/gunicorn.conf
COPY ./docker/frameworks/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN ln -s /usr/local/bin/docker-entrypoint.sh / \
  && mkdir -p ${APP_ROOT_SRC}/reports \
  && chgrp -R 0 \
    /usr/local/bin/docker-entrypoint.sh \
    /etc/passwd \
    ${APP_ROOT_SRC}/webapp-frameworks \
    ${APP_ROOT_SRC}/scripts \
    ${APP_ROOT_SRC}/reports \
  && chmod -R g+rwX \
    /usr/local/bin/docker-entrypoint.sh \
    /etc/passwd \
    ${APP_ROOT_SRC}/webapp-frameworks \
    ${APP_ROOT_SRC}/scripts \
    ${APP_ROOT_SRC}/reports \
  && chmod 770 \
    /usr/local/bin/docker-entrypoint.sh \
    /etc/passwd \
  && chmod -R 770 \
    ${APP_ROOT_SRC}/scripts

EXPOSE 8001 5000
ENTRYPOINT ["docker-entrypoint.sh"]