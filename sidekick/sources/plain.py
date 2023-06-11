# -*- coding: utf-8 -*-


def parse(file_path):
    """Plain text files return a single chunk, it will be further
    chunked during embedding if required.
    """
    with open(file_path, 'r', encoding='utf-8') as fin:
        return [fin.read()]
