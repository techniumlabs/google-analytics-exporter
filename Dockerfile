ARG  IMAGE_REGISTRY
ARG  IMAGE_REPOSITORY
FROM ${IMAGE_REGISTRY}/${IMAGE_REPOSITORY}/base:3.10-alpine-r11

WORKDIR /app
COPY requirements.txt /app

RUN apk add --no-cache \
  python3=3.7.5-r1 \
  && pip3 install -r requirements.txt

COPY analytics.py /app/analytics.py

EXPOSE 8080

ENTRYPOINT ["cinit", "--", "python3", "analytics.py"]
