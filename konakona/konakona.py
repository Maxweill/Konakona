import os
import base64
import random
import subprocess

import yaml
import pytwitter


def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(script_dir, 'config.yaml'), 'r') as stream:
        data = yaml.safe_load(stream)

    settings = {
        'consumer_key': data['twitter']['consumerKey'],
        'consumer_secret': data['twitter']['consumerSecret'],
        'token': data['twitter']['token'],
        'token_secret': data['twitter']['tokenSecret'],

        'directory': data['directory'],
        'file_ending': data['fileEnding'],

        'save': data['save'],
        'save_images': data['saveDirectory']['images'],
        'save_clips': data['saveDirectory']['clips'],

        'image_count': data['screenshot']['imageCount'],
        'image_seconds_apart': data['screenshot']['secondsApart'],

        'clip_count': data['clip']['clipCount'],
        'clip_seconds_apart': data['clip']['secondsApart'],
        'clip_length': data['clip']['clipLength'],

        'chance_clip': data['chance']['clip']
    }

    return settings


def get_random_filepath(directory, file_ending):
    file_list = os.listdir(directory)
    new_file_list = list(filter(lambda x: x.endswith(file_ending), file_list))

    random_file = random.choice(new_file_list)
    random_filepath = os.path.join(directory, random_file)

    return random_filepath


def get_file_length(filepath):
    script = [
        'ffprobe',
        '-i', filepath,
        '-show_entries', 'format=duration',
        '-v', 'quiet',
        '-of', 'csv=%s' % 'p=0'
    ]

    duration = subprocess.check_output(script)

    return float(duration)


def generate_screenshot_local(filepath, duration, image_count, seconds_apart):
    if image_count >= 5:
        image_count = random.randint(1, 4)

    random_time = random.uniform(0.00, duration - seconds_apart * image_count)
    output_name_list = ('out_0.png', 'out_1.png', 'out_2.png', 'out_3.png')

    for i in range(image_count):
        script = [
            'ffmpeg', '-y',
            '-ss', str(random_time),
            '-i', filepath,
            '-vframes', '1',
            '-vf', 'scale=1920:-1',
            '-q:v', '1',
            '-qmin', '1',
            output_name_list[i]
        ]

        random_time += seconds_apart
        subprocess.call(script)

    return output_name_list


def generate_clip_local(filepath, duration, clip_count, seconds_apart, clip_length):
    if clip_count >= 5:
        clip_count = random.randint(1, 4)

    calc = seconds_apart * clip_count + float(clip_length) * clip_count
    random_time = random.uniform(0.00, duration - calc)
    output_video_list = ('out_0.mp4', 'out_1.mp4', 'out_2.mp4', 'out_3.mp4')

    for i in range(clip_count):
        script = [
            'ffmpeg', '-y',
            '-ss', str(random_time),
            '-i', filepath,
            '-t', str(clip_length),
            '-ac', '2',
            '-sn',
            '-map_chapters', '-1',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-vf', 'scale=1280:-1',
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            output_video_list[i]
        ]

        random_time += clip_length + seconds_apart
        subprocess.call(script)

    return output_video_list


def check_generate(chance_clip):
    r = random.random()
    if r <= chance_clip:
        return True
    else:
        return False


def save_files(operation):
    """
    this function will be added later on
    """
    if operation:
        print('\nclip')
    if not operation:
        print('\nimage')


def post_update(upload):
    with open(upload, "rb") as image_file:
        data = {"media_data": base64.b64encode(image_file.read())}

    api = pytwitter.Api(consumer_key=config['consumer_key'],
                        consumer_secret=config['consumer_secret'],
                        access_token=config['token'],
                        access_secret=config['token_secret'])

    url = "https://upload.twitter.com/1.1/media/upload.json?media_category=tweet_image"

    response = api._request(url, verb="POST", data=data)
    media_id = response.json()["media_id"]
    result = api.create_tweet(
        text="", media_media_ids=[str(media_id)], media_tagged_user_ids=[])

    print(result)


if __name__ == '__main__':
    config = load_config()

    filepath = get_random_filepath(config['directory'], config['file_ending'])
    duration = get_file_length(filepath)

    if check_generate(config['chance_clip']):
        output = generate_clip_local(filepath, duration, config['clip_count'], config['clip_seconds_apart'],
                                     config['clip_length'])
    else:
        output = generate_screenshot_local(filepath, duration, config['image_count'], config['image_seconds_apart'])

    if config['save']:
        save_files(check_generate(config['chance_clip']))

    post_update(output)
