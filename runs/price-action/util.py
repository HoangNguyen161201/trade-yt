import MetaTrader5 as mt5
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor
import os
import re
from PIL import Image, ImageDraw, ImageFont
import imageio
from moviepy import AudioFileClip, concatenate_videoclips, VideoFileClip, ImageClip
import azure.cognitiveservices.speech as speechsdk
import subprocess
from datetime import datetime, timedelta, timezone

import time
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

gemini_keys = [
    'AIzaSyA5Dhdav1JfroDhO5G6OVdzFATvYTXwNuM',
    'AIzaSyB2j_rHJOnMA9Zi7fziRd-ccB2NANTTctA',
    'AIzaSyA5AZYheK24asDX0smMWHmzTcOuFgIAcRw',
    'AIzaSyDO1kguNUtt--NUE2gbEyZDWhga2BuGXeI',
    'AIzaSyD2zA0PJvQAUWyWGk-UunQP5XeMbhlYBA8',
    'AIzaSyAO3zWuhyUKzPsweyiEDKcuiZxLKkdUNNk',
    'AIzaSyA9T58LWbmaHJFuCPCbJiXxPx_Y2DoiIVk'
    ]
azure_keys = [
    {
        "speech_key": "2JgozCp7ZimaAYM2TlazGQGu7YjMzcZroS9YFQgnkuFcy6KlloLsJQQJ99BEAC3pKaRXJ3w3AAAYACOGTYKT",
        "service_region": "eastasia" 
    }
]

def connect_to_mt5(login, password, server, terminal):
    mt5.initialize(path= terminal, login= login,password= password,server= server)

def get_old_candels(file_path):
    if os.path.exists(file_path):
        data = []
        # Mở file với mã hóa UTF-8 (hoặc mã hóa phù hợp)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:  # Sử dụng 'utf-8' và bỏ qua lỗi
            lines = f.readlines()

        for line in lines:
            line = line.strip()  # Xóa ký tự thừa (newline, space)
            if line:
                line = str(line)
                line = re.sub(r'[^\x20-\x7E]', '', line)
                parts = line.split("-")
                if len(parts) == 8:
                    try:
                        item = {
                            "time": int(parts[0]),
                            'time_readable': datetime.utcfromtimestamp(int(parts[0])).strftime('%Y-%m-%d %H:%M:%S'),
                            "open": float(parts[1]),
                            "close": float(parts[2]),
                            "high": float(parts[3]),
                            "low": float(parts[4]),
                            "bollinger_band_upper": float(parts[5]),
                            "bollinger_band_middle": float(parts[6]),
                            "bollinger_band_lower": float(parts[7])
                        }
                        data.append(item)
                    except ValueError:
                        print(f"Lỗi dữ liệu dòng: {line}")

        # Nếu có dữ liệu hợp lệ, trả về mảng, nếu không trả về None
        return data if data else None
    else:
        print("File không tồn tại.")
        return None
    
