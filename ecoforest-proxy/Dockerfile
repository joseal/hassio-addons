ARG BUILD_FROM
FROM $BUILD_FROM

COPY ecoforest-proxy.py /

RUN pip install --no-cache-dir requests

HEALTHCHECK --interval=2m --timeout=30s CMD curl --fail http://localhost:8998/healthcheck || exit 1

ENTRYPOINT [ "" ]

CMD [ "python3", "/ecoforest-proxy.py" ]
