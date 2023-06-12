# -*- coding: utf-8 -*-

import mistune
from mistune.renderers.markdown import MarkdownRenderer

import sidekick.tools as T
from sidekick.payload import Payload


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
        self.chunks.append(Payload(body=text,
                                   headings=list(self.current_heading_chain)))
        return ''


def parse(file_path, uri, timestamp, platform):
    with open(file_path, 'r', encoding='utf-8') as file:
        markdown_text = file.read()

    renderer = CustomMarkdownRenderer()
    mistune.create_markdown(renderer=renderer)(markdown_text)

    out = renderer.chunks
    for chunk in out:
        chunk.source_unit_id = uri
        chunk.uri = T.append_anchor_to_uri(uri, chunk.headings)
        chunk.timestamp = timestamp
        chunk.platform = platform

    return out


def main():
    chunks = parse('res/test/local/butterfly-biology.md',
                   'file://res/test/local/butterfly-biology.md',
                   None,
                   'local:altair.local')

    from pprint import pprint
    pprint(chunks)


if __name__ == '__main__':
    main()
