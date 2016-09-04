"""
The script is used to parse PDF and DOCX files predominantly resumes and extract all the relevant information from it.
The extracted information is stored on to a Django model, this can be replaced to suite your needs.
"""
__author__ = "ssharad"
__license__ = "GPL v.3.0"
# -*- coding: utf-8 -*-
import pyPdf
import docx
import string

#Extract text from PDF
def getPDFContent(path):
    content = ""
    # Load PDF into pyPDF
    pdf = pyPdf.PdfFileReader(file(path, "rb"))
    # Iterate pages
    for i in range(0, pdf.getNumPages()):
        # Extract text from page and add to content
        content += pdf.getPage(i).extractText() + "\n"
    # Collapse whitespace
    content = " ".join(content.replace(u"\xa0", " ").strip().split())
    return content

#Extract text from DOCX
def getText(filename):
    doc = docx.Document(filename)
    fullText = ""
    for para in doc.paragraphs:
        fullText += para.text
    return fullText

#To store extracted resumes
resume = ""
#Select a path to the file - code needs os.path #to be addded
filename = raw_input("Enter file name / path : ")
#Invoking document parsers based on file format
#Note: for TXT - do a normal f.read()
if filename.endswith(".pdf"):
    resume = getPDFContent(filename).encode("ascii", "ignore") 
elif filename.endswith(".docx"):
     resume = getText(filename).encode("ascii", "ignore")  
else:
    print "File format is currently not supported"
    exit(0)

print "processing..... \nplease wait...."
#Importing NLTK for stopword removal and tokenizing
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

#Tokenizing/ Filtering the resume off stopwords and punctuations 
print "tokenizing the given file ......"
tokens = word_tokenize(resume)
punctuations = ['(',')',';',':','[',']',',']
stop_words = stopwords.words('english')
#storing the cleaned resume
filtered = [w for w in tokens if not w in stop_words and  not w in string.punctuation]
print "removing the stop words....\nCleaning the resumes....\nExtracting Text ......."
print filtered
#get the name from the resume
name  = str(filtered[0])+' ' +str(filtered[1])
print "Name : " + name

#using regular expressions we extract phone numbers and mail ids
import re
#get contact info - from resume
#email
email = ""
match_mail = re.search(r'[\w\.-]+@[\w\.-]+', resume)
#handling the cases when mobile number is not given
if(match_mail != None):
    email = match_mail.group(0)
print "Email : " + email

#mobile number
mobile = ""
match_mobile = re.search(r'((?:\(?\+91\)?)?\d{9})',resume)
#handling the cases when mobile number is not given
if(match_mobile != None):
    mobile = match_mobile.group(0)
print "Mobile : " +  mobile

parsed_resume = ' '.join(filtered)
print "Parsed Resume in plain Text : ", parsed_resume
r = str(parsed_resume)

#shingles - for eeach parsed resume
shingle = []
# form n-grams - basically the singles for LSH
from nltk.util import ngrams
#form the shingles of the filtered resume - the length of each shingle is 10
make_shingle = ngrams(filtered,10)
#print the shingles
for s in make_shingle:
    shingle.append(s)  

print "Shingles for the resume : ",shingle
#save the name and contact details in separate fields - the parsed resume in anohter field
# the parsed information is stored in a database (Django Model)
import django
#configure the Django envronment to the location of your app
import os
import sys
sys.path.append('/home/sharad/resumes/')
os.environ['DJANGO_SETTINGS_MODULE']='resumes.settings'
django.setup()
#os.environ.setdefault(“DJANGO_SETTINGS_MODULE”, “resumes.settings”)
from django.conf import settings
#Edit the django model
from view_db.models import parsed_resume
#add the new entries to the table
r = parsed_resume(name = name,email = email, mobile = mobile, parsed_resume = r, shingles = shingle)
#commit the changes
r.save()
