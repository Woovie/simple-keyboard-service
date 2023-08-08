FROM python:3.11

WORKDIR /code
COPY . /code
RUN pip install --no-cache-dir --upgrade -r /code/requirements.lock
WORKDIR /code/src/simple_keyboard_service

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]