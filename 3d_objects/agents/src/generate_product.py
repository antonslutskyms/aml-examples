from semantic_kernel import __version__
import os

from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents import ChatMessageContent, TextContent, ImageContent
from semantic_kernel.contents.utils.author_role import AuthorRole

import time
import asyncio
import json
import base64

import kernel_services

print("Semantic Kernel Version: ", __version__)

from datetime import datetime
import os

now = datetime.now()
output_dir = f"./output/{now.strftime('%Y_%m_%d_%H_%M_%S')}"
os.makedirs(output_dir, exist_ok=True)

async def main():

    categories = open("categories.txt", "r").read()

    run_time_logs = {}

    def save_logs(logs):
        with open(f"{output_dir}/run_time_logs.json", "w") as f:
            f.write(json.dumps(logs, indent=4))

    input = "Home & Kitchen"

    product_category = "Soap Dish"

    run_time_logs["input"] = input
    save_logs(run_time_logs)
    print("Input: ", input)




    prompt = f"""GENERATE A ONE-SENTENCE IDEA FOR A {product_category} THAT CAN BE 3D PRINTED BY A RASIN 3D PRINTER.  
                IT SHOULD BE A USEFUL AND PRACTICAL HOUSEHOLD PRODUCT.  IT SHOULD BE FUNNY, CREATIVE AND WIMSICAL.

    The {product_category} must not have any moving parts or digital components.
    The {product_category} is made of firm plastic and cannot be squeezed or flexed by the user.
    The {product_category} must be free-standing and not require any support or attachment to a wall or other surface.
    The {product_category} must be 3D printable.

    Product must fall within one of these categories and subcategories:
    {categories}
    
    BE CREATIVE AND FUNNY. I WANT TO LAUGH.
    """+"""
    Respond in the folloiwng JSON format:
    {
        "idea": "Product Idea",
        "category": "Product Category",
        "sub_category": "Product Subcategory",
    }
    """

    run_time_logs["initial_prompt"] = prompt
    save_logs(run_time_logs)
    print("Prompt: ", prompt)


    print("Generating product idea...")
    idea = await kernel_services.get_chat_message_content(prompt)

    idea = str(idea).replace("```json", "").replace("```", "")
    idea = json.loads(idea)
    run_time_logs["product_idea"] = idea
    save_logs(run_time_logs)

    print("Product Idea:")
    print(idea)
    print("")

    ### Generate Base Image

    print("Generating BASE image...")
    print_idea = f"""Generate a photo of a plastic 3D-printed product based on the following idea: {idea['idea']}
    The photo should be in a realistic style, with a white background and no text.
    The product must be usable and practical, and it should be a 3D-printed object.
    The object should be the only thing in the image, and it should be centered in the frame.
    The object should be a 3D-printable object, and it should be in a realistic style.
    The product should be simple, with no removable parts or moving parts.
    There should only be one object in the image, and it should be the only thing in the frame.
    The product dimensions must be not be larger than a small hamster.
    The image must not be a drawing, painting, or cartoon.

    Product should be GRAY color with no other colors.

    """

    base_image_path = f"{output_dir}/image.png"
    await kernel_services.generate_image(print_idea, base_image_path)

    print("Base image generated.", base_image_path)

    ### Evaluate Image
    print("Evaluating image for 3D printing suitability...")

    prompt = f"""I'm preparing this image for a 3D printing project. What objects should be removed from the image to make it more suitable for 3D printing?""" 
    eval_response = await kernel_services.evaluate_image(base_image_path, prompt)
    print("Image evaluation response:")
    print(eval_response)
    run_time_logs["eval_response"] = eval_response
    save_logs(run_time_logs)

    ### Generate Final Image
    print("Generating FINAL image...")
    image_base_64 = kernel_services.edit_image(open(f"{output_dir}/image.png", "rb").read(), open("mask.png", "rb").read(), eval_response)  

    if image_base_64:

        image_data = base64.b64decode(image_base_64)


        iter_image_path = f"{output_dir}/image2.png"
        with open(iter_image_path, "wb") as image_file:
            image_file.write(image_data)
        print("Final image generated.", iter_image_path)

        ### Generate Marketing Examples
        print("Generating marketing examples...")
        marketing1 = f"""
                    Now is {now}.
                    Consider the following product that is described as: {idea}


                    Generate a photo of this product in a realistic use scenario."""

        marks = ["a business desk", "a kitchen table", "a bathroom counter", "a coffee table", "a shelf"]

        #marks = ["a business desk", "a kitchen table"]

        product_images = [iter_image_path]

        i = -1
        for mark in marks:
            i += 1
            m_out_image_path = f"{output_dir}/image2_{i}.png"
            if os.path.exists(m_out_image_path):
                print(f"File {m_out_image_path} already exists. Skipping...")
                continue
            prompt = f"{marketing1}."

            #print(prompt)
            m_image_path = f"{output_dir}/image2.png"
            image_base_64 = kernel_services.edit_image(open(m_image_path, "rb").read(), open("mask.png", "rb").read(), prompt)  

            product_images.append(m_out_image_path)

            image_data = base64.b64decode(image_base_64)
            
            with open(m_out_image_path, "wb") as image_file:
                image_file.write(image_data)
                
        ### Generate Product Description
        

        
        prompt = f"""Generate a product name and description for this product.
        Also classify the product into one of the following categories:
        {categories}

        Also estimate the product height, width and depth in inches.
        Also generate a list of keywords that describe the product.
        """+"""Respond as JSON object, such as:
        {
            "name": "Product Name",
            "description": "Product Description",
            "category": "Product Category",
            "keywords": [
                "keyword1",
                "keyword2"
            ],
            "dimensions": {
                "height": 10,
                "width": 20,
                "depth": 30
            },
            "features": [
                "Feature 1",
                "Feature 2"
            ]
        }
        """

        product_response = await kernel_services.evaluate_image(product_images, prompt)

        product_response = json.loads(product_response.replace("```json", "").replace("```", ""))

        run_time_logs["product_response"] = product_response
        print("Product response:")
        print(product_response)
        save_logs(run_time_logs)

    print("Product Generation Complete.")

asyncio.run(main())
