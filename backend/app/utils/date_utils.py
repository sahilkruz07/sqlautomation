from datetime import datetime, timedelta, timezone

def get_now_ist() -> datetime:
    """
    Returns the current time in Indian Standard Time (IST) as a naive datetime.
    This ensures MongoDB stores the literal IST time.
    """
    ist_offset = timezone(timedelta(hours=5, minutes=30))
    # Get aware IST time and then remove the timezone info to make it naive
    return datetime.now(ist_offset).replace(tzinfo=None)
