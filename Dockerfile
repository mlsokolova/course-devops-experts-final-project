FROM python:3.11-slim
ENV MPLBACKEND=Agg
COPY Quakewatch/ /Quakewatch/
WORKDIR /Quakewatch
RUN pip install --no-cache-dir -r requirements.txt \
    && python -c "import duckdb; conn = duckdb.connect(':memory:'); conn.execute('install spatial')"
EXPOSE 5000
CMD ["python", "app.py"]
