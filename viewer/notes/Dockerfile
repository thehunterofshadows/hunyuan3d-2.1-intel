FROM python:3.12-alpine
WORKDIR /app
COPY viewer/notes/*.py /app/
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 NOTES_DIR=/data
USER 1000:1000
EXPOSE 8080
CMD ["python", "/app/server.py"]
