# Risu-backend-python
Inspired by local/multiple API supporting roleplay frontend, RisuAI(https://github.com/kwaroran/RisuAI), but found out that it has some issues with it.
This project is to completely move all functionalities of RisuAI to a single backend, making it easy to connect with frontend. 
After finishing some functions, I will also make a python based frontend for easy testing.

please add ideas to the discussion if you have anything wanted to be implemented on this that are not in the todo list.


## Update logs
v0.0.1 (2024/5/15)
 - improved python files readability and ease of use.
 - Automatically formats system prompt with given character card(json)
 - Both monolyth and llama-cpp-python exists(doesn't have chat_loop on monolyth API)
 - Has summary, chat based retrieval functions inside(not used yet)

TODO:
Add supa/hypa/hanurai memory []
Add Claude, OpenAI, Gemini, Openrouter API support []
Add exllamav2, TensorRT-LLM support for local []
Add regular expression []
Add chat history manipulating function while on chat loop []
Add character card creating functions []
Create a frontend(required for better testing) [] 
Add DB for both chat history or vectorDB []


**I hope this could be a great baseline for projects to start!**

