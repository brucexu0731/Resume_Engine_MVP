# Resume Engine MVP

## Project Overview

This is a standalone MVP built to test Become Consulting's resume parser.
It implements the end-to-end workflow in an isolated environment with its
own backend, database, and infrastructure, with the goal of integrating
the validated solution into the company's production backend and database.


## Backend /SpringBootBackend
This directory contains the backend of the resume parser workflow deployed 
to AWS ECS. It hosts two main workflows: resume parsing and saving, and RAG 
retrival. For API contracts, database schemas and data flow charts, reference
the files below.

### /docs/architecture.md
Basic System Architecture and core components
```mermaid
---
config:
  layout: elk
---
flowchart TD

subgraph APP["Application"]
    direction TD 
    C["Client"]
    API["API Gateway"]
    B["Spring Boot Backend"]
    S3[("AWS S3")]
    L["Parser Lambda"]
    DB[("PostgreSQL")]
    
    C <-->|"1. Presign / 3. Parse / 5. Save"| API
    API <-->|"REST API"| B
    C -->|"2. Upload file"| S3
    B <-->|"4. Invoke / return JSON"| L
    L -->|"Read file"| S3
    B -->|"6. Persist validated data"| DB
end

subgraph LOGS["Observability"]
    O["CloudWatch Logs & Metrics"]
end

L -->|"Parser Script & Lambda Logs"| O
B -->|"Backend Logs"| O

```

### /docs/API.md
API documentation

### /docs/database.md
Database schema

### /docs/workflows
Contains core data flow of two main backend workflows: Resume Parsing & RAG

## Frontend /resume-pipeline-frontend

This directory contains a basic frontend for testing, written in REACT

## PDF Extraction /resume-parser-lambda

Serverless resume parsing script using LLMs and Python libraries hosted 
on AWS Lambda with Github Actions CI/CD.