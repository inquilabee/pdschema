from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence


def compare(op: str, left: object, right: object) -> bool:
    reflected = {"__lt__": "__gt__", "__le__": "__ge__", "__gt__": "__lt__", "__ge__": "__le__"}
    for obj, name in ((left, op), (right, reflected[op])):
        method = getattr(obj, name, None)
        if method is None:
            continue
        try:
            result = method(right if obj is left else left)
        except TypeError:
            continue
        if result is not NotImplemented:
            return bool(result)
    return False


class Validator(ABC):
    @abstractmethod
    def validate(self, value: object) -> bool:
        pass

    def __call__(self, value: object) -> bool:
        return self.validate(value)

    def __str__(self) -> str:
        return type(self).__name__


class CallableValidator(Validator):
    def __init__(self, fn: Callable[[object], bool]):
        self.fn = fn

    def validate(self, value: object) -> bool:
        return bool(self.fn(value))

    def __str__(self) -> str:
        return getattr(self.fn, "__name__", type(self.fn).__name__)


class IsPositive(Validator):
    def validate(self, value: object) -> bool:
        return compare("__gt__", value, 0)


class IsNonEmptyString(Validator):
    def validate(self, value: object) -> bool:
        return isinstance(value, str) and len(value.strip()) > 0


class BoundComparison(Validator):
    def __init__(self, threshold: object, *, exclusive: bool, upper: bool):
        self.threshold = threshold
        self.exclusive = exclusive
        self.upper = upper

    def validate(self, value: object) -> bool:
        if self.upper:
            op = "__lt__" if self.exclusive else "__le__"
        else:
            op = "__gt__" if self.exclusive else "__ge__"
        return compare(op, value, self.threshold)

    def __str__(self) -> str:
        op = ("<" if self.exclusive else "<=") if self.upper else (">" if self.exclusive else ">=")
        return f"{type(self).__name__}({op} {self.threshold})"


class GreaterThan(BoundComparison):
    def __init__(self, threshold: object):
        super().__init__(threshold, exclusive=True, upper=False)


class GreaterThanOrEqual(BoundComparison):
    def __init__(self, threshold: object):
        super().__init__(threshold, exclusive=False, upper=False)


class LessThan(BoundComparison):
    def __init__(self, threshold: object):
        super().__init__(threshold, exclusive=True, upper=True)


class LessThanOrEqual(BoundComparison):
    def __init__(self, threshold: object):
        super().__init__(threshold, exclusive=False, upper=True)


class Min(GreaterThanOrEqual):
    def __init__(self, min_value: object):
        super().__init__(min_value)
        self.min_value = min_value


class Max(LessThanOrEqual):
    def __init__(self, max_value: object):
        super().__init__(max_value)
        self.max_value = max_value


class Choice(Validator):
    def __init__(self, choices: Sequence[object]):
        self.choices = frozenset(choices)

    def validate(self, value: object) -> bool:
        return value in self.choices


class Length(Validator):
    def __init__(self, min_length: int | None = None, max_length: int | None = None):
        if min_length is None and max_length is None:
            raise ValueError("At least one of min_length or max_length must be provided.")
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value: object) -> bool:
        if not isinstance(value, str | list | dict | tuple):
            return False
        length = len(value)
        if self.min_length is not None and length < self.min_length:
            return False
        if self.max_length is not None and length > self.max_length:
            return False
        return True


class Range(Validator):
    def __init__(self, min_value: object, max_value: object):
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: object) -> bool:
        return compare("__le__", self.min_value, value) and compare("__le__", value, self.max_value)
