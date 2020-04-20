ARG  IMAGE_REGISTRY
ARG  IMAGE_REPOSITORY
FROM ${IMAGE_REGISTRY}/${IMAGE_REPOSITORY}/base:3.10-alpine-r11

RUN addgroup -g 1000 appuser && \
  adduser -S -G appuser -u 1000 appuser

WORKDIR /app
COPY --chown=appuser requirements.txt /app

RUN apk add --no-cache \
  python3=3.7.5-r1 \
  && pip3 install -r requirements.txt

COPY --chown=appuser analytics.py /app/analytics.py

USER appuser

EXPOSE 8000

ENTRYPOINT ["cinit", "--"]

CMD ["python3", "analytics.py"]
