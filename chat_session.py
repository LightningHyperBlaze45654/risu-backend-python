import os
import json
import uuid

class ChatSession:
    '''
    Manages chat sessions, including creating, loading, and maintaining chat history and metadata.
    '''
    def __init__(self, char_name=None, chat_name=None, session_id=None):
        '''
        Initializes a ChatSession object.
        
        Args:
            char_name (str): The name of the character for the session.
            chat_name (str): The name of the chat session.
            session_id (str): The unique identifier for the session.
        '''
        if session_id:
            self.session_id = session_id
            self.load_metadata()
        else:
            self.char_name = char_name
            self.chat_name = chat_name
            self.session_id = self.create_session_id()
        self.session_file_path = self.get_session_file_path()
        self.memory_file_path = self.get_memory_file_path()
        self.history = self.get_chat_history()
        self.memory = self.get_memory()

    def create_session_id(self):
        '''
        Generates a unique identifier for the chat session.
        
        Returns:
            str: The generated session ID.
        '''
        return str(uuid.uuid4())

    def get_session_file_path(self):
        '''
        Constructs the file path for storing chat history using the session ID.
        
        Returns:
            str: The file path for the session.
        '''
        return f"./chat_history/{self.session_id}.json"

    def get_memory_file_path(self):
        '''
        Constructs the file path for storing memory summaries using the session ID.
        
        Returns:
            str: The file path for the memory file.
        '''
        return f"./chat_memory/{self.session_id}_memory.json"

    def get_metadata(self):
        '''
        Returns metadata for the chat session, including the character's name and the chat session name.
        
        Returns:
            dict: Metadata for the session.
        '''
        return {
            "char_name": self.char_name,
            "chat_name": self.chat_name
        }

    def load_metadata(self):
        '''
        Loads metadata from the session file. If the file is not found or is corrupted, default values are used.
        '''
        try:
            with open(self.get_session_file_path(), 'r') as file:
                data = json.load(file)
                metadata = data.get("metadata", {})
                self.char_name = metadata.get("char_name", "unknown")
                self.chat_name = metadata.get("chat_name", "unknown")
        except (json.JSONDecodeError, FileNotFoundError):
            self.char_name = "unknown"
            self.chat_name = "unknown"

    def get_chat_history(self):
        '''
        Loads chat history from the session file. If the file is not found or is corrupted, an empty list is returned.
        
        Returns:
            list: The chat history.
        '''
        try:
            with open(self.session_file_path, 'r') as file:
                data = json.load(file)
                history = data.get("history", [])
        except (json.JSONDecodeError, FileNotFoundError):
            history = []
        return history

    def append_chat_history(self, chat_list):
        '''
        Appends new chat entries to the existing chat history and saves it back to the session file.
        
        Args:
            chat_list (list): The list of new chat entries to append.
        '''
        try:
            with open(self.session_file_path, 'r') as file:
                data = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            data = {"metadata": self.get_metadata(), "history": []}
        data["history"].extend(chat_list)
        with open(self.session_file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def initialize_session_file(self):
        '''
        Initializes a new session file with metadata and an empty chat history. Creates directories if they do not exist.
        '''
        if not os.path.exists("./chat_history"):
            os.makedirs("./chat_history")
        if not os.path.exists("./chat_memory"):
            os.makedirs("./chat_memory")
        with open(self.session_file_path, 'w') as file:
            json.dump({"metadata": self.get_metadata(), "history": []}, file)
        with open(self.memory_file_path, 'w') as file:
            json.dump([], file)  # Initialize with empty memory

    def get_memory(self):
        '''
        Loads the memory summary from the memory file. If the file is not found or is corrupted, an empty list is returned.
        
        Returns:
            list: The memory summary.
        '''
        try:
            with open(self.memory_file_path, 'r') as file:
                memory = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            memory = []
        return memory

    def save_memory(self, memory):
        '''
        Saves the memory summary to the memory file.
        
        Args:
            memory (list): The memory summary to save.
        '''
        with open(self.memory_file_path, 'w') as file:
            json.dump(memory, file)

    def load_character_data(self):
        '''
        Loads character data from a specified file based on the character's name.
        
        Returns:
            dict: The character data.
        '''
        with open(f'./character_prompts/{self.char_name}.json', 'r', encoding='utf-8') as file:
            return json.load(file)

    def load_system_prompt(self):
        '''
        Loads the system prompt from a specified file.
        
        Returns:
            str: The system prompt.
        '''
        with open('./system_prompts/pingpong_test.txt', 'r', encoding='utf-8') as file:
            return file.read()

    def mark_memory_summary(self, summary, index):
        '''
        Marks the memory summary with a summary text and the index up to which the chat history has been summarized.
        
        Args:
            summary (str): The summary text.
            index (int): The index up to which the chat history has been summarized.
        '''
        self.memory.append({"summary_text": summary, "index": index})
        self.save_memory(self.memory)

    def get_effective_history(self):
        '''
        Determines the effective history by starting from the index of the last summary.
        
        Returns:
            list: The effective chat history.
        '''
        last_summary_index = 0
        if self.memory:
            last_summary_index = self.memory[-1]["index"]
        effective_history = self.history[last_summary_index:]
        return effective_history

    @staticmethod
    def list_sessions():
        '''
        Lists all existing chat sessions by reading the metadata from each session file in the chat_history directory.
        
        Returns:
            list: A list of session metadata.
        '''
        sessions = []
        if os.path.exists("./chat_history"):
            for filename in os.listdir("./chat_history"):
                if filename.endswith(".json"):
                    session_id = filename.split(".json")[0]
                    with open(f"./chat_history/{filename}", 'r') as file:
                        try:
                            data = json.load(file)
                            if isinstance(data, dict) and "metadata" in data:
                                metadata = data["metadata"]
                                sessions.append({
                                    "session_id": session_id,
                                    "char_name": metadata.get("char_name", "unknown"),
                                    "chat_name": metadata.get("chat_name", "unknown")
                                })
                        except (json.JSONDecodeError, FileNotFoundError):
                            continue
        return sessions

    @staticmethod
    def load_session(session_id):
        '''
        Loads a chat session by its session ID.
        
        Args:
            session_id (str): The session ID to load.
        
        Returns:
            ChatSession: The loaded chat session.
        '''
        return ChatSession(session_id=session_id)
