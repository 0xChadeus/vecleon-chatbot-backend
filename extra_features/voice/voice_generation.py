from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav
import boto3
import random
import string


class AudioGenerator():
    s3 = boto3.client('s3')
    s3_bucket_name = 'mychatbucket123'

    def generate(self, text):
        # download and load all models
        preload_models()

        # generate audio from text
        audio_array = generate_audio(text)

        # save audio to disk
        filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=64)) + '.mpeg'
        
        local_file = '/home/saze/Documents/projects/Galatea/chatbot/generated_audio/' + filename
        
        upload_key = 'audio/' + filename
        write_wav(local_file, SAMPLE_RATE, audio_array)
        self.s3.upload_file(local_file, self.s3_bucket_name, upload_key, ExtraArgs={'ContentType': 'audio/mpeg'})
        return f'https://{self.s3_bucket_name}.s3.amazonaws.com/{upload_key}'