def generate_content(content, key = gemini_keys[0]):
    genai.configure(api_key= key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(content)
    return response.text

def generate_introduce_content( symbol, time_frame_big, time_frame_tiny, name_channel, key = gemini_keys[0]):
    print("tạo phần giới thiệu cho video")
    return generate_content(f"""
        tôi có kênh youtube tên là {name_channel}, chuyên phân tích forex, cung cấp tín hiệu mua hoặc bán và xu hướng giá đi trong tương lai.
        hôm nay tôi đang làm video về phân tích {symbol} với khung thời gian {time_frame_big} và {time_frame_tiny}.
        bạn hãy tạo ra câu chào, hoặc giới thiệu, kêu gọi đăng ký,... hấp dẫn, thân thiện, câu từ đừng quá lố  trước khi đi vào phân tích cho tôi.
        để tôi có thể làm phần nói đầu tiên trong video của mình. bạn chỉ cần trả ra kết quả, bằng tiếng anh, không cần nói gì thêm.
    """, key)

def generate_support_resistance(old_candles, time_frame, low, high, gemini_key, symbol):
    print(f'bắt đầu tạo hỗ trợ và kháng cự khung {time_frame}')

    prompt_base = f"""{old_candles} Đây là thông tin của các cây nến (bao gồm cả thông tin Bollinger Bands) khung {time_frame} phút của {symbol}, áp dụng phương pháp price action, vui lòng trả lời cho tôi 1 vùng support  và 1 vùng resistance tốt nhất, support phải dưới giá {low} và resistance phải trên giá {high}.
    support và resistance không được dính nhau và phải có khoảng cách để trade.
    trả lời dưới Định dạng: <type>-<giá trên>-<giá dưới>-<time1>-<time2>-<high price from time1 to time2>-<low price from time1 to time2>-<lý do không phải nằm trong khoảng 150 tới 250 ký tự, viết bằng tiếng anh, viết làm sao để tôi có thể nói trong video youtube, và nêu lý do vì sao hình thành support hoặc resistance thui, trong lý dó không được ghi price1-price2, mà phải ghi là price tới price, không cần phải nêu ra hướng trade đâu.> (type là support hoặc resistance, time1 time2 là bằng chứng, còn trong lý do nếu có nêu thời gian thì dựa vào thời gian time_readable để xin ra ngày giờ phút).
    .tốt nhất nên trả ra cả resistance và support.nếu không có resistance tìm năng thì chỉ trả lời <resistance>-null và phải trả ra support. nếu không có support tiềm năng thì trả ra <support>-null và phải trả ra resistance.
    """

    # Tạo 5 task chạy song song generate_content
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(generate_content, prompt_base, gemini_key) for _ in range(5)]
        contents = [f.result() for f in futures]

    # Tóm tắt và chọn ra vùng tốt nhất
    summary_prompt = f"""{contents} hãy chọn ra 1 supprot và 1 resistance tốt nhất và được nhắc tới nhiều nhất. nếu resistance có resistance-null nhiều thì đừng lấy, còn nếu ít hoặc không có thì lấy nhá. nếu support-null nhiều đừng lấy, còn nếu ít hoặc không thì lấy nhá. support và resistance không được dính nhau và phải có khoảng cách để trade. trả ra item đó dưới Định dạng: <type>-<giá trên>-<giá dưới>-<time1>-<time2>-<high price from time1 to time2>-<low price from time1 to time2>-<lý do (lấy lý do có sẵn, không thêm không bớt)> (type là support hoặc resistance, không được viết hoa, tất cả viết thường), và không nói gì hết nữa, không ghi thêm hay giải thích gì hết."""
    return generate_content(summary_prompt, gemini_key)

def generate_trendline(old_candles, time_frame, gemini_key, symbol):
    print('bắt đầu tạo trendline')

    # Prompt template
    prompt_template = f"""
    {old_candles}
    Đây là dữ liệu nến (bao gồm cả thông tin Bollinger Bands) của {symbol} với khung thời gian {time_frame} phút.

    Dựa trên phân tích Price Action, hãy tìm **1 trendline duy nhất** thoả điều kiện sau:

    ### Yêu cầu bắt buộc:
    - gần với giá thời gian hiện tại (ưu tiên cây nến cuối cùng, quan trọng).
    - Nếu giá đi ngang hoặc không tìm được đường thỏa điều kiện trên thì trả về `null`.
    - Chỉ sử dụng dữ liệu tôi cung cấp (không dự đoán tương lai).
    - phải gần sát với giá hiện tại mà tôi cung cấp {old_candles[old_candles.__len__() - 1]} để có thể phân tích và trade trong tương lai (quan trọng).

    ### Kết quả trả về:
    Chỉ trả 1 dòng duy nhất theo định dạng:
    `trendline-<price1>-<price2>-<time1 bắt đầu>-<time2 kết thúc>-<lý do>`

    **Không giải thích, không thêm nội dung nào khác. không xuống dòng, đầu và cuối không có khoảng cách. không được viết hoa, viết thường hết.**
    """

    # Gọi song song 5 lần generate_content
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(generate_content, prompt_template, gemini_key)
            for _ in range(5)
        ]
        prompts = [f.result() for f in futures]

    # Gộp kết quả vào final prompt
    final_prompt = f"""Đây là dữ liệu nến của {symbol} với khung thời gian {time_frame} phút. thông tin các đường trendlines:
    {prompts}
    Hãy lọc ra 1 trendline nào lặp lại và hợp lý nhất trong các gợi ý trên, gần với giá hiện tại mà tôi cung cấp. Nếu đa số trả `null`, thì kết quả trả ra cuối cùng là `null`, không trả ra thêm hoặc giải thích gì hết. Nếu không, chỉ chọn 1 trendline rõ ràng nhất, trả ra đúng định dạng:

    `trendline-<price1>-<price2>-<time1>-<time2>`

    Không thêm bất kỳ lời giải thích hay chú thích nào khác.
    """

    return generate_content(final_prompt, gemini_key)


