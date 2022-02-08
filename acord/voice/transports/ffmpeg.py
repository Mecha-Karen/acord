# Generate a proper PCM source for .mp3 files
from __future__ import annotations
from asyncio import subprocess
import io
from typing import Union
import os
import subprocess
import logging

from .writer import BasePlayer
from acord.voice.core import VoiceConnection
from acord.voice.opus import Encoder
from acord.errors import VoiceError


logger = logging.getLogger(__name__)
__all__ = (
    "PIPED_PCM_FFMPEG_PLAYER",
    "FfmpegPlayer"
)


PIPED_PCM_FFMPEG_PLAYER = (
    '-loglevel', 'warning', 
    '-i', '-', 
    '-f', 's16le', 
    '-ar', '48000', 
    '-ac', '2', 
    'pipe:1'
)


class FfmpegPlayer(BasePlayer):
    def __init__(self, 
        conn: VoiceConnection, 
        source_file: Union[io.BufferedIOBase, os.PathLike], 
        encoder: Encoder = None,
        executable: str = "ffmpeg",
        subprocess_args: tuple = (),
        subprocess_kwds: dict = {},
        **encoder_kwds
    ) -> None:
        super().__init__(conn, source_file, encoder, **encoder_kwds)
        self.process: subprocess.Popen = None

        args = (executable, *subprocess_args)
        kwds = {"stdout": subprocess.PIPE, "stdin": subprocess.PIPE}
        kwds.update(subprocess_kwds)

        # Used for reseting state
        self._spawn_process_args = (args, kwds)

        self._spawn_proc(args, kwds)

    def _spawn_proc(self, args, kwds):
        logger.debug("Attempting to spawn ffmpeg process")
        try:
            self.process = subprocess.Popen(
                args, creationflags=subprocess.CREATE_NO_WINDOW,
                **kwds
            )
            logger.info("Sucessfully spawned ffmpeg process at %s", self.process.pid)
        except FileNotFoundError as exc:
            raise VoiceError(f"path provided for ffmpeg executable not found") from exc
        except subprocess.SubprocessError:
            raise

    def _kill_proc(self):
        if not self.process:
            return

        try:
            self.process.kill()
        except Exception:
            logger.exception(f"Failed to kill ffmpeg process at pid={self.process.pid}", exc_info=1)
        
        if self.process.poll() is None:
            logger.info('ffmpeg process at pid=%s not terminated, waiting...', self.process.pid)
            self.process.communicate()
            logger.info('ffmpeg process at pid=%s has terminated with return code %s', self.process.pid, self.process.returncode)
        else:
            logger.info('ffmpeg process at pid=%s has terminated sucessfully with return code %s', self.process.pid, self.process.returncode)

    def get_next_packet(self):
        data = super().get_next_packet()

        try:
            d, *_ = self.process.communicate(data)
        except Exception:
            logger.exception("Failed write process with ffmpeg source pid=%s. This is not always an issue", self.process.pid, exc_info=1)
            self.process.terminate()
            return

        return d

    async def cleanup(self, *, reset: bool = True) -> None:
        super().cleanup()
        self._kill_proc()

        if reset:
            self._spawn_proc(*self._spawn_process_args)
