FROM python:3.9-alpine
RUN apk update && apk upgrade
RUN pip install -U pip
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5580
CMD ["gunicorn", "-b", "0.0.0.0:5580", "-w", "2", "app:app"]
