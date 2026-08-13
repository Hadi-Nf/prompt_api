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

@app.put("/prompts/{prompt_id}")
def update_prompt(prompt_id : int, updated_prompt : Prompt_Input):
    prompts = load_prompts()
    for prompt in prompts:
        if prompt['id'] == prompt_id:
            prompt['text'] = updated_prompt.text
            save_prompts(prompts)
            return{"message" : f"the prompt in prompt ID '{prompt['id']}' has been updated to the following:\n {prompt['text']}"}
    return{"error" : f"Prompt with an ID of '{prompt_id}' could not be found"}
@app.delete("/prompts/{prompt_id}")
def delete_prompt(prompt_id : int):
    prompts = load_prompts()
    for prompt in prompts:
        if prompt['id'] == prompt_id:
            prompts.remove(prompt)
            for remaining_prompt in prompts:
                if remaining_prompt['id'] > prompt_id:
                        remaining_prompt['id'] -= 1
            save_prompts(prompts)
            return{"message" : f"Prompt with ID '{prompt['id']}' and text '{prompt['text']}' has been removed"}
    return{"error" : f"Prompt with an ID of '{prompt_id}' could not be found"}

    