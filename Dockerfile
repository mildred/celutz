FROM python:3.9

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

VOLUME /data

ENV CELUTZ_DATA_DIR=/data
ENV CELUTZ_DB_NAME=/data/db.sqlite3
ENV CELUTZ_MEDIA_DIR=/data/media

ENTRYPOINT ["./entrypoint.sh"]
CMD ["manage.py", "runserver", "8000"]
