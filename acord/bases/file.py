import os
import io
from typing import TYPE_CHECKING, Optional, Union, Type
import pydantic


class File(pydantic.BaseModel):
    if TYPE_CHECKING:
        fp: io.BufferedIOBase
        """ A file object or the path to the file """
        filename: str
        """ Name of file, if not given tries to read ``fp.name`` before returning ``unknown`` """
    else:
        fp: Union[str, Type[os.PathLike], io.BufferedIOBase]
        """ A file object or the path to the file """
        filename: Optional[str]
        """ Name of file, if not given tries to read ``fp.name`` before returning ``unknown`` """
    position: int = 0
    """ Position to were the file should be read from """
    spoiler: bool = False
    """ Whether the file should be marked as a spoiler """
    is_closed: bool = False
    """ Whether ``fp`` is open or closed """

    @pydantic.validator("fp")
    def _validate_fp(cls, fp, **kwargs):
        if not isinstance(fp, io.BufferedIOBase):
            fp = open(fp, "rb")
        else:
            kwargs["values"]["position"] = fp.tell()

        return fp

    @pydantic.validator('filename')
    def _validate_filename(cls, filename: Optional[str], **kwargs):
        if filename is None:
            fp: Type[io.BufferedIOBase] = kwargs["values"]["fp"]
            return getattr(fp, "name") or "unknown"
        return filename

    @pydantic.validator("spoiler")
    def _validate_spoiler(cls, spoiler, **kwargs):
        filename = kwargs["values"]["filename"]

        if filename and filename is not None and not filename.startswith("SPOILER_"):
            filename = "SPOILER_" + filename
            kwargs["values"]["filename"] = filename

        return spoiler

    def reset(self, seek: bool = False, position: int = 0) -> None:
        """ Resets a files position

        Parameters
        ----------
        seek: optional :class:`bool` = `False`
            Whether to reset position
        position: optional :class:`int` = `0`
            Optional field to seek to a specific location in file
        """
        if not seek:
            return
        self.fp.seek(position)

    def close(self) -> None:
        """ Closes the file, which prevents it from being sent again """
        self.fp.close()
        self.is_closed = True
