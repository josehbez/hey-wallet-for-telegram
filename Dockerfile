
FROM python:3.6-stretch
LABEL version="1.0.0"
LABEL maintainer="José Hernández - @josehbez"
LABEL company ="Sentilis"

ENV MYHOME=/heywallet

WORKDIR ${MYHOME}
COPY ./ ${MYHOME}

RUN pip install --upgrade pip 
RUN pip install -r ${MYHOME}/requirements.txt

ENTRYPOINT ["python"]

CMD ["main.py"]