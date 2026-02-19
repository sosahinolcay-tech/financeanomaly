FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY apps/ ./apps/
COPY configs/ ./configs/
ENV PYTHONPATH=/app:/app/src
EXPOSE 8501
CMD ["streamlit", "run", "apps/dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
