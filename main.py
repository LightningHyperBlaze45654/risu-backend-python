import json
from llama_cpp import Llama
from helper import hybrid_lorebook_pulling, emotion_pull
from monolyth import monolyth_generator
from chat_session import ChatSession
from memory import supa_memory

class ChatBot:
    def __init__(self, model_path, n_ctx):
        self.llm = Llama(
            model_path=model_path,
            n_gpu_layers=-1,
            temperature=1.0,
            n_ctx=n_ctx,
            repeat_penalty=2.0,
            verbose=False
        )
        self.token_limit = n_ctx

    def format_system_prompt(self, system_prompt, char_json, chat_history, memory, username):
        char = char_json["char"]
        char_desc = char_json["char_desc"]
        lorebook = char_json['lorebook']
        activate_words, lore_list = lorebook['activate_words'], lorebook['lore_list']
        retrieved_lore = hybrid_lorebook_pulling(chat_history=chat_history[-4:], lorebook=lore_list, activation_words=activate_words)
        return system_prompt.format(char=char, user=username, char_desc=char_desc, memory=memory, lorebook=retrieved_lore)

    def prompt_formatter(self, user_prompt, system_prompt, char_json, chat_history, memory="", username="user"):
        formatted_prompt = []
        system_prompt = self.format_system_prompt(system_prompt, char_json, chat_history, memory, username)
        formatted_prompt.append({"role": "system", "content": system_prompt})
        formatted_prompt.extend(chat_history)
        formatted_prompt.append({"role": "user", "content": user_prompt})
        return formatted_prompt

    def conversational_generator_summary(self, input_prompt):
        res = self.llm.create_chat_completion(
            messages=input_prompt,
            temperature=0.8,
            presence_penalty=0.8
        )
        return res['choices'][0]['message']

    def conversational_memory_lorebook(self, user_prompt, system_prompt, char_json, chat_history, memory="", username="user"):
        input_prompt = self.prompt_formatter(user_prompt, system_prompt, char_json, chat_history, memory, username)
        return self.conversational_generator_summary(input_prompt)

    def monolyth_conv_memory_lorebook(self, user_prompt, system_prompt, char_json, chat_history, modelname="soliloquy-l3", memory="", username="user"):
        input_prompt = self.prompt_formatter(user_prompt, system_prompt, char_json, chat_history, memory, username)
        return monolyth_generator(input_prompt, modelname)

def select_chat_session():
    sessions = ChatSession.list_sessions()
    if not sessions:
        print("No existing sessions found.")
        return None
    print("Available chat sessions:")
    for idx, session in enumerate(sessions):
        print(f"{idx + 1}. Chat Name: {session['chat_name']}, Character: {session['char_name']}, Session ID: {session['session_id']}")
    try:
        choice = int(input("Select a session number or enter 0 to create a new session: "))
        if choice == 0:
            return None
        if 1 <= choice <= len(sessions):
            return ChatSession.load_session(sessions[choice - 1]["session_id"])
        else:
            print("Invalid selection.")
            return select_chat_session()
    except ValueError:
        print("Invalid input. Please enter a number.")
        return select_chat_session()

# Main chat loop function
def chat_loop(model_path, n_ctx):
    chat_session = select_chat_session()
    if not chat_session:
        char_name = input("Enter the character name: ")
        chat_name = input("Enter the chat session name: ")
        chat_session = ChatSession(char_name, chat_name)
        chat_session.initialize_session_file()
    char_json = chat_session.load_character_data()
    system_prompt = chat_session.load_system_prompt()

    chat_bot = ChatBot(model_path, n_ctx)

    try:
        while True:
            user_input = input("You: ")
            memory, chat_session.history = supa_memory(chat_session, user_input, token_limit=chat_bot.token_limit, user_name="User", model_type="llama3")
            effective_history = chat_session.get_effective_history()
            response = chat_bot.conversational_memory_lorebook(
                user_prompt=user_input,
                system_prompt=system_prompt,
                char_json=char_json,
                chat_history=effective_history,
                memory=memory,
                username="User"
            )
            print("AI:", response['content'])
            current_chat = [{"role": "user", "content": user_input}, response]
            chat_session.append_chat_history(current_chat)
            if memory:
                chat_session.mark_memory_summary()
            else:
                chat_session.remove_memory_flag()
    except KeyboardInterrupt:
        print(f"Chat stopped for session: {chat_session.session_id}")

# Main entry point
if __name__ == "__main__":
    model_path = "./models/Llama-3-Soliloquy-8B-v2.Q4_K_M.gguf"
    n_ctx = 8192  # Ensure this matches the token limit
    chat_loop(model_path, n_ctx)
