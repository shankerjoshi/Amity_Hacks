FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 BIND_HOST=0.0.0.0
WORKDIR /app
COPY sentinel ./sentinel
COPY web ./web
RUN useradd --create-home --uid 10001 sentinel && mkdir /app/data && chown sentinel:sentinel /app/data
USER sentinel
CMD ["python", "-m", "sentinel.control"]
