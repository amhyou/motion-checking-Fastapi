FROM python:3.10-slim-buster


WORKDIR /saas


COPY ./requirements.txt /saas/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /saas/requirements.txt


COPY ./app /saas/app

 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]