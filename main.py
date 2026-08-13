from fastapi import FastAPI
import json
from pydantic import BaseModel

app = FastAPI()

class Prompt_Input(BaseModel):
    text : str

def load_prompts():
    try:
        with open("prompts.json", "r") as file:
            prompts = json.load(file)
            return prompts
    except FileNotFoundError:
        print("Prompt file not found! making new prompt file.")
        prompts = []
        return prompts
    
def save_prompts(prompts_list):
    with open("prompts.json", "w") as file:
        json.dump(prompts_list, file, indent= 4)

@app.get("/prompts")
def get_prompts():
    return{"data" : load_prompts()}

@app.get("/prompts/{prompt_id}")
def get_single_prompt(prompt_id : int):
    prompts_list = load_prompts()

    for prompt in prompts_list:
        if prompt['id'] == prompt_id:
            return {"data": prompt}
    return {"error": "prompt not found!"}

@app.post("/prompts")
def create_prompt(new_prompt: Prompt_Input):  
    prompts = load_prompts()  
    new_id = len(prompts) + 1
    new_prompt_dict = {'id' : new_id, 'text' : new_prompt.text }
    prompts.append(new_prompt_dict)
    save_prompts(prompts)
    return{"message" : "added new prompt!"}

    