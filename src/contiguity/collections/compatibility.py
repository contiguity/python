from typing_extensions import deprecated

from .async_collection import AsyncCollection
from .collection import Collection
from .common import ItemT


@deprecated("This class has been renamed to `Collection` and will be removed in a future release.")
class Base(Collection[ItemT]):
    pass


@deprecated("This class has been renamed to `AsyncCollection` and will be removed in a future release.")
class AsyncBase(AsyncCollection[ItemT]):
    pass
