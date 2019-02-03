FROM nginx:1.13.12-alpine

COPY ./docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./docker/nginx/index.html /usr/share/nginx/html

RUN ln -sf /dev/stdout /var/log/nginx/access.log \
  && ln -sf /dev/stderr /var/log/nginx/error.log \
  && rm /etc/nginx/conf.d/default.conf \
  # setup NGINX directories for 'root' group access (for restrictive K8 deplioyments)
  && mkdir -p \
    /tmp/nginx \
    /spool/nginx \
    /spool/nginx/uwsgi_temp \
    /spool/nginx/scgi_temp \
    /spool/nginx/proxy_temp \
    /spool/nginx/fastcgi_temp \
    /spool/nginx/client_temp \
  && chmod 777 -R \
    /var/log \
    /var/cache \
    /var/run \
    /tmp/nginx \
    /spool/nginx \
  && chgrp -R 0 \
    /etc/nginx \
    /tmp/nginx \
    /spool/nginx \
  && chmod -R g+rwX \
    /etc/nginx \
    /tmp/nginx \
    /spool/nginx \
  && chgrp -R 0 \
    /etc/passwd \
    /usr/share/nginx/ \
  && chmod -R g+rwX \
    /etc/passwd \
    /usr/share/nginx/ \
  && chmod 770 \
    /etc/passwd

EXPOSE 8080
ENTRYPOINT ["nginx", "-g", '"daemon off;"', "-c", "/etc/nginx/nginx.conf"]