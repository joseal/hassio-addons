FROM python:2.7.17
COPY requirements.txt /
COPY ecoforest-proxy.py /
RUN pip install --no-cache-dir -r requirements.txt
HEALTHCHECK --interval=5m --timeout=5s CMD curl --fail http://localhost:8998/healthcheck || exit 1
CMD [ "python", "/ecoforest-proxy.py" ]
