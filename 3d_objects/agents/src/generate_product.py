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
import product_generator_agent

print("Semantic Kernel Version: ", __version__)

from datetime import datetime
import os
import sys
import time

categories = open("categories.txt", "r").read()

async def main():

    #try:
    if True:
        run_time_logs = {}

        suffix = ""
        if len(sys.argv) > 1:
            suffix = sys.argv[1]


        now = datetime.now()
        model_number = f"{now.strftime('%Y%m%d%H%M%S')}{suffix}"


        output_dir = f"./output/{model_number}"
        os.makedirs(output_dir, exist_ok=True)

        

        def save_logs(logs):
            with open(f"{output_dir}/run_time_logs.json", "w") as f:
                f.write(json.dumps(logs, indent=4))


        run_time_logs["model_number"] = model_number
        save_logs(run_time_logs)



        colors = ["pink", "orange", "blue", "red", "green", "white"]

        import random
        import time

        seed = int(time.time())
        random.seed(seed)

        color = colors[random.randint(0, len(colors) - 1)]

        ###################################################################################################
        product_image, product_uses, product_idea = await product_generator_agent.generate_product(color, output_dir=output_dir)

        if False:
            run_time_logs["product_idea"] = str(product_idea)
            save_logs(run_time_logs)

            product_image_path = f"{output_dir}/image2.png"
            with open(product_image_path, "wb") as image_file:
                image_data = base64.b64decode(product_image)
                image_file.write(image_data)


            for i in range(len(product_uses)):
                use = product_uses[i]
                use_image_path = f"{output_dir}/image2_{i}.png"

                with open(use_image_path, "wb") as image_file:
                    image_data = base64.b64decode(use)
                    image_file.write(image_data)

            ###################################################################################################

            prompt = f"""Generate a product name and description for this product.
            The product name should be catchy and memorable and the description should be detailed and informative.
            
            Also classify the product into one of the following categories:
            {categories}

            The name should include the name of the subcategory.

            Also estimate the product width, length and height in inches.
            
            Also generate a list of keywords that describe the product.
            Product description should include all of the keywords.
            Make sure description is at least 200 words long.
            Sometimes, use common misspellings of the keywords in the description.

            Estimate likely weight of the object in grams when 3D printed with a resin printer.  Assume object is hollow and has a wall thickness of 2mm.
            Estime likely production costs in USD to produce this object on a Resin 3D printer is currently $40/kg.



            """+"""Respond as JSON object, such as:
            {
                "name": "Product Name",
                "description": "Product Description",
                "category": "Product Category",
                "production_cost": 10.99,
                "weight": 5.5,
                "keywords": [
                    "keyword1",
                    "keyword2"
                ],
                "dimensions": {
                    "height": 10,
                    "width": 20,
                    "length": 30
                },
                "features": [
                    "Feature 1",
                    "Feature 2"
                ]
            }
            """

            product_response = await kernel_services.evaluate_image(product_uses, prompt)

            product_response = json.loads(product_response.replace("```json", "").replace("```", ""))

            run_time_logs["product_response"] = product_response
            print("Product response:")
            print(product_response)
            save_logs(run_time_logs)

            m_chart_path = f"{output_dir}/image2_chart.png"
            print("Generating product chart...", product_image_path)
            kernel_services.edit_image_to_file(product_image_path, "mask.png", 
                                    "Generate an image showing the parts of the product that best correspond to each of the following keywords: " + 
                                                (", ".join(product_response["keywords"]))+
                                                ".  The image should be a chart showing the product with the keywords labeled on the image.",
                                    m_chart_path)



            print("Product Generation Complete.")
        # except:
        #     print("Error: ", sys.exc_info())
        #     run_time_logs["error"] = str(sys.exc_info()[1])
        #     save_logs(run_time_logs)
        #     print("Product Generation Failed.")
            

asyncio.run(main())
