# DALL-E 3 requires version 1.0.0 or later of the openai-python library.
import os
from openai import AzureOpenAI
import json
import requests
import sys


sys_prompt = sys.argv[3]
prompt = json.load(open(sys.argv[1], "r"))["choices"][0]["message"]["content"]

if not prompt.endswith("."):
    prompt += "."


prompt += f" {sys_prompt}"

print("Prompt:", prompt)

output_images = sys.argv[2]

# You will need to set these environment variables or edit the following values.
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("OPENAI_API_VERSION", "2024-04-01-preview")
deployment = os.getenv("DEPLOYMENT_NAME", "dall-e-3")
api_key = os.getenv("AZURE_OPENAI_API_KEY")

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=api_key,
)

result = client.images.generate(
    model=deployment,
    prompt=prompt,
    n=1,
    style="vivid",
    quality="standard",
)

image_url = json.loads(result.model_dump_json())['data'][0]['url']
print(image_url)

response = requests.get(image_url)

generated_image = response.content

with open(f"{output_images}/main.png", "wb") as file:
    file.write(generated_image)



# variation_response = client.images.create_variation(
#     image=generated_image,  # generated_image is the image generated above
#     n=10,
#     size="1024x1024",
#     response_format="url",
# )

# # print response
# print(variation_response)

# variation_urls = [datum.url for datum in variation_response.data]  # extract URLs
# variation_images = [requests.get(url).content for url in variation_urls]

# for i, image in enumerate(variation_images):
#     with open(f"{output_images}/variation_{i}.png", "wb") as file:
#         file.write(image)

