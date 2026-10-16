from fastapi import FastAPI
import os
import requests
from dotenv import load_dotenv
import json
from pydantic import BaseModel

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

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

@app.post("/prompts/{prompt_id}/run")
def run_prompt(prompt_id: int):
    prompts = load_prompts()
    for prompt in prompts:
        if prompt['id'] == prompt_id:
            prompt_text = prompt['text']
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={API_KEY}"
            headers = {'Content-Type': 'application/json'}
            data = {"contents": [{"parts":[{"text": prompt_text}]}]}
            try:
                response = requests.post(url, headers= headers, json=data)
                response.raise_for_status()
                full_response = response.json()
                AI_response = full_response['candidates'][0]['content']['parts'][0]['text']
                return{"ai_response" : AI_response}
            except requests.exceptions.RequestException as e:
                return{"error" : str(e)}
            except (KeyError, IndexError): 
                return{"error" : f"\n[!] Error: The AI returned an unexpected format. It may have been blocked by safety filters. Raw response for debugging:, {full_response}, \n"}
    return{"error" : f"Prompt with an ID of '{prompt_id}' could not be found"}