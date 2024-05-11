import json
from embedding import ChatEmbeddings
import requests
import os

''' 
HELPER FUNCTIONS
Mostly for chat history, retrieval.
'''
def append_chat_history(file_path, chat_list):
    # Step 2: Open the JSON file and read its content
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)  # Load the data as a Python list
    except json.JSONDecodeError:
        # If the file is empty and causes a JSONDecodeError, start with an empty list
        data = []
    # Step 3: Append the new dictionary to the list
    data.extend(chat_list)
    # Step 4: Write the updated list back to the JSON file
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)  # Use `indent` for pretty-printing


def get_chat_history(file_path):
    try:
        with open(file_path, 'r') as file:
            history = json.load(file)
    except json.JSONDecodeError:
        history = []
    return history

def simple_conversational_generator(user_prompt, system_prompt, chat_history=[]):

    return

def RAG_generator(user_prompt, system_prompt, retriever):
    return

def monolyth_generator(user_prompt, system_prompt, chat_history, modelname="soliloquy-l3", extra_state=""):
    API = os.getenv('MONOLYTH_API_KEY')
    input_prompt = []
    input_prompt.append({"role": "system", "content": f"{system_prompt}"})
    input_prompt.extend(chat_history)
    input_prompt.append({"role": "user", "content": f"{user_prompt}"})
    response = requests.post(
        url="https://api.monolyth.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API}",
        },
    data=json.dumps({
        "model": f"{modelname}", # Ex: gpt-3.5-turbo
        "messages": input_prompt,
        "repeat_penalty": 1,
        "temperature" : 0.7,
        "max_tokens" : 800,
        "stop" : ["<|eot_id|>", "user:" ]
    })
    ).json()
    return response['choices'][0]['message']


def chat_loop():
    history = get_chat_history("./chat_history/chat.json")
    with open('./sysprompt/sqweegirl.txt', 'r', encoding='utf-8') as file:
        system_prompt = file.read()
    try:
        while True: 
            user_input = input("You: ")
            response = monolyth_generator(user_prompt=user_input, system_prompt=system_prompt, chat_history=history[-300:])
            print("AI:", response['content'])
            # Append current chat to history and file
            current_chat = [{"role": "user", "content": user_input}, response]
            history.extend(current_chat)
            append_chat_history("./chat_history/chat.json", current_chat)
    except KeyboardInterrupt:
        print("Chat stopped")

chat_loop()