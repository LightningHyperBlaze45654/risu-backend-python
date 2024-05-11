import json
from llama_cpp import Llama
from monolyth import monolyth_generator
from helper import hybrid_lorebook_pulling, summary, emotion_pull

llm = Llama(
    model_path = "./models/Llama-3-Soliloquy-8B.Q4_K_M.gguf",
    n_gpu_layers= -1,
    temperature = 1.0,
    n_ctx = 24000,
    repeat_penalty = 2.0,
    verbose = False
    )

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

def conversational_generator_summary(user_prompt, system_prompt, chat_history_summary, chat_history_short=[]):
    input_prompt = []
    input_prompt.append({"role": "system", "content": f"{system_prompt}"})
    input_prompt.extend(chat_history_short)
    input_prompt.append({"role": "user", "content": f"{user_prompt}"})
    res = llm.create_chat_completion(
        messages=input_prompt,
        temperature=0.8,
        presence_penalty=0.8
    )
    return res['choices'][0]['message']

def chat_loop(char_name):
    history = get_chat_history("./chat_history/chat.json")
    with open(f'./character_prompts/{char_name}.json', 'r', encoding='utf-8') as file:
        char_prompt = file.read()
        char = char_prompt['char']
        char_desc = char_prompt['char_desc']
        lorebook = char_prompt['lorebook']
    with open('./system_prompts/short_chat.txt', 'r', encoding='utf-8') as file:
        system_prompt = file.read()
    system_prompt = system_prompt.format(char=char, char_desc=char_desc, lorebook=lorebook)
    try:
        while True:
            user_input = input("You: ")
            response = monolyth_generator(user_prompt=user_input, system_prompt=system_prompt, chat_history=history[-100:])
            print("AI:", response['content'])
            # Append current chat to history and file
            current_chat = [{"role": "user", "content": user_input}, response]
            history.extend(current_chat)
            append_chat_history("./chat_history/chat.json", current_chat)
    except KeyboardInterrupt:
        print("Chat stopped")

chat_loop("hatsune_miku")