def generate_fibonacci(old_candles, time_frame, suport_resitances, trend_line, gemini_key, symbol):
    print('bắt đầu tạo fibonacci')

    # Prompt template
    prompt_template = f"""
    {old_candles}
    Đây là dữ liệu nến (bao gồm cả thông tin Bollinger Bands) của {symbol} với khung thời gian {time_frame}, được cấu hình:
    <type>-<giá trên>-<giá dưới>-<time1>-<time2>-<high price from time1 to time2>-<low price from time1 to time2>-<lý do không dưới 100 ký tự> (type là support hoặc resistance, time1 time2 là bằng chứng).
    các vùng support và resitance: {suport_resitances}.
    đây là đường trendline khung lớn hơn: {trend_line}.
    Dựa trên phân tích Price Action và các dữ liệu mà tôi cung cấp, hãy đưa ra thông tin fibonacci để có thể trade:
    
    ### Kết quả trả về:
    Chỉ trả 1 dòng duy nhất theo định dạng:
    fibonacci-<price1>-<price2>-<time1 bắt đầu>-<time2 kết thúc>-<lý do>`

    ### Yêu cầu bắt buộc:
    - bắt buộc phải cung cấp thông tin cho tôi, bao gồm:
    - cân nhắc kĩ trước khi đưa ra quyết định.
    - nếu bạn phân tích sẽ tăng trong tương lai, thì price1 phải thấp hơn price 2.
    - nếu bạn phân tích sẽ giảm trong tương lai, thì price1 phải lớn hơn price 2.
    - fibonacci phải hợp lý và tiềm năng.
    - fibonacci gần với giá thời gian hiện tại (ưu tiên cây nến cuối cùng, quan trọng).

    **Không giải thích, không thêm nội dung nào khác. không xuống dòng, đầu và cuối không có khoảng cách. không được viết hoa, viết thường hết.**
    """

    # Gọi song song 5 lần generate_content
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(generate_content, prompt_template, gemini_key)
            for _ in range(5)
        ]
        prompts = [f.result() for f in futures]

    # Gộp kết quả vào final prompt
    final_prompt = f"""{old_candles} Đây là dữ liệu nến của {symbol} với khung thời gian {time_frame} phút. thông tin của fibonacci:
    {prompts}
    Hãy lọc ra 1 fibonacci nào lặp lại và hợp lý nhất và có thể dựa vào đó để trade trong các gợi ý trên, gần với giá thời gian hiện tại. trả ra đúng định dạng:

    `fibonacci-<price1>-<price2>-<time1>-<time2>`

    Không thêm bất kỳ lời giải thích hay chú thích nào khác.
    """

    return generate_content(final_prompt, gemini_key)


