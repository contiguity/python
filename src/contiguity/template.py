from pathlib import Path
from typing import NoReturn


class Template:
    def local(self, file_path: "Path | str") -> str:
        try:
            file_path = Path(file_path)
            return file_path.read_text()
        except OSError as exc:
            msg = "reading files is not supported in the this environment"
            raise ValueError(msg) from exc

    async def online(self, file_path: str) -> NoReturn:
        # Coming soon
        raise NotImplementedError
