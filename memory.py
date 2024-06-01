from helper import summarize_history
from tokenizer import history_token_length, text_token_length
from chat_session import ChatSession

def periodic_summary(chat_session, token_threshold, user_name, model_type, system_prompt_template, char_json, chat_history, memory, retrieved_lore):
    '''
    Summarizes the chat history periodically based on the given token threshold.
    
    Args:
        chat_session (ChatSession): The chat session object.
        token_threshold (int): The token threshold for periodic summarization.
        user_name (str): The name of the user.
        model_type (str): The type of the model.
        system_prompt_template (str): The template for the system prompt.
        char_json (dict): The character data.
        chat_history (list): The chat history.
        memory (list): The memory summary.
        retrieved_lore (str): The retrieved lorebook content.
        
    Returns:
        list: The updated memory summary.
    '''
    current_token_length = history_token_length(chat_history=chat_history, model_type=model_type)
    if current_token_length >= token_threshold:
        summarized_history = summarize_history(user_name=user_name, chat_history=chat_history)
        summary_text = summarized_history[0]["summary_text"] if summarized_history else ""
        chat_session.mark_memory_summary(summary_text, len(chat_history))  # Mark the history with a summary indicator
        memory.append({"summary_text": summary_text, "index": len(chat_history)})
        chat_history = []
    return memory, chat_history

def supa_memory(chat_session, user_input, token_limit, user_name, model_type, system_prompt_template, char_json, chat_history, memory, retrieved_lore, summary_threshold=1000):
    '''
    Manages memory by summarizing chat history when the token limit is exceeded and periodically based on a token threshold.
    
    Args:
        chat_session (ChatSession): The chat session object.
        user_input (str): The user input.
        token_limit (int): The maximum number of tokens.
        user_name (str): The name of the user.
        model_type (str): The type of the model.
        system_prompt_template (str): The template for the system prompt.
        char_json (dict): The character data.
        chat_history (list): The chat history.
        memory (list): The memory summary.
        retrieved_lore (str): The retrieved lorebook content.
        summary_threshold (int): The token threshold for periodic summarization.
        
    Returns:
        tuple: A tuple containing the summary text and the new chat history.
    '''
    # Periodic summarization
    memory, chat_history = periodic_summary(chat_session, summary_threshold, user_name, model_type, system_prompt_template, char_json, chat_history, memory, retrieved_lore)

    system_prompt = system_prompt_template.format(char=char_json["char"], user=user_name, char_desc=char_json["char_desc"], memory=memory, lorebook=retrieved_lore)
    system_prompt_length = text_token_length(system_prompt, model_type=model_type)
    current_total_length = history_token_length(chat_history=chat_history, model_type=model_type) + text_token_length(user_input, model_type=model_type) + system_prompt_length

    if current_total_length >= (token_limit - len(chat_history) * 3):  # added this for eos related tokens       
        summarized_history = summarize_history(user_name=user_name, chat_history=chat_history)
        summary_text = summarized_history[0]["summary_text"] if summarized_history else ""
        chat_session.mark_memory_summary(summary_text, len(chat_history))  # Mark the history with a summary indicator
        return summary_text, []  # This empty list is new chat_history. It's empty, change the value of memory
    else:
        return "", chat_history  # Not needed to be summarized at all. No memory returned, chat_history is as it was before.

def hypa_memory():
    '''
    Placeholder for another memory management function.
    '''
    return

def hanurai_memory():
    '''
    Placeholder for another memory management function.
    '''
    return
