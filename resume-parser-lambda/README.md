# Lambda Parser 

This directory contains the python script that parses the resume PDFs into 
structured JSON fields. Containerized and deployed on AWS Lambda.

### Architecture and Flow

```mermaid
---
config:
  layout: elk
---
flowchart LR
PDF["PDF Resume<br/>Multi-page document"]

EXTRACT["1. PyMuPDF Text Extraction<br/>Read pages, extract embedded text, combine pages"]

CLEAN["2. Text Cleaning & Normalization<br/>Encoding repair, Unicode normalization, whitespace cleanup"]

subgraph LLM["3. Three LLM Extraction Passes"]
    direction LR
    PERSONAL["Personal"]
    WORK["Work"]
    EDU["Education"]
end

JSON["4. Structured JSON<br/>personal · work · education"]

PDF --> EXTRACT
EXTRACT --> CLEAN

CLEAN --> PERSONAL
CLEAN --> WORK
CLEAN --> EDU

PERSONAL --> JSON
WORK --> JSON
EDU --> JSON

style PERSONAL fill:#06231a,stroke:#16a34a,color:#ffffff
style WORK fill:#06231a,stroke:#16a34a,color:#ffffff
style EDU fill:#06231a,stroke:#16a34a,color:#ffffff
```

### Testing Locally
1. Navigate to directory: `cd resume-parser-lambda`
2. Create virtual environment: `python3.12 -m venv .venv`
3. Activate .venv (mac): `source .venv/bin/activate`
4. Install Dependencies: `pip install -r requirementsDocker.txt`
5. Configure environment variables: 
   - OPENAI_API_KEY=your-api-key
   - OPENAI_CHAT_MODEL=your-gpt-model(default gpt-4.1-mini)
6. Add your test resume in the /data directory, and configure `line 280` in main.py 
to match your test file's name: `result = extract_text_from_resume("data/A5.pdf")`
7. run main.py: `python main.py`