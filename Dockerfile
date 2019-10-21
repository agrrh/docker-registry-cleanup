FROM python:3-slim

ENV PYTHONDONTWRITEBYTECODE true

WORKDIR /app

COPY ./requirements.txt ./

RUN pip install -r requirements.txt

COPY ./ ./

ENTRYPOINT ["python3"]
CMD ["main.py"]
