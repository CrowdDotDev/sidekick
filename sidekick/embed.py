# -*- coding: utf-8 -*-

import re
import uuid

from qdrant_client.models import PointStruct

import tiktoken

from numpy import array, average

from sidekick import Config
from sidekick.apis.oai import get_embeddings
from sidekick.apis.qdrant import get_qdrant_client

C = Config['openai']


# Split a text into smaller chunks of size n, preferably ending at the
# end of a paragraph or, if no end of paragraph is found, a sentence.
def chunks(text, n, tokenizer):
    """Yield successive n-sized chunks from text."""
    tokens = tokenizer.encode(re.sub(r'[ \t]+', ' ', text))
    i = 0
    while i < len(tokens):
        # Find the nearest end of paragraph within a range of 0.5 * n and 1.5 * n tokens
        j = min(i + int(1.5 * n), len(tokens))
        while j > i + int(0.5 * n):
            # Decode the tokens and check for full stop or newline
            chunk = tokenizer.decode(tokens[i:j])
            if chunk.endswith("\n"):
                break
            j -= 1

        # If no end of paragraph found, try to find end of sentence
        if j == i + int(0.5 * n):
            j = min(i + int(1.5 * n), len(tokens))
            while j > i + int(0.5 * n):
                # Decode the tokens and check for full stop or newline
                chunk = tokenizer.decode(tokens[i:j])
                if chunk.endswith("."):
                    break
                j -= 1

        # If no end of sentence found, use n tokens as the chunk size
        if j == i + int(0.5 * n):
            j = min(i + n, len(tokens))
        yield tokens[i:j], tokenizer.decode(tokens[i:j])
        i = j


def get_col_average_from_list_of_lists(list_of_lists):
    """Return the average of each column in a list of lists."""
    if len(list_of_lists) == 1:
        return list_of_lists[0]

    list_of_lists_array = array(list_of_lists)
    average_embedding = average(list_of_lists_array, axis=0)
    return average_embedding.tolist()


def create_embeddings(text, tokenizer=None):
    """Return a list of tuples (text_chunk, embedding) and an average
    embedding for a text."""
    tokenizer = tokenizer or tiktoken.get_encoding(C['OAI_EMBEDDING_ENCODING'])

    # Should just return the number of tokens and the text chunks
    token_chunks, text_chunks = list(zip(*chunks(re.sub('\n+','\n', text),
                                                 C['OAI_EMBEDDING_CHUNK_SIZE'],
                                                 tokenizer)))

    # Split text_chunks into shorter arrays of max length 100
    text_chunks_arrays = [text_chunks[i:i+C['OAI_MAX_TEXTS_TO_EMBED_BATCH_SIZE']]
                          for i in range(0, len(text_chunks),
                                         C['OAI_MAX_TEXTS_TO_EMBED_BATCH_SIZE'])]

    # Call get_embeddings for each shorter array and combine the results
    embeddings = []
    for text_chunks_array in text_chunks_arrays:
        embeddings += get_embeddings(text_chunks_array)

    text_embeddings = [{'text': t,
                        'embedding': e}
                       for t, e in (zip(text_chunks, embeddings))]

    if len(text_embeddings) > 1:
        total_tokens = sum(len(chunk) for chunk in token_chunks)
        if total_tokens >= C['OAI_EMBEDDING_CTX_LENGTH']:
            average_embedding = get_col_average_from_list_of_lists(embeddings)
        else:
            average_embedding = get_embeddings(['\n\n'.join(text_chunks)])[0]
        text_embeddings.append({'text': text,
                                'embedding': average_embedding})

    return text_embeddings


def make_id(source_unit_id, text):
    return str(uuid.uuid5(uuid.NAMESPACE_X500, source_unit_id + text))


def embed(text, source_unit_id):
    """The source_unit_id is the id of the atomic source unit. If the
    source is notion, for example, the atomic source unit is the
    document, and the source_unit_id would be the document id. If the
    source is local the source unit is the file (in most cases) and
    the source unit id will be the file name.
    """
    Cq = Config['qdrant']
    q_client = get_qdrant_client()

    text_embeddings = create_embeddings(text)
    q_client.upsert(
        collection_name=Cq['QDRANT_COLLECTION'],
        points=[PointStruct(id=make_id(source_unit_id, t_e['text']),
                            vector=t_e['embedding'],
                            payload={Cq['QDRANT_SUID_FIELD']: source_unit_id,
                                     Cq['QDRANT_TEXT_FIELD']: t_e['text']})
                for t_e in text_embeddings])

    return text_embeddings
