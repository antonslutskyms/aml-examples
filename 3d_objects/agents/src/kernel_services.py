from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents import ChatMessageContent, TextContent, ImageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
import base64
import os
import time
import sys
from semantic_kernel import Kernel

from services import Service
from service_settings import ServiceSettings
from image_gen_text_to_image import ImageGenTextToImage
import requests
from openai import AsyncAzureOpenAI, AsyncOpenAI, OpenAI
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

from datetime import datetime

pref = "data:image/png;base64,"

kernel = Kernel()

service_settings = ServiceSettings()

# Select a service to use for this notebook (available services: OpenAI, AzureOpenAI, HuggingFace)
selectedService = (
    Service.AzureOpenAI
    #Service.OpenAI
    # if service_settings.global_llm_service is None
    # else Service(service_settings.global_llm_service.lower())
)
print(f"Using service type: {selectedService}")

print("endpoint: ", os.getenv("AZURE_IMAGE_GEN_ENDPOINT"))

image_client = AsyncAzureOpenAI(
    azure_endpoint=os.getenv("AZURE_IMAGE_GEN_ENDPOINT"),
    api_key=os.getenv("AZURE_IMAGE_GEN_API_KEY"),
    api_version=os.getenv("AZURE_IMAGE_GEN_API_VERSION"),
) if selectedService == Service.AzureOpenAI else AsyncOpenAI()

#image_client = AsyncOpenAI()
   

# Remove all services so that this cell can be re-run without restarting the kernel
kernel.remove_all_services()

