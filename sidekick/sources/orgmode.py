# -*- coding: utf-8 -*-

import re

from sidekick.sources import combine_headings


def parse(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        org_lines = file.readlines()

    current_heading_chain = []
    current_text = []
    chunks = []

    for line in org_lines:
        heading_match = re.match(r'(\*+)\s(.+)', line)
        if heading_match:
            level = len(heading_match.group(1))
            heading = heading_match.group(2).strip()

            # If there's text accumulated, save it as a new chunk
            text_so_far = ' '.join(current_text).strip()
            if text_so_far:
                chunks.append({
                    'headings': list(current_heading_chain),
                    'text': text_so_far
                })
                current_text = []

            # Adjust the current heading chain to match the new level and heading
            current_heading_chain = current_heading_chain[:level - 1]
            current_heading_chain.append(heading)
        else:
            current_text.append(line.strip())

    # Don't forget the last chunk
    if current_text:
        chunks.append({
            'headings': list(current_heading_chain),
            'text': ' '.join(current_text).strip()
        })

    return [combine_headings(**chunk) for chunk in  chunks]
