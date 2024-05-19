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