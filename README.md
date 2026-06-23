# 📄 Plagiarism Checker

A web-based plagiarism detection tool built with Python and Flask, deployed on Render. Upload a document and get an instant similarity score to detect potential plagiarism.

🔗 **Live Demo:** [plagiarism-checker-b8kx.onrender.com](https://plagiarism-checker-b8kx.onrender.com/)

---

## ✨ Features

- Upload documents and check for plagiarism instantly
- Similarity score calculation
- Clean, minimal web interface
- Secure API key handling via environment variables

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS (Jinja2 templates) |
| Deployment | Render |
| Environment | python-dotenv |

---

## 📁 Project Structure

```
Plagiarism-Checker/
├── static/          # CSS and JS assets
├── templates/       # HTML templates (Jinja2)
├── uploads/         # Temporarily stores uploaded files
├── app.py           # Main Flask application
├── requirements.txt # Python dependencies
├── Procfile         # Render deployment config
└── .gitignore       # Excludes .env and uploads
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/PragyaJ23/Plagiarism-Checker.git
   cd Plagiarism-Checker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   Create a `.env` file in the root directory:
   ```
   API_KEY=your_api_key_here
   ```

4. **Run the app**
   ```bash
   python app.py
   ```

5. Open your browser and go to `http://localhost:5000`

---

## 🌐 Deployment

This project is deployed on **Render** using the `Procfile`:

```
web: gunicorn app:app
```

To deploy your own instance:
1. Push the repo to GitHub
2. Connect it to [Render](https://render.com)
3. Add your environment variables in the Render dashboard
4. Deploy!

---

## 🔒 Security

- API keys are stored in `.env` and never committed to version control
- The `.gitignore` excludes `.env` and the `uploads/` folder

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📌 Future Improvements

- [ ] PDF and DOCX file support
- [ ] Sentence-level highlighting of matched content
- [ ] Detailed similarity report with matched sources
- [ ] Upload history and result storage
- [ ] User authentication

---

## 👩‍💻 Author

**PragyaJ23** — [GitHub Profile](https://github.com/PragyaJ23)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