def generate_result_future(old_candles, old_candles2, time_frame, time_frame2, suport_resitances, suport_resitances2, trend_line, fibonacci, gemini_key, gemini_key_2, symbol):
    print('bắt đầu tạo dự đoán tương lai')

    # Prompt template
    prompt_template = f"""
    {old_candles}
    Đây là dữ liệu nến (bao gồm cả thông tin Bollinger Bands) của {symbol} với khung thời gian {time_frame}, được cấu hình:
    <type>-<giá trên>-<giá dưới>-<time1>-<time2>-<high price from time1 to time2>-<low price from time1 to time2>-<lý do không dưới 100 ký tự> (type là support hoặc resistance, time1 time2 là bằng chứng).
    các vùng support và resitance của {time_frame}: {suport_resitances}.
    tiếp theo {old_candles2} Đây là dữ liệu nến (bao gồm cả thông tin Bollinger Bands) của {symbol} với khung thời gian {time_frame2}.
    các vùng support và resitance của {time_frame2}: {suport_resitances2}.
    thông tin fibonacci: {fibonacci}.
    Dựa trên phân tích Price Action, trendline, fibonacci, bollinger_band và các dữ liệu mà tôi cung cấp, hãy cung cấp giá sẽ đi như thế nào trong tương lai cho tôi để có thể vẽ đường line:

    ### Kết quả trả về:
    trả ra nhiều dự đoán theo định dạng:
    `future-<price1>-<price2>-<price3>-...-<priceN>-<lý do dài từ 150 tới 300 ký tự, trả lời bằng tiếng anh, nêu lý do sao cho hay để tôi có thể generate ra voice để đăng lên youtube>

    ### Yêu cầu bắt buộc:
    - price1 phải bắt đầu từ giá hiện tại là {old_candles[old_candles.__len__() - 1]['close']}.
    - phải có nhiều điểm giá để vẽ ZigZag.
    - Phải có ít nhất 4 điểm giá (price1 đến price4 trở lên) để có thể vẽ ZigZag.
    - Các điểm giá nên dao động lên xuống để phản ánh xu hướng thị trường.
    - nếu price1 của fibonacci < price2 của fiboonacci thì phân tích theo xu hướng tăng.
    - nếu price1 của fibonacci > price2 của fiboonacci thì phân tích theo xu hướng giảm.
    - bắt buộc phải cung cấp thông tin cho tôi, bao gồm:
    - cân nhắc kĩ trước khi đưa ra quyết định.
    - kết quả phải hợp lý và tiềm năng.

    **Không giải thích, không thêm nội dung nào khác. không xuống dòng, đầu và cuối không có khoảng cách. không được viết hoa, viết thường hết.**
    """

    # Gọi song song 5 lần generate_content
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(generate_content, prompt_template, gemini_key)
            for _ in range(5)
        ]
        prompts = [f.result() for f in futures]

    # Gộp kết quả vào final prompt
    final_prompt = f"""{old_candles} Đây là dữ liệu nến của {symbol} với khung thời gian {time_frame} phút. {old_candles2} Đây là dữ liệu nến của {symbol} với khung thời gian {time_frame2} phút. support and resistance: {suport_resitances} {suport_resitances2}. thông tin của fibonacci: {fibonacci}.
    thông tin dự đoán tương lai giá sẽ đi: {prompts}.
    Hãy lọc ra 1 dự đoán nào tiềm năng, lặp lại nhiều và hợp lý nhất và có thể dựa vào đó để trade trong các gợi ý trên. trả ra đúng định dạng:
    future-<price1>-<price2>-<price3>-...-<priceN>-<lý do, lấy lại lý do mà tôi đã cung cấp>.
    price1 phải bắt đầu từ giá hiện tại là {old_candles[old_candles.__len__() - 1]['close']}.
    Không thêm bất kỳ lời giải thích hay chú thích nào khác.
    """

    return generate_content(final_prompt, gemini_key_2)





