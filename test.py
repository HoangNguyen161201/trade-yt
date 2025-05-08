from datetime import datetime, timedelta, timezone

def format_utc_time_range(start_timestamp: int, duration_hours: int = 4) -> str:
    """
    Chuyển timestamp sang định dạng: '12H AM - 4H PM DD/MM/YYYY' theo giờ quốc tế (UTC)
    """
    # Chuyển sang datetime UTC
    dt_start = datetime.fromtimestamp(start_timestamp, tz=timezone.utc)
    dt_end = dt_start + timedelta(hours=duration_hours)

    # Format giờ và ngày (tương thích Windows)
    start_str = dt_start.strftime("%I").lstrip("0") + "H " + dt_start.strftime("%p")
    end_str = dt_end.strftime("%I").lstrip("0") + "H " + dt_end.strftime("%p")
    date_str = dt_start.strftime("%d/%m/%Y")

    return f"{start_str} - {end_str} {date_str}"

# Ví dụ sử dụng
timestamp = 1746711000
print(format_utc_time_range(timestamp))