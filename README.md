📰 Fake News Detector

An interactive Streamlit web app that helps analyze the authenticity of news content using the Groq API and LLM-powered classification.

This project is built for educational purposes only and demonstrates how to integrate LLMs, APIs, and web scraping for news credibility analysis.

🚀 Features

🔤 Accepts raw text or news article URLs

📰 Extracts article content with the newspaper3k
 library

🤖 Uses Groq’s LLaMA 3 model for classification

✅ Classifies news as:

True

Fake

Unverifiable

📊 Displays confidence scores for both real and fake predictions

🎨 Simple, user-friendly Streamlit UI

📦 Installation

Clone the repository and install dependencies:

git clone https://github.com/your-username/fake-news-detector.git
cd fake-news-detector
pip install -r requirements.txt

🔑 API Key Setup

This app requires a Groq API key.

Get your API key from Groq
.

In your project folder, create a .streamlit/secrets.toml file:

GROQ_API_KEY = "your_api_key_here"

▶️ Run the App

Launch the Streamlit app locally:

streamlit run fake_news_app.py


Then open your browser at http://localhost:8501
.

📷 Screenshots

(Add screenshots of your app here once you run it locally)

Example layout:

Input section (text/URL)

Results with prediction and confidence levels

⚠️ Disclaimer

This tool is for educational and demonstration purposes only.
Do not rely on it for real-world fact-checking or decision-making.

🛠️ Tech Stack

Streamlit
 – UI framework

Newspaper3k
 – Article extraction

Groq API
 – LLM-based classification

Python Requests
 – API calls

🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to improve.
