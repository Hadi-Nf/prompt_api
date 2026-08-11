from fastapi import FastAPI
import json

app = FastAPI()

def load_prompts():
    try:
        with open("prompts.json", "r") as file:
            prompts = json.load(file)
            return prompts
    except FileNotFoundError:
        print("Prompt file not found! making new prompt file.")
        prompts = []
        return prompts

@app.get("/prompts")
def get_prompts():
    return{"data" : load_prompts()}