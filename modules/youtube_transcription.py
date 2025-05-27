import re
import html
from youtube_transcript_api import YouTubeTranscriptApi
import googleapiclient.discovery
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def extract_video_id(youtube_url):
    """
    Extract YouTube video ID from URL
    """
    # Regular expressions to match YouTube URL patterns
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?]+)',
        r'(?:youtube\.com\/embed\/)([^&\n?]+)',
        r'(?:youtube\.com\/v\/)([^&\n?]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    return None

def get_youtube_transcript(youtube_url, api_key=None):
    """
    Get transcript from YouTube video using youtube-transcript-api
    """
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return "Error: Invalid YouTube URL format", None, "Could not extract video ID from URL"
    
    try:
        # Get video title first if API key is provided
        video_title = "YouTube video"
        if api_key:
            try:
                youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=api_key)
                video_response = youtube.videos().list(part='snippet', id=video_id).execute()
                if video_response.get('items'):
                    video_title = video_response['items'][0]['snippet']['title']
            except Exception as e:
                print(f"Error getting video title: {str(e)}")
        
        # Try to get transcripts directly
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'id'])
            
            # If we get here, we have transcript data
            full_transcript = ""
            for entry in transcript_data:
                if isinstance(entry, dict) and 'text' in entry:
                    full_transcript += entry['text'] + " "
            
            # Clean up the transcript
            full_transcript = re.sub(r'\n', ' ', full_transcript)
            full_transcript = html.unescape(full_transcript)
            
            return full_transcript.strip(), 100, f"Transcript extracted from: {video_title}"
            
        except Exception as inner_e:
            print(f"Direct transcript fetch error: {str(inner_e)}")
            # Continue to the alternative approach below
        
        # If direct approach failed, try with listing transcripts first
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Find available languages and try them
        available_transcripts = list(transcript_list)
        if not available_transcripts:
            return "Error: No transcripts available for this video", None, "This YouTube video does not have captions/subtitles"
        
        # Try to get transcript in any available language
        transcript = available_transcripts[0]  # Just use the first available transcript
        
        # Get the transcript data
        transcript_data = transcript.fetch()
        
        # Process transcript data
        if not transcript_data:
            return "Error: Empty transcript data", None, "The transcript exists but contains no data"
        
        # Combine all text entries
        full_transcript = ""
        for entry in transcript_data:
            if isinstance(entry, dict) and 'text' in entry:
                full_transcript += entry['text'] + " "
        
        # Clean up the transcript
        full_transcript = re.sub(r'\n', ' ', full_transcript)
        full_transcript = html.unescape(full_transcript)
        
        return full_transcript.strip(), 100, f"Transcript extracted from: {video_title}"
        
    except Exception as e:
        error_msg = str(e)
        print(f"YouTube transcript error: {error_msg}")
        
        # Provide more specific error messages based on common issues
        if "no element found" in error_msg:
            return "Error: Could not parse transcript data", None, "The video may have malformed captions or none at all"
        elif "Transcript unavailable" in error_msg:
            return "Error: Transcript unavailable", None, "This video does not have captions/subtitles available"
        else:
            return f"Error: {error_msg}", None, "An error occurred while fetching the YouTube transcript" 