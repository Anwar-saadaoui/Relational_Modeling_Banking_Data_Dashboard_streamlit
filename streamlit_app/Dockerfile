FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir \
    streamlit \
    pandas \
    sqlalchemy \
    psycopg2-binary \
    python-dotenv \
    plotly \
    seaborn \
    matplotlib

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]