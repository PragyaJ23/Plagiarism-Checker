
from serpapi import GoogleSearch
import os
from dotenv import load_dotenv
load_dotenv()
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from docx import Document
import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from PyPDF2 import PdfReader
from flask import Flask,render_template,request
app=Flask(__name__)
def extract_text(filepath):

    if filepath.endswith(".txt"):

        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    elif filepath.endswith(".docx"):

        doc = Document(filepath)

        text = ""

        for para in doc.paragraphs:
            text += para.text + "\n"

        return text

    elif filepath.endswith(".pdf"):

        reader = PdfReader(filepath)

        text = ""

        for page in reader.pages:
            text += page.extract_text() + "\n"

        return text
    elif filepath.endswith(".csv"):

        with open(filepath, "r", encoding="utf-8") as f:
             return f.read()
    else:
        return "Unsupported file type"
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["document"]
    ALLOWED = {'txt', 'pdf', 'docx', 'csv'}
    ext = file.filename.split('.')[-1].lower()
    if ext not in ALLOWED:
        return "Invalid file type. Please upload txt, pdf, docx or csv.", 400

    filepath = "uploads/" + file.filename

    file.save(filepath)

    # Extract text from uploaded file
    content = extract_text(filepath)

    # Break file into sentences
    sentences = get_sentences(content)

    all_matches = []

    urls = []

    # Check first 3 sentences
    for sentence in sentences[:3]:

        sentence_urls = search_web(sentence)

        # Save first set of URLs for display
        if not urls:
            urls = sentence_urls

        # Visit each URL
        for url in sentence_urls:

            website_text = get_website_text(url)

            print("URL:", url)
            print("Website Length:", len(website_text))
            print("-" * 50)

            # Convert website text into sentences
            website_sentences = get_sentences(website_text)

            best_score = 0

            # Compare uploaded sentence with website sentences
            for website_sentence in website_sentences:

                current_score = calculate_similarity(
                    sentence,
                    website_sentence
                )

                if current_score > best_score:
                    best_score = current_score

            # Save match if similarity is high enough
            if best_score > 30:

                all_matches.append({
                    "sentence": sentence,
                    "url": url,
                    "score": best_score
                })

    # Sort highest score first
    all_matches.sort(
        key=lambda x: x["score"],
        reverse=True
    )
    total_sentences = len(sentences[:3])
    if all_matches and total_sentences > 0:
        avg_match_score = sum(m["score"] for m in all_matches) / len(all_matches)
        coverage = len(all_matches) / total_sentences
        score = round(avg_match_score * coverage, 2)
    else:
        score = 0

    print("Total Matches:", len(all_matches))
    print("Highest Score:", score)
    pdf_file = generate_pdf(
    file.filename,
    score,
    all_matches
)
    return render_template(
        "results.html",
        score=score,
        filename=file.filename,
        urls=urls,
        matches=all_matches,
        pdf_file=pdf_file
    )
    
def get_sentences(text):

    sentences = text.split(".")

    cleaned = []

    for sentence in sentences:

        sentence = sentence.strip()

        if len(sentence) > 20:
            cleaned.append(sentence)

    return cleaned
def search_web(sentence):

    api_key = os.getenv("SERPAPI_KEY")
    print("SERPAPI_KEY:", api_key)

    params = {
        "engine": "google",
        "q": sentence,
        "api_key": api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    print("SERPAPI RESULTS:", results)

    urls = []

    if "organic_results" in results:
        for result in results["organic_results"][:5]:
            if "link" in result:
                urls.append(result["link"])

    print("FOUND URLS:", urls)

    return urls
def calculate_similarity(text1, text2):

    documents = [
        text1,
        text2
    ]

    tfidf = TfidfVectorizer()

    matrix = tfidf.fit_transform(documents)

    similarity = cosine_similarity(
        matrix[0:1],
        matrix[1:2]
    )[0][0]

    return round(similarity * 100, 2)
def get_website_text(url):

    try:

        response = requests.get(url, timeout=5)

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        text = soup.get_text()

        print("URL:", url)
        print("Website text length:", len(text))

        return text

    except Exception as e:

        print("Error:", e)

        return ""
def get_website_text(url):

    try:

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        print("STATUS:", response.status_code)

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        text = soup.get_text()

        print("TEXT LENGTH:", len(text))

        return text

    except Exception as e:

        print("SCRAPE ERROR:", e)

        return ""
def generate_pdf(filename, score, matches):

    pdf_file = "static/report.pdf"

    doc = SimpleDocTemplate(pdf_file)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("Plagiarism Report", styles["Title"])
    )

    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(f"File Name: {filename}",
        styles["Normal"])
    )

    elements.append(
        Paragraph(f"Overall Similarity Score: {score}%",
        styles["Normal"])
    )

    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph("Matched Results",
        styles["Heading2"])
    )

    for match in matches:

        elements.append(
            Paragraph(
                f"Sentence: {match['sentence']}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"Score: {match['score']}%",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"Source: {match['url']}",
                styles["Normal"]
            )
        )

        elements.append(
            Spacer(1, 10)
        )
    
    doc.build(elements)

    return pdf_file
if __name__=="__main__":
    app.run(debug=True) 
