""" 
Resume parsing utilities. This module provides functions for: 
- Cleaning raw text extracted from PDF resumes. 
- Building LLM prompts for personal, work, and education extraction. 
- Sending resume text to an OpenAI chat model through LangChain. 
- Extracting text from multi-page PDF resumes using PyMuPDF. 
- Returning structured resume data as Python dictionaries. 
"""
import re
from pathlib import Path
import pymupdf

import unicodedata

from dotenv import load_dotenv
import os
import json
from datetime import datetime




### Clean Parsed Raw Text ###
COMMON_TEXT_REPLACEMENTS = {
    "—": "-",
    "–": "-",
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "×": "x",
    "â€”": "-",
    "â€“": "-",
    "â€˜": "'",
    "â€™": "'",
    "â€œ": '"',
    "â€�": '"',
    "Ã—": "x",
    "Â": "",
}

def clean_text(text: str) -> str:
    """ 
    Clean and normalize text extracted from a PDF document. 
    The function replaces common encoding artifacts, 
    removes invisible Unicode formatting characters, 
    converts Unicode spaces into regular spaces, normalizes whitespace, 
    and removes excessive blank lines. 
    
    Args: text: Raw text extracted from a PDF document. 

    Returns: The cleaned and normalized text. """

    print("Cleaning Text ...")
    cleaned_text = text

    for old_value, new_value in COMMON_TEXT_REPLACEMENTS.items():
        cleaned_text = cleaned_text.replace(old_value, new_value)

    cleaned = []

    for char in cleaned_text:
        category = unicodedata.category(char)

        # Remove invisible formatting characters like zero-width spaces
        if category == "Cf":
            continue

        # Convert Unicode space characters to a normal space
        if category == "Zs":
            cleaned.append(" ")
        else:
            cleaned.append(char)

    cleaned_text = "".join(cleaned)

    # Collapse spaces/tabs
    cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text)

    # Strip whitespace from every line
    lines = [line.strip() for line in cleaned_text.splitlines()]

    # Rebuild first, THEN collapse excessive blank lines
    cleaned_text = "\n".join(lines)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)

    return cleaned_text.strip()

###





### Loading Environment Variables for LLM extraction ###
load_dotenv()
openai_api_key=os.getenv("OPENAI_API_KEY")
embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
openai_model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini")


def build_extraction_prompt_personal(resume_text: str) -> list[tuple[str, str]]:
    current_date = datetime.now()
    system_message = (
        "You extract structured personal information data from parsed resume text. Return only a "
        "valid JSON object. Do not include markdown, explanations, or extra "
        "text. If a field is missing, use null."
    )
    user_message = f"""
        Extract the following fields from the resume text:
        - name (usually the first line)
        - phoneNumber (just numbers)
        - email
        - latestCompany (if they have any separators like '|', only return what's before)
        - latestRole
        - isCurrent (Yes if the most recent job doesn't have an end date or end date is 'present', or explicitly stated on resume,
        otherwise No)

        - highestDegree (Only choose between: Associate's, Bachelor's, Master's, PhD, if not specified return null)
        - highestDegreeSchool 
        - highestDegreeGraduationDate (mm/yyyy)
        - highestDegreeMajor (array)
        - skills (array)

        

        Resume document text:
        {resume_text}
        """.strip()

    return [
        ("system", system_message),
        ("user", user_message),
    ]

def build_extraction_prompt_work(resume_text: str) -> list[tuple[str, str]]:
    current_date = datetime.now()
    system_message = (
        "You extract structured work information data from parsed resume text. Return only a "
        "valid nested JSON object containing each parsed work experience . Do not include markdown,"
        " explanations, or extra text. If a field is missing, use null."
        "example format: [{...}, {...}, {...}]"
    )
    user_message = f"""
        Extract the following fields for each work experience listed:
        - companyName (if they have any separators like '|', only return what's before)
        - title
        - employmentType (Intern / Full-time / Contract / Part-time)
        - start (mm/yyyy)
        - end ('Present' if stated, or mm/yyyy if it's past experience)
        - contents (array of corresponding resume bullets)

        Extract these into a json object for each role

        Resume document text:
        {resume_text}
        """.strip()

    return [
        ("system", system_message),
        ("user", user_message),
    ]

def build_extraction_prompt_edu(resume_text: str) -> list[tuple[str, str]]:
    current_date = datetime.now()
    system_message = (
        "You extract structured school information data from parsed resume text. Return only a "
        "valid nested JSON object containing each parsed education history. Do not include markdown,"
        "explanations, or extra text. If a field is missing, use null."
        "example format: [{...}, {...}, {...}]"
    )
    user_message = f"""
        Extract the following fields for each work experience listed:
        - schoolName (if they have any separators like '|', only return what's before)
        - degree (Only choose between: Associate's, Bachelor's, Master's, PhD, if not specified return null)
        - major
        - grade
        - graduationDate (mm/yyyy)

        Extract these into a json object for each role

        Resume document text:
        {resume_text}
        """.strip()

    return [
        ("system", system_message),
        ("user", user_message),
    ]

###





### Extract Structured Fields Based on 3 Prompt Categories: Personal, Work and Education
def extract_fields(
        resume_text: str,
        parsing_type: str
) -> dict | None:
    if not openai_api_key:
        print("OPENAI_API_KEY is not set. Skipping structured extraction." )
        return None
    
    from langchain_openai import ChatOpenAI

    print("Parsing Text ...")

    chat_model = ChatOpenAI(
        model = openai_model,
        api_key= openai_api_key,
        temperature=0
    )
    prompt = []
    if parsing_type == "personal":
        prompt = build_extraction_prompt_personal(resume_text)
    elif parsing_type == "work":
        prompt = build_extraction_prompt_work(resume_text)
    elif parsing_type == "education":
        prompt = build_extraction_prompt_edu(resume_text)
    else:
        print("Invalid parsing type provided, can only parse 'personal' or 'work' or 'education")
        return None


    response = chat_model.invoke(prompt)
    extracted_data = json.loads(response.content)

    return extracted_data

###








### Main Function Call: Combines All Steps ###
def extract_text_from_resume(pdf_path: Path) -> str:
    """ 
    Parse a PDF resume and extract structured candidate information. 
    The function reads every page of the supplied PDF using PyMuPDF, 
    combines the extracted page text, cleans the resulting text, 
    and performs separate LLM extraction passes for 
    personal information, work experience, and education history. 
    
    
    Args: pdf_path: Path to the PDF resume to process. 
    
    
    Returns: A dictionary containing three top-level fields: 
    ``personal``: Extracted personal and candidate-level information. 
    ``work``: A list of extracted work experiences. 
    ``education``: A list of extracted education entries. 
    """


    # supports multi-page resume
    text_by_page = []

    with pymupdf.open(pdf_path) as document:
        for page_number, page in enumerate(document, start = 1):
            page_text = page.get_text()
            text_by_page.append(f"\n {page_number} --- \n {page_text}")
    
    res = "\n".join(text_by_page).strip()
    cleaned_text = clean_text(res)
    output = {}
    output['personal'] = extract_fields(cleaned_text, 'personal')
    output['work'] = extract_fields(cleaned_text, 'work')
    output['education'] = extract_fields(cleaned_text, 'education')

    return output


if __name__ == "__main__":
    result = extract_text_from_resume("data/A5.pdf")
    #result = extract_text_from_resume("data/A5.pdf", "personal")
    print(result)

