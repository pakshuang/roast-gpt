FROM python:3.10-alpine

RUN pip install pipenv
ADD Pipfile.lock .
RUN pipenv requirements > requirements.txt
RUN pip uninstall pipenv -y
RUN pip install -r requirements.txt

ADD main.py .
ADD config.py .
ADD .env .

CMD ["python", "-u", "./main.py"] 