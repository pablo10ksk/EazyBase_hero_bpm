from datetime import date, datetime


class Utils:
    @staticmethod
    def try_parse_date(s: str) -> str | date:
        # Try ISO format parsing
        try:
            return date.fromisoformat(s)
        except ValueError:
            pass  # Not in ISO format
        try:
            return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            pass
        # Try custom timestamp format
        try:
            if len(s) == 17:
                # Parse up to seconds
                datetime_part = datetime.strptime(s[:14], "%Y%m%d%H%M%S")
                # Parse milliseconds
                milliseconds = int(s[14:])
                # Return combined date with microseconds
                final_datetime = datetime_part.replace(microsecond=milliseconds * 1000)
                return final_datetime.date()
        except (ValueError, IndexError):
            pass  # Not in the expected custom format

        # If all parsing fails, return the original string
        return s
