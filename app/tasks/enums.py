from enum import StrEnum


class TaskStatus(StrEnum):
    INITIATED: str = "INITIATED"
    IN_PROGRESS: str = "IN_PROGRESS"
    FAILED: str = "FAILED"
    COMPLETED: str = "COMPLETED"


class TaskType(StrEnum):
    TICKER_CREATOR: str = "TICKER_CREATOR"
    TICKER_PRICE_FETCHER: str = "TICKER_PRICE_FETCHER"
    INDEX_CREATOR: str = "INDEX_CREATOR"
