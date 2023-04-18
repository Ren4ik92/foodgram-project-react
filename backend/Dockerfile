FROM python:3.10.10
WORKDIR /app
COPY . .
RUN pip3 install -r /app/requirements.txt --no-cache-dir
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000" ]
LABEL author='Belotserkovets Mikhail' version=1.0.0
