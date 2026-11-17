from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class Pagination:
    limit: int
    offset: int
    total: int

    def to_payload(self) -> dict:
        return {**asdict(self), "has_more": self.offset + self.limit < self.total}
