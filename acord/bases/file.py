import os
import io
from typing import Optional, Union


class File:
    def __init__(
        self, *,
        fp: Union[str, os.PathLike, io.BufferedIOBase],
        filename: Optional[str] = None,
        spoiler: Optional[bool] = False
    ):
        if not isinstance(fp, io.BufferedIOBase):
            self._fp = open(fp, 'rb')
            self._positon = 0
        else:
            self._fp = fp
            self._positon = fp.tell()
        
        self.filename = filename
        
        if spoiler and self.filename is not None and not self.filename.startswith('SPOILER_'):
            self.filename = "SPOILER_" + self.filename

    def reset(self):
        self._fp.seek(0)

    def close(self):
        self._fp.close()