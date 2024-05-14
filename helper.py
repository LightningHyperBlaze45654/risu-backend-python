import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel, pipeline, AutoModelForSequenceClassification

def hybrid_lorebook_pulling(chat_history=[], lorebook=[], activation_words=[], prob_threshold=0.2):
    try:
        tokenizer = AutoTokenizer.from_pretrained('nvidia/dragon-multiturn-query-encoder')
        query_encoder = AutoModel.from_pretrained('nvidia/dragon-multiturn-query-encoder')
        context_encoder = AutoModel.from_pretrained('nvidia/dragon-multiturn-context-encoder')
        
        formatted_query = '\n'.join([f"{turn['role']}: {turn['content']}" for turn in chat_history]).strip()
        
        query_input = tokenizer(formatted_query, return_tensors='pt')
        ctx_input = tokenizer(lorebook, padding=True, truncation=True, max_length=512, return_tensors='pt')
        query_emb = query_encoder(**query_input).last_hidden_state[:, 0, :]
        ctx_emb = context_encoder(**ctx_input).last_hidden_state[:, 0, :]
        
        similarities = query_emb.matmul(ctx_emb.transpose(0, 1))
        softmax_values = F.softmax(similarities, dim=-1).squeeze()
        
        relevant_docs_indices = (softmax_values > prob_threshold).nonzero(as_tuple=True)[0].tolist()
        relevant_docs = {lorebook[i]: softmax_values[i].item() for i in relevant_docs_indices}
        
        word_based_docs = {}
        for doc in lorebook:
            if any(any(word.lower() in doc.lower() for word in sublist) for sublist in activation_words):
                word_based_docs[doc] = "Activation Word Match"
        
        merged_docs = {**word_based_docs, **relevant_docs}
        
        result_list = list(merged_docs.keys())
        if not result_list:
            return "No additional information"
        
        return '\n'.join(result_list)
    
    except IndexError:
        return "No additional information"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "No additional information"

'''
# Run the function and print the results
docs = hybrid_lorebook_pulling_dragon(chat_history=chat_history, lorebook=lorebook, activation_words=activation_words, prob_threshold=0.2)
print("Unified List of Documents:")
for doc in docs:
    print(doc)'''

def summary(user_name, chat_history):
    formatted_query = '\n'.join([f"{user_name if turn['role'] == 'user' else turn['role']}: {turn['content']}" for turn in chat_history]).strip()
    chatsum = pipeline("summarization", model="KoalaAI/ChatSum-Large")
    return(chatsum(formatted_query))

'''
PULLING OUT INFORMATION WITH SEPERATE MODERATOR IS NOT WORKING
MAKE THE LLM GENERATE THOSE INFORMATIONS
only use sentiment analysis :(
'''
def emotion_pull(text):
    model = AutoModelForSequenceClassification.from_pretrained('jitesh/emotion-english')
    classifier = pipeline("text-classification", model=model, tokenizer='jitesh/emotion-english')
    prediction = classifier(text)
    return(prediction[0]['label'])

