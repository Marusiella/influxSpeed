FROM python:alpine3.15
WORKDIR /app
COPY .env .env
COPY main.py main.py
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
CMD ["python","-u","main.py"]