def create_transition_gif(image1_path, image2_path, output_path, steps=10, duration=5):
    print('tạo gif')
    img1 = Image.open(image1_path).convert("RGBA")
    img2 = Image.open(image2_path).convert("RGBA")
    img2 = img2.resize(img1.size)

    frames = []

    # Fade out image1
    for i in range(steps + 1):
        alpha = 255 - int((i / steps) * 255)
        faded = img1.copy()
        faded.putalpha(alpha)

        frame = img2.copy()
        frame.paste(faded, (0, 0), faded)
        frames.append(frame)

    # Fade in image1
    for i in range(steps + 1):
        alpha = int((i / steps) * 255)
        faded = img1.copy()
        faded.putalpha(alpha)

        frame = img2.copy()
        frame.paste(faded, (0, 0), faded)
        frames.append(frame)

    # Convert frames to a format that imageio can handle
    frames = [frame.convert("RGB") for frame in frames]

    # Save as GIF using imageio
    imageio.mimsave(output_path, frames, duration=duration / 1000, loop=0)

def extract_data_future_number_or_reason(text, change_name=None, is_reason=False):
    parts = text.split('-')
    result = []
    reason = ''

    if parts[0].startswith("future"):
        # Đổi tên nếu có yêu cầu
        result.append(str(change_name) if change_name is not None else parts[0])
        
        for i in range(1, len(parts)):
            try:
                float(parts[i])  # kiểm tra nếu là số (gồm cả float)
                result.append(parts[i])
            except ValueError:
                # Khi gặp phần không phải số thì đó là lý do (reason)
                reason = '-'.join(parts[i:])
                break

    if is_reason:
        return reason.strip()

    # Dùng str(x) để tránh lỗi khi join nếu có phần tử không phải str
    return '-'.join([str(x) for x in result])

def generate_voice_azure(content, out_path):
    # Cấu hình
    print(f'bắt đầu tạo audio {out_path}')
    speech_config = speechsdk.SpeechConfig(subscription=azure_keys[0]['speech_key'], region=azure_keys[0]['service_region'])
    speech_config.speech_synthesis_voice_name = "en-US-GuyNeural" 

    # Tạo đối tượng synthesizer
    audio_config = speechsdk.audio.AudioOutputConfig(filename= out_path)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    result = synthesizer.speak_text_async(content).get()

    # Kiểm tra kết quả
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return True
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation = result.cancellation_details
        if cancellation.reason == speechsdk.CancellationReason.Error:
            print("Chi tiết:", cancellation.error_details)
        return False
    

def check_draw_done(file_path, text):
    if not os.path.exists(file_path):
        return False
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        first_line = file.readline().strip()
        first_line = re.sub(r'[^\x20-\x7E]', '', first_line)
        return text.strip().lower() in first_line.strip().lower()
    

def generate_voice_data(introduce_content, reason_contents, future_reason):
    print('bắt đầu tạo voice')
    generate_voice_azure(introduce_content, './audios/intro.mp3')
    for index, item in enumerate(reason_contents):
        generate_voice_azure(item, f'./audios/reason-{index + 1}.mp3')
    generate_voice_azure(future_reason, './audios/future-price.mp3')


def combine_image_audios(image_paths, audio_paths, intro_path,  output_path):
    clip_intro = VideoFileClip(intro_path)
    clip_intro = clip_intro.resized((1920, 1080))
    clips = [clip_intro]

   

    for image_path, audio_path in zip(image_paths, audio_paths):
        image_clip = ImageClip(image_path).resized((1920, 1080))
        audio_clip = AudioFileClip(audio_path)

        image_clip = image_clip.with_duration(audio_clip.duration)
        video_clip = image_clip.with_audio(audio_clip)

        clips.append(video_clip)

    # Nối tất cả các video clip lại
    final_clip = concatenate_videoclips(clips).resized((1920, 1080))

    # Xuất video ra file
    final_clip.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

