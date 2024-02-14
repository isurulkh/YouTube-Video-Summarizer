import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# Set Streamlit page configuration
st.set_page_config(page_title="YouTube Video Summarizer", layout="wide")

# Sidebar for user inputs
google_api_key = st.sidebar.text_input("Enter your Google API Key:", type="password")
youtube_link = st.sidebar.text_input("Enter YouTube Video Link:")

# Summary length customization
summary_length = st.sidebar.select_slider(
    "Select Summary Length:", options=['Short', 'Medium', 'Long'], value='Medium'
)

# Define functions
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(segment["text"] for segment in transcript)
    except Exception as e:
        st.sidebar.error(f"An error occurred: {e}")
        return None

def generate_gemini_content(transcript_text, prompt, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

def create_pdf(summary_text):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(72, 800, "Summary")
    text = c.beginText(40, 780)
    text.setFont("Helvetica", 12)
    for line in summary_text.split('\n'):
        text.textLine(line)
    c.drawText(text)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# UI elements
st.title("YouTube Video Summarizer")

# Display video thumbnail
if youtube_link:
    video_id = youtube_link.split("=")[1]
    video_thumbnail = f"http://img.youtube.com/vi/{video_id}/0.jpg"
    st.image(video_thumbnail, caption="Video Thumbnail", use_column_width=True)

# Process and display summary
if google_api_key and youtube_link and st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)
    if transcript_text:
        prompt = """You are a YouTube video summarizer. Summarize the video content into key points within 1500 words."""
        customized_prompt = f"{prompt} Please generate a {summary_length.lower()} summary."
        summary = generate_gemini_content(transcript_text, customized_prompt, google_api_key)
        if summary:
            st.success("Transcript extracted and summary generated successfully!")
            st.subheader("Detailed Notes:")
            st.write(summary)
            # PDF download
            pdf_bytes = create_pdf(summary)
            st.download_button(label="Download Summary as PDF",
                               data=pdf_bytes,
                               file_name="YouTube_Summary.pdf",
                               mime="application/pdf")
        else:
            st.error("Failed to generate summary.")
    else:
        st.error("Failed to extract transcript.")
