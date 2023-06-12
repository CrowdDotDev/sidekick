# -*- coding: utf-8 -*-

import os
from datetime import datetime
import socket
from pytz import utc

import sidekick.tools as T
from sidekick.sources.state import State
from sidekick.embed import embed_source_unit

from sidekick.sources import markdown
from sidekick.sources import orgmode
from sidekick.sources import plain


def ingest():
    state = State()
    supported_extensions = ["md", "org", "txt", "text"]

    parsers = {
        "md": markdown.parse,
        "org": orgmode.parse,
        "txt": plain.parse,
        "text": plain.parse,
    }

    embedded_payloads = []
    source_name = 'local'
    hostname = socket.gethostname()

    # pylint: disable=too-many-nested-blocks
    for source in T.get_source_config(source_name, []):
        directory = source['directory']

        extensions = source.get('extensions', supported_extensions)
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                file_extension = os.path.splitext(filename)[-1].lower()[1:]
                if file_extension in extensions and file_extension in supported_extensions:
                    file_path = os.path.join(dirpath, filename)

                    # Check the file's last modified time in UTC
                    file_modified_dt = datetime.utcfromtimestamp(
                        os.path.getmtime(file_path)).replace(tzinfo=utc)

                    last_seen_dt = state.get_last_seen(source_name, file_path)

                    if last_seen_dt is None or file_modified_dt > last_seen_dt:
                        uri = T.file_to_uri(file_path)
                        parser = parsers[file_extension]
                        payloads = parser(file_path,
                                          uri=uri,
                                          timestamp=file_modified_dt,
                                          platform=source_name + ':' + hostname)
                        embed_source_unit(payloads,
                                          source_unit_id=file_path)
                        state.update_last_seen(source_name, file_path)
                        embedded_payloads += payloads

    return embedded_payloads


def main():
    embedded = ingest()
    print('Ingested from:')
    print('  ' + '\n  '.join([e['file_path'] for e in embedded]))

    # from pprint import pprint
    # pprint(embedded)


if __name__ == "__main__":
    main()
