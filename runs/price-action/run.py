from util import update_thumbnail, trim_keywords_to_limit, format_utc_time_range, generate_content, upload_yt, connect_to_mt5, get_old_candels, create_video_from_gif_and_audio, create_video_from_image_and_audio, concat_videos_ffmpeg, combine_image_audios, check_draw_done, generate_voice_data, generate_voice_azure, gemini_keys, extract_data_future_number_or_reason, generate_introduce_content, create_transition_gif, generate_support_resistance, generate_result_future, generate_trendline, generate_fibonacci
import MetaTrader5 as mt5
import re
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import freeze_support
import time
from slugify import slugify

# info --------------------------------------------------------
# account
account = {
    "passowrd": 'Cuem1612@',
    "login": 79788688,
    "server": 'Exness-MT5Trial8'
}

symbol = 'GOLD (XAUUSD)'

# files path
folder_path = r'C:\Users\hoang\AppData\Roaming\MetaQuotes\Terminal\53785E099C927DB68A545C249CDBCE06\MQL5\Files'
txt_path = folder_path + r'\price-action.txt'
info_candle_m15_path = folder_path + r'\candle-m15.txt'
info_candle_m5_path = folder_path + r'\candle-m5.txt'
picture1_path = folder_path + r'\picture1.png'
picture2_path = folder_path + r'\picture2.png'

