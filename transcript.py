from youtube_transcript_api import YouTubeTranscriptApi
import re

def extract_video_id(url):
    """
    Extracts video ID from YouTube URL.
    
    Args:
    - url (str): The YouTube video URL
    
    Returns:
    - str: The extracted video ID, or None if not found
    """
    # Regex pattern to match YouTube video ID
    pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    
    # Attempt to find the video ID in the URL
    match = re.search(pattern, url)
    
    if match:
        return match.group(1)  # Return the video ID part of the URL
    else:
        return None  # Return None if no match found

# Example usage:

