import time
import speech_recognition as sr
import os
import openai
import pygame

# Function to play text as speech using OpenAI TTS
def play_text_as_speech(text, language='en'):
    response = openai.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text,
    )
    temp_speech_path = "temp_speech.mp3"
    response.stream_to_file(temp_speech_path)
    
    pygame.mixer.init()
    pygame.mixer.music.load(temp_speech_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.music.unload()
    os.remove(temp_speech_path)

# Function to transcribe audio using Whisper API
def transcribe_audio(audio_data, language='en'):
    temp_wav_path = "temp_audio.wav"
    with open(temp_wav_path, "wb") as f:
        f.write(audio_data.get_wav_data())
    
    with open(temp_wav_path, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language
        )
    
    os.remove(temp_wav_path)
    return transcript.text

# Function to listen for the wake word
def listen_for_wake_word(wake_word="hello", language='en'):
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print(f"Say '{wake_word}' to start")
        audio = recognizer.listen(source)
        try:
            transcription = transcribe_audio(audio, language).lower()
            if wake_word in transcription:
                pygame.mixer.init()
                pygame.mixer.music.load('C:\\Users\\ufo11\\jarvis\\in.wav')
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                pygame.mixer.music.unload()
                return True
        except Exception as e:
            print(f"Error in wake word recognition: {e}")
    return False

# Function to transcribe audio, send to ChatGPT, and read aloud
def listen_and_respond(after_prompt=True, language='en'):
    start_listening = not after_prompt
    with sr.Microphone() as source:
        if after_prompt:
            recognizer.adjust_for_ambient_noise(source)
            print("Say 'Hello' to start" if language == 'en' else "'안녕하세요'라고 말하세요")
            audio = recognizer.listen(source)
            try:
                transcription = transcribe_audio(audio, language)
                if (language == 'en' and transcription.lower() == "hello") or \
                   (language == 'ko' and transcription == "안녕하세요"):
                    start_listening = True
            except Exception as e:
                print(f"Error in initial transcription: {e}")
                start_listening = False
        
        if start_listening:
            try:
                recognizer.adjust_for_ambient_noise(source)
                print("Listening for question..." if language == 'en' else "질문을 듣고 있습니다...")
                audio = recognizer.listen(source)

                pygame.mixer.music.load('C:\\Users\\ufo11\\jarvis\\in.wav')
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                pygame.mixer.music.unload()

                print("Processing speech...")
                transcription = transcribe_audio(audio, language)
                print(f"Input text: {transcription}")
                if transcription == "" or transcription == "you" or transcription == ". . .": return
                conversation_history.append({"role": "user", "content": transcription})

                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=conversation_history,
                )
                response_text = response.choices[0].message.content.strip()
                print(f"Response text: {response_text}")                
                conversation_history.append({"role": "assistant", "content": response_text})
                play_text_as_speech(response_text, language)
            
            except Exception as e:
                print(f"Error in transcription or processing: {e}")

# OpenAI API 설정
openai.api_key = os.environ["OPENAI_API_KEY"]

recognizer = sr.Recognizer()

conversation_history = [
    {"role": "system", "content": "You are an English Assistant. If someone uses awkward English expressions, you correct them to sound natural."}
]

first_question = True
last_question_time = time.time()
threshold = 60 # 1 minute
language = 'en'

while True:
    if first_question or (time.time() - last_question_time > threshold):
        if listen_for_wake_word(wake_word="hello", language=language):
            listen_and_respond(after_prompt=False, language=language)
            first_question = False
    else:
        listen_and_respond(after_prompt=False, language=language)
    
    last_question_time = time.time()