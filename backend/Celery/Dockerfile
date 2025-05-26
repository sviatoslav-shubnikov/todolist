FROM python:3.11


WORKDIR /app


COPY . /app


RUN pip install --no-cache-dir -r requirements.txt


RUN groupadd celery && useradd -m -g celery celery

RUN chown -R celery:celery /app && chmod -R 755 /app

USER celery

CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info"]