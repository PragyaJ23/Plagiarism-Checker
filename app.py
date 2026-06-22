from serpapi import GoogleSearch
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

    # Overall score
    if all_matches:
        total = 0
        for match in all_matches:
            total += match["score"]

        score = round(
            total / len(all_matches),
            2
        )

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

    params = {
        "engine": "google",
        "q": sentence,
        "api_key": "822ca8568afc48bfd8f53f88727e9b6c5a9f22752542fe004ffe2e7d6aa0587b"
    }

    search = GoogleSearch(params)

    results = search.get_dict()

    urls = []

    if "organic_results" in results:

        for result in results["organic_results"][:5]:

            if "link" in result:
                urls.append(result["link"])

    return urls
def find_matching_sentences(sentences, website_text):

    matches = []

    website_sentences = get_sentences(website_text)

    for sentence in sentences:

        best_score = 0
        best_url=""
        
        for website_sentence in website_sentences:

            score = calculate_similarity(
                sentence,
                website_sentence
            )

            if score > best_score:

                best_score = score

        if best_score > 50:

            matches.append({
                "sentence": sentence,
                "score": best_score
            })
            


    return matches
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
print(search_web("Python programming language"))
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