def create_video_from_gif_and_audio(gif_path, audio_path, output_path):
    """
    Ghép ảnh GIF động và âm thanh thành video với độ dài chính xác bằng âm thanh, đồng thời chuẩn hóa video.
    """
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration

    cmd = [
        "ffmpeg",
        "-y",                           # Ghi đè file nếu tồn tại
        "-stream_loop", "-1",            # Lặp lại GIF vô hạn
        "-i", gif_path,                  # Đầu vào GIF
        "-i", audio_path,                # Đầu vào âm thanh
        "-t", str(duration),             # Đặt độ dài video bằng độ dài của âm thanh
        "-c:v", "libx264",               # Mã hóa video với codec x264
        "-c:a", "aac",                   # Mã hóa âm thanh với codec AAC
        "-b:a", "192k",                  # Bitrate âm thanh
        "-ar", "44100",                  # Tần số mẫu âm thanh
        "-ac", "2",                      # 2 kênh âm thanh
        "-pix_fmt", "yuv420p",           # Định dạng màu video
        "-movflags", "+faststart",       # Đảm bảo video có thể phát ngay lập tức
        "-vf", "fps=30,format=yuv420p",  # Tạo video với frame rate và định dạng chuẩn
        "-af", "aresample=async=1",      # Chuẩn hóa âm thanh
        "-preset", "fast",               # Tối ưu hóa tốc độ
        "-crf", "23",                    # Chất lượng video (lower = tốt hơn)
        "temp_video.mp4"
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"Video tạm đã được tạo: temp_video.mp4")

        # Chuẩn hóa video
        normalize_video("temp_video.mp4", output_path)
        print(f"Video đã được chuẩn hóa và lưu tại: {output_path}")

    except subprocess.CalledProcessError as e:
        print(f"Đã xảy ra lỗi trong quá trình tạo video: {e}")

    finally:
        # Xóa video tạm thời
        if os.path.exists("temp_video.mp4"):
            os.remove("temp_video.mp4")

def create_video_from_image_and_audio(image_path, audio_path, output_path):
    """
    Ghép hình ảnh và âm thanh thành video với độ dài chính xác bằng âm thanh, đồng thời chuẩn hóa video.
    """
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration

    cmd = [
        "ffmpeg",
        "-y",                           # Ghi đè file nếu tồn tại
        "-loop", "1",                    # Lặp hình ảnh
        "-framerate", "30",              # Đặt frame rate cố định
        "-i", image_path,                # Đầu vào hình ảnh
        "-i", audio_path,                # Đầu vào âm thanh
        "-t", str(duration),             # Đặt độ dài video bằng độ dài của âm thanh
        "-c:v", "libx264",               # Mã hóa video với codec x264
        "-tune", "stillimage",           # Tối ưu hóa cho hình ảnh tĩnh
        "-c:a", "aac",                   # Mã hóa âm thanh với codec AAC
        "-b:a", "192k",                  # Bitrate âm thanh
        "-ar", "44100",                  # Tần số mẫu âm thanh
        "-ac", "2",                      # 2 kênh âm thanh
        "-pix_fmt", "yuv420p",           # Định dạng màu video
        "-movflags", "+faststart",       # Đảm bảo video có thể phát ngay lập tức
        "-vf", "fps=30,format=yuv420p",  # Tạo video với frame rate và định dạng chuẩn
        "-af", "aresample=async=1",      # Chuẩn hóa âm thanh
        "-preset", "fast",               # Tối ưu hóa tốc độ
        "-crf", "23",                    # Chất lượng video (lower = tốt hơn)
        output_path
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"Video đã được tạo thành công: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Đã xảy ra lỗi trong quá trình tạo video: {e}")



def normalize_video(input_path, output_path):
    """Chuẩn hóa 1 video để tránh lỗi concat."""
    command = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-c:a", "aac",            # Chuyển âm thanh về codec aac
        "-b:a", "192k",           # Bitrate âm thanh
        "-ar", "44100",           # Tần số mẫu 44100Hz
        "-ac", "2", 
        "-vf", "fps=30,format=yuv420p",
        "-af", "aresample=async=1",
        "-preset", "fast",
        "-crf", "23",
        output_path
    ]

    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def concat_videos_ffmpeg(intro_path, video_paths, output_path):
    """
    Chuẩn hóa intro và nối nhiều video lại với nhau bằng ffmpeg.

    :param intro_path: Đường dẫn video mở đầu (intro).
    :param video_paths: Danh sách các video cần nối sau intro.
    :param output_path: Đường dẫn video đầu ra.
    """
    if not video_paths:
        print("Danh sách video rỗng.")
        return

    # # Tạo video intro chuẩn hóa tạm thời
    # normalized_intro_path = "normalized_intro.mp4"
    # normalize_video(intro_path, normalized_intro_path)

    # Danh sách video đã chuẩn hóa (gồm intro + các video chính)
    # all_videos = [normalized_intro_path] + video_paths
    all_videos = [] + video_paths

    # Tạo file input.txt
    with open("input.txt", "w", encoding="utf-8") as f:
        for path in all_videos:
            abs_path = os.path.abspath(path).replace("\\", "/")
            f.write(f"file '{abs_path}'\n")

    # Nối video
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", "input.txt",
        "-c", "copy",
        output_path
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"Đã nối xong video: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi nối video: {e}")
    finally:
        if os.path.exists("input.txt"):
            os.remove("input.txt")
        # if os.path.exists(normalized_intro_path):
        #     os.remove(normalized_intro_path)


