import MetaTrader5 as mt5
import google.generativeai as genai

def connect_to_mt5(login, password, server, terminal):
    mt5.initialize(path= terminal, login= login,password= password,server= server)

def get_old_candels(symbol, timeframe, n_bars=200):
    # Lấy dữ liệu nến từ MT5
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n_bars)

    # Chuyển đổi dữ liệu thành dạng dễ đọc (có thể sử dụng pandas để hiển thị đẹp)
    candles = []
    for rate in rates:
        ohlcv = {
            'time': rate[0],
            'open': rate[1],
            'high': rate[2],
            'low': rate[3],
            'close': rate[4],
            'volume': rate[5]
        }
        candles.append(ohlcv)

    return candles

def generate_content(content):
    genai.configure(api_key="AIzaSyArae1nyjhAiRedUMkrUWd7p_-BJglXBNU")
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(content)
    return response.text