import json
from embedding import ChatEmbeddings
from llama_cpp import Llama

llm = Llama(
    model_path = "./Llama-3-Soliloquy-8B.Q4_K_M.gguf",
    n_gpu_layers= -1,
    temperature = 1.15,
    n_ctx = 8192,
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

def LSTM_conversational_generator(user_prompt, system_prompt, chat_history_short=[], chat_history_old=[], character_vectorstore=None):
    input_prompt = []
    input_prompt.append({"role": "system", "content": f"{system_prompt}"})
    input_prompt.extend(chat_history_old)
    input_prompt.extend(chat_history_short)
    input_prompt.append({"role": "user", "content": f"{user_prompt}"})

    res = llm.create_chat_completion(
        messages=input_prompt,
        temperature=1.4,
        repeat_penalty=2.0
    )
    return res['choices'][0]['message']

def chat_loop():
    history = get_chat_history("./chat.json")
    with open('./system_prompt.txt', 'r', encoding='utf-8') as file:
        system_prompt = file.read()
    chat_embeddings = ChatEmbeddings()  # Initialize or load existing index

    try:
        while True:
            user_input = input("You: ")
            response = LSTM_conversational_generator(user_prompt=user_input, system_prompt=system_prompt, chat_history_short=history[-100:])
            print("AI:", response['content'])
            current_chat = [{"role": "user", "content": user_input}, {"role": "assistant", "content": response['content']}]
            history.extend(current_chat)
            append_chat_history("./chat.json", current_chat)

            if current_chat[0]['content'] and current_chat[1]['content']:
                chat_embeddings.add_to_index(current_chat[0]['content'], current_chat[1]['content'])

            if len(history) % 10 == 0:
                chat_embeddings.save_index()

    except KeyboardInterrupt:
        try:
            chat_embeddings.save_index()
            print("Chat ended and index saved.")
        except Exception as e:
            print(f"Error saving index: {e}")
chat_loop()