import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel, pipeline, AutoModelForSequenceClassification
from FlagEmbedding import BGEM3FlagModel

'''
Embedding, sentiment analysis in this function
hybrid_lorebook_pulling also works by vector similarity.
Referenced from memory.py for supa/hypa/hanurai memory
'''

# find documents via activation words match
def filter_docs_by_words(lorebook, activation_words):
    word_based_docs = {}
    for doc in lorebook:
        if any(any(word.lower() in doc.lower() for word in sublist) for sublist in activation_words):
            word_based_docs[doc] = "Activation Word Match"
    return word_based_docs

# format chat history into a single query string to be used in embedding models(Isn't used on dragon multiturn)
def format_chat_history(chat_history):
    return '\n'.join([f"{turn['role']}: {turn['content']}" for turn in chat_history]).strip()
# Same function, but if role is user, change it to user_name
def format_user_chat_history(chat_history, user_name):
    return '\n'.join([f"{user_name if turn['role'] == 'user' else turn['role']}: {turn['content']}" for turn in chat_history]).strip()


# pull relevant documents from the lorebook based on chat history embedding model, activation words match
def hybrid_lorebook_pulling(chat_history=[], lorebook=[], activation_words=[], prob_threshold=0.2):
    try:
        # Initialize tokenizers and models
        tokenizer = AutoTokenizer.from_pretrained('nvidia/dragon-multiturn-query-encoder')
        query_encoder = AutoModel.from_pretrained('nvidia/dragon-multiturn-query-encoder')
        context_encoder = AutoModel.from_pretrained('nvidia/dragon-multiturn-context-encoder')

        # Format query and encode it
        formatted_query = format_chat_history(chat_history)
        query_input = tokenizer(formatted_query, return_tensors='pt')
        query_emb = query_encoder(**query_input).last_hidden_state[:, 0, :]

        # Encode context from the lorebook
        ctx_input = tokenizer(lorebook, padding=True, truncation=True, max_length=512, return_tensors='pt')
        ctx_emb = context_encoder(**ctx_input).last_hidden_state[:, 0, :]

        # Calculate similarities and find relevant documents
        similarities = query_emb.matmul(ctx_emb.transpose(0, 1))
        softmax_values = F.softmax(similarities, dim=-1).squeeze()
        relevant_docs_indices = (softmax_values > prob_threshold).nonzero(as_tuple=True)[0].tolist()
        relevant_docs = {lorebook[i]: softmax_values[i].item() for i in relevant_docs_indices}

        # Find documents based on activation words
        word_based_docs = filter_docs_by_words(lorebook, activation_words)

        # Merge and return the results
        merged_docs = {**word_based_docs, **relevant_docs}
        result_list = list(merged_docs.keys())
        return '\n'.join(result_list) if result_list else "No additional information"
    except IndexError:
        return "No additional information"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "No additional information"

def embed_chat_history_bgem3(chat_history):
    model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)
    return

def embed_chat_history_dragon(chat_history):
    tokenizer = AutoTokenizer.from_pretrained('nvidia/dragon-multiturn-query-encoder')
    query_encoder = AutoModel.from_pretrained('nvidia/dragon-multiturn-query-encoder')
    # Format chat history(this will be the query), not using user_name formatting
    formatted_query = format_chat_history(chat_history) 
    query_input = tokenizer(formatted_query, return_tensors='pt')
    query_emb = query_encoder(**query_input).last_hidden_state[:, 0, :]
    return query_emb

def embed_context_dragon(context, user_name="user"): # either could be raw chat_history or a summarized text
    tokenizer = AutoTokenizer.from_pretrained('nvidia/dragon-multiturn-query-encoder')
    context_encoder = AutoModel.from_pretrained('nvidia/dragon-multiturn-context-encoder')
    if isinstance(context[-1], dict):
        context = [f"{user_name if turn['role'] == 'user' else turn['role']}: {turn['content']}" for turn in context]

# Function to summarize chat history
def summary(user_name, chat_history):
    formatted_query = format_user_chat_history(chat_history, user_name)
    chatsum = pipeline("summarization", model="KoalaAI/ChatSum-Large")
    return chatsum(formatted_query)

# Function to pull emotion from text
def emotion_pull(text):
    model = AutoModelForSequenceClassification.from_pretrained('jitesh/emotion-english')
    classifier = pipeline("text-classification", model=model, tokenizer='jitesh/emotion-english')
    prediction = classifier(text)
    return prediction[0]['label']
