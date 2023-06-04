from rest_framework.views import APIView
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Video
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import speech_recognition as sr
import openai


# Create your views here.
class VideoToText(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        start_time = request.data["StartTime"]
        end_time = request.data["EndTime"]

        # Retrieve the Video object
        video = get_object_or_404(Video, title="test")

        # Perform audio extraction and speech-to-text conversion
        audio_file = "temp_audio.wav"

        # Load video
        clip = VideoFileClip(video.video_file.path)

        # Select the subclip between 'start_time' and 'end_time' (in seconds)
        subclip = clip.subclip(start_time, end_time)

        # Write the result to a file (convert it to mono to ensure compatibility with pydub)
        subclip.audio.write_audiofile(audio_file, codec='pcm_s16le', fps=44100)

        # Load wav file using pydub
        audio = AudioSegment.from_wav(audio_file)

        # Perform speech-to-text conversion
        text = self.speech_to_text(audio_file)
        openai.api_key = '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'  # Replace with your actual OpenAI API key

        prompt = "what is this about:\n\n" + "Big O Expression"
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        if response.choices and len(response.choices) > 0:
            analysis = response.choices[0].text.strip()
            text = analysis
            print("analysis is: " + analysis)
        

        # Remove the temporary audio file
        # You can uncomment the following line if you want to delete the temporary audio file
        # os.remove(audio_file)

        return Response({"text": text})

    def speech_to_text(self, audio_file):
        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data)
            return text