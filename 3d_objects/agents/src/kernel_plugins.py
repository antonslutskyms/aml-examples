from typing import TypedDict, Annotated

import kernel_services
from semantic_kernel.functions import kernel_function  
from semantic_kernel.functions.kernel_plugin import KernelPlugin
import base64
from semantic_kernel.contents.image_content import ImageContent
from pydantic_core._pydantic_core import Url
from datetime import datetime

pref = kernel_services.pref

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
                        
                        Parameters:
                        - prompt -- instructions describing what image to generate.
                        
                        Returns:
                        - Local Path to the edited image. Returned Local Path is of the following format: ./output/pro_* 
                        
                    """
    )
    async def generate_image(self, prompt):

        now = datetime.now()
        model_number = f"{now.strftime('%Y%m%d%H%M%S')}"
        
        generated_image_file = f"{self.output_dir}/image1_{model_number}.png"

        #generated_image_file = f"{self.output_dir}/image1.png"
        print("!!!!!!!!!!!!!!!!!!!! Generating Image !!!!!!!!!!!!!!!!!!")
        response = await kernel_services.generate_image(prompt, generated_image_file, save_image=True, 
                            external_chat_history = kernel_services.chat_history)
        print("!!!!!!!!!!!!!!!!!! Image Generation Done !!!!!!!!!!!!!!!!!!!!!")
        return generated_image_file



    @kernel_function(name = "edit_last_image",
        description = """
                        Edits the last generated image for a given prompt.  
                        Parameters:
                        - prompt -- instructions describing what needs to be changed in the image.
                        
                        Returns:
                        - Local Path to the edited image. Returned Local Path is of the following format: ./output/pro_* 
                        
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


    # @kernel_function(name = "describe_image",
    # description = """
    #                 Describes an image.  
    #                 Parameters:
    #                 - uri -- Uri to the image.  May be base64 or local path.
                    
    #                 Returns:
    #                 - Image description            
    #             """)
    async def _describe_image(
      self,
      uri: str,
      eval_prompt = "Describe this image"
    ):

        # if str(uri).startswith(pref):
        #     base64_image = str(uri) #str(uri).replace(pref, "")    
        # else:
        #     base64_image = kernel_services.file_to_base64(uri)

        print("URIIIIIIII:", uri)


        eval_response = await kernel_services.evaluate_image(uri, eval_prompt, to_base64_converter=lambda x: x)

        return eval_response