def create_rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask

def update_thumbnail(
    image_path: str,
    output_path: str,
    text: str,
    position: tuple = (190, 880),
    font_path: str = "arial.ttf",
    font_size: int = 90,
    text_color: str = "#faff1c",
    rotation_angle: int = 8,  # Góc xoay chữ
    thickness: int = 2,        # Độ đậm (vẽ nhiều lớp)
    overlay_path: str = None,              # Đường dẫn ảnh chèn thêm
    overlay_path_2: str = None,              # Đường dẫn ảnh chèn thêm

):
    try:
        # Mở ảnh chính
        image = Image.open(image_path).convert("RGBA")

        # Tạo lớp ảnh tạm để vẽ chữ
        txt_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)

        # Tải font
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()
            print(f"[!] Không tìm thấy font {font_path}, dùng font mặc định.")

        # Tạo hiệu ứng chữ đậm giả
        x, y = position
        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                draw.text((x + dx, y + dy), text, font=font, fill=text_color)

        # Xoay lớp chữ nếu cần
        if rotation_angle != 0:
            txt_layer = txt_layer.rotate(rotation_angle, resample=Image.BICUBIC, center=position)

        # Ghép ảnh chính và chữ
        combined = Image.alpha_composite(image, txt_layer)

        # Thêm ảnh nhỏ vào
        if overlay_path:
            overlay = Image.open(overlay_path).convert("RGBA")
            overlay = overlay.resize((750, 350))
            width, height = overlay.size
            right_top_half = overlay.crop((
                200,    
                0,             
                width - 130,          
                height    
            ))
            rounded_mask = create_rounded_mask(right_top_half.size, radius=30)
            combined.paste(right_top_half, (50, 50), rounded_mask)
        if overlay_path_2:
            overlay = Image.open(overlay_path_2).convert("RGBA")
            overlay = overlay.resize((750, 350))
            width, height = overlay.size
            right_top_half = overlay.crop((
                100,    
                0,             
                width,          
                height     
            ))
            rounded_mask = create_rounded_mask(right_top_half.size, radius=30)
            combined.paste(right_top_half, (540, 50), rounded_mask)
        # Lưu kết quả
        combined.convert("RGB").save(output_path, format="JPEG", optimize=True)
        print(f"[✓] Đã lưu ảnh ra: {output_path}")

    except Exception as e:
        print(f"[X] Lỗi: {e}")


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


