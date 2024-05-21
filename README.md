# Risu-backend-python
Inspired by local/multiple API supporting roleplay frontend, RisuAI(https://github.com/kwaroran/RisuAI), but found out that it has some issues with it.

This project is to completely move all functionalities of RisuAI to a single backend, making it easy to connect with frontend. 
After finishing some functions, I will also make a python based frontend for easy testing. At that point the project will be seperated to different purposes.

please add ideas to the discussion if you have anything wanted to be implemented on this that are not in the todo list.


## Update logs
v0.0.1 (2024/5/15)
 - improved python files readability and ease of use.
 - Automatically formats system prompt with given character card(json)
 - Both monolyth and llama-cpp-python exists(doesn't have chat_loop on monolyth API)
 - Has summary, chat based retrieval functions inside(not used yet)
hotfix on 2024/5/16

v0.0.2 (2024/05/18)
 - added supamemory
 - added tokenizer for models
 - need few updates to stabilize and etc.
 - found out that the model over-simplifies - maybe summarize more frequently?


TODO:
- [X] Add supa memory 
- [ ] Add hypa memory 
- [ ] Add hanurai memory
- [ ] Add new memory system, which no one has tried yet
- [X] Add chat session functions
- [ ] Add Claude, OpenAI, Gemini, Openrouter API and Custom(OpenAI compatible) API support 
- [ ] Add exllamav2, TensorRT-LLM support for local 
- [ ] Add regular expression 
- [ ] Add chat history manipulating function while on chat loop 
- [ ] Add character card creating functions
- [ ] Create a frontend(required for better testing) 
- [ ] Add DB for both chat history or vectorDB management that could be used on any chatbot service
