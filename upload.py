from util import count_files_in_mega_folder, get_file_from_mega, get_first_video_info, upload_yt
import os
import shutil
import time

count = count_files_in_mega_folder('price-action')
if(count == 2):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(base_dir, './videos')
    if os.path.exists(folder): shutil.rmtree(folder)
    os.makedirs(folder)
    get_file_from_mega('price-action', folder)
    
    thumbnail_path = f'{folder}/thumbnail.png'
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".mp4")]
    video = files[0]
    
    video_data = get_first_video_info()
    title = video_data.get("title")
    description = video_data.get("description")
    tags = video_data.get("tags")
    
    print(f'title: {title}')
    print(f'description: {description}')
    print(f'tags: {tags}')
    print(f'thumbnail: {thumbnail_path}')
    print(f'video: {video}')
    print('done')
    
    #upload video ------------------------------------------
    upload_yt(
        '',
        title,
        description,
        tags,
        video,
        thumbnail_path,
    )
else:
    print('wait')
    time.sleep(120)