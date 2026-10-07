FROM nginx:1.30-alpine@sha256:0985e772fb9f729e6fa0980da05fca5d9c468e870eed43071545afa9d2e27d94
ARG SOURCE_COMMIT=unknown
COPY index.html /usr/share/nginx/html/
RUN echo "$SOURCE_COMMIT" > /usr/share/nginx/html/version.txt
