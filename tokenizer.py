from transformers import PreTrainedTokenizerFast
import sentencepiece as spm
import tiktoken
from helper import format_chat_history, format_user_chat_history

sp = spm.SentencePieceProcessor()
def history_token_length(chat_history, model_type):
    formatted_history = format_chat_history(chat_history=chat_history)
    if model_type == "llama3":
        sp.load('./tokenizer/llama/llama.model')
        return len(sp.encode_as_pieces(formatted_history))
    elif model_type =="mistral":
        sp.load("./tokenizer/mistral/tokenizer.model")
        return len(sp.encode_as_pieces(formatted_history))
    elif model_type =="nai":
        sp.load("./tokenizer/nai/tokenizer.model")
        return len(sp.encode_as_pieces(formatted_history))
    elif model_type =="trin":
        sp.load("./tokenizer/trin/spiece.model")
        return len(sp.encode_as_pieces(formatted_history))
    elif model_type == "claude":
        tokenizer = PreTrainedTokenizerFast(tokenizer_file="./tokenizer/claude/claude.json")
        return len(tokenizer.tokenize(formatted_history))
    else:
        # defaults to cl100k_base, chatgpt's tokenizer
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(formatted_history))
    
def text_token_length(text, model_type):
    if model_type == "llama3":
        sp.load('./tokenizer/llama/llama.model')
        return len(sp.encode_as_pieces(text))
    elif model_type =="mistral":
        sp.load("./tokenizer/mistral/tokenizer.model")
        return len(sp.encode_as_pieces(text))
    elif model_type =="nai":
        sp.load("./tokenizer/nai/tokenizer.model")
        return len(sp.encode_as_pieces(text))
    elif model_type =="trin":
        sp.load("./tokenizer/trin/spiece.model")
        return len(sp.encode_as_pieces(text))
    elif model_type == "claude":
        tokenizer = PreTrainedTokenizerFast(tokenizer_file="./tokenizer/claude/claude.json")
        return len(tokenizer.tokenize(text))
    else:
        # defaults to cl100k_base, chatgpt's tokenizer
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

chat_history = [{'role': "system", 'content': "You are a very helpful assistant"},{'role': "user", 'content': "dududu max verstappen goes vroom"},{'role': "assistant", 'content': "erm what the sigma"},{'role': "user", 'content': "L to you Chatgpt"},]

# TODO: add multimodal tokenizing support, but idk how. HELP
import time

def loop(model_type):
    if model_type.lower() not in ["llama3", "mistral", "nai", "trin", "claude", "other"]:
        print("Invalid model type. Please enter a valid model type from the list: llama3, mistral, nai, trin, claude, other.")
        return

    print(f"Model selected: {model_type}. Type 'exit' to stop.")

    while True:
        # Get user input for text
        text = input("Enter your text: ")
        if text.lower() == 'exit':
            print("Exiting the program.")
            break

        # Measure the time taken to tokenize the text
        start_time = time.time()
        token_length = text_token_length(text, model_type)
        elapsed_time = time.time() - start_time

        print(f"Number of tokens in the provided text: {token_length}")
        print(f"Time taken for tokenization: {elapsed_time:.8f} seconds")

# Example usage
model_type = input("Enter the model type to use: ")
loop(model_type)