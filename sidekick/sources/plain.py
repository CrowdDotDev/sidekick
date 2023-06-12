# -*- coding: utf-8 -*-

from sidekick.payload import Payload


def parse(file_path, uri, timestamp, platform):
    """Plain text files return a single chunk, it will be further
    chunked during embedding if required.
    """
    with open(file_path, 'r', encoding='utf-8') as fin:
        return [Payload(body=fin.read(),
                        source_unit_id=uri,
                        uri=uri,
                        headings=[],
                        platform=platform,
                        timestamp=timestamp)]
