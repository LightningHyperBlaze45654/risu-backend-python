from transformers import PreTrainedTokenizerFast
import sentencepiece as spm
from helper import format_chat_history, format_user_chat_history
# Path to your JSON file
json_file_path = 'path_to_your_tokenizer.json'

# Load the tokenizer
tokenizer = PreTrainedTokenizerFast(tokenizer_file=json_file_path)

# Example usage
text = "Hello, world! How are you doing today?"
tokens = tokenizer.tokenize(text)
token_count = len(tokens)

print("Tokens:", tokens)
print("Number of tokens:", token_count)

sp = spm.SentencePieceProcessor()
sp.load('your_model.model')

# Example text
text = "This is an example sentence."

# Tokenize text
tokens = sp.encode_as_pieces(text)
print("Tokenized:", tokens)

def token_length(chat_history):
    return#int
    