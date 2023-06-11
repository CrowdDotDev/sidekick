# -*- coding: utf-8 -*-

import os
from datetime import datetime
from pytz import utc

from sidekick.sources.state import State
from sidekick.embed import embed
from sidekick.apis import qdrant

from sidekick.sources import SourceConfig
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

    embedded = []
    source_name = 'local'
    # pylint: disable=too-many-nested-blocks
    for source in SourceConfig.get(source_name, []):
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
                        parser = parsers[file_extension]
                        chunks = parser(file_path)
                        text_embeddings = []
                        qdrant.clean_source_unit(source_unit_id=file_path)
                        for chunk in chunks:
                            text_embeddings += embed(chunk, source_unit_id=file_path)
                        embedded.append({'file_path': file_path,
                                         'texts': [t_e['text']
                                                   for t_e in text_embeddings]})

                    state.update_last_seen(source_name, file_path)

    return embedded


def main():
    embedded = ingest()
    print('Ingested from:')
    print('  ' + '\n  '.join([e['file_path'] for e in embedded]))

    # from pprint import pprint
    # pprint(embedded)


if __name__ == "__main__":
    main()
