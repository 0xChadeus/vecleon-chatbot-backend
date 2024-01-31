import json
from urllib import request
import urllib
import json
from openai import OpenAI
import boto3
import random
import time
import string

#This is the ComfyUI api prompt format.

#If you want it for a specific workflow you can "enable dev mode options"
#in the settings of the UI (gear beside the "Queue Size: ") this will enable
#a button on the UI to save workflows in api format.

#keep in mind ComfyUI is pre alpha software so this format will change a bit.

#this is the one for the default workflow

class ImageGenerator():

    workflow1 = json.load(open('workflow_api.json'))
    workflow = json.load(open('workflow_api1.json'))

    openai_client = OpenAI(
        api_key='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',
        base_url='http://127.0.0.1:5000/v1'
    )
    
    server_address = "127.0.0.1:8188"

    s3 = boto3.client('s3')
    s3_bucket_name = 'mychatbucket123'

    image_input_folder = '/home/saze/Software/ComfyUI/input/'
    image_output_folder =  '/home/saze/Software/ComfyUI/output/'

    def queue_prompt(self, workflow):
        p = {"prompt": workflow}
        data = json.dumps(p).encode('utf-8')
        req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
        return json.loads(urllib.request.urlopen(req).read())
    
    def get_image(self, filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen("http://{}/view?{}".format(self.server_address, url_values)) as response:
            return response.read()

    def get_history(self, prompt_id):
        with urllib.request.urlopen("http://{}/history/{}".format(self.server_address, prompt_id)) as response:
            return json.loads(response.read())

    def generate_image(self, positive_prompt='', negative_prompt=''):
        seed = int(str(random.random()).split('.')[-1])
        self.workflow["3"]["inputs"]["text"] = positive_prompt
        self.workflow["4"]["inputs"]["text"] = negative_prompt
        self.workflow["8"]["inputs"]["noise_seed"] = seed
        
        prompt_id = self.queue_prompt(self.workflow)['prompt_id']
        return self.get_images(prompt_id)


    def generate_self_image(self, img_url='', positive_prompt='', negative_prompt=''):
        filename = img_url.split('/')[-1]
        self.s3.download_file(self.s3_bucket_name, 'images/' + filename, self.image_input_folder + filename)
        
        seed = int(str(random.random()).split('.')[-1])
        self.workflow1["15"]["inputs"]["image"] = filename
        self.workflow1["3"]["inputs"]["text"] = positive_prompt
        self.workflow1["4"]["inputs"]["text"] = negative_prompt
        self.workflow1["8"]["inputs"]["noise_seed"] = seed

        prompt_id = self.queue_prompt(self.workflow1)['prompt_id']
        return self.get_images(prompt_id)
    

    def get_images(self, prompt_id):
        i = 0
        while True:
            try:
                history = self.get_history(prompt_id)[prompt_id]

                output_images = []
                for node_id in history['outputs']:
                    node_output = history['outputs'][node_id]
                    if 'images' in node_output:
                        for image in node_output['images']:
                            output_images.append(image['filename'])
                if len(output_images) > 0:
                    upload_key = 'generated/' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=64)) + '.png'
                    self.s3.upload_file(self.image_output_folder + output_images[0], self.s3_bucket_name, upload_key, ExtraArgs={'ContentType': 'image/png'})
                    return f'https://{self.s3_bucket_name}.s3.amazonaws.com/{upload_key}'
                else:
                    print('empty image output history')
                    return 'error'


            except Exception as e:
                print(e)
                i += 1
                time.sleep(1)
                if i > 15:
                    print('couldnt generate in 15 seconds')
                    return 'error'
        

    def get_b_generate_img(self, user_input):
        # get whether or not to write to the vector db
        f = open('generate_image_b_prompt.txt')
        prompt = f.read()
        f.close()

        completion = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt + user_input},
            ],
        )

        print(completion.choices[0].message.content)
        if 'yes' in completion.choices[0].message.content.lower():
            return (True, completion.choices[0].message.content.split('.')[-1])
        else:
            return (False, '')
        
    def get_b_generate_self_img(self, user_input):
        # get whether or not to write to the vector db
        f = open('generate_self_image_b_prompt.txt')
        prompt = f.read()
        f.close()
        

        completion = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt + user_input},
            ],
        )
        

        print(completion.choices[0].message.content)
        if 'yes' in completion.choices[0].message.content.lower():
            return (True, completion.choices[0].message.content.split('.')[-1])
        else:
            return (False, '')

