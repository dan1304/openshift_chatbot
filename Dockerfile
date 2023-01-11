FROM python:3.10
COPY ./src/rq.txt /opt/rq.txt
RUN pip install -r /opt/rq.txt
COPY ./src/ /opt/
WORKDIR /opt/
ENTRYPOINT [ "sh", "start.sh" ]