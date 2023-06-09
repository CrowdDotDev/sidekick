import openai
import os
import dotenv


openai.api_key = os.environ.get("OPENAI_API_KEY")


def generate_embeddings(input_text):
    return openai.Embedding.create(input=input_text, model="text-embedding-ada-002")[
        "data"
    ][0]["embedding"]


def chat(sytem_prompt, user_prompt):
    return openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": sytem_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )["choices"][0]["message"]["content"]
