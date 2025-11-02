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
import pandas as pd
import pyperclip

import time
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


gemini_keys = ['AIzaSyC4ZvI-VjW3GPf9DMzZT4iOMmT6DvjUH-8']
azure_keys = [
    {
        "speech_key": "2JgozCp7ZimaAYM2TlazGQGu7YjMzcZroS9YFQgnkuFcy6KlloLsJQQJ99BEAC3pKaRXJ3w3AAAYACOGTYKT",
        "service_region": "eastasia" 
    }
]

def connect_to_mt5(login, password, server, terminal):
    mt5.initialize(path= terminal, login= login,password= password,server= server)

def get_candles_simple(symbol: str, timeframe: int, n_candles: int = 180) -> list:
    if not mt5.initialize():
        raise Exception(f"Không thể khởi tạo MT5: {mt5.last_error()}")

    if not mt5.symbol_select(symbol, True):
        mt5.shutdown()
        raise Exception(f"Không thể chọn symbol: {symbol}")

    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n_candles)
    mt5.shutdown()

    if rates is None or len(rates) == 0:
        raise Exception("Không có dữ liệu được trả về.")

    df = pd.DataFrame(rates)
    df['time'] = df['time'].astype(int)

    result = []
    for i, row in df.iterrows():
        result.append({
            "time": int(row['time']),
            "tick_volume": int(row['tick_volume']),
            "time_readable": datetime.utcfromtimestamp(int(row['time'])).strftime('%Y-%m-%d %H:%M:%S'),
            "open": float(row['open']),
            "close": float(row['close']),
            "high": float(row['high']),
            "low": float(row['low'])
        })

    return result
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
                if len(parts) == 9:
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
                            "bollinger_band_lower": float(parts[7]),
                            "tick_volume": float(parts[8])
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
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
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

    prompt_base = f"""{old_candles}
    Đây là thông tin của các cây nến (bao gồm cả thông tin Bollinger Bands) khung {time_frame} của {symbol}.
    Áp dụng phương pháp price action, vui lòng trả lời cho tôi 1 vùng support và 1 vùng resistance tốt nhất.

    Yêu cầu:
    - Support phải dưới giá {low}, resistance phải trên giá {high}.
    - Hai vùng **không được gần nhau**: khoảng cách giữa **giá trên của support** và **giá dưới của resistance** phải **ít nhất bằng 1.5% giá hiện tại**.
    - Ưu tiên vùng có **nhiều lần chạm lại (touchback)** hoặc **đi ngang (sideway accumulation)** rõ ràng.
    - Không chọn vùng ngay sát nhau như “đè lên”.
    - Mỗi vùng nên bao phủ **ít nhất 2 cây nến quan trọng** (có thân lớn hoặc bóng dài).
    
    ❗❗❗ RẤT QUAN TRỌNG:
    - KHÔNG TRẢ DƯỚI DẠNG JSON, KHÔNG TRẢ DƯỚI DẠNG DANH SÁCH, KHÔNG TRẢ DƯỚI DẠNG OBJECT.
    - CHỈ TRẢ VỀ **chuỗi văn bản duy nhất**, theo đúng định dạng:
    <type>-<giá trên>-<giá dưới>-<time1>-<time2>-<high price from time1 to time2>-<low price from time1 to time2>-<lý do>
    - Không có ký tự nào khác, không có dấu ngoặc, không xuống dòng thừa.
    - Nếu có 2 vùng (support và resistance), trả mỗi vùng trên 1 dòng, không bọc JSON.

    Yêu cầu chi tiết:
    - type: phải là "support" hoặc "resistance", viết thường.
    - time1, time2: là **UNIX timestamp (ví dụ: 1761867900)**, không được viết chữ, không định dạng ngày giờ.
    - high price from time1 to time2 và low price from time1 to time2: là giá cao nhất và thấp nhất trong khoảng đó.
    - lý do: phải dài ít nhất 250 ký tự, viết bằng tiếng Anh, giải thích logic tại sao vùng đó hình thành (không được ghi trực tiếp giá, mà phải nói kiểu “from price to price”), không cần nêu hướng trade.
    - bắt buộc phải trả ra kết quả
    """

    content = generate_content(prompt_base, gemini_key)

    return content

