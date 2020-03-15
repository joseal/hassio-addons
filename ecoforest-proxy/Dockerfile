ARG BUILD_FROM
FROM $BUILD_FROM

COPY ecoforest-proxy.py /

RUN pip install --no-cache-dir requests

HEALTHCHECK --interval=5m --timeout=5s CMD curl --fail http://localhost:8998/healthcheck || exit 1

CMD [ "python", "/ecoforest-proxy.py" ]
