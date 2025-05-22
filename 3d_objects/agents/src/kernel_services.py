from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents import ChatMessageContent, TextContent, ImageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
import base64
import os
import time
from semantic_kernel import Kernel

from services import Service
from service_settings import ServiceSettings
from image_gen_text_to_image import ImageGenTextToImage
import requests
from openai import AsyncAzureOpenAI

kernel = Kernel()

service_settings = ServiceSettings()

# Select a service to use for this notebook (available services: OpenAI, AzureOpenAI, HuggingFace)
selectedService = (
    Service.AzureOpenAI
    if service_settings.global_llm_service is None
    else Service(service_settings.global_llm_service.lower())
)
print(f"Using service type: {selectedService}")

print("endpoint: ", os.getenv("AZURE_IMAGE_GEN_ENDPOINT"))

image_client = AsyncAzureOpenAI(
    azure_endpoint=os.getenv("AZURE_IMAGE_GEN_ENDPOINT"),
    api_key=os.getenv("AZURE_IMAGE_GEN_API_KEY"),
    api_version=os.getenv("AZURE_IMAGE_GEN_API_VERSION"),
)   

# Remove all services so that this cell can be re-run without restarting the kernel
kernel.remove_all_services()

service_id = None
if selectedService == Service.OpenAI:
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

    service_id = "default"
    kernel.add_service(
        OpenAIChatCompletion(
            service_id=service_id,
        ),
    )
elif selectedService == Service.AzureOpenAI:
    from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

    service_id = "default"
    kernel.add_service(
        AzureChatCompletion(
            service_id=service_id,
        ),
    )

    from semantic_kernel.connectors.ai.open_ai import OpenAITextToImage 

    image_gen_service = ImageGenTextToImage (
        async_client=image_client,
        ai_model_id="gpt-image-1",
        service_id="gpt-image-1", # Optional; for targeting specific services within Semantic Kernel
    )
    kernel.add_service(image_gen_service)

image_gen_service = kernel.get_service(service_id="gpt-image-1")
text_gen_service = kernel.get_service(service_id="default")

chat_history = ChatHistory()

# Function to convert a file to Base64
def file_to_base64(file_path):
    with open(file_path, "rb") as file:
        # Read the file in binary mode and encode it to Base64
        base64_encoded = base64.b64encode(file.read()).decode("utf-8")
    return base64_encoded

async def generate_image(prompt, image_path):
    chat_history.add_message(ChatMessageContent(
        role=AuthorRole.USER,
        items=[TextContent(text=prompt)]
    ))

    image = await image_gen_service.generate_image(
        description=prompt, width=1024, height=1024, quality="auto"
    )

    image_data = base64.b64decode(image)

    with open(image_path, "wb") as image_file:
        image_file.write(image_data)

    base64_string = file_to_base64(image_path)

    chat_history.add_message(ChatMessageContent(
        role=AuthorRole.USER,
        items=[
                TextContent(text=prompt), 
                ImageContent(uri=f"data:image/png;base64,{base64_string}")
        ]
    ))

    return image

async def get_chat_message_content(prompt):

    seed = int(time.time())
    print(f"Seed: {seed}")
    execution_settings = OpenAIChatPromptExecutionSettings(seed=seed)

    #chat_history = ChatHistory()

    chat_history.add_message(ChatMessageContent(
        role=AuthorRole.USER,
        items=[TextContent(text=prompt)]
    ))

    return await text_gen_service.get_chat_message_content(
        chat_history=chat_history,
        settings=execution_settings,
    )

async def evaluate_image(image_paths, prompt):

    if not isinstance(image_paths, list):
        image_paths = [image_paths]


    execution_settings = OpenAIChatPromptExecutionSettings()

    text_gen_service = kernel.get_service(service_id="default")

    
  

    # prompt = """Evaluate the following image from the point of view of marketability and ease of 3D printing.  
    #                                 Make a one-sentense improvement suggestion.
    #                                 Only respond with the suggestion.  Do not explain the reasons for the suggestion.
    #                                 """

    items = [TextContent(text=prompt)]

    for image_path in image_paths:
        base64_string = file_to_base64(image_path)
        items.append(ImageContent(uri=f"data:image/png;base64,{base64_string}"))

    chat_history.add_message(ChatMessageContent(
            role=AuthorRole.USER,
            items=items
        ))

    # Get the chat completion response
    eval_response = await text_gen_service.get_chat_message_content(
        chat_history=chat_history,
        settings=execution_settings,
    )

    eval_response = str(eval_response)
    return eval_response



def edit_image(image, mask, prompt):
    url = f"{os.getenv('AZURE_IMAGE_GEN_ENDPOINT')}/openai/deployments/{os.getenv('AZURE_IMAGE_GEN_DEPLOYMENT_NAME')}/images/edits?api-version={os.getenv('AZURE_IMAGE_GEN_API_VERSION')}"

    headers = {
        "Authorization": f"Bearer {os.getenv('AZURE_IMAGE_GEN_API_KEY')}"
    }

    files = {
        'image': ('image.png', image),
        'mask': ('image.png', mask)
    }
    
    
    data = {
        "prompt": prompt
    }

    response = requests.post(url, data=data, files=files, headers=headers)

    print("Status Code:", response.status_code)

    if response.status_code == 200:
        with open("response.json", "w") as f:
            f.write(response.text)

        response_js = response.json()
        return response_js["data"][0]["b64_json"]
    else:
        print("Error:", response.text)
        return None