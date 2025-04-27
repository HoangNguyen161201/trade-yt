from util import connect_to_mt5, get_old_candels, generate_content
import MetaTrader5 as mt5
from collections import Counter
import time
try:
    connect_to_mt5(405397927, 'Cuem161201@', 'Exness-MT5Real8', "C:/Program Files/MetaTrader 5 EXNESS/terminal64.exe")

    # vẽ kháng cự, và hỗ trợ --------------------
    old_candles = get_old_candels('XAUUSDm', mt5.TIMEFRAME_H4, 200)
    print('bắt đầu tạo kháng cự và hỗ trợ')

    current_candle = get_old_candels('XAUUSDm', mt5.TIMEFRAME_H4, 1)[0]
    contentGetResistances = f"{old_candles} Đây là thông tin của 200 cây nến khung 4 giờ, vui lòng liệt kê ra các vùng giá kháng cự có giá trị cho việc phán đoán các kịch bản, các vùng kháng cự gần với giá hiện tại, lưu ý mỗi kháng cự là một vùng có giá trên và giá dưới hãy liệt kê ra theo định dạng sau: <giá trên>-<giá dưới>-<lý do>, giá trên và giá dưới không được là giá ngẫu nhiên mà phải dựa trên các giá của các cây nến tôi truyền vào, vùng kháng cự phải chất lượng không cần nhiều và phải có nhiều cây nến đi qua vùng giá đó. Vùng kháng cự phải cao hơn giá hiện tại {current_candle['high']}, tối đa 3 kháng cự, nếu không có thì trả lời null, không nói gì hết nữa. CHỈ LIỆT KÊ KHÔNG ĐƯỢC NÓI GÌ KHÁC."
    resultGetResistances = generate_content(contentGetResistances)

    current_candle = get_old_candels('XAUUSDm', mt5.TIMEFRAME_H4, 1)[0]
    contentGetSupports = f"{old_candles} Đây là thông tin của 200 cây nến khung 4 giờ, vui lòng liệt kê ra các vùng giá hỗ trợ có giá trị cho việc phán đoán các kịch bản, các vùng hỗ trợ gần với giá hiện tại, lưu ý mỗi hỗ trợ là một vùng có giá trên và giá dưới hãy liệt kê ra theo định dạng sau: <giá trên>-<giá dưới>-<lý do>, giá trên và giá dưới không được là giá ngẫu nhiên mà phải dựa trên các thông tin giá của các cây nến tôi truyền vào, vùng hỗ trợ phải chất lượng không cần nhiều và phải có nhiều cây nến đi qua vùng giá đó. Vùng hỗ trợ phải thấp hơn giá hiện tại {current_candle['low']}, tối đa 3 hỗ trợ, nếu không có thì trả lời null, không nói gì hết nữa. CHỈ LIỆT KÊ KHÔNG ĐƯỢC NÓI GÌ KHÁC."
    resultGetSupports = generate_content(contentGetSupports)

    print(resultGetResistances)
    print(resultGetSupports)


except:
    print('An exception occurred')