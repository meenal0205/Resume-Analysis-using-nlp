from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import io
import nltk
from spacy.matcher import Matcher
import re
import spacy
from nltk.corpus import stopwords
from spacy.matcher import Matcher
import pandas as pd
import requests
import spacy


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            
            resource_manager = PDFResourceManager()
            
           
            fake_file_handle = io.StringIO()
            
            
            converter = TextConverter(
                                resource_manager, 
                                fake_file_handle, 
                                codec='utf-8', 
                                laparams=LAParams()
                        )

            
            page_interpreter = PDFPageInterpreter(
                                resource_manager, 
                                converter
                            )

            
            page_interpreter.process_page(page)
            
            
            text = fake_file_handle.getvalue()
            yield text

          
            converter.close()
            fake_file_handle.close()

nlp = spacy.load('en_core_web_sm')

matcher = Matcher(nlp.vocab)

def extract_mobile_number(text):
    phone = re.findall(re.compile(r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'), text)
    
    if phone:
        number = ''.join(phone[0])
        if len(number) > 10:
            return '+' + number
        else:
            return number

def extract_email(email):
    email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", email)
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return None

nlp = spacy.load('en_core_web_sm')

def extract_skills(resume_text):
    nlp_text = nlp(resume_text)

    
    tokens = [token.text for token in nlp_text if not token.is_stop]
    
   
    data = pd.read_csv("skills.csv") 
    
    skills = list(data.columns.values)
    
    skillset = []
    
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)
    
    for token in nlp_text.noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    
    return [i.capitalize() for i in set([i.lower() for i in skillset])]

STOPWORDS = set(stopwords.words('english'))

EDUCATION = [
            'BE','B.E.', 'B.E', 'BS', 'B.S', 
            'ME', 'M.E', 'M.E.', 'MS', 'M.S', 
            'BTECH', 'B.TECH', 'M.TECH', 'MTECH', 
            'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII'
        ]

def extract_education(resume_text):
    nlp_text = nlp(resume_text)

    
    nlp_text = [sent.string.strip() for sent in nlp_text.sents]

    edu = {}
    
    for index, text in enumerate(nlp_text):
        for tex in text.split():
            
            tex = re.sub(r'[?|$|.|!|,]', r'', tex)
            if tex.upper() in EDUCATION and tex not in STOPWORDS:
                edu[tex] = text + nlp_text[index + 1]

    
    education = []
    for key in edu.keys():
        year = re.search(re.compile(r'(((20|19)(\d{2})))'), edu[key])
        if year:
            education.append((key, ''.join(year[0])))
        else:
            education.append(key)
    return education

text=''
for page in extract_text_from_pdf("C:/EDI SEM1/Affan_Shaikh_Resume.pdf"):
    text += ' ' + page
# print(text)

# print(extract_mobile_number(text))
# print(extract_email(text))
# print(extract_skills(text))
# print(extract_education(text))