from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import os
import re

@api_view(['POST'])
def summarize_video(request):
    # Get the video URL from the request data
    video_url = request.data.get('videoUrl')

    # Check if the URL is provided
    if not video_url:
        return Response({'error': 'No video URL provided'}, status=status.HTTP_400_BAD_REQUEST)

    # Use a regular expression to extract the video ID
    match = re.search(r'(?<=v=)[^&]+', video_url)
    if not match:
        return Response({'error': 'Invalid YouTube URL'}, status=status.HTTP_400_BAD_REQUEST)
    video_id = match.group(0)

    try:
        # 1. Get the video transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ' '.join([d['text'] for d in transcript_list])

        # 2. Set up the OpenAI API key securely
        # This uses the Django Environ library
        openai.api_key = os.environ.get("OPENAI_API_KEY")

        if not openai.api_key:
            return Response({'error': 'OpenAI API key not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 3. Call the OpenAI API for summarization
        # Check the transcript length to avoid exceeding token limits
        if len(transcript_text) > 10000: # Adjust this limit as needed
             transcript_text = transcript_text[:10000] # Truncate if too long

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                {"role": "user", "content": f"Summarize the following YouTube video transcript in a concise paragraph:\n\n{transcript_text}"}
            ]
        )
        summary = response.choices[0].message.content

        # 4. Return the summary to the frontend
        return Response({'summary': summary}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)