service_id = None
if selectedService == Service.OpenAI:
    sync_image_client = OpenAI()

    
    service_id = "default"
    kernel.add_service(
        OpenAIChatCompletion(
            service_id=service_id,
            ai_model_id="gpt-4.1"
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

print("image_client: ", image_client)

image_gen_service = ImageGenTextToImage (
    async_client=image_client,
    ai_model_id="gpt-image-1",
    service_id="gpt-image-1", # Optional; for targeting specific services within Semantic Kernel
)
kernel.add_service(image_gen_service)

# ---------------- Register Non-AOAI service -----------
# from azure.ai.inference.aio import ChatCompletionsClient
# from azure.identity.aio import DefaultAzureCredential

# from semantic_kernel.connectors.ai.azure_ai_inference import AzureAIInferenceChatCompletion

# chat_completion_service = AzureAIInferenceChatCompletion(
#     ai_model_id="<deployment-name>",
#     client=ChatCompletionsClient(
#         endpoint=f"{str(<your-azure-open-ai-endpoint>).strip('/')}/openai/deployments/{<deployment_name>}",
#         credential=DefaultAzureCredential(),
#         credential_scopes=["https://cognitiveservices.azure.com/.default"],
#     ),
# )


image_gen_service = kernel.get_service(service_id="gpt-image-1")
text_gen_service = kernel.get_service(service_id="default")

chat_history = ChatHistory()

# Function to convert a file to Base64
def file_to_base64(file_path):
    with open(file_path, "rb") as file:
        # Read the file in binary mode and encode it to Base64
        base64_encoded = base64.b64encode(file.read()).decode("utf-8")
    return base64_encoded

async def generate_image(prompt, image_path, save_image=True, external_chat_history=None):
    _chat_history = external_chat_history if external_chat_history else chat_history
    _chat_history.add_message(ChatMessageContent(
        role=AuthorRole.USER,
        items=[TextContent(text=prompt)]
    ))

    a = datetime.now()
    print(f"-- Image Generated starting at {a} seconds")
    image = await image_gen_service.generate_image(
        description=prompt, width=1024, height=1024, quality="auto", chat_history = _chat_history
    )
    print(f"-- Image Generated in {datetime.now()-a} seconds")

    if save_image:
        image_data = base64.b64decode(image)

        with open(image_path, "wb") as image_file:
            image_file.write(image_data)

        print("Saved Image to: ", image_path)
#    base64_string = file_to_base64(image_path)

    _chat_history.add_message(ChatMessageContent(
        role=AuthorRole.USER,
        items=[
                #ImageContent(uri=f"data:image/png;base64,{image}")
                ImageContent(uri=f"{image_path}")
        ]
    ))

    return image

async def get_chat_message_content(prompt, external_chat_history=None):
    _chat_history = external_chat_history if external_chat_history else chat_history


    seed = int(time.time())
    print(f"Seed: {seed}")
    execution_settings = OpenAIChatPromptExecutionSettings(seed=seed)

    _chat_history.add_message(ChatMessageContent(
        role=AuthorRole.USER,
        items=[TextContent(text=prompt)]
    ))

    a = datetime.now()
    print(f"-- text_gen_service.get_chat_message_content starting at {a} seconds")
    return await text_gen_service.get_chat_message_content(
        chat_history=_chat_history,
        settings=execution_settings,
    )
    print(f"-- text_gen_service.get_chat_message_content in {datetime.now()-a} seconds")


import os

async def evaluate_image(image_paths, prompt, to_base64_converter=file_to_base64, external_chat_history=None):
    _chat_history = external_chat_history if external_chat_history else chat_history

    if not isinstance(image_paths, list):
        image_paths = [image_paths]

    execution_settings = OpenAIChatPromptExecutionSettings()

    text_gen_service = kernel.get_service(service_id="default")

    items = [TextContent(text=prompt)]

    for image_path in image_paths:
        if os.path.exists(image_path):
            base64_string = file_to_base64(image_path) if not image_path.startswith(pref) else image_path
            items.append(ImageContent(uri=f"data:image/png;base64,{base64_string}"))

    _chat_history.add_message(ChatMessageContent(
            role=AuthorRole.USER,
            items=items
        ))

    a = datetime.now()

    print(f"-- evaluate_image.text_gen_service.get_chat_message_content starting at {a}")

    # Get the chat completion response
    eval_response = await text_gen_service.get_chat_message_content(
        chat_history=_chat_history,
        settings=execution_settings,
    )
    print(f"-- evaluate_image.text_gen_service.get_chat_message_content in {datetime.now()-a} seconds")

    eval_response = str(eval_response)
    return eval_response


async def edit_image_to_file(images, mask, prompt, file_name, n=1, converter_func=lambda x: open(x, "rb").read()):
    result_images = []
    _images = []
    
    print("edit_image_to_file.images: ", len(images))

    for image in images:
        _images.append(converter_func(image))


    image_base_64 = await edit_image(_images, converter_func(mask) if mask else mask, prompt, n)  

    if not isinstance(image_base_64, list):
        image_base_64 = [image_base_64]

    result_images.extend(image_base_64)

    print("RESULT IMAGES: ", len(result_images))
    
    image = result_images[0]

    image_data = base64.b64decode(image)

    with open(file_name, "wb") as image_file:
        image_file.write(image_data)

    print(f"Saved edited image to: {file_name}")
    
    
    print(f"KS: Adding generated image to ChatHistory: ${file_name}")
    chat_history.add_message(ChatMessageContent(
        role=AuthorRole.USER,
        #items=[ImageContent(uri=f"data:image/png;base64,{result}")]
        items=[ImageContent(uri=f"{file_name}")]
    ))
    return image


async def edit_image(images, mask, prompt, n=1, external_chat_history=None):
    #_chat_history = external_chat_history if external_chat_history else chat_history

    _chat_history = chat_history

    result = None

    if selectedService == Service.OpenAI:
        print("Editing image using OPENAI API...")
        result = sync_image_client.images.edit(
            model="gpt-image-1",
            image = [open(image, "rb") for image in images],
            # image=[
            #     open(image, "rb"),
            # ],
            prompt=prompt,
            n = n
        )

        result = result.data[0].b64_json
    else:
        print("Editing image using AZURE API...")
        result = await edit_image_azure(images, mask, prompt)


    

    return result           



async def edit_image_azure(images, mask, prompt, n=1):
    return edit_image_base(images, mask, prompt, n)


async def edit_image_base_2(images, mask, prompt, n=1):

    result = await image_client.images.edit(
        model="gpt-image-1",
        image = images,
        prompt=prompt)

    return result.data[0].b64_json



def edit_image_base(images, mask, prompt, n=1):

    print("Images: ", len(images))
    url = f"{os.getenv('AZURE_IMAGE_GEN_ENDPOINT')}/openai/deployments/{os.getenv('AZURE_IMAGE_GEN_DEPLOYMENT_NAME')}/images/edits?api-version={os.getenv('AZURE_IMAGE_GEN_API_VERSION')}"
    
    headers = {
        "Authorization": f"Bearer {os.getenv('AZURE_IMAGE_GEN_API_KEY')}"
    }

    files = {}


    i=-1
    i_pref = ""
    for image in images:
        files[f'image{i_pref}'] = (f'image{i_pref}.png', image)
        # TODO: just one image
        break
        i_pref = f"_{++i}"
        


    #print("files:", files)

    if mask:
        files['mask'] = ('mask.png', mask)    
    
    data = {
        "prompt": prompt,
        "n": n,
        #"temperature": 0.6
    }


    a = datetime.now()
    print(f"-- /edits (requests.post) starting at {a}")
    response = None
#    for i in range(3):
#        try:
    response = requests.post(url, data=data, files=files, headers=headers, timeout=300)
#            break
#        except:
#            print("Exception in /edits (requests.post):")
#            print("0", sys.exc_info()[0])
#            print("1", sys.exc_info()[1])
#            print("2", sys.exc_info()[2])

    print(f"-- /edits (requests.post) in {datetime.now()-a} seconds")

    print(f"Status Code[{n}]:", response.status_code)

    if response.status_code == 200:
        with open("response.json", "w") as f:
            f.write(response.text)

        response_js = response.json()

        result_images = []
        for i in range(len(response_js["data"])):
            result_images.append(response_js["data"][i]["b64_json"])
        
        #return response_js["data"][0]["b64_json"]
        return result_images[0] if len(result_images) == 1 else result_images
    else:
        print("Error:", response.text)
        return None