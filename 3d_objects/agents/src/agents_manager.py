print("Agents Manager Module Loading...")

import yaml
import sys
import kernel_services
print("Kernel Services Loaded")
from semantic_kernel.prompt_template import PromptTemplateConfig
from enum import Enum
import asyncio
print("Loading kernel plugins...")
import kernel_plugins
print("Kernel plugins loaded")

from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureChatPromptExecutionSettings

from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.contents import ChatMessageContent
from datetime import datetime
import os
import pickle

from local_python_plugin import LocalPythonPlugin

from semantic_kernel.contents.image_content import ImageContent


now = datetime.now()
project_id = f"pro_{now.strftime('%Y%m%d%H%M')}"

output_dir = f"./output/{project_id}"

os.makedirs(output_dir, exist_ok=True)

print("Imports Loaded")
class SupportedAgents(Enum):
    IDEA_GENERATOR = "idea_generator",
    IMAGE_AI = "image_ai",


available_agents = {}
print("Agents Available: ", available_agents)

def create_chat_completion_agent(agent_type: SupportedAgents, 
                                    template_file="./src/agent_templates/orchestrator_agent.yaml",
                                    plugins=[],
                                     **kwargs):
    
    # Read the YAML file
    with open(template_file, "r", encoding="utf-8") as file:
        generate_story_yaml = file.read()

    # Parse the YAML content
    data = yaml.safe_load(generate_story_yaml)

    # Use the parsed data to create a PromptTemplateConfig object
    prompt_template_config = PromptTemplateConfig(**data)

    agent = ChatCompletionAgent(
        service = kernel_services.text_gen_service,
        prompt_template_config = prompt_template_config,
        arguments = KernelArguments(**kwargs),
        kernel = kernel_services.kernel,
        plugins = plugins)

    return agent

def setup_agents(output_dir):
    image_gen_plugin = kernel_plugins.ImageAIPlugin(output_dir)
    
    kernel_services.kernel.add_plugin(
        image_gen_plugin,
        "image_ai"
    )

    executor_plugin = LocalPythonPlugin()
    executor_plugin._set_output_dir(output_dir)

    kernel_services.kernel.add_plugin(plugin_name="LocalCodeExecutionTool", plugin=executor_plugin)

    agent = create_chat_completion_agent(SupportedAgents.IDEA_GENERATOR, plugins = ["image_ai"])
    available_agents[SupportedAgents.IDEA_GENERATOR] = agent

    agent = create_chat_completion_agent(SupportedAgents.IMAGE_AI)

    available_agents[SupportedAgents.IMAGE_AI] = agent


def get_agent(agent_type: SupportedAgents):
    if agent_type not in available_agents:
        raise ValueError(f"Agent type {agent_type} is not available.")
    return available_agents[agent_type]

print("Functions Defined")

ctrl_c = '\x03'

def print_log(out, s):
        print(s)
        out.write(s+"\n")

def dump_history(inflate_image = False):

    print("Saving ChatHistory to PKL file")
    
    pkl_file = f"{output_dir}/chat_history.pkl"
    output = open(pkl_file, 'wb')
    pickle.dump(kernel_services.chat_history, output)
    output.close()
    print("Saved ChatHistory to: ", pkl_file)

    with open(f"{output_dir}/history.txt", "w") as out:
        inflated_chat_history = ChatHistory()

        print_log(out, f"Chat History Sz:: {len(kernel_services.chat_history)}")

        j = 1
        for message in kernel_services.chat_history:
            print_log(out, "..............................................................................................................")
            print_log(out, f"#{j}")
            print_log(out, f"[{message.role}] Message: {message}")

            print_log(out, "\tItems: ")
            i = 1

            inflated_items = []

            for item in message.items:
                _item = item

                if inflate_image and isinstance(item, ImageContent):
                    print_log(out, f"Image content detected...")
                    
                    try:
                        if not str(item.uri).startswith("data:image/"):
                            _item = ImageContent(uri=f"data:image/png;base64,{kernel_services.file_to_base64(str(item.uri))}")
                    except AttributeError as ex:
                        print_log(out, f"Error creating new content: {ex}, {item}") 

                print_log(out, f"\t\tItem[{j}{++i}]: {type(_item)}, {str(_item)[:300]}...")

                inflated_items.append(_item)

            inflated_chat_history.add_message(ChatMessageContent(
                role = message.role,
                items=inflated_items
            ))

            j=j+1

        return inflated_chat_history



async def main():
    


    print("------------- [Main] Creating chat completion agent...", sys.argv)

    


    if len(sys.argv) > 1:
        new_output_dir = sys.argv[1]
        print(f"Setting output_dir: {new_output_dir}")

        output_dir = f"./output/{new_output_dir}"


    saved_chat_history = f"{output_dir}/chat_history.pkl"

    if os.path.isfile(saved_chat_history):
        print("Loading Saved Chat History")
        pkl_file = open(saved_chat_history, 'rb')

        chat_history_loaded = pickle.load(pkl_file)
        
        kernel_services.chat_history = chat_history_loaded 
        print("Chat History Loaded")
        dump_history()
    # Example usage
    setup_agents(output_dir)

    print("Agents setup completed.\n")
    agent = get_agent(SupportedAgents.IDEA_GENERATOR)

    print("Agent Instructions :")
    print("=====================================================")
    print(agent.instructions)
    print("=====================================================")
    print("Agent created successfully.\n")

    agent_handlers = {
        "/chat": get_agent(SupportedAgents.IDEA_GENERATOR)
    }




    #chat_history = kernel_services.chat_history





    command_handlers = {"\\history" : dump_history}

    default_prompt = """Generate an image of a tree.  
                        Then generate python code using cv2 to display the generated image.  
                        Then execute the generated code.
                        Once the code is executed, give control back to the user.
                        """

    print("Default Prompt: ", default_prompt)
    while True:

        user_input = input(f"\nUser Input: ") or default_prompt
        
        print(f"User input received: {user_input}\n")

        if user_input.startswith("\\"):
            command_handlers[user_input]()
            continue

        if user_input.startswith("/"):
            command = user_input.split()[0]
            if command in agent_handlers:
                agent = agent_handlers[command]
                print(f"Using agent for command: {command}")
            else:
                print(f"No Command detected. Using default agent.")

        execution_settings = AzureChatPromptExecutionSettings()
        execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        kernel_services.chat_history.add_user_message(user_input)
        
        print("Chat history updated with user input.")
        #response = agent.invoke(chat_history=chat_history)
        #response = await agent.get_response(messages=f"User input at {datetime}: {user_input}")

        inflated_chat_history = dump_history(True)

        print("Getting Response from Agent...")
        response = await agent.get_response(# TODO: ??? chat_history = inflated_chat_history, 
                                                settings = execution_settings,
                                                messages = inflated_chat_history)
        print("\n\nAgent Response: ============================================\n", response, "\n===================================")

        kernel_services.chat_history.add_message(
            ChatMessageContent(    
                role=AuthorRole.ASSISTANT, 
                content=str(response)
            )
        )
#        print("kernel_services.chat_history", kernel_services.chat_history)

asyncio.run(main())