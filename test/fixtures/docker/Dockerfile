FROM nginxinc/nginx-unprivileged:1.30-alpine@sha256:15c994d10d6d78658721c3bcafff14cb281fba2a4bdf9d5ba92c416a472516e3
USER root
COPY index.html /usr/share/nginx/html/
ARG SOURCE_COMMIT=unknown
RUN echo "$SOURCE_COMMIT" > /usr/share/nginx/html/version.txt
USER 101
