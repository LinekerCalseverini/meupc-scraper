from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class DataPoint:
    sku_hash: str
    date: int  # unix timestamp - first second of the day
    value: float

    def date_str(self) -> str:
        """
        Formats date into YYYY-MM-DD from a Unix timestamp.
        """
        # Convert the integer timestamp to a datetime object
        # Passing tz=timezone.utc prevents local machine timezone shifts
        dt = datetime.fromtimestamp(self.date, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d")
