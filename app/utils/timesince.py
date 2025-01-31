from datetime import datetime, timezone


def timesince(created_at):
    """
    Returns a human-readable "time ago" string for the given datetime with
    singular/plural handling.
    :param created_at: datetime object representing the past time
    :return: str in the format 'X second/minute/hour/day/week/month/year ago'
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    ago = now - created_at

    seconds = ago.total_seconds()

    def pluralize(value, unit):
        """Returns the unit in singular or plural form based on the value."""
        return f"{value} {unit}" + ("s" if value > 1 else "")

    match seconds:
        case _ if seconds < 60:
            return f"{pluralize(int(seconds), 'second')} ago"
        case _ if seconds < 3600:
            minutes = int(seconds // 60)
            return f"{pluralize(minutes, 'minute')} ago"
        case _ if seconds < 86400:
            hours = int(seconds // 3600)
            return f"{pluralize(hours, 'hour')} ago"
        case _ if seconds < 604800:
            days = int(seconds // 86400)
            return f"{pluralize(days, 'day')} ago"
        case _ if seconds < 2592000:
            weeks = int(seconds // 604800)
            return f"{pluralize(weeks, 'week')} ago"
        case _ if seconds < 31536000:
            months = int(seconds // 2592000)
            return f"{pluralize(months, 'month')} ago"
        case _:
            years = int(seconds // 31536000)
            return f"{pluralize(years, 'year')} ago"

# Example usage:
# created_at = datetime.datetime.now() - datetime.timedelta(days=1, seconds=45)
# print(timesince(created_at))  # Output: '1 day ago'
