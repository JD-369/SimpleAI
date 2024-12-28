FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PORT=8501
EXPOSE $PORT

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD streamlit run --server.port $PORT --server.address 0.0.0.0 newapp.py
