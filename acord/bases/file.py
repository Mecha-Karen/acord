import os
import io
from typing import Optional, Union, Type
import pydantic


class File(pydantic.BaseModel):
    fp: Union[str, Type[os.PathLike], Type[io.BufferedIOBase]]
    position: Optional[int] = 0
    filename: Optional[str]
    spoiler: Optional[bool] = False
    is_closed: Optional[bool] = False

    @pydantic.validator('fp')
    def _validate_fp(cls, fp, **kwargs):
        if not isinstance(fp, io.BufferedIOBase):
            fp = open(fp, 'rb')
        else:
            kwargs['values']['position'] = fp.tell()
        
        return fp

    @pydantic.validator('spoiler')
    def _validate_spoiler(cls, spoiler, **kwargs):
        filename = kwargs['values']['filename']
        
        if filename and filename is not None and not filename.startswith('SPOILER_'):
            filename = "SPOILER_" + filename
            kwargs['values']['filename'] = filename

        return spoiler

    def reset(self, seek: Optional[bool] = False, position: Optional[int] = 0) -> None:
        if not seek:
            return
        self.fp.seek(position)

    def close(self) -> None:
        self.fp.close()
        self.is_closed = True