def generate_trendline(old_candles, time_frame, gemini_key, symbol):
    print('bắt đầu tạo trendline')

    # Prompt template
    prompt_template = f"""
    {old_candles}
    Đây là dữ liệu nến (bao gồm cả thông tin Bollinger Bands) của {symbol} với khung thời gian {time_frame}.

    Dựa trên phân tích Price Action, hãy tìm **1 trendline duy nhất** thoả điều kiện sau:

    ### Yêu cầu bắt buộc:
    - trendline phải được vẽ gần với giá hiện tại (ưu tiên cây nến cuối cùng, rất quan trọng).
    - chỉ sử dụng dữ liệu tôi cung cấp, không được dự đoán tương lai.
    - nếu giá đi ngang hoặc không tìm được đường thỏa điều kiện trên thì trả về `null`.
    - trendline phải gần sát với giá hiện tại trong cây nến cuối cùng mà tôi cung cấp: {old_candles[-1]}.

    ### Kết quả trả về:
    ❗❗❗ RẤT QUAN TRỌNG:
    - KHÔNG TRẢ DƯỚI DẠNG JSON, KHÔNG TRẢ DƯỚI DẠNG DANH SÁCH, KHÔNG TRẢ DƯỚI DẠNG OBJECT.
    - CHỈ TRẢ VỀ **chuỗi văn bản duy nhất**, theo đúng định dạng:
    trendline-<price1>-<price2>-<time1>-<time2>
    - Không có ký tự nào khác, không có dấu ngoặc, không xuống dòng thừa.
    Trả **chính xác 1 dòng duy nhất**

    ### Quy định định dạng:
    - tất cả viết thường, không có chữ hoa.
    - không xuống dòng, không thêm dấu chấm, dấu phẩy hay ký tự nào khác ngoài dấu gạch ngang (-).
    - <time1> và <time2> phải là **UNIX timestamp** (ví dụ: 1761867900), tuyệt đối không được viết dạng ngày/giờ.
    - chỉ trả kết quả duy nhất, không có mô tả, không có lời giải thích.
    """
    
    content = generate_content(prompt_template, gemini_key)


  

    return content


