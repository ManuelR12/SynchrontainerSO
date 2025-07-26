
FROM python:3

WORKDIR /usr/src/app


COPY ./myapp/ .

RUN pip3 install -r requirements.txt

RUN mkdir -p /sync_files

RUN mkdir -p /sync_files/public
RUN mkdir -p /sync_files/private

RUN chmod -R 777 /sync_files

EXPOSE 5000

CMD ["python3", "./app.py"]
