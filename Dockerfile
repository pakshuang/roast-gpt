FROM public.ecr.aws/docker/library/python:3.10-alpine

RUN apk add py3-pip
RUN pip install pipenv
ADD Pipfile.lock .
RUN pipenv requirements > requirements.txt
RUN pip uninstall pipenv -y
RUN pip install -r requirements.txt

ADD main.py .
ADD config.py .

CMD ["python", "-u", "./main.py"] 
