FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/fastapi/generated_scripts /app/gherkin_scenarios /app/steps /app/config && \
    chmod -R 777 /app/fastapi/generated_scripts /app/gherkin_scenarios /app/steps /app/config /app/output.py

# Allow 777 acccess to config/*.xlsx
RUN chmod -R 777 "/app/config/Direct Patient for ref reject.xlsx"
RUN chmod -R 777 "/app/config/Direct Patient.xlsx"
RUN chmod -R 777 "/app/config/Direct Patient for ref reject.xlsx"

EXPOSE 8000

CMD ["python", "fastapi/fastapi_workflow_api.py"]
