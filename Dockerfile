FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "newapp.py", "--server.port=8501", "--server.address=0.0.0.0"]