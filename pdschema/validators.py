from abc import ABC, abstractmethod


class Validator(ABC):
    @abstractmethod
    def validate(self, value) -> bool:
        pass

    def __call__(self, value) -> bool:
        return self.validate(value)


class IsPositive(Validator):
    def validate(self, value) -> bool:
        return value > 0


class IsNonEmptyString(Validator):
    def validate(self, value) -> bool:
        return isinstance(value, str) and len(value.strip()) > 0


class Max(Validator):
    def __init__(self, max_value):
        self.max_value = max_value

    def validate(self, value) -> bool:
        return value <= self.max_value


class Min(Validator):
    def __init__(self, min_value):
        self.min_value = min_value

    def validate(self, value) -> bool:
        return value >= self.min_value


class GreaterThan(Validator):
    def __init__(self, threshold):
        self.threshold = threshold

    def validate(self, value) -> bool:
        return value > self.threshold


class GreaterThanOrEqual(Validator):
    def __init__(self, threshold):
        self.threshold = threshold

    def validate(self, value) -> bool:
        return value >= self.threshold


class LessThan(Validator):
    def __init__(self, threshold):
        self.threshold = threshold

    def validate(self, value) -> bool:
        return value < self.threshold


class LessThanOrEqual(Validator):
    def __init__(self, threshold):
        self.threshold = threshold

    def validate(self, value) -> bool:
        return value <= self.threshold


class Choice(Validator):
    def __init__(self, choices: list):
        self.choices = choices

    def validate(self, value) -> bool:
        return value in self.choices


class Length(Validator):
    def __init__(self, min_length: int | None = None, max_length: int | None = None):
        if min_length is None and max_length is None:
            raise ValueError(
                "At least one of min_length or max_length must be provided."
            )
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value) -> bool:
        if not isinstance(value, str | list | dict | tuple):
            return False

        length = len(value)

        if self.min_length is not None and length < self.min_length:
            return False
        if self.max_length is not None and length > self.max_length:
            return False
        return True


class Range(Validator):
    def __init__(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value) -> bool:
        return self.min_value <= value <= self.max_value
