FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir flask
COPY app.py .
ENV DATA_DIR=/data
EXPOSE 8080
CMD ["python", "app.py"]
