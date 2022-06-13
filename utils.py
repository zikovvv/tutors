import datetime
import traceback


def current_time():
    return clear_tzinfo(datetime.datetime.now(datetime.timezone.utc))

def clear_tzinfo(date : datetime.datetime) :
    return date.replace(tzinfo = None)

def last_exception(limit = 4000):
    return traceback.format_exc()[:limit]
