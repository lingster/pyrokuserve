FROM python:3.6
COPY . /app
WORKDIR /app
RUN python -m pip install pipenv
#RUN pip install pipenv
RUN pipenv install
EXPOSE 8000
CMD ["python", "pyrokuserve.py"]