def generate_fibonacci(old_candles, time_frame, suport_resitances, trend_line, gemini_key, symbol):
    print('bắt đầu tạo fibonacci')

    # Prompt template
    prompt_template = f"""
    {old_candles}
    Đây là dữ liệu nến (bao gồm cả thông tin Bollinger Bands) của {symbol} với khung thời gian {time_frame}, được cấu hình theo định dạng:
    <type>-<giá trên>-<giá dưới>-<time1>-<time2>-<high price from time1 to time2>-<low price from time1 to time2>-<lý do>
    (type là support hoặc resistance, time1 và time2 là bằng chứng).

    Các vùng support và resistance: {suport_resitances}.
    Đường trendline của khung lớn hơn: {trend_line}.

    Dựa trên phân tích Price Action và các dữ liệu tôi cung cấp, hãy xác định thông tin **fibonacci** phù hợp để phục vụ việc trade.

    ### Kết quả trả về:
    Chỉ trả đúng **1 dòng duy nhất**, theo định dạng:
    `fibonacci-<price1>-<price2>-<time1>-<time2>`

    ### Quy định bắt buộc:
    - tất cả viết thường, không viết hoa, không có ký tự nào khác ngoài dấu gạch ngang (-).
    - không xuống dòng, không khoảng trắng đầu hoặc cuối.
    - <time1> và <time2> phải là **UNIX timestamp** (ví dụ: 1761867900), tuyệt đối không được viết dạng ngày/giờ.
    - fibonacci phải hợp lý và tiềm năng, dựa trên cấu trúc giá hiện tại.
    - nếu xu hướng được phân tích là tăng → price1 < price2.
    - nếu xu hướng được phân tích là giảm → price1 > price2.
    - fibonacci phải gần với giá của cây nến cuối cùng (ưu tiên cao nhất).
    - nếu không thể xác định được fibonacci hợp lệ thì trả về `null`.

    **Chỉ trả kết quả duy nhất, không kèm lời giải thích hoặc mô tả.**
    """

    # Gọi song song 5 lần generate_content
    content = generate_content( prompt_template, gemini_key)
    return content


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
    Dựa trên phân tích Price Action, tick_volume, trendline, fibonacci, bollinger_band và các dữ liệu mà tôi cung cấp, hãy cung cấp giá sẽ đi như thế nào trong tương lai cho tôi để có thể vẽ đường line:

    ### Kết quả trả về:
    trả ra nhiều dự đoán theo định dạng:
    `future-<price1>-<price2>-<price3>-...-<priceN>-<lý do dài trên 250 ký tự, trả lời bằng tiếng anh, nêu lý do sao cho hay để tôi có thể generate ra voice để đăng lên youtube>

    ### Yêu cầu bắt buộc:
    - price1 phải bắt đầu từ giá hiện tại là {old_candles[-1]['close']}.
    - phải có nhiều điểm giá để vẽ ZigZag.
    - Phải có ít nhất 4 điểm giá (price1 đến price4 trở lên).
    - Tối đa chỉ được có 6 điểm giá (price1 đến price6).
    - Các điểm giá nên dao động lên xuống để phản ánh xu hướng thị trường.
    - nếu price1 của fibonacci < price2 của fibonacci thì phân tích theo xu hướng tăng.
    - nếu price1 của fibonacci > price2 của fibonacci thì phân tích theo xu hướng giảm.
    - bắt buộc phải cung cấp thông tin cho tôi, bao gồm:
    - cân nhắc kỹ trước khi đưa ra quyết định.
    - kết quả phải hợp lý và tiềm năng.

    **Không giải thích, không thêm nội dung nào khác. không xuống dòng, đầu và cuối không có khoảng cách. không được viết hoa, viết thường hết.**
    """

  
    prompts = generate_content( prompt_template, gemini_key)

    # Gộp kết quả vào final prompt
    final_prompt = f"""{old_candles} Đây là dữ liệu nến của {symbol} với khung thời gian {time_frame} phút. {old_candles2} Đây là dữ liệu nến của {symbol} với khung thời gian {time_frame2} phút. support and resistance: {suport_resitances} {suport_resitances2}. thông tin của fibonacci: {fibonacci}.
    thông tin dự đoán tương lai giá sẽ đi: {prompts}.
    Hãy lọc ra 1 dự đoán nào tiềm năng, lặp lại nhiều và hợp lý nhất và có thể dựa vào đó để trade trong các gợi ý trên. trả ra đúng định dạng:
    future-<price1>-<price2>-<price3>-...-<priceN>-<lý do, lấy lại lý do mà tôi đã cung cấp>.
    price1 phải bắt đầu từ giá hiện tại là {old_candles[old_candles.__len__() - 1]['close']}.
    Không thêm bất kỳ lời giải thích hay chú thích nào khác.
    """

    return generate_content(final_prompt, gemini_key_2)



def generate_bearish_or_bullish(content, gemini_key):
    print('bắt đầu phân biejt là tăng hay giảm')

    # Prompt template
    prompt_template = f"""
    tôi có dự toán tương lại như sau: {content}.
    bạn phải cho tôi biết dự đoán này là tăng hay giảm, nếu tăng thì bạn trả ra là bullish, còn nếu giảm thì trả ra là bearish.

    **Không giải thích, không thêm nội dung nào khác. không xuống dòng, đầu và cuối không có khoảng cách. không được viết hoa, viết thường hết. chỉ ghi là bullish hoặc bearish**
    """

    content = generate_content( prompt_template, gemini_key)
    return content





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
    

def generate_voice_data(introduce_content, reason_contents, future_reason, folder_audio):
    print('bắt đầu tạo voice')
    generate_voice_azure(introduce_content, f'{folder_audio}/intro.mp3')
    for index, item in enumerate(reason_contents):
        generate_voice_azure(item, f'{folder_audio}/reason-{index + 1}.mp3')
    generate_voice_azure(future_reason, f'{folder_audio}/future-price.mp3')


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
    # Dùng context manager để tự động đóng audio_clip
    with AudioFileClip(audio_path) as audio_clip:
        duration = audio_clip.duration

    cmd = [
        "ffmpeg",
        "-y",
        "-stream_loop", "-1",
        "-i", gif_path,
        "-i", audio_path,
        "-t", str(duration),
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "44100",
        "-ac", "2",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-vf", "fps=30,format=yuv420p",
        "-af", "aresample=async=1",
        "-preset", "fast",
        "-crf", "23",
        "temp_video.mp4"
    ]

    try:
        subprocess.run(cmd, check=True)
        print("✅ Video tạm đã được tạo: temp_video.mp4")

        normalize_video("temp_video.mp4", output_path)
        print(f"✅ Video đã được chuẩn hóa và lưu tại: {output_path}")

    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi tạo video: {e}")

    finally:
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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    intro_path = f'{base_dir}/public/intro.mp4'
    
    all_videos = [intro_path] + video_paths

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

def format_utc_time_range(days: int = 7) -> str:
    dt_start = datetime.now(timezone.utc)
    dt_end = dt_start + timedelta(days=days)

    start_str = dt_start.strftime("%d/%m")
    end_str = dt_end.strftime("%d/%m/%Y")

    return f"{start_str} - {end_str}"

def upload_yt(user_data_dir, title, description, tags, video_path, video_thumbnail, comment=None, is_not_wait_check=False):
    # dùng để tạo ra 1 user
    # chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    # user_data_dir = "C:/Path/To/Chrome/news-us"
    # subprocess.Popen([chrome_path, f'--remote-debugging-port=9223', f'--user-data-dir={user_data_dir}'])
    # time.sleep(5)

    # Tạo đối tượng ChromeOptions
    chrome_options = Options()

    # Chỉ định đường dẫn đến thư mục user data
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_argument(f"user-data-dir={user_data_dir}")
    # Nếu bạn muốn sử dụng profile mặc định
    chrome_options.add_argument("profile-directory=Default")
    # chrome_options.add_argument("--headless")  # Chạy trong chế độ không giao diện
    # chrome_options.add_argument("--disable-gpu")  # Tắt GPU (thường dùng trong môi trường máy chủ)

    # Sử dụng Service để chỉ định ChromeDriver
    service = Service(ChromeDriverManager().install())

    # Khởi tạo WebDriver với các tùy chọn
    browser = webdriver.Chrome(service=service, options=chrome_options)

    browser.get("https://studio.youtube.com/")
    # await browser load end
    element = WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//ytcp-button[@icon="yt-sys-icons:video_call"]'))
    )
    element.click()
    time.sleep(1)

    WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable((By.ID, 'text-item-0'))
    )

    browser.find_element(By.ID, 'text-item-0').click()
    time.sleep(10)

    # upload video
    print('upload video in youtube')
    WebDriverWait(browser, 100).until(
        lambda d: len(d.find_elements(By.TAG_NAME, 'input')
                      ) > 1  # Đảm bảo có ít nhất 2 input
    )

    file_input = browser.find_elements(By.TAG_NAME, 'input')[1]
    file_input.send_keys(video_path)
    time.sleep(3)

    # upload thumbnail
    print('upload thumbnail in youtube')
    WebDriverWait(browser, 100).until(
        EC.presence_of_all_elements_located((By.ID, 'file-loader'))
    )
    thumbnail_input = browser.find_element(By.ID, 'file-loader')
    thumbnail_input.send_keys(video_thumbnail)
    time.sleep(3)

    # enter title
    print('nhập title in youtube')
    WebDriverWait(browser, 100).until(
        EC.presence_of_all_elements_located((By.ID, 'textbox'))
    )

    title_input = browser.find_element(By.ID, 'textbox')

    check_clean_title = False
    while check_clean_title is False:
        # Xoá bằng Ctrl+A + Delete
        title_input.send_keys(Keys.CONTROL, "a")
        title_input.send_keys(Keys.DELETE)
        title_input.clear()
        time.sleep(1)
        if title_input.text.strip() == "":
            check_clean_title = True

    time.sleep(1)
    title_input.send_keys(title)
    time.sleep(1)

    # enter description
    print('nhập description in youtube')
    des_input = browser.find_elements(By.ID, 'textbox')[1]
    des_input.clear()
    time.sleep(1)
    # Copy vào clipboard
    pyperclip.copy(description)
    des_input.click()
    time.sleep(1)
    des_input.send_keys(Keys.CONTROL, 'v')
    time.sleep(1)

    # enter hiển thị thêm
    # Đợi cho phần tử scrollable-content xuất hiện
    scrollable_element = WebDriverWait(browser, 100).until(
        EC.presence_of_element_located((By.ID, "scrollable-content"))
    )
    # Scroll xuống cuối cùng của phần tử scrollable-content
    browser.execute_script(
        "arguments[0].scrollTo(0, arguments[0].scrollHeight);", scrollable_element)
    time.sleep(2)

    WebDriverWait(browser, 100).until(
        EC.presence_of_all_elements_located((By.ID, 'toggle-button'))
    )
    show_more_btn = browser.find_element(By.ID, 'toggle-button')
    show_more_btn.click()
    time.sleep(2)

    # enter tags
    print('nhập tags in youtube')
    WebDriverWait(browser, 100).until(
        EC.presence_of_all_elements_located((By.ID, 'text-input'))
    )
    tags_input = browser.find_element(By.ID, 'text-input')
    tags_input.send_keys(tags)
    time.sleep(2)

    # next btn
    browser.find_element(By.ID, 'next-button').click()
    time.sleep(10)

    # # add end screens
    # WebDriverWait(browser, 10).until(
    #     EC.presence_of_all_elements_located((By.ID, 'endscreens-button'))
    # )
    # browser.find_element(By.ID, 'endscreens-button').click()
    # time.sleep(2)
    # canvas_element = WebDriverWait(browser, 10).until(
    #     EC.element_to_be_clickable((By.TAG_NAME, "canvas"))
    # )
    # browser.execute_script("arguments[0].click();", canvas_element)
    # time.sleep(2)
    # browser.find_element(By.ID, 'save-button').click()
    # time.sleep(4)

    # next
    WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable((By.ID, 'next-button'))
    )
    browser.find_element(By.ID, 'next-button').click()
    time.sleep(10)

    while is_not_wait_check is False:
        try:
            element = browser.find_elements(
                By.XPATH, '//*[@check-status="UPLOAD_CHECKS_DATA_COPYRIGHT_STATUS_COMPLETED" or @check-status="UPLOAD_CHECKS_DATA_COPYRIGHT_STATUS_STARTED"]')
            if element:
                break  # Thoát vòng lặp nếu tìm thấy
        except:
            print('')
        print("Chưa tìm thấy, tiếp tục kiểm tra...")
        time.sleep(2)  # Đợi 2 giây trước khi kiểm tra lại

    WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable((By.ID, 'next-button'))
    )
    browser.find_element(By.ID, 'next-button').click()
    time.sleep(2)

    # done
    print('upload video in youtube thành công')
    WebDriverWait(browser, 100).until(
        EC.element_to_be_clickable((By.ID, 'done-button'))
    )
    browser.find_element(By.ID, 'done-button').click()

    # vào youtube để nhập bình luận
    if comment is not None:
        WebDriverWait(browser, 100).until(
            EC.presence_of_all_elements_located((By.ID, 'share-url'))
        )
        link_redirect = browser.find_element(By.ID, 'share-url')
        href = link_redirect.get_attribute('href')
        browser.get(href)
        WebDriverWait(browser, 100).until(
            EC.presence_of_all_elements_located((By.ID, 'above-the-fold'))
        )
        time.sleep(5)
        is_Find_comment = False
        while is_Find_comment is False:
            try:
                browser.execute_script("window.scrollBy(0, 50);")
                time.sleep(1)
                comment_box = browser.find_element(
                    By.ID, 'simplebox-placeholder')
                if (comment_box):
                    is_Find_comment = True
                time.sleep(3)
            except:
                time.sleep(3)

        comment_box = browser.find_element(By.ID, 'simplebox-placeholder')
        comment_box.click()
        textarea = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div#contenteditable-root[contenteditable='true']"))
        )
        pyperclip.copy(comment)
        textarea.click()
        time.sleep(1)
        textarea.send_keys(Keys.CONTROL, 'v')
        time.sleep(2)
        submit_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "submit-button"))
        )
        submit_button.click()

    try:
        WebDriverWait(browser, 30).until(
            EC.element_to_be_clickable((By.ID, 'secondary-action-button'))
        )
        browser.find_element(By.ID, 'secondary-action-button').click()
    except:
        print('Không tồn tại dialog')
    
    time.sleep(10)
    WebDriverWait(browser, 100).until(
        EC.presence_of_element_located(
            (By.XPATH, "//tp-yt-paper-dialog[@id='dialog']"))
    )
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


def create_thumbnail(
    background_path: str,
    overlay_path: str,
    output_path: str = "result.jpg",
    left: int = 0,
    top: int = 0,
    overlay_size: tuple | None = None,
    opacity: float = 1.0,
    border_radius: int = 0,
    symbol: str | None = None,
    day: str | None = None,
    des: str | None = None,
):
    # Mở ảnh
    bg = Image.open(background_path).convert("RGBA")
    ol = Image.open(overlay_path).convert("RGBA")

    # Resize nếu có
    if overlay_size:
        ol = ol.resize(overlay_size)

    # Bo góc nếu có
    if border_radius > 0:
        mask = Image.new("L", ol.size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle([(0, 0), ol.size], radius=border_radius, fill=255)
        ol.putalpha(mask)

    # Giảm độ trong suốt nếu có
    if opacity < 1.0:
        alpha = ol.getchannel("A")
        alpha = alpha.point(lambda p: int(p * opacity))
        ol.putalpha(alpha)

    # Dán overlay lên background
    bg.paste(ol, (left, top), ol)

    # Nếu có text thì tự động chèn vào giữa overlay
    if symbol:
        draw = ImageDraw.Draw(bg)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(base_dir, './public/inter/Inter_28pt-Bold.ttf')
        font = ImageFont.truetype(font_path, size=190)

        text_x = 185
        text_y = 505

        # Viền mờ cho dễ đọc
        shadow_offset = 2
        draw.text((text_x + shadow_offset, text_y + shadow_offset), symbol, font=font, fill=(0, 0, 0))
        draw.text((text_x, text_y), symbol, font=font, fill=(255, 255, 255))

    if des:
        draw = ImageDraw.Draw(bg)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(base_dir, './public/inter/Inter_28pt-SemiBold.ttf')
        font = ImageFont.truetype(font_path, size=83)

        # Vùng chứa text
        box_x = 185
        box_y = 895
        box_width = 1670

        # ✅ Tính kích thước chữ
        try:
            bbox = draw.textbbox((0, 0), des, font=font)
            text_width = bbox[2] - bbox[0]
        except AttributeError:
            text_width, text_height = draw.textsize(des, font=font)

        # ✅ Căn giữa theo chiều ngang
        text_x = box_x + (box_width - text_width) // 2
        text_y = box_y

        # ✅ Viền mờ cho dễ đọc
        shadow_offset = 2
        draw.text((text_x + shadow_offset, text_y + shadow_offset), des, font=font, fill=(0, 0, 0))
        draw.text((text_x, text_y), des, font=font, fill=(255, 255, 255))

    if day:
        draw = ImageDraw.Draw(bg)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(base_dir, './public/inter/Inter_28pt-SemiBold.ttf')
        font = ImageFont.truetype(font_path, size=100)

        # Vị trí khung chứa text
        box_x = 190
        box_y = 355
        box_width = 748

        # ✅ Tính kích thước chữ
        try:
            bbox = draw.textbbox((0, 0), day, font=font)
            text_width = bbox[2] - bbox[0]
        except AttributeError:
            text_width, text_height = draw.textsize(day, font=font)

        # ✅ Căn giữa theo chiều ngang trong khung 748px
        text_x = box_x + (box_width - text_width) // 2
        text_y = box_y

        # ✅ Viền mờ cho dễ đọc
        shadow_offset = 2
        draw.text((text_x + shadow_offset, text_y + shadow_offset), day, font=font, fill=(0, 0, 0))
        draw.text((text_x, text_y), day, font=font, fill=(0, 0, 0))

    # Lưu ảnh
    bg.convert("RGB").save(output_path)
    print(f"✅ Ảnh đã lưu tại: {output_path} (tọa độ: left={left}, top={top})")


def open_chrome_to_edit(yt_path, driver_path="C:/Program Files/Google/Chrome/Application/chrome.exe"):
    user_data_dir = yt_path
    process = subprocess.Popen(
        [driver_path, f'--remote-debugging-port=9223', f'--user-data-dir={user_data_dir}'])
    input('nhấn bất kì để đóng chrome:')
    process.terminate()  # gửi tín hiệu terminate
    try:
        process.wait(timeout=30)  # đợi chrome tắt
    except subprocess.TimeoutExpired:
        process.kill()  # nếu không tắt thì kill hẳn là sao không hiểu
        
        
def check_identity_verification(yt_path):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        video_path = f"{base_dir}/public/intro.mp4"
        thumb_path = f"{base_dir}/public/thumbnail-price-action.png"
        user_data_dir = yt_path

        # Tạo đối tượng ChromeOptions
        chrome_options = Options()

        # Chỉ định đường dẫn đến thư mục user data
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        user_data_dir_abspath = os.path.abspath(user_data_dir)
        chrome_options.add_argument(f"user-data-dir={user_data_dir_abspath}")
        # Nếu bạn muốn sử dụng profile mặc định
        chrome_options.add_argument("profile-directory=Default")
        # chrome_options.add_argument("--headless")  # Chạy trong chế độ không giao diện
        # chrome_options.add_argument("--disable-gpu")  # Tắt GPU (thường dùng trong môi trường máy chủ)

        # Sử dụng Service để chỉ định ChromeDriver
        service = Service(ChromeDriverManager().install())

        # Khởi tạo WebDriver với các tùy chọn
        browser = webdriver.Chrome(service=service, options=chrome_options)

        browser.get("https://studio.youtube.com/")
        # await browser load end
        element = WebDriverWait(browser, 100).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//ytcp-button[@icon="yt-sys-icons:video_call"]'))
        )
        element.click()
        time.sleep(1)

        WebDriverWait(browser, 100).until(
            EC.element_to_be_clickable((By.ID, 'text-item-0'))
        )

        browser.find_element(By.ID, 'text-item-0').click()
        time.sleep(10)

        # upload video
        print('upload video in youtube')
        # chờ tối đa 100 giây cho ít nhất 2 input xuất hiện
        WebDriverWait(browser, 100).until(
            lambda d: d.find_elements(By.TAG_NAME, 'input') if len(
                d.find_elements(By.TAG_NAME, 'input')) > 1 else False
        )
        file_input = browser.find_elements(By.TAG_NAME, 'input')[1]
        file_input.send_keys(video_path)
        time.sleep(3)

        # upload thumbnail
        print('upload thumbnail in youtube')
        WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'file-loader'))
        )
        thumbnail_input = browser.find_element(By.ID, 'file-loader')
        thumbnail_input.send_keys(thumb_path)
        time.sleep(3)
    except:
        print('error')

    input('nhấn bất kì để đóng chrome:')
    browser.quit()