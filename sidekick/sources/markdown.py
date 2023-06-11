# -*- coding: utf-8 -*-

import mistune
from mistune.renderers.markdown import MarkdownRenderer

from sidekick.sources import combine_headings


class CustomMarkdownRenderer(MarkdownRenderer):
    def __init__(self):
        super().__init__()
        self.current_heading_chain = []
        self.chunks = []

    def heading(self, token, state) -> str:
        level = token['attrs']['level']
        text = self.render_children(token, state)

        self.current_heading_chain = self.current_heading_chain[:level - 1]
        self.current_heading_chain.append(text)
        return ''

    def paragraph(self, token, state) -> str:
        text = self.render_children(token, state)
        self.chunks.append(combine_headings(list(self.current_heading_chain), text))
        return ''


def parse(file_path):
    with open(file_path, 'r') as file:
        markdown_text = file.read()

    renderer = CustomMarkdownRenderer()
    mistune.create_markdown(renderer=renderer)(markdown_text)

    return renderer.chunks
