FROM python:3.8
WORKDIR "/code"
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./photographer_service.py /code
COPY ./models.py /code
ENV MONGO_HOST 172.17.0.2
CMD ["uvicorn", "photographer_service:app", "--host", "0.0.0.0", "--port", "80"]