def main():
    try:
        connect_to_mt5(account['login'], account['passowrd'], account['server'], "C:/Program Files/MetaTrader 5 EXNESS/terminal64.exe")
        # index pictue
        index = 3

        # old candels
        old_candles_m15 = get_old_candels(info_candle_m15_path)
        old_candles_m5 = get_old_candels(info_candle_m5_path)
        
        # chuẩn bị content
        # chuẩn bị content để upload video
        time_thumbnail = format_utc_time_range(int(old_candles_m5[old_candles_m5.__len__() - 1]['time']))
        title = f'GOLD BUY OR SELL? GOLD/XAUUSD 4H FORECAST | {time_thumbnail}'
        title_slug = slugify(str(title))
        description=''
        tags=''

        # vẽ kháng cự, và hỗ trợ, trendline --------------------
        current_candle_m15 = old_candles_m15[old_candles_m15.__len__() - 1]
        current_candle_m5 = old_candles_m5[old_candles_m5.__len__() - 1]
        # hỗ trợ kháng cự
        support_resistance_m15_content = ''
        support_resistance_m5_content = ''
        # trendline
        trend_line = ''
        # introduce
        introduce_content = ''

        start_time = time.time()
        with ProcessPoolExecutor() as executor:
            future_m15 = executor.submit(generate_support_resistance, old_candles_m15, '15 phút', current_candle_m15['low'], current_candle_m15['high'], gemini_keys[0], symbol)
            future_m5 = executor.submit(generate_support_resistance, old_candles_m5, '5 phút', current_candle_m5['low'], current_candle_m5['high'], gemini_keys[1], symbol)
            future_trend_line = executor.submit(generate_trendline, old_candles_m15, '15 phút', gemini_keys[2], symbol)
            intro = executor.submit(generate_introduce_content, symbol, "15 phút", "5 phút", "FOREX_SIGNAL", gemini_keys[3])
            description_generate = executor.submit(generate_content,f'tôi đang có title là: {title}, tôi đang tạo ra video phân tích trade và đưa ra xu hướng trade tương lai cho {symbol} với khung thời gian 15 phút và 5 phút. Hãy viết lại description bằng tiếng anh sao cho hay và nổi bật, chuẩn seo, có các hastag,... để cho tôi gắn vào phần mô tả cho video youtube của tôi. trả ra description cho tôi luôn, không cần phải ghi thêm gì hết.', gemini_keys[6])
            tags_generate = executor.submit(generate_content,f'tôi đang có title là: {title}, tôi đang tạo ra video phân tích trade và đưa ra xu hướng trade tương lai cho {symbol} với khung thời gian 15 phút và 5 phút. Hãy cung cấp tags bằng tiếng anh chuẩn seo, nhiều người tìm kiếm trên youtube, không phải hastag, tag nào quan trọng phải được liệt kê trước, (các tag phải ngăn cách bằng dấu "," ví dụ tag1,tag2,tag3,...). để cho tôi gắn vào phần tags cho video youtube của tôi. trả ra tags cho tôi luôn, không cần phải ghi thêm gì hết.', gemini_keys[6])


            support_resistance_m15_content = future_m15.result()
            support_resistance_m5_content = future_m5.result()
            trend_line = future_trend_line.result()
            introduce_content = intro.result()
            description = description_generate.result()
            tags = tags_generate.result()
        tags = trim_keywords_to_limit(tags.replace(', ', ','), 400)
        print(description)
        print(tags)
        time.sleep(1000000)

        # convert lại để vẽ trong mql5
        reason_contents = [
            f'{reason.split('-')[2]}'
            for _, _, _, _, _, reason in re.findall(
                r'(support|resistance)-([\d.]+)-([\d.]+)-(\d+)-(\d+)-(.*)',
                f'{support_resistance_m15_content} {support_resistance_m5_content}'
            )
        ]
         
        datas = [
            f'{type_draw}-{p1}-{p2}-{old_candles_m15[-1]["time"]}-{old_candles_m15[0]["time"]}-{t1}-{t2}-{"230,153,153" if type_draw == "resistance" else "153,230,202"}-{'M15' if f'{type_draw}-{p1}-{p2}' in support_resistance_m15_content else 'M5'}'
            for type_draw, p1, p2, t1, t2 in re.findall(
                r'(support|resistance)-([\d.]+)-([\d.]+)-(\d+)-(\d+)',
                f'{support_resistance_m15_content} {support_resistance_m5_content}'
            )
        ]
        datas2 = [
            f'{type_draw}-{p1}-{p2}-{old_candles_m15[-1]["time"]}-{old_candles_m15[0]["time"]}-{t1}-{t2}-{"255,220,220" if type_draw == "resistance" else "219,255,242"}-{'M15' if f'{type_draw}-{p1}-{p2}' in support_resistance_m15_content else 'M5'}'
            for type_draw, p1, p2, t1, t2 in re.findall(
                r'(support|resistance)-([\d.]+)-([\d.]+)-(\d+)-(\d+)',
                f'{support_resistance_m15_content} {support_resistance_m5_content}'
            )
        ]

        proof_m15 = [
            f'{'proof1' if type_draw == 'resistance' else 'proof2'}-{high}-{low}-{t1}-{t2}'
            for type_draw, _, _, t1, t2, high, low in re.findall(
                r'(support|resistance)-([\d.]+)-([\d.]+)-(\d+)-(\d+)-([\d.]+)-([\d.]+)',
                f'{support_resistance_m15_content}'
            )
        ]
        proof_m5 = [
            f'{'proof1' if type_draw == 'resistance' else 'proof2'}-{high}-{low}-{t1}-{t2}'
            for type_draw, _, _, t1, t2, high, low  in re.findall(
                r'(support|resistance)-([\d.]+)-([\d.]+)-(\d+)-(\d+)-([\d.]+)-([\d.]+)',
                f'{support_resistance_m5_content}'
            )
        ]
       
        # tạo fibonacci
        fibonacci = generate_fibonacci(old_candles_m5, '5 phút', support_resistance_m15_content + ". "+ support_resistance_m5_content, trend_line, gemini_keys[4], symbol)
        # tạo dự đoán tương lai
        future_result = generate_result_future(old_candles_m15, old_candles_m5, "15 phút", "5 phút", support_resistance_m15_content, support_resistance_m5_content, trend_line, fibonacci, gemini_keys[5], gemini_keys[3], symbol)
        future = extract_data_future_number_or_reason(future_result.strip(), f'future-{old_candles_m15[old_candles_m15.__len__() - 1]['time']}')
        future_reason = extract_data_future_number_or_reason(future_result, is_reason= True)

        # truyền thông tin để vẽ vào mql5
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f'clear-m15\n')
            f.write(f'{trend_line}\n')
            for item in datas:
                f.write(f'{item}\n')
            f.write(f'snapshort-picture1.png\n')
            for item in datas2:
                f.write(f'{item}\n')
            f.write(f'snapshort-picture2.png\n')
            for item in proof_m15:
                f.write(f'{item}\n')
                f.write(f'snapshort-picture{index}.png\n')
                f.write(f'{item}-cancel\n')
                index += 1
            
            f.write(f'change-m5\n')
            for item in proof_m5:
                f.write(f'{item}\n')
                f.write(f'snapshort-picture{index}.png\n')
                f.write(f'{item}-cancel\n')
                index += 1
            f.write(f'{fibonacci}\n')
            f.write(f'snapshort-picture{index}.png\n')
            index += 1
            f.write(f'change-m15\n')
            f.write(f'{future}\n')
            f.write(f'snapshort-picture{index}.png\n')
        
        
        # đợi hình ảnh lưu xong
        while True:
            if check_draw_done(txt_path, 'drawdone'):
                break
            else:
                print("đợi vẽ xong...")
                time.sleep(1)


        with ProcessPoolExecutor() as executor:
            create_gif = executor.submit(create_transition_gif, picture1_path, picture2_path,  './public/picture1.gif')
            generate_voice = executor.submit(generate_voice_data, introduce_content, reason_contents, future_reason)
            create_thumbnail = executor.submit(
                update_thumbnail,
                './public/thumbnail-initial.png',
                './public/thumbnail.png',
                time_thumbnail,
                overlay_path= folder_path + f'/picture{reason_contents.__len__() + 2}.png',
                overlay_path_2= folder_path + f'/picture{reason_contents.__len__() + 4}.png'
                )

            create_thumbnail.result()
            create_gif.result()
            generate_voice.result()

        # bắt đầu tạo video
        print('generate video ---------------')
        images = []
        audios = []
        for index, item in enumerate(reason_contents):
            images.append(folder_path + f'/picture{index + 3}.png')
            audios.append(f'./audios/reason-{index + 1}.mp3')
        images.append(folder_path + f'/picture{reason_contents.__len__() + 4}.png')
        audios.append(f'./audios/future-price.mp3')

        data_video_paths = []
        data_video_paths.append(f'./public/video-1.mp4')
        with ProcessPoolExecutor() as executor:
            data = []
            intro_video = executor.submit(create_video_from_gif_and_audio, './public/picture1.gif', './audios/intro.mp3', f'./public/video-1.mp4')
            for index, item in enumerate(images):
                out_path = f'./public/video-{index + 2}.mp4'
                data.append(executor.submit(create_video_from_image_and_audio,item, audios[index], out_path))
                data_video_paths.append(out_path)
            intro_video.result()
            for item in data:
                item.result()

        concat_videos_ffmpeg('./public/intro.mp4', data_video_paths, f'./videos/{title_slug}.mp4')

        # upload video
        upload_yt(
            "C:/Path/To/Chrome/news-us-global",
            title,
            description,
            tags,
            f'./videos/{title_slug}.mp4',
            f"./public/thumbnail.png",
        )

        end_time = time.time()
        print(f"Thời gian thực thi: {end_time - start_time:.2f} giây") 

    except Exception as e:
        print(f'An exception occurred: {e}')


if __name__ == '__main__':
    freeze_support()
    main()


