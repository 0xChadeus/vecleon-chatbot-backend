from openai import OpenAI

client = OpenAI(
    api_key='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',
)
def speech_to_text(audiofile_path):
    audio_file= open(audiofile_path, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    return transcript

