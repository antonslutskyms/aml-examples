import kernel_services
import json
import base64
from semantic_kernel.contents.chat_history import ChatHistory
import jsonpickle
from semantic_kernel.connectors.ai.open_ai.exceptions.content_filter_ai_exception import ContentFilterAIException



prompt = f"""
GENERATE A ONE-SENTENCE IDEA FOR A PRODUCT THAT CAN BE 3D PRINTED BY A 3D PRINTER.

The product must be a useful and practical household product. It should be funny, creative, and whimsical.
The product must not have any moving parts or digital components.
The product is made of firm plastic and cannot be squeezed or flexed by the user.
The product must be free-standing and not require any support or attachment to a wall or other surface.
The product must be 3D printable.
The product must not be used to contain food or water.

IMPORTANT: The product must be in huge demand and easy to sell on Amazon Marketplace.

The product must fit into the following dimensions:
- Length: 20 cm
- Width: 20 cm
- Height: 20 cm

"""






async def generate_product(color, output_dir="."):

    print("Generating product idea...")
    chat_history = ChatHistory()

#    colors = "#87bd29, #f7eb00"
    colors = "black, red, green, blue, yellow"

    prompt_puzzle = f"""
        GENERATE A IDEA FOR A JIGSAW PUZZLE.

        The puzzle must use strictly the following colors: {colors}

        Do not include the word puzzle or jigsaw in the description.

        """

    prompt = prompt_puzzle

    idea = await kernel_services.get_chat_message_content(prompt, external_chat_history=chat_history)


    print(f">>>>>>>> Product idea:\n{idea}\n>>>>>>>>>>")

    parts = 16
    border = "#ffffff" #"#e4011a"
    
    print_idea = f"""
    Generate a square picture based on the following idea: {idea}.  
    Only use black, red, green and blue {colors}. 
    """

#    Ensure that all jigsaw pieces are clearly separated by a thick, white border.

    print("Generating Product Idea image....", print_idea)
    base64_image = await kernel_services.generate_image(print_idea, f"{output_dir}/image.png", save_image=True, external_chat_history=ChatHistory())

    do_eval = False

    edited_image_base_64 = base64_image

    try:
        from PIL import Image
    except ImportError:
        import Image

    background = Image.open(f"{output_dir}/image.png")
    overlay = Image.open('puzzle_base_masked_2.png')

    background = background.convert("RGBA")
    overlay = overlay.convert("RGBA")

    new_img = Image.alpha_composite(background, overlay)

    new_img.save(f'{output_dir}\\image_blended.png',"PNG")

    def dump_chat_history(_chat_history):
        print("INFO: Dumping ChatHistory")
        history = [str(ch.items) for ch in _chat_history]
        with open(f"{output_dir}/chat_history.json", "w") as out:
            out.write(json.dumps(history))



    if do_eval:
        for i in range(30):
            print(f"\n~~~~~~~~~~~~ Evaluation {i} ~~~~~~~~~~~~~~~")
            # eval_prompt = f"""
            #                 I'm preparing this image for a 3D printing project. 
            #                 What objects should be removed from the image to make it more suitable for 3D printing?

            #                     """

            eval_prompt = f"""
            The AI agent that generated this image was given the following requirements:
            {print_idea}

            Did the AI agent comply with the requirements?  
            
            The most important aspect is to make sure the appropriate number of puzzle pieces are separated by the {border} border.
            If the number of pieces is acheived and the color scheme is roughly in the ballpark, the image is considered good enough.

            Respond "yes" or "no".

            Also provide instructions to the AI agent that generated this image as to how the AI agent needs to modify the image to comply with requirements.
            
            In your instructions, first praise the AI agent for complying with requirements as appropriate.  
            Then summarize all the previous attempts and offer constructive guidance to help the AI agent complete the task.


            """+"""
            Respond in the following JSON structure:
            {
                "complies" : "no",
                "instructions" : "praise and constructive guidance"
            }

            """

            print("Critiquing the image...") 
            
            try:
                eval_response = await kernel_services.evaluate_image(base64_image, eval_prompt, to_base64_converter=lambda x: x, external_chat_history=chat_history)
                print("Image evaluation response:")
                print(eval_response)

                eval_response_json = json.loads(eval_response.replace("\n", " ").replace("```json", "").replace("```", ""))
                if eval_response_json["complies"] == "no":
                    #for i in range(1):
                    print(f"Modifying image for evaluation: {eval_response}")
                    out_path = f"{output_dir}/image_{i}.png"

                    update_instructions = f"""
                    You are an AI agent tasked with helping generate a jigsaw puzzle.
                    Your initial instructions were: {print_idea}.

                    After evaluation, another helpful AI agent responded with the following instructions:

                    {eval_response_json['instructions']}

                    Update the image according to these instructions.


                    """

                    edited_image_base_64 = kernel_services.edit_image_to_file(edited_image_base_64, 
                                                                                None, f"Version [{out_path}]: {update_instructions}", 
                                                                                out_path, 
                                                                                converter_func=base64.b64decode) 

                    dump_chat_history(chat_history)
                else:
                    print("Looks good!", eval_response)
                    dump_chat_history(chat_history)
                    break
            except ContentFilterAIException as ex:
                print("WARNING WARNING WARNING")
                print("WARNING!!", ex)
                print("WARNING! Dumping Chat History")
                chat_history = ChatHistory()
                continue

    


    uses = [edited_image_base_64]
    #for j in range(1):
    #uses_prompt = f"[{i}:{j}] Generate photo of this product in practical use."

    if False:
        uses_prompt = f"""Separate this picture into its jigsaw puzzle pieces.  
                        Pieces need to be functional and it must be possible to put the puzzle together using these pieces. """
        print("Generating product use image...", uses_prompt)
        out_path = f"{output_dir}/image_0.png"
        uses.append(kernel_services.edit_image_to_file(edited_image_base_64, 
                                                        None, f"Version [{out_path}]:{uses_prompt}", 
                                                        out_path, 
                                                        converter_func=base64.b64decode))

    if False:
        eval_prompt = """
                        Do you think this project be in high demand on Amazon Marketplace?
                        
                        If you feel this product is good enough to be in demand on Amazon Marketplace, respond "yes" and explain why in the notes.
                        If you feel this product needs work, respond "no" and generate suggestions in the notes what specifically should be done to improve this product's performance on Amazon Marketplace.  

                        Respond in the following JSON format:
                        {
                            "success": "yes or no",
                            "notes": "what can be done to improve the product?",
                        }
                        """

        print("------------ CRITIQUE -----------------")
        print(eval_prompt)
        eval_response_json = await kernel_services.evaluate_image(uses, eval_prompt, to_base64_converter=lambda x: x, external_chat_history=chat_history)

        eval_response_json = json.loads(eval_response_json.replace("```json", "").replace("```", ""))

        print("Image evaluation response:")
        print(eval_response_json)
        print("-----------------------------------------")
        if eval_response_json["success"] == "yes":
            print("Product is a success!")
#            break
        else:
            eval_response = eval_response_json["notes"]
            print("Product is not a success. Suggestion:", eval_response)

    return edited_image_base_64, uses, idea
