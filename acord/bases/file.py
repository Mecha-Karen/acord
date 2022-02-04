import io
from typing import Optional, Union
import pydantic


class File(pydantic.BaseModel):
    fp: io.BufferedIOBase
    """ A file like object or the path to the file """
    position: Optional[int] = 0
    """ Position to were the file should be read from """
    filename: Optional[str]
    """ Name of file, if not given tries to read ``fp.name`` before returning ``unknown`` """
    spoiler: Optional[bool] = False
    """ Whether the file should be marked as a spoiler """
    is_closed: Optional[bool] = False
    """ Whether ``fp`` is open or closed """

    @pydantic.validator("fp", pre=True)
    def _validate_fp(cls, fp):
        if not isinstance(fp, io.BufferedIOBase):
            fp = open(fp, "rb")

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

    def reset(self, seek: Optional[bool] = False, position: int = 0) -> None:
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

    def read(self) -> Union[bytes, str]:
        """Reads file from start and closes it

        Parameters
        ----------
        position: :class:`int`
            change were to read file from
        """
        data = self.fp.read()

        return data

    def close(self) -> None:
        """Closes the file, which prevents it from being sent again"""
        self.fp.close()
        self.is_closed = True
