from util import connect_to_mt5, get_candles_simple, gemini_keys, generate_content
import MetaTrader5 as mt5

account = {
    "passowrd": 'Cuem161201@',
    "login": 77015891,
    "server": 'RoboForex-ECN'
}

connect_to_mt5(account['login'], account['passowrd'], account['server'], "C:/Program Files/RoboForex MT5 Terminal/terminal64.exe")

data = {
    "XAUUSD": {
        "m5": get_candles_simple("XAUUSD", mt5.TIMEFRAME_M5, 180),
        "m1": get_candles_simple("XAUUSD", mt5.TIMEFRAME_M1, 180),
    },
    "EURUSD": {
        "m5": get_candles_simple("EURUSD", mt5.TIMEFRAME_M5, 180),
        "m1": get_candles_simple("EURUSD", mt5.TIMEFRAME_M1, 180),
    },
    "GBPUSD": {
        "m5": get_candles_simple("GBPUSD", mt5.TIMEFRAME_M5, 180),
        "m1": get_candles_simple("GBPUSD", mt5.TIMEFRAME_M1, 180),
    },
    "AUDUSD": {
        "m5": get_candles_simple("AUDUSD", mt5.TIMEFRAME_M5, 180),
        "m1": get_candles_simple("AUDUSD", mt5.TIMEFRAME_M1, 180),
    },
    "USDJPY": {
        "m5": get_candles_simple("USDJPY", mt5.TIMEFRAME_M5, 180),
        "m1": get_candles_simple("USDJPY", mt5.TIMEFRAME_M1, 180),
    },
    "EURJPY": {
        "m5": get_candles_simple("EURJPY", mt5.TIMEFRAME_M5, 180),
        "m1": get_candles_simple("EURJPY", mt5.TIMEFRAME_M1, 180),
    },
} 
prompt = f"""
{data}

Đây là dữ liệu giá của khung thời gian M5 và M1 của các cặp tiền tệ.

Yêu cầu: Dựa trên dữ liệu trên, hãy phân tích và chọn ra đúng **1 cặp tiền tệ duy nhất** phù hợp nhất để giao dịch trong thời điểm hiện tại, theo tiêu chí sau:

1. Có xu hướng rõ ràng (tăng hoặc giảm).
2. Biến động vừa phải (không quá mạnh, không quá nhiễu).
3. Có vùng hỗ trợ và kháng cự rõ ràng.
4. Dễ dàng để giao dịch theo phương pháp **scalping** (giao dịch nhanh trong thời gian ngắn).

Bắt buộc:
- Trả ra đúng 1 cặp tiền duy nhất.
- Giải thích lý do chọn cặp tiền đó (dựa theo các tiêu chí trên).
- Giải thích lý do **loại bỏ các cặp tiền còn lại** (vì nhiễu, sideway, không rõ xu hướng, biến động mạnh, v.v).
"""
result = generate_content(prompt, gemini_keys[gemini_keys.__len__() - 1])
print(result)
