import os
import io
from typing import Optional, Union, Type
import pydantic


class File(pydantic.BaseModel):
    fp: Union[str, Type[os.PathLike], Type[io.BufferedIOBase]]  # type: ignore
    """ A file object or the path to the file """
    position: Optional[int] = 0
    """ Position to were the file should be read from """
    filename: Optional[str]
    """ Name of file, if not given tries to read ``fp.name`` before returning ``unknown`` """
    spoiler: Optional[bool] = False
    """ Whether the file should be marked as a spoiler """
    is_closed: Optional[bool] = False
    """ Whether ``fp`` is open or closed """

    @pydantic.validator("fp")
    def _validate_fp(cls, fp, **kwargs):
        if not isinstance(fp, io.BufferedIOBase):
            fp = open(fp, "rb")
        else:
            kwargs["values"]["position"] = fp.tell()

        return fp

    @pydantic.validator("filename")
    def _validate_filename(cls, filename, **kwargs):
        if not filename:
            fp = kwargs["values"]["fp"]
            return fp.name or "unknown"
        return filename

    @pydantic.validator("spoiler")
    def _validate_spoiler(cls, spoiler, **kwargs):
        filename = kwargs["values"]["filename"]

        if filename and filename is not None and not filename.startswith("SPOILER_"):
            filename = "SPOILER_" + filename
            kwargs["values"]["filename"] = filename

        return spoiler

    def reset(self, seek: Optional[bool] = False, position: Optional[int] = 0) -> None:
        """Resets a files position

        Parameters
        ----------
        seek: :class:`bool`
            Whether to reset position
        position: :class:`int`
            Optional field to seek to a specific location in file
        """
        if not seek:
            return
        self.fp.seek(position)

    def read_and_close(self, *, position: int = 0, decode: bool = False):
        """Reads file from start and closes it

        Parameters
        ----------
        position: :class:`int`
            change were to read file from
        """
        self.reset(True, position)

        data = self.fp.read()
        if decode:
            data = data.decode()

        self.close()
        return data

    def close(self) -> None:
        """Closes the file, which prevents it from being sent again"""
        self.fp.close()
        self.is_closed = True
