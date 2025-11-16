import pathlib
from urllib.parse import urlparse
from typing import Iterator

class Sprite:
    def __init__(self, path: str | pathlib.Path, x: int, y: int, width: int, height: int, blinking: bool = False) -> None:
        self.path = path
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.blinking = blinking


    # ======== CLASS-METHODS ========
    @classmethod
    def init_from_dict(cls, data: dict[str, str | int]):
        return cls(
            path=data["path"],  # type: ignore
            x=int(data["x"]),   # type: ignore
            y=int(data["y"]),   # type: ignore
            width=int(data["width"]),   # type: ignore
            height=int(data["height"]), # type: ignore
            blinking=bool(data.get("blinking", False))
        )


    # ======== DUNDER ========
    def __str__(self) -> str:
        return repr({
            "path": str(self.path) if isinstance(self.path, pathlib.Path) else self.path,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "pos": self.pos,
            "size": self.size,
            "blinking": self.blinking
        })

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"path={repr(str(self.path) if isinstance(self.path, pathlib.Path) else self.path)}, "
            f"x={repr(self.x)}, y={repr(self.y)}, "
            f"width={repr(self.width)}, height={repr(self.height)}, "
            f"blinking={repr(self.blinking)})"
        )

    def __iter__(self) -> Iterator[tuple[str, object]]:
        data = {
            "path": self.path,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "pos": self.pos,
            "size": self.size,
            "blinking": self.blinking
        }
        return iter(data.items())


    # ======== PROPERTIES ========
    @property
    def path(self) -> str | pathlib.Path:
        return self.__path

    @path.setter
    def path(self, new: str | pathlib.Path) -> None:
        if isinstance(new, pathlib.Path):
            self.__path = new
            return
        if isinstance(new, str):
            parsed = urlparse(new)
            if parsed.scheme in {"http", "https", "ftp", "s3"} and (parsed.netloc or parsed.path):
                self.__path = new  # url - keep as string
            else:
                self.__path = pathlib.Path(new)  # file - convert to Path
            return
        raise TypeError("path must be a str or pathlib.Path")

    @property
    def x(self) -> int:
        return self.__x
    @x.setter
    def x(self, new: int) -> None:
        if not isinstance(new, int):
            raise TypeError("x must be an integer")
        self.__x: int = new

    @property
    def y(self) -> int:
        return self.__y
    @y.setter
    def y(self, new: int) -> None:
        if not isinstance(new, int):
            raise TypeError("y must be an integer")
        self.__y: int = new

    @property
    def width(self) -> int:
        return self.__width
    @width.setter
    def width(self, new: int) -> None:
        if not isinstance(new, int):
            raise TypeError("width must be an integer")
        self.__width: int = new

    @property
    def height(self) -> int:
        return self.__height
    @height.setter
    def height(self, new: int) -> None:
        if not isinstance(new, int):
            raise TypeError("height must be an integer")
        self.__height: int = new


    # ======== DERIVATIVES ========
    @property
    def pos(self) -> tuple[int, int]:
        return self.x, self.y

    @property
    def size(self) -> tuple[int, int]:
        return self.width, self.height
