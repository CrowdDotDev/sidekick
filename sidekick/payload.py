# -*- coding: utf-8 -*-

import datetime
from typing import Any, Dict, List, Union

import sidekick.tools as T


class Payload(dict):
    def __init__(self,
                 body: str,
                 source_unit_id: str = None,
                 uri: str = None,
                 headings: List[str] = None,
                 platform: str = '',
                 timestamp: Union[datetime.datetime, str] = None,
                 metadata: Dict[str, Any] = None):
        super().__init__()

        self['body'] = body
        self['source_unit_id'] = source_unit_id

        # Setter will validate
        self.uri = uri
        self.timestamp = timestamp

        self['headings'] = headings
        self['platform'] = platform
        self['metadata'] = metadata or {}

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError(f"No such attribute: {name}")

    def __setattr__(self, name, value):
        if name == 'timestamp':
            self[name] = T.timestamp_as_utc(value).isoformat()
        elif name == 'uri':
            self[name] = T.validate_uri(value)
        else:
            self[name] = value
