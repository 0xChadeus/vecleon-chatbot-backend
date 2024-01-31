from openai import OpenAI

client = OpenAI(
    api_key='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',
)


def get_imagedesc(image_url):
    client.models.list()

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What’s in this image?"},
                    {
                        "type": "image_url",
                        "image_url": image_url,
                    },
                ],
            }
        ],
        max_tokens=300,
    )

    print(response.choices[0])
    return response.choices[0]
