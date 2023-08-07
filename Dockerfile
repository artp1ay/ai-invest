FROM python:3.10

WORKDIR /invest
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir app
COPY app /invest/app/
COPY main.py /invest
EXPOSE 5000

CMD ["python", "main.py"]
