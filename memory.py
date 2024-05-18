from helper import format_chat_history, format_user_chat_history
from helper import summarize_history, embed_chat_history_dragon, embed_context_dragon, max_token_retrieve
from tokenizer import history_token_length, text_token_length
def supa_memory(chat_history, user_input, token_limit, user_name, model_type):
    '''
    model type: llama3, mistral, nai, trin, claude, chatgpt. if the model type is unrecognized, defaults to chatgpt
    '''
    current_total_length = history_token_length(chat_history=chat_history, model_type=model_type) + text_token_length(user_input, model_type=model_type)
    if current_total_length >= (token_limit - len(chat_history)*3): #added this for eos related tokens       
        summarized_history = summarize_history(user_name=user_name, chat_history=chat_history)
        return summarized_history, []#this empty list is new chat_history. it's empty, change the value of memory
    else:
        return "", chat_history # Not needed to be summarized at all. No memory returned, chat_history is as it was before.
    
def hypa_memory():
    return
def hanurai_memory():
    return