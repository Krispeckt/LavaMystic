from types import SimpleNamespace
from typing import Any, Iterator

__all__ = (
    "Namespace",
    "ExtrasNamespace",
)


class Namespace(SimpleNamespace):
    def __iter__(self) -> Iterator[tuple[str, Any]]:
        return iter(self.__dict__.items())


class ExtrasNamespace(Namespace):
    """A subclass of :class:`types.SimpleNameSpace`.

    You can construct this namespace with a :class:`dict` of `str` keys and `Any` value, or with keyword pairs or
    with a mix of both.

    You can access a dict version of this namespace by calling `dict()` on an instance.


    Examples
    --------

        .. code:: python

            ns: ExtrasNamespace = ExtrasNamespace({"hello": "world!"}, stuff=1)

            # Later...
            print(ns.hello)
            print(ns.stuff)
            print(dict(ns))
    """

    def __init__(self, __dict: dict[str, Any] = {}, /, **kwargs: Any) -> None:
        updated = __dict | kwargs
        super().__init__(**updated)
