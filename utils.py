import requests
import os
from dotenv import load_dotenv
from groq import Groq
load_dotenv()

groq_api_key = os.getenv("GROR_API_KEY")

client = Groq(api_key=groq_api_key)

# HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"   # free public model
# HF_URL = f" https://router.huggingface.co/hf-inference/models/{HF_MODEL}"

def llm_generater(prompt:str, max_tokens:int =100)->str:

    # payload = {
    #     "inputs": prompt,
    #     "parameters": {
    #         "max_tokens": max_tokens,
    #         "return_full_text": False,
    #         "do_sample": True,
    #         "temperature": 0.7
    #     }
    # }

    # try:
    #     response = requests.post(HF_URL, json=payload, timeout=60)
    #     response.raise_for_status()
    #     data = response.json()

    #     if isinstance(data,list) and "generated_text" in data[0]:
    #         return data[0]["generated_text"].strip()
        
    #     return str(data)
    # except Exception as e:
    #     return f"[LLM ERROR]: {str(e)}"

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )

        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"[LLM ERROR]: {str(e)}"