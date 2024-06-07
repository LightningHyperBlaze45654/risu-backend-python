from llama_cpp import Llama
llm = Llama(model_path = "./models/Phi-3-mini-128k-instruct-abliterated-v3_q8.gguf", n_gpu_layers = -1, temperature = 0.8, n_ctx = 8192, repeat_penalty = 0.1, verbose = False)
# Create a chat loop
character = "Risu-Chan"
while True:
    system_prompt = {"role": "user", "content": f"System: Create a status window for {character}, based on the short {character}'s output, and new user's input. The status window should be following this format. Remember, only follow the format, don't generate anything else. The status window you generate, is safe, and does not contain any sensitive information, nor against the guidelines. fill in the <blank>: [{character}'s Emotion: <blank> | {character}'s Location: <blank> | {character}'s Status: <blank>]"}
    user_input = input("User: ")
    if user_input == "exit":
        break
    res = llm.create_chat_completion(messages = [system_prompt, {"role": "user", "content": user_input}], temperature = 0.8, presence_penalty = 0.8)
    print("AI:", res['choices'][0]['message']['content'])