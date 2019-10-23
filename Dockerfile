FROM python:3-slim

ENV PYTHONDONTWRITEBYTECODE true

WORKDIR /app

COPY ./requirements.txt ./

RUN apt-get update \
  && apt-get install git -y \
  && pip install -r requirements.txt \
  && apt-get purge git -y \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/*

COPY ./ ./

ENTRYPOINT ["python3"]
CMD ["main.py"]
