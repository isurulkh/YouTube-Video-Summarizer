import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Define the prompt
prompt = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 1500 words. Please provide the summary of the text given here:  """

## getting the transcript data from yt videos
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]
        return transcript
    except Exception as e:
        raise e

## getting the summary based on Prompt from Google Gemini Pro
def generate_gemini_content(transcript_text, prompt, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

st.title("YouTube Video Summarizer")

# Display the link to get the Google API key
st.markdown(
    "If you don't have a Google API Key, you can get one [here](https://makersuite.google.com/app/apikey).",
    unsafe_allow_html=True
)

# Get the API key from user input
google_api_key = st.text_input("Enter your Google API Key:", type="password")

if google_api_key:
    youtube_link = st.text_input("Enter YouTube Video Link:")

    if youtube_link:
        video_id = youtube_link.split("=")[1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
        
    if st.button("Get Detailed Notes"):
        # Call function to extract transcript
        try:
            transcript_text = extract_transcript_details(youtube_link)
            if transcript_text:
                st.success("Transcript extracted successfully!")
                # Generate detailed notes
                summary = generate_gemini_content(transcript_text, prompt, google_api_key)
                st.markdown("## Detailed Notes:")
                st.write(summary)
            else:
                st.error("Failed to extract transcript.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
