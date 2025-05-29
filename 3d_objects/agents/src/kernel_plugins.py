from typing import TypedDict, Annotated

import kernel_services
from semantic_kernel.functions import kernel_function  
from semantic_kernel.functions.kernel_plugin import KernelPlugin
import base64
from semantic_kernel.contents.image_content import ImageContent
from pydantic_core._pydantic_core import Url
from datetime import datetime

class ImageAIModel(TypedDict):
    id: int
    name: str
    image: str | None
    prompt: str | None


class ImageAIPlugin:

    def __init__(self, output_dir):
        self.output_dir = output_dir
   
    @kernel_function(
        name="image_generator_agent",
        description="""Image generation plugin. Use this to generate images, such as
        - "Generate a landscape image" or "Create an avatar for a user profile".
        - "Edit an existing image" or "Modify a picture to add a sunset background".
        - "Generate an image based on a description" or "Create a picture of a futuristic cityscape".
    """,
    )


    @kernel_function(
        name = "generate_image",
        description = """
                        Generate an image for the given prompt.  
                        Returns local path the the generated image.
                    """
    )
    async def generate_image(self, prompt):
        generated_image_file = f"{self.output_dir}/image1.png"
        print("!!!!!!!!!!!!!!!!!!!! Generating Image !!!!!!!!!!!!!!!!!!")
        response = await kernel_services.generate_image(prompt, generated_image_file, save_image=True, 
                            external_chat_history = kernel_services.chat_history)
        print("!!!!!!!!!!!!!!!!!! Image Generation Done !!!!!!!!!!!!!!!!!!!!!")
        return generated_image_file



    @kernel_function(name = "edit_last_image",
        description = """
                        Edits the last generated image for a given prompt.  
                        Returns local path to the edited image.
                        Parameters:
                        - base64_image -- must be full base64 encoded content of the image.
                        - prompt -- instructions describing what needs to be changed in the image.
                    """)
    async def edit_last_image(
      self,
      prompt: str
    ):
        print("~~ Edit Image Plugin Active ~~")

        now = datetime.now()
        model_number = f"{now.strftime('%Y%m%d%H%M%S')}"
        
        out_path = f"{self.output_dir}/image1_{model_number}.png"
        

        kernel_services.chat_history

        base64_images = []
        uris = []

        for message in kernel_services.chat_history:

            for item in message.items:
                
                if isinstance(item, ImageContent):
                    uri = None

                    try:
                        uri = str(item.uri)
                    except AttributeError as ex:
                        print("Cant find URI, trying URL: ")
                        uri = str(item) 

                    print("Image content detected.  Item URI:")
                    
                    pref = "data:image/png;base64,"
                        
                    if not uri.startswith(pref):
                        base64_images.append(kernel_services.file_to_base64(uri))
                        uris.append(uri)
                    else:
                        base64_images.append(uri.replace(pref, ""))
                        uris.append(uri[:150])
                    print(f"Loaded Image contents: {base64_images[-1][:100]}..")


        base64_image = base64_images[-1]


        #print("image_path: ", image_path)
        print(f"Base64 Image: {uris[-1]} |_{base64_image[:100]}..._|")
        kernel_services.edit_image_to_file(base64_image, 
                        None, f"Version [{out_path}]: {prompt}", 
                        out_path, 
                        converter_func=base64.b64decode)

        return out_path
