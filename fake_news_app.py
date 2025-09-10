import streamlit as st
import json
import requests
from newspaper import Article
import time

# --- API and Configuration for Groq ---

# Retrieve the Groq API key from Streamlit secrets
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("GROQ_API_KEY not found in secrets.toml. Please add it to your secrets file.")
    st.stop()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# The headers required for the Groq API request.
HEADERS = {
    'Authorization': f"Bearer {GROQ_API_KEY}",
    'Content-Type': 'application/json'
}

# --- Text Classification Function using Groq API ---

def classify_text_with_api(text):
    """
    Sends text to the Groq API for classification as "True", "Fake", or "Unverifiable".
    The API returns a JSON object with the prediction and confidence scores.
    """
    prompt = f"""
    You are an expert fact-checker. Analyze the following text and classify it as "True", "Fake", or "Unverifiable".
    Provide a prediction and two confidence scores (from 0.0 to 1.0) for "real" and "fake" news.
    
    Text to analyze: "{text}"

    Please respond with a JSON object in the following format. Ensure the response is only the JSON object, with no extra text or markdown formatting.
    {{
      "prediction": "True" | "Fake" | "Unverifiable",
      "real_confidence": number,
      "fake_confidence": number
    }}

    If you cannot confidently classify the text (e.g., it's not a news statement, is too short, or is an opinion), classify it as "Unverifiable".
    """
    
    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "model": "llama3-8b-8192",  # A fast and powerful model available on Groq
        "temperature": 0.1,  # Lower temperature for more consistent, factual responses
        "response_format": {"type": "json_object"}
    }
    
    retries = 3
    for i in range(retries):
        try:
            response = requests.post(GROQ_API_URL, headers=HEADERS, json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes
            result = response.json()
            
            # The API returns a choice object with the content
            if result and "choices" in result and result["choices"]:
                response_content = result["choices"][0]["message"]["content"]
                return json.loads(response_content)
            else:
                st.error("API response was empty or malformed.")
                return {"prediction": "Error", "real_confidence": 0.0, "fake_confidence": 0.0}
        
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 429: # Too Many Requests
                st.warning(f"Rate limit exceeded. Retrying in {2**(i+1)} seconds...")
                time.sleep(2**(i+1))
            else:
                st.error(f"HTTP error occurred: {err}")
                break
        except Exception as e:
            st.error(f"Error calling the Groq API: {e}")
            break
            
    return {"prediction": "Error", "real_confidence": 0.0, "fake_confidence": 0.0}

# --- URL Text Extraction ---

def extract_text_from_url(url):
    """
    Downloads and parses an article from a given URL, returning the main text.
    Uses the `newspaper` library for robust web scraping of news articles.
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text[:2000]
    except Exception as e:
        return f"Error fetching URL: {str(e)}"

# --- Streamlit App UI ---

st.set_page_config(page_title="Fake News Detector", layout="wide")

st.title("🗞️ Fake News Detector")
st.header("Educational Purpose Only")
st.write("Enter text or a URL to analyze its authenticity.")

# Create two columns for the side-by-side layout
col1, col2 = st.columns(2)

with col1:
    input_type = st.radio(
        "Select your input type:",
        ("Text", "URL"),
        help="Choose whether to analyze raw text or an online article via its URL."
    )

    if input_type == "Text":
        user_input = st.text_area(
            "Enter the text to analyze:",
            height=250,
            placeholder="Paste your news text here..."
        )
        url_to_display = None
    else:
        user_input = st.text_input(
            "Enter the URL to analyze:",
            placeholder="e.g., https://www.nytimes.com/..."
        )
        url_to_display = user_input

    analyze_button = st.button("Analyze", type="primary")

with col2:
    if analyze_button:
        if not user_input or not user_input.strip():
            st.warning("⚠️ Please provide text or a URL to analyze.")
        else:
            with st.spinner("🔍 Analyzing Please wait."):
                if input_type == "URL":
                    text_to_classify = extract_text_from_url(user_input)
                    if "Error" in text_to_classify:
                        st.error(text_to_classify)
                        st.stop()
                else:
                    text_to_classify = user_input

                api_result = classify_text_with_api(text_to_classify)
                
                if api_result["prediction"] == "Error":
                    st.error("Could not get a valid response from the API.")
                else:
                    prediction = api_result.get("prediction", "N/A")
                    real_prob = api_result.get("real_confidence", 0.0)
                    fake_prob = api_result.get("fake_confidence", 0.0)

                    st.success("✅ Analysis complete!")
                    st.markdown("---")

                    if url_to_display:
                        st.markdown(f"**URL Analyzed:** [{url_to_display}]({url_to_display})")
                    
                    st.write(f"**Prediction:** {prediction}")

                    if prediction == "True":
                        st.markdown("This content is likely to be **REAL NEWS**.")
                    elif prediction == "Fake":
                        st.markdown("This content is likely to be **FAKE NEWS**.")
                    elif prediction == "Unverifiable":
                        st.markdown("Unable to make a definitive prediction.")
                    
                    if real_prob is not None and fake_prob is not None:
                        st.markdown("---")
                        st.markdown("### Confidence Levels")
                        st.progress(real_prob, text=f"Real News Confidence: {real_prob:.2%}")
                        st.progress(fake_prob, text=f"Fake News Confidence: {fake_prob:.2%}")
