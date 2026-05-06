from pathlib import Path
from typing import Optional, Union

from .run_output_file import RunOutputFile


class MetadataFile(RunOutputFile):
    DEFAULT_FILENAME = "METADATA"
    EXT = ".meta.json"

    def __init__(
        self,
        output_dir: Union[str, Path],
        filename: str = DEFAULT_FILENAME,
        data: Optional[dict] = None,
        save_every_set: bool = True,
        **kwargs,
    ):
        super().__init__(
            output_dir=output_dir,  # type: ignore
            filename=filename,
            ext=self.EXT,
            data=data,
            save_every_set=save_every_set,
            **kwargs,
        )
