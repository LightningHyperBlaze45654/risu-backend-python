import os
import json
import uuid

class ChatSession:
    MEMORY_FLAG = "[MEMORY FLAG]"

    def __init__(self, char_name=None, chat_name=None, session_id=None):
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
        return str(uuid.uuid4())

    def get_session_file_path(self):
        return f"./chat_history/{self.session_id}.json"

    def get_memory_file_path(self):
        return f"./chat_memory/{self.session_id}_memory.json"

    def get_metadata(self):
        return {
            "char_name": self.char_name,
            "chat_name": self.chat_name
        }

    def load_metadata(self):
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
        try:
            with open(self.session_file_path, 'r') as file:
                data = json.load(file)
                history = data.get("history", [])
        except (json.JSONDecodeError, FileNotFoundError):
            history = []
        return history

    def append_chat_history(self, chat_list):
        try:
            with open(self.session_file_path, 'r') as file:
                data = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            data = {"metadata": self.get_metadata(), "history": []}
        data["history"].extend(chat_list)
        with open(self.session_file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def initialize_session_file(self):
        if not os.path.exists("./chat_history"):
            os.makedirs("./chat_history")
        if not os.path.exists("./chat_memory"):
            os.makedirs("./chat_memory")
        with open(self.session_file_path, 'w') as file:
            json.dump({"metadata": self.get_metadata(), "history": []}, file)
        with open(self.memory_file_path, 'w') as file:
            json.dump("", file)  # Initialize with empty memory

    def get_memory(self):
        try:
            with open(self.memory_file_path, 'r') as file:
                memory = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            memory = ""
        return memory

    def save_memory(self, memory):
        with open(self.memory_file_path, 'w') as file:
            json.dump(memory, file)

    def load_character_data(self):
        with open(f'./character_prompts/{self.char_name}.json', 'r', encoding='utf-8') as file:
            return json.load(file)

    def load_system_prompt(self):
        with open('./system_prompts/pingpong_test.txt', 'r', encoding='utf-8') as file:
            return file.read()

    def mark_memory_summary(self):
        # Remove existing memory flag if it exists
        self.history = [entry for entry in self.history if entry != self.MEMORY_FLAG]
        # Add new memory flag
        self.history.append(self.MEMORY_FLAG)
        self.save_memory(self.get_memory())

    def get_effective_history(self):
        effective_history = []
        memory_flag_found = False
        for entry in self.history:
            if entry == self.MEMORY_FLAG:
                memory_flag_found = True
            elif not memory_flag_found:
                effective_history.append(entry)
        return effective_history

    def remove_memory_flag(self):
        self.history = [entry for entry in self.history if entry != self.MEMORY_FLAG]

    @staticmethod
    def list_sessions():
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
        return ChatSession(session_id=session_id)
