# -*- coding: utf-8 -*-


from sidekick import Config
from sidekick.apis import oai, qdrant


def format_context(ctx):
    ctx_list = ['```']
    for field in ('uri', 'timestamp', 'title', 'source'):
        if field in ctx:
            ctx_list.append(field + ': ' + ctx[field])
    ctx_list.append('content: ' + ctx['text'])
    ctx_list.append('```')

    return '\n'.join(ctx_list)


def process_question(question):
    with open(Config['openai']['OAI_SYSTEM_PROMPT'], encoding='utf-8') as fin:
        system_prompt = fin.read()

    all_context = qdrant.search(oai.get_embeddings([question])[0])

    user_prompt = '\n\n'.join(['# Context:',
                               '\n'.join([format_context(ctx) for ctx in all_context]),
                               '# Question',
                               question])

    answer = oai.ask_question(system_prompt, user_prompt)
    return answer


if __name__ == '__main__':
    import sys
    question = sys.argv[1]
    print(process_question(question))