def upload_yt( user_data_dir, title, description, tags, video_path, video_thumbnail, is_short = False):
    ### dùng để tạo ra 1 user
    # chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    # user_data_dir = "C:/Path/To/Chrome/news-us"
    # subprocess.Popen([chrome_path, f'--remote-debugging-port=9223', f'--user-data-dir={user_data_dir}'])
    # time.sleep(5)


    # Tạo đối tượng ChromeOptions
    chrome_options = Options()

    # Chỉ định đường dẫn đến thư mục user data
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_argument(f"user-data-dir={user_data_dir}")
    chrome_options.add_argument("profile-directory=Default")  # Nếu bạn muốn sử dụng profile mặc định
    # chrome_options.add_argument("--headless")  # Chạy trong chế độ không giao diện
    # chrome_options.add_argument("--disable-gpu")  # Tắt GPU (thường dùng trong môi trường máy chủ)

    # Sử dụng Service để chỉ định ChromeDriver
    service = Service(ChromeDriverManager().install())


    # Khởi tạo WebDriver với các tùy chọn
    browser = webdriver.Chrome(service=service, options=chrome_options)

    browser.get("https://studio.youtube.com/")
    # await browser load end
    WebDriverWait(browser, 100).until(
        EC.presence_of_all_elements_located((By.ID, 'create-icon'))
    )


    browser.find_element(By.ID, 'create-icon').click()
    time.sleep(1)

    browser.find_element(By.ID, 'text-item-0').click()
    time.sleep(10)

    # upload video
    print('upload video in youtube')
    file_input = browser.find_elements(By.TAG_NAME, 'input')[1]
    file_input.send_keys(video_path)
    time.sleep(3)

    if is_short is False:
        # upload thumbnail
        print('upload thumbnail in youtube')
        WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.ID, 'file-loader'))
        )
        thumbnail_input = browser.find_element(By.ID, 'file-loader')
        thumbnail_input.send_keys(video_thumbnail)
        time.sleep(3)


    # enter title
    print('nhập title in youtube')
    WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.ID, 'textbox'))
    )
    title_input = browser.find_element(By.ID, 'textbox')
    title_input.clear()
    time.sleep(1)
    title_input.send_keys(title)
    time.sleep(1)

    # enter description
    print('nhập description in youtube')
    des_input = browser.find_elements(By.ID, 'textbox')[1]
    des_input.clear()
    time.sleep(1)
    des_input.send_keys(description)
    time.sleep(1)

    # enter hiển thị thêm
    # Đợi cho phần tử scrollable-content xuất hiện
    scrollable_element = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "scrollable-content"))
    )
    # Scroll xuống cuối cùng của phần tử scrollable-content
    browser.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", scrollable_element)
    time.sleep(2)

    WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.ID, 'toggle-button'))
    )
    show_more_btn = browser.find_element(By.ID, 'toggle-button')
    show_more_btn.click()
    time.sleep(2)

    # enter tags
    print('nhập tags in youtube')
    WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.ID, 'text-input'))
    )
    tags_input = browser.find_element(By.ID, 'text-input')
    tags_input.send_keys(tags)
    time.sleep(2)

    # next btn
    browser.find_element(By.ID, 'next-button').click()
    time.sleep(2)

    # next
    WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.ID, 'next-button'))
    )
    browser.find_element(By.ID, 'next-button').click()
    time.sleep(2)

    while True:
        element = browser.find_elements(By.XPATH, '//*[@check-status="UPLOAD_CHECKS_DATA_COPYRIGHT_STATUS_COMPLETED" or @check-status="UPLOAD_CHECKS_DATA_COPYRIGHT_STATUS_STARTED"]')
        
        if element:
            break  # Thoát vòng lặp nếu tìm thấy

        print("Chưa tìm thấy, tiếp tục kiểm tra...")
        time.sleep(2)  # Đợi 2 giây trước khi kiểm tra lại

    browser.find_element(By.ID, 'next-button').click()
    time.sleep(2)

    # chọn upload trực tiếp hay lên lịch
    current_time = datetime.now()
    current_hour = current_time.hour
        

    # done
    print('upload video in youtube thành công')
    WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.ID, 'done-button'))
    )
    browser.find_element(By.ID, 'done-button').click()

    time.sleep(10)
    browser.quit()

def trim_keywords_to_limit(keywords_str, limit=400):
    keywords = [kw.strip() for kw in keywords_str.split(',')]
    result = []
    total_length = 0

    for kw in keywords:
        kw_len = len(kw)
        # Cộng thêm 1 cho dấu phẩy nếu đã có từ trước
        if result:
            kw_len += 1
        if total_length + kw_len <= limit:
            result.append(kw)
            total_length += kw_len
        else:
            break

    return ",".join(result)