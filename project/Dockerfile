FROM python:3.8

COPY ./techtrends /src

WORKDIR /src

RUN pip3 install -r requirements.txt

RUN python init_db.py

EXPOSE 3111

ENTRYPOINT ["python", "app.py"]
