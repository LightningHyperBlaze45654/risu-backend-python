import os
import json
import uuid

class ChatSession:
    MEMORY_FLAG = "[MEMORY FLAG]"

    def __init__(self, char_name, user_name):
        self.char_name = char_name
        self.user_name = user_name
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

    def get_chat_history(self):
        try:
            with open(self.session_file_path, 'r') as file:
                history = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            history = []
        return history

    def append_chat_history(self, chat_list):
        try:
            with open(self.session_file_path, 'r') as file:
                data = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            data = []
        data.extend(chat_list)
        with open(self.session_file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def initialize_session_file(self):
        if not os.path.exists("./chat_history"):
            os.makedirs("./chat_history")
        if not os.path.exists("./chat_memory"):
            os.makedirs("./chat_memory")
        with open(self.session_file_path, 'w') as file:
            json.dump([], file)
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
