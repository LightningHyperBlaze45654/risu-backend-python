from helper import summarize_history
from tokenizer import history_token_length, text_token_length
from chat_session import ChatSession

def supa_memory(chat_session, user_input, token_limit, user_name, model_type):
    chat_history = chat_session.history
    current_total_length = history_token_length(chat_history=chat_history, model_type=model_type) + text_token_length(user_input, model_type=model_type)
    if current_total_length >= (token_limit - len(chat_history) * 3):  # added this for eos related tokens       
        summarized_history = summarize_history(user_name=user_name, chat_history=chat_history)
        chat_session.save_memory(summarized_history)  # Save the summarized history to memory
        chat_session.mark_memory_summary()  # Mark the history with a summary indicator
        return summarized_history, []  # This empty list is new chat_history. It's empty, change the value of memory
    else:
        return "", chat_history  # Not needed to be summarized at all. No memory returned, chat_history is as it was before.
    
def hypa_memory():
    return

def hanurai_memory():
    return
