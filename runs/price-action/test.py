from util import create_video_from_gif_and_audio, create_video_from_image_and_audio
import os
from concurrent.futures import ProcessPoolExecutor

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder_audio = f'{base_dir}/audios'
    folder_video = f'{base_dir}/videos'
    gif_path = f'{folder_video}/picture1.gif'
    folder_path = r'C:\Users\hoang nguyen\AppData\Roaming\MetaQuotes\Terminal\53785E099C927DB68A545C249CDBCE06\MQL5\Files'

    # Tạo thư mục nếu chưa tồn tại
    os.makedirs(folder_audio, exist_ok=True)
    os.makedirs(folder_video, exist_ok=True)

    print('generate video ---------------')

    images = [
        folder_path + f'/picture1.png',
        folder_path + f'/picture2.png',
        folder_path + f'/picture3.png',
        folder_path + f'/picture4.png',
    ]

    audios = [
        f'{folder_audio}/reason-1.mp3',
        f'{folder_audio}/reason-2.mp3',
        f'{folder_audio}/reason-3.mp3',
        f'{folder_audio}/future-price.mp3',
    ]

    data_video_paths = []
    data_video_paths.append(f'{folder_video}/video-1.mp4')

    # Dùng ProcessPoolExecutor trong block main
    with ProcessPoolExecutor() as executor:
        data = []
        intro_video = executor.submit(
            create_video_from_gif_and_audio,
            gif_path,
            f'{folder_audio}/intro.mp3',
            f'{folder_video}/video-1.mp4'
        )

        for index, item in enumerate(images):
            out_path = f'{folder_video}/video-{index + 2}.mp4'
            data.append(executor.submit(
                create_video_from_image_and_audio,
                item,
                audios[index],
                out_path
            ))
            data_video_paths.append(out_path)

        # Chờ các tiến trình hoàn tất
        intro_video.result()
        for item in data:
            item.result()

    print("✅ All videos generated:", data_video_paths)

# Bắt buộc có dòng này khi dùng multiprocessing trên Windows
if __name__ == '__main__':
    main()