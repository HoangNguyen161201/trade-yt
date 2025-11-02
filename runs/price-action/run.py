from util import check_identity_verification, open_chrome_to_edit, generate_bearish_or_bullish, create_thumbnail, trim_keywords_to_limit, format_utc_time_range, generate_content, upload_yt, connect_to_mt5, get_old_candels, create_video_from_gif_and_audio, create_video_from_image_and_audio, concat_videos_ffmpeg, combine_image_audios, check_draw_done, generate_voice_data, generate_voice_azure, gemini_keys, extract_data_future_number_or_reason, generate_introduce_content, create_transition_gif, generate_support_resistance, generate_result_future, generate_trendline, generate_fibonacci
import MetaTrader5 as mt5
import re
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import freeze_support
import time
from slugify import slugify
import os
import random
from datetime import datetime
import shutil
import glob
from data import chrome_driver, account, symbols, name_channel
from data import terminal, folder_path, txt_path, info_candle_m15_path, info_candle_m1_path, picture1_path, picture2_path


def main():
    is_start = True
    index_symbol = 0
    while is_start:
        try:
            symbol = symbols[index_symbol]['symbol']
            symbol_title_generate_content = symbols[index_symbol]['symbol_title_generate_content']
            symbol_title = symbols[index_symbol]['symbol_title']

            base_dir = os.path.dirname(os.path.abspath(__file__))
            folder_audio = os.path.join(base_dir, './audios')
            folder_video = os.path.join(base_dir, './videos')
            if os.path.exists(folder_audio):
                shutil.rmtree(folder_audio)
            if not os.path.exists(folder_audio):
                os.makedirs(folder_audio)
            if os.path.exists(folder_video):
                shutil.rmtree(folder_video)
            if not os.path.exists(folder_video):
                os.makedirs(folder_video)
            # Lấy danh sách tất cả file .png trong thư mục
            png_files = glob.glob(os.path.join(folder_path, "*.png"))
            for file_path in png_files:
                try:
                    os.remove(file_path)
                    print(f"Đã xóa: {file_path}")
                except Exception as e:
                    print(f"Lỗi khi xóa {file_path}: {e}")
            intro_path = os.path.join(base_dir, './public/intro.mp4')
            gif_path = f'{folder_video}/picture1.gif'
            bg = os.path.join(base_dir, './public/thumbnail-price-action.png')
            thumbnail_output = f'{folder_video}/thumbnail.png'

            connect_to_mt5(account['login'], account['password'], account['server'],
                           terminal)
            # index pictue
            index = 3

            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f'symbol-{symbol}\n')
                f.write(f'clear-m15\n')
            # đợi chart thay đổi
            time.sleep(10)

            # old candels
            old_candles_m15 = get_old_candels(info_candle_m15_path)
            old_candles_m1 = get_old_candels(info_candle_m1_path)

            # vẽ kháng cự, và hỗ trợ, trendline --------------------
            current_candle_m15 = old_candles_m15[old_candles_m15.__len__() - 1]
            current_candle_m1 = old_candles_m1[old_candles_m1.__len__() - 1]
            # hỗ trợ kháng cự
            support_resistance_m15_content = ''
            support_resistance_m1_content = ''
            # trendline
            trend_line = ''
            # introduce
            introduce_content = ''

            start_time = time.time()
            support_resistance_m15_content = generate_support_resistance(
                old_candles_m15, '15 phút', current_candle_m15['low'], current_candle_m15['high'], gemini_keys[0], symbol_title_generate_content)
            support_resistance_m1_content = generate_support_resistance(
                old_candles_m1, '1 phút', current_candle_m1['low'], current_candle_m1['high'], gemini_keys[0], symbol_title_generate_content)
            trend_line = generate_trendline(
                old_candles_m15, '15 phút', gemini_keys[0], symbol_title_generate_content)
            introduce_content = generate_introduce_content(
                symbol_title_generate_content, "15 phút", "1 phút", name_channel, gemini_keys[0])

            # convert lại để vẽ trong mql5
            pattern = re.compile(
                r'(support|resistance)-([\d.]+)-([\d.]+)-(\d+)-(\d+)-([\d.]+)-([\d.]+)-(.*?)\s*(?=(support|resistance)-|$)',
                re.DOTALL
            )
            reason_contents = [
                match[7].strip()
                for match in pattern.findall(f'{support_resistance_m15_content} {support_resistance_m1_content}')
            ]

            datas = [
                f'{type_draw}-{p1}-{p2}-{old_candles_m15[-1]["time"]}-{old_candles_m15[0]["time"]}-{t1}-{t2}-{
                    "230,153,153" if type_draw == "resistance" else "153,230,202"}-{'m15' if f'{type_draw}-{p1}-{p2}' in support_resistance_m15_content else 'm1'}'
                for type_draw, p1, p2, t1, t2 in re.findall(
                    r'(support|resistance)-([\d.]+)-([\d.]+)-(\d+)-(\d+)',
                    f'{support_resistance_m15_content} {
                        support_resistance_m1_content}'
                )
            ]
            datas2 = [
                f'{type_draw}-{p1}-{p2}-{old_candles_m15[-1]["time"]}-{old_candles_m15[0]["time"]}-{t1}-{t2}-{
                    "255,220,220" if type_draw == "resistance" else "219,255,242"}-{'m15' if f'{type_draw}-{p1}-{p2}' in support_resistance_m15_content else 'm1'}'
                for type_draw, p1, p2, t1, t2 in re.findall(
                    r'(support|resistance)-([\d.]+)-([\d.]+)-(\d+)-(\d+)',
                    f'{support_resistance_m15_content} {
                        support_resistance_m1_content}'
                )
            ]

            proof_m15 = [
                f'{'proof1' if type_draw ==
                    'resistance' else 'proof2'}-{high}-{low}-{t1}-{t2}'
                for type_draw, _, _, t1, t2, high, low in re.findall(
                    r'(support|resistance)-([\d.]+)-([\d.]+)-(\d+)-(\d+)-([\d.]+)-([\d.]+)',
                    f'{support_resistance_m15_content}'
                )
            ]
            proof_m1 = [
                f'{'proof1' if type_draw ==
                    'resistance' else 'proof2'}-{high}-{low}-{t1}-{t2}'
                for type_draw, _, _, t1, t2, high, low in re.findall(
                    r'(support|resistance)-([\d.]+)-([\d.]+)-(\d+)-(\d+)-([\d.]+)-([\d.]+)',
                    f'{support_resistance_m1_content}'
                )
            ]
            # tạo fibonacci
            fibonacci = generate_fibonacci(old_candles_m1, '1 phút', support_resistance_m15_content + ". " +
                                           support_resistance_m1_content, trend_line, gemini_keys[0], symbol_title_generate_content)
            print(fibonacci)
            # tạo dự đoán tương lai
            future_result = generate_result_future(old_candles_m15, old_candles_m1, "15 phút", "1 phút", support_resistance_m15_content,
                                                   support_resistance_m1_content, trend_line, fibonacci, gemini_keys[0], gemini_keys[0], symbol_title_generate_content)
            future = extract_data_future_number_or_reason(future_result.strip(
            ), f'future-{old_candles_m15[old_candles_m15.__len__() - 1]['time']}')
            future_reason = extract_data_future_number_or_reason(
                future_result, is_reason=True)

            # xác định tăng hay giảm để tọa title
            bearish_or_bullish = generate_bearish_or_bullish(
                future_reason, gemini_keys[0])
            # tạo title
            title_path = 'bullish.txt' if 'bullish' in bearish_or_bullish.lower() else 'bearish.txt'
            file_path = os.path.join(base_dir, title_path)
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            lines = [line.strip() for line in lines if line.strip()]
            lines = [line.replace("symbol", symbol_title) for line in lines]
            today = datetime.now()
            date_str = today.strftime("%B %d")
            title = f'{symbol_title} Price Forecast Today, Technical Analysis ({
                date_str}):'
            remain = 100 - len(title)
            filtered_lines = [line for line in lines if len(line) < remain]
            random_index = random.randint(0, len(filtered_lines) - 1)
            title = f'{title} {filtered_lines[random_index]}'
            title_slug = slugify(str(title))

            # tạo description và tag
            description = ''
            tags = ''
            print('bắt đầu tạo description')
            description = generate_content(
                f"""
                The video title is: "{title}".
                It provides a technical analysis and future trading trend forecast for {symbol_title_generate_content}
                using the 15-minute and 1-minute charts.

                Please:
                1. Write a professional, SEO-optimized YouTube description in English.
                2. Include relevant hashtags at the end (e.g. #trading #forex #priceaction).
                3. After that, on a new line, write "tags:" followed by a comma-separated list of tags.
                4. Do NOT include any "Description:" label or introduction — output only the content.

                Example format:

                <description text here>

                tags: tag1, tag2, tag3, tag4, ...
                """,
                gemini_keys[0]
            )

            print('bắt đầu tạo tags')
            tags = generate_content(f'tôi đang có title là: {title}, tôi đang tạo ra video phân tích trade và đưa ra xu hướng trade tương lai cho {
                                    symbol_title_generate_content} với khung thời gian 15 phút và 1 phút. Hãy cung cấp tags bằng tiếng anh chuẩn seo, nhiều người tìm kiếm trên youtube, không phải hastag, tag nào quan trọng phải được liệt kê trước, (các tag phải ngăn cách bằng dấu "," ví dụ tag1,tag2,tag3,...). để cho tôi gắn vào phần tags cho video youtube của tôi. trả ra tags cho tôi luôn, không cần phải ghi thêm gì hết.', gemini_keys[0])
            tags = trim_keywords_to_limit(tags.replace(', ', ','), 400)

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

                f.write(f'change-m1\n')
                for item in proof_m1:
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
                # tạo ảnh động
                create_gif = executor.submit(
                    create_transition_gif, picture1_path, picture2_path,  gif_path)
                # tạo voice
                generate_voice = executor.submit(
                    generate_voice_data, introduce_content, reason_contents, future_reason, folder_audio)
                # tạo thumbnail
                update_thumbnail = executor.submit(
                    create_thumbnail,
                    bg,
                    picture2_path,
                    thumbnail_output,
                    left=1113,
                    top=279,
                    overlay_size=(740, 409),
                    border_radius=18,
                    symbol=symbol_title,
                    day=date_str,
                    des=filtered_lines[random_index])

                update_thumbnail.result()
                create_gif.result()
                generate_voice.result()

            # bắt đầu tạo video
            print('generate video ---------------')
            images = []
            audios = []
            for index, item in enumerate(reason_contents):
                images.append(folder_path + f'/picture{index + 3}.png')
                audios.append(f'{folder_audio}/reason-{index + 1}.mp3')
            images.append(
                folder_path + f'/picture{reason_contents.__len__() + 4}.png')
            audios.append(f'{folder_audio}/future-price.mp3')

            data_video_paths = []
            data_video_paths.append(f'{folder_video}/video-1.mp4')
            with ProcessPoolExecutor() as executor:
                data = []
                intro_video = executor.submit(create_video_from_gif_and_audio, gif_path, f'{
                                              folder_audio}/intro.mp3', f'{folder_video}/video-1.mp4')
                for index, item in enumerate(images):
                    out_path = f'{folder_video}/video-{index + 2}.mp4'
                    data.append(executor.submit(
                        create_video_from_image_and_audio, item, audios[index], out_path))
                    data_video_paths.append(out_path)
                intro_video.result()
                for item in data:
                    item.result()

            concat_videos_ffmpeg(intro_path, data_video_paths, f'{
                                 folder_video}/{title_slug}.mp4')

            # upload video
            base_dir = os.path.dirname(os.path.abspath(__file__))
            folder_youtubes = os.path.join(base_dir, './youtubes')
            folders = [
                name for name in os.listdir(folder_youtubes)
                if os.path.isdir(os.path.join(folder_youtubes, name))
            ]
            upload_yt(
                f'{folder_youtubes}/{folders[0]}',
                title,
                description,
                tags,
                f'{folder_video}/{title_slug}.mp4',
                thumbnail_output,
            )

            end_time = time.time()
            print(f"Thời gian thực thi: {end_time - start_time:.2f} giây")
            index_symbol += 1
            if index_symbol >= symbols.__len__():
                print('đã đăng đủ video trong hôm nay đợi qua ngày mai')
                index_symbol = 0
                time.sleep((24 - symbols.__len__()) * 360)
            print(f"Đợi 1 tiếng để đăng tiếp")
            time.sleep(360)

        except Exception as e:
            print(f'An exception occurred: {e}')
            print('lỗi đợi 1 phút rồi đăng lại')
            time.sleep(60)


if __name__ == "__main__":
    is_exit = False
    while is_exit is False:
        print('|-----------------------------------------------|')
        print('|-------       tool youtube linux        -------|')
        print('|-0. Thoát chương trình                  -------|')
        print('|-1. Chỉnh sửa danh sách chrome youtube  -------|')
        print('|-2. Chạy youtube                        -------|')

        input_data = input("Nhập chọn chức năng: ")
        func = int(input_data)
        if func == 1:
            while func == 1:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                folder_youtubes = os.path.join(base_dir, './youtubes')
                if not os.path.exists(folder_youtubes):
                    os.makedirs(folder_youtubes)
                folders = [
                    name for name in os.listdir(folder_youtubes)
                    if os.path.isdir(os.path.join(folder_youtubes, name))
                ]
                print('|-----------------------------------------------|')
                print('|---   Chỉnh sửa danh sách chrome youtube   ----|')
                print('|- DANH SÁCH YOUTUBE:                    -------|')
                if (folders.__len__() > 0):
                    print(folders)
                else:
                    print('Trống vui lòng thêm youtube mới')
                print('|-0. Quay lại                            -------|')
                print('|-1. Thêm youtube mới (nhập 1-name)      -------|')
                print('|-2. Xóa youtube (nhập 2-name)           -------|')
                print('|-3. xác minh danh tính (nhập 3-name)    -------|')
                func1 = input("Nhập chọn chức năng: ")

                if (' ' in func1):
                    print('lỗi cú pháp, không được chứa dấu cách')
                elif func1 == 0 or func1 == '0':
                    func = 'exit'
                elif func1.startswith("1-"):
                    text = func1[2:]
                    if (folders is not None and folders.__len__() > 0 and any(item == text for item in folders)):
                        print('đã tồn tại chrome youtube này rồi')
                    else:
                        open_chrome_to_edit(
                            f'{folder_youtubes}/{text}', chrome_driver)
                elif func1.startswith("2-"):
                    text = func1[2:]
                    if (folders is not None and folders.__len__() > 0 and any(item == text for item in folders)):
                        try:
                            shutil.rmtree(f"{folder_youtubes}/{text}")
                        except:
                            print('')
                    else:
                        print('Không thể xóa vì chưa tồn tại chrome youtube này')
                elif func1.startswith("3-"):
                    text = func1[2:]
                    if (folders is not None and folders.__len__() > 0 and any(item == text for item in folders)):
                        check_identity_verification(
                            f'{folder_youtubes}/{text}')
                    else:
                        print('Chưa tồn tại trình duyệt này')

        elif func == 2:
            freeze_support()
            main()
        elif func == 0:
            is_exit = True
        else:
            print('Thoát thành công')
