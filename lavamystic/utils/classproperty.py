from typing import Generic, Callable, TypeVar, Any, Optional, NoReturn, Type

T_co = TypeVar("T_co", covariant=True)

__all__ = (
    "classproperty"
)


class classproperty(Generic[T_co]):
    def __init__(self, fget: Callable[[Any], T_co]) -> None:
        self.fget = fget

    def __get__(self, instance: Optional[Any], owner: Type[Any]) -> T_co:
        return self.fget(owner)

    def __set__(self, instance, value) -> NoReturn:
        raise AttributeError("cannot set attribute")
