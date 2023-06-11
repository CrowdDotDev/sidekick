# -*- coding: utf-8 -*-

import os
import openai

from tenacity import retry, wait_random_exponential
from tenacity import stop_after_attempt, retry_if_not_exception_type

from sidekick import Config, load_environment

C = Config['openai']
load_environment()
openai.api_key = os.environ.get('OPENAI_API_KEY')


@retry(wait=wait_random_exponential(min=1, max=20),
       stop=stop_after_attempt(6),
       retry=retry_if_not_exception_type(openai.InvalidRequestError))
def get_embeddings(text_or_tokens_array, model=C['OAI_EMBEDDING_MODEL']):
    return [r['embedding'] for r in
            openai.Embedding.create(input=text_or_tokens_array, model=model)["data"]]


@retry(wait=wait_random_exponential(min=1, max=20),
       stop=stop_after_attempt(6),
       retry=retry_if_not_exception_type(openai.InvalidRequestError))
def ask_question(sytem_prompt, user_prompt):
    return openai.ChatCompletion.create(
        model=C['OAI_MODEL'],
        messages=[
            {"role": "system", "content": sytem_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )["choices"][0]["message"]["content"]
