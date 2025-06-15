FROM ubuntu:latest

RUN apt-get update && apt-get install -y python3-pip python3-venv
RUN python3 -m venv venv
RUN . venv/bin/activate
RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

EXPOSE 8000


