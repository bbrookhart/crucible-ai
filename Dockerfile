FROM python:3.12.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

RUN addgroup --system crucible && adduser --system --ingroup crucible crucible
WORKDIR /app
COPY crucible /app/crucible
USER crucible
EXPOSE 8080
ENTRYPOINT ["python", "-m", "crucible.service"]
