from datetime import datetime, timedelta


def get_unix_timestamps(fixed_hours):
    print(fixed_hours)
    now = datetime.utcnow()
    timestamps = []
    for hour in fixed_hours:
        future_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if hour < now.hour:
            future_time += timedelta(days=1)
        unix_timestamp = int(future_time.timestamp())
        timestamps.append(unix_timestamp)

    return timestamps
