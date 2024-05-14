import json
from llama_cpp import Llama
from helper import hybrid_lorebook_pulling, summary, emotion_pull

# Function to append chat history to a JSON file
def append_chat_history(file_path, chat_list):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)  # Load the data as a Python list
    except (json.JSONDecodeError, FileNotFoundError):
        # If the file is empty or does not exist, start with an empty list
        data = []
    data.extend(chat_list)
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)  # Use `indent` for pretty-printing

# Function to get chat history from a JSON file
def get_chat_history(file_path):
    try:
        with open(file_path, 'r') as file:
            history = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        history = []
    return history

# Function to format the system prompt using character data and chat history
def format_system_prompt(system_prompt, char_json, chat_history, chat_history_summary, username):
    char = char_json["char"]
    char_desc = char_json["char_desc"]
    lorebook = char_json['lorebook']
    activate_words, lore_list = lorebook['activate_words'], lorebook['lore_list']
    retrieved_lore = hybrid_lorebook_pulling(chat_history=chat_history[-4:], lorebook=lore_list, activation_words=activate_words)
    return system_prompt.format(char=char, user=username, char_desc=char_desc, chat_summary=chat_history_summary, lorebook=retrieved_lore)

# Function to format the entire prompt for the chat
def prompt_formatter(user_prompt, system_prompt, char_json, chat_history, chat_history_summary="", username="user"):
    formatted_prompt = []
    system_prompt = format_system_prompt(system_prompt, char_json, chat_history, chat_history_summary, username)
    formatted_prompt.append({"role": "system", "content": system_prompt})
    formatted_prompt.extend(chat_history)
    formatted_prompt.append({"role": "user", "content": user_prompt})
    return formatted_prompt

# Function to generate a chat response using the LLM
def conversational_generator_summary(llm, input_prompt):
    res = llm.create_chat_completion(
        messages=input_prompt,
        temperature=0.8,
        presence_penalty=0.8
    )
    return res['choices'][0]['message']

# Function to generate a chat response with lorebook integration
def conversational_summary_lorebook(llm, user_prompt, system_prompt, char_json, chat_history, chat_history_summary="", username="user"):
    input_prompt = prompt_formatter(user_prompt, system_prompt, char_json, chat_history, chat_history_summary, username)
    return conversational_generator_summary(llm, input_prompt)

# Main chat loop function
def chat_loop(llm, char_name, user_name):
    history = get_chat_history("./chat_history/chat.json")
    with open(f'./character_prompts/{char_name}.json', 'r', encoding='utf-8') as file:
        char_json = json.load(file)
    with open('./system_prompts/pingpong_test.txt', 'r', encoding='utf-8') as file:
        system_prompt = file.read()

    try:
        while True:
            user_input = input("You: ")
            response = conversational_summary_lorebook(
                llm=llm,
                user_prompt=user_input,
                system_prompt=system_prompt,
                char_json=char_json,
                chat_history=history[-100:],
                username=user_name
            )
            print("AI:", response['content'])
            current_chat = [{"role": "user", "content": user_input}, response]
            history.extend(current_chat)
            append_chat_history("./chat_history/chat.json", current_chat)
    except KeyboardInterrupt:
        print("Chat stopped")

# Main entry point
if __name__ == "__main__":
    llm = Llama(
        model_path="./models/Llama-3-Soliloquy-8B-v2-Q4_K_M.gguf",
        n_gpu_layers=-1,
        temperature=1.0,
        n_ctx=8192,
        repeat_penalty=2.0,
        verbose=False
    )
    chat_loop(llm, "hatsune_miku", "Hyperblaze")
