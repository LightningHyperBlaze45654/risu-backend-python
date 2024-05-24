import json
from llama_cpp import Llama
from helper import hybrid_lorebook_pulling, emotion_pull
from monolyth import monolyth_generator
from chat_session import ChatSession
from memory import supa_memory
from tokenizer import text_token_length

class ChatBot:
    '''
    ChatBot class handles the interaction with the LLM.
    '''
    def __init__(self, model_path, n_ctx):
        '''
        Initializes the ChatBot with the LLM model.
        
        Args:
            model_path (str): The path to the LLM model.
            n_ctx (int): The context size for the LLM.
        '''
        self.llm = Llama(
            model_path=model_path,
            n_gpu_layers=-1,
            temperature=1.0,
            n_ctx=n_ctx,
            repeat_penalty=2.0,
            verbose=False
        )
        self.token_limit = n_ctx

    def format_system_prompt(self, system_prompt, char_json, chat_history, memory, username, retrieved_lore):
        '''
        Formats the system prompt by inserting character and lorebook information into the prompt template.
        
        Args:
            system_prompt (str): The system prompt template.
            char_json (dict): The character data.
            chat_history (list): The chat history.
            memory (str): The memory summary.
            username (str): The name of the user.
            retrieved_lore (str): The retrieved lorebook content.
        
        Returns:
            str: The formatted system prompt.
        '''
        char = char_json["char"]
        char_desc = char_json["char_desc"]
        return system_prompt.format(char=char, user=username, char_desc=char_desc, memory=memory, lorebook=retrieved_lore)

    def prompt_formatter(self, user_prompt, system_prompt, char_json, chat_history, memory="", username="user", retrieved_lore=""):
        '''
        Constructs the full prompt for the LLM by combining the system prompt, chat history, and user input.
        
        Args:
            user_prompt (str): The user's input.
            system_prompt (str): The system prompt template.
            char_json (dict): The character data.
            chat_history (list): The chat history.
            memory (str): The memory summary.
            username (str): The name of the user.
            retrieved_lore (str): The retrieved lorebook content.
        
        Returns:
            list: The formatted prompt for the LLM.
        '''
        formatted_prompt = []
        system_prompt = self.format_system_prompt(system_prompt, char_json, chat_history, memory, username, retrieved_lore)
        formatted_prompt.append({"role": "system", "content": system_prompt})
        formatted_prompt.extend(chat_history)
        formatted_prompt.append({"role": "user", "content": user_prompt})
        return formatted_prompt

    def conversational_generator_summary(self, input_prompt):
        '''
        Generates a response from the LLM using the provided input prompt.
        
        Args:
            input_prompt (list): The formatted input prompt.
        
        Returns:
            dict: The response from the LLM.
        '''
        res = self.llm.create_chat_completion(
            messages=input_prompt,
            temperature=0.8,
            presence_penalty=0.8
        )
        return res['choices'][0]['message']

    def conversational_memory_lorebook(self, user_prompt, system_prompt, char_json, chat_history, memory="", username="user", retrieved_lore=""):
        '''
        Generates a response from the LLM, integrating the formatted prompt with memory and lorebook information.
        
        Args:
            user_prompt (str): The user's input.
            system_prompt (str): The system prompt template.
            char_json (dict): The character data.
            chat_history (list): The chat history.
            memory (str): The memory summary.
            username (str): The name of the user.
            retrieved_lore (str): The retrieved lorebook content.
        
        Returns:
            dict: The response from the LLM.
        '''
        input_prompt = self.prompt_formatter(user_prompt, system_prompt, char_json, chat_history, memory, username, retrieved_lore)
        return self.conversational_generator_summary(input_prompt)

    def monolyth_conv_memory_lorebook(self, user_prompt, system_prompt, char_json, chat_history, modelname="soliloquy-l3", memory="", username="user", retrieved_lore=""):
        '''
        Uses a different generator (monolyth_generator) to produce a response from the LLM.
        
        Args:
            user_prompt (str): The user's input.
            system_prompt (str): The system prompt template.
            char_json (dict): The character data.
            chat_history (list): The chat history.
            modelname (str): The model name for the generator.
            memory (str): The memory summary.
            username (str): The name of the user.
            retrieved_lore (str): The retrieved lorebook content.
        
        Returns:
            dict: The response from the generator.
        '''
        input_prompt = self.prompt_formatter(user_prompt, system_prompt, char_json, chat_history, memory, username, retrieved_lore)
        return monolyth_generator(input_prompt, modelname)

def select_chat_session():
    '''
    Lists all available chat sessions and allows the user to select an existing session or create a new one.
    
    Returns:
        ChatSession: The selected or created chat session.
    '''
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
    '''
    Main function that manages the chat loop. Allows the user to select or create a chat session.
    Loads character data and system prompt. Continuously processes user input, generates responses,
    and updates the chat history. Handles memory management by marking and removing memory flags as needed.
    Ensures the session is saved and can be resumed later.
    
    Args:
        model_path (str): The path to the LLM model.
        n_ctx (int): The context size for the LLM.
    '''
    chat_session = select_chat_session()
    if not chat_session:
        char_name = input("Enter the character name: ")
        chat_name = input("Enter the chat session name: ")
        chat_session = ChatSession(char_name, chat_name)
        chat_session.initialize_session_file()
    char_json = chat_session.load_character_data()
    system_prompt_template = chat_session.load_system_prompt()

    chat_bot = ChatBot(model_path, n_ctx)

    lorebook = char_json['lorebook']
    activate_words, lore_list = lorebook['activate_words'], lorebook['lore_list']
    retrieved_lore = hybrid_lorebook_pulling(chat_history=chat_session.history[-4:], lorebook=lore_list, activation_words=activate_words)

    try:
        while True:
            user_input = input("You: ")
            memory, chat_session.history = supa_memory(chat_session, user_input, token_limit=chat_bot.token_limit, user_name="User", model_type="llama3", system_prompt_template=system_prompt_template, char_json=char_json, chat_history=chat_session.history, memory=chat_session.memory, retrieved_lore=retrieved_lore)
            effective_history = chat_session.get_effective_history()
            system_prompt = chat_bot.format_system_prompt(system_prompt_template, char_json, effective_history, memory, "User", retrieved_lore)
            response = chat_bot.conversational_memory_lorebook(
                user_prompt=user_input,
                system_prompt=system_prompt,
                char_json=char_json,
                chat_history=effective_history,
                memory=memory,
                username="User",
                retrieved_lore=retrieved_lore
            )
            print("AI:", response['content'])
            current_chat = [{"role": "user", "content": user_input}, response]
            chat_session.append_chat_history(current_chat)
    except KeyboardInterrupt:
        print(f"Chat stopped for session: {chat_session.session_id}")

# Main entry point
if __name__ == "__main__":
    model_path = "./models/Llama-3-Soliloquy-8B-v2.Q4_K_M.gguf"
    n_ctx = 8192  # Ensure this matches the token limit
    chat_loop(model_path, n_ctx)
