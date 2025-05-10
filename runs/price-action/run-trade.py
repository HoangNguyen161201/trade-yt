from util import update_thumbnail, trim_keywords_to_limit, format_utc_time_range, generate_content, upload_yt, connect_to_mt5, get_old_candels, create_video_from_gif_and_audio, create_video_from_image_and_audio, concat_videos_ffmpeg, combine_image_audios, check_draw_done, generate_voice_data, generate_voice_azure, gemini_keys, extract_data_future_number_or_reason, generate_introduce_content, create_transition_gif, generate_support_resistance, generate_result_future, generate_trendline, generate_fibonacci
import MetaTrader5 as mt5
import re
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import freeze_support
import time
from slugify import slugify
import os

# info --------------------------------------------------------
# account
account = {
    "passowrd": 'Cuem1612@',
    "login": 79788688,
    "server": 'Exness-MT5Trial8'
}

symbol = 'AUDJPYm'

# files path
folder_path = r'C:\Users\hoang\AppData\Roaming\MetaQuotes\Terminal\53785E099C927DB68A545C249CDBCE06\MQL5\Files'
txt_path = folder_path + r'\price-action.txt'
info_candle_m5_path = folder_path + r'\candle-m5.txt'
info_candle_m1_path = folder_path + r'\candle-m1.txt'
picture1_path = folder_path + r'\picture1.png'
picture2_path = folder_path + r'\picture2.png'

def main():
    while True:
        try:
            connect_to_mt5(account['login'], account['passowrd'], account['server'], "C:/Program Files/MetaTrader 5 EXNESS/terminal64.exe")

            # old candels
            old_candles_m5 = get_old_candels(info_candle_m5_path)
            old_candles_m1 = get_old_candels(info_candle_m1_path)
            

            # vẽ kháng cự, và hỗ trợ, trendline --------------------
            current_candle_m5 = old_candles_m5[old_candles_m5.__len__() - 1]
            current_candle_m1 = old_candles_m1[old_candles_m1.__len__() - 1]
            # hỗ trợ kháng cự
            support_resistance_m5_content = ''
            support_resistance_m1_content = ''
            # trendline
            trend_line = ''

            start_time = time.time()
            with ProcessPoolExecutor() as executor:
                future_m5 = executor.submit(generate_support_resistance, old_candles_m5, '5 phút', current_candle_m5['low'], current_candle_m5['high'], gemini_keys[0], symbol)
                future_m1 = executor.submit(generate_support_resistance, old_candles_m1, '1 phút', current_candle_m1['low'], current_candle_m1['high'], gemini_keys[1], symbol)
                future_trend_line = executor.submit(generate_trendline, old_candles_m5, '5 phút', gemini_keys[2], symbol)

                support_resistance_m5_content = future_m5.result()
                support_resistance_m1_content = future_m1.result()
                trend_line = future_trend_line.result()

            # convert lại để vẽ trong mql5
            datas = [
                f'{type_draw}-{p1}-{p2}-{old_candles_m5[-1]["time"]}-{old_candles_m5[0]["time"]}-{t1}-{t2}-{"230,153,153" if type_draw == "resistance" else "153,230,202"}-{'M5' if f'{type_draw}-{p1}-{p2}' in support_resistance_m5_content else 'M1'}'
                for type_draw, p1, p2, t1, t2 in re.findall(
                    r'(support|resistance)-([\d.]+)-([\d.]+)-(\d+)-(\d+)',
                    f'{support_resistance_m5_content} {support_resistance_m1_content}'
                )
            ]
            datas2 = [
                f'{type_draw}-{p1}-{p2}-{old_candles_m5[-1]["time"]}-{old_candles_m5[0]["time"]}-{t1}-{t2}-{"255,220,220" if type_draw == "resistance" else "219,255,242"}-{'M5' if f'{type_draw}-{p1}-{p2}' in support_resistance_m5_content else 'M1'}'
                for type_draw, p1, p2, t1, t2 in re.findall(
                    r'(support|resistance)-([\d.]+)-([\d.]+)-(\d+)-(\d+)',
                    f'{support_resistance_m5_content} {support_resistance_m1_content}'
                )
            ]

            proof_m5 = [
                f'{'proof1' if type_draw == 'resistance' else 'proof2'}-{high}-{low}-{t1}-{t2}'
                for type_draw, _, _, t1, t2, high, low in re.findall(
                    r'(support|resistance)-([\d.]+)-([\d.]+)-(\d+)-(\d+)-([\d.]+)-([\d.]+)',
                    f'{support_resistance_m5_content}'
                )
            ]
            proof_m1 = [
                f'{'proof1' if type_draw == 'resistance' else 'proof2'}-{high}-{low}-{t1}-{t2}'
                for type_draw, _, _, t1, t2, high, low  in re.findall(
                    r'(support|resistance)-([\d.]+)-([\d.]+)-(\d+)-(\d+)-([\d.]+)-([\d.]+)',
                    f'{support_resistance_m1_content}'
                )
            ]
        
            # tạo fibonacci
            fibonacci = generate_fibonacci(old_candles_m1, '1 phút', support_resistance_m5_content + ". "+ support_resistance_m1_content, trend_line, gemini_keys[4], symbol)
            # tạo dự đoán tương lai
            future_result = generate_result_future(old_candles_m5, old_candles_m1, "5 phút", "1 phút", support_resistance_m5_content, support_resistance_m1_content, trend_line, fibonacci, gemini_keys[5], gemini_keys[3], symbol)
            future = extract_data_future_number_or_reason(future_result.strip(), f'future-{old_candles_m5[old_candles_m5.__len__() - 1]['time']}')
            future_reason = extract_data_future_number_or_reason(future_result, is_reason= True)

            # vẽ vào mql5 để xem trước
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f'clear-m5\n')
                f.write(f'{trend_line}\n')
                for item in datas:
                    f.write(f'{item}\n')
                for item in datas2:
                    f.write(f'{item}\n')
                for item in proof_m5:
                    f.write(f'{item}\n')
                for item in proof_m1:
                    f.write(f'{item}\n')
                f.write(f'{fibonacci}\n')
                f.write(f'{future}\n')

            end_time = time.time()
            print(f"Thời gian thực thi: {end_time - start_time:.2f} giây")

            user_input = input("Nhập bất kỳ để chạy tiếp: ").strip()
            print(user_input)

        except Exception as e:
            print(f'An exception occurred: {e}')


if __name__ == '__main__':
    freeze_support()
    main()


