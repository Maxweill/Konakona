import os
import random
import shutil
import datetime
import subprocess

import yaml
import tweepy


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
        'video_directory': data['altVidDirectory'],
        'file_ending': data['fileEnding'],

        'save': data['save'],
        'save_images': data['saveDirectory']['images'],
        'save_clips': data['saveDirectory']['clips'],

        'image_count': data['screenshot']['imageCount'],
        'image_seconds_apart': data['screenshot']['secondsApart'],

        'clip_count': data['clip']['clipCount'],
        'clip_seconds_apart': data['clip']['secondsApart'],
        'clip_length': data['clip']['clipLength'],
        'clip_subtitles':data['clip']['forceSubTrack'],
        'chance_clip': data['chance']['clip'],
        'chance_sub': data['chance']['subtitle']
    }

    return settings


def get_random_filepath(directory, file_ending):
    items = os.listdir(directory)
    #gather the list of valid files to work on, subdirectories and files of the correct filetype.
    matching_files = list(filter(lambda x: os.path.isfile(os.path.join(directory, x)) and x.endswith(file_ending), items))
    subdirectories = list(filter(lambda x: os.path.isdir(os.path.join(directory, x)), items))

    #pull one at random from the combined list    
    validchoices = matching_files+subdirectories
    random_selection = random.choice(validchoices)
    
    # if we picked a directory, then we should recursively traverse the tree
    if os.path.isdir(os.path.join(directory, random_selection)):
        random_file=get_random_filepath(os.path.join(directory, random_selection),file_ending)
    #otherwise, lets use the file
    elif os.path.isfile(os.path.join(directory, random_selection)):
        random_file=random_selection
    #finally, if there was no valid selection in our list, then quit out. if we were smarter we could probably make this
    #into a DFS, but i think for now we can say it's user error if there is a dead-end subdirectory.
    else:
        return ""
    
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


def generate_screenshot_local(filepath, duration, image_count, seconds_apart, use_subtitles):
    if image_count >= 5:
        image_count = random.randint(1, 4)

    random_time = random.uniform(0.00, duration - seconds_apart * image_count)

    output_name_list = []
    for i in range(image_count):
        output_name = f"out_{i}.png"
        output_name_list.append(output_name)
    
    vfString="scale=1920:-1"
    if use_subtitles:
        vfString="subtitles='"+filepath+"',"+vfString 
    for i in range(image_count):
        script = [
            'ffmpeg', '-y',
            '-ss', str(random_time),
            '-copyts',
            '-i', filepath,
            '-ss', str(random_time),
            '-vframes', '1',
            '-vf', vfString,
            '-q:v', '1',
            '-qmin', '1',
            output_name_list[i]
        ]

        random_time += seconds_apart
        subprocess.call(script)

    return output_name_list


def generate_clip_local(filepath, duration, clip_count, seconds_apart, clip_length,use_subtitles):
    if clip_count >= 5:
        clip_count = random.randint(1, 4)

    calc = seconds_apart * clip_count + float(clip_length) * clip_count
    random_time = random.uniform(0.00, duration - calc)

    output_video_list = []
    for i in range(clip_count):
        output_name = f"out_{i}.mp4"
        output_video_list.append(output_name)
    
    print("use subtitles:"+str(use_subtitles))
    vfString="scale=1280:-1"
    if use_subtitles:
        vfString="subtitles='"+filepath+"',"+vfString 
    for i in range(clip_count):
        script = [
            'ffmpeg', '-y',
            '-ss', str(random_time),
            '-copyts',
            '-i', filepath,
            '-ss', str(random_time),
            '-t', str(clip_length),
            '-ac', '2',
            '-sn',
            '-map_chapters', '-1',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-vf', vfString,
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            '-avoid_negative_ts', 'make_zero',
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


def post_update(upload):
    """
    upload with the v1.1 API and post with the v2 API
    I hate twitter
    """
    auth = tweepy.OAuth1UserHandler(
        config['consumer_key'],
        config['consumer_secret'],
        config['token'],
        config['token_secret']
    )
    api = tweepy.API(auth)

    media_ids = []
    for item in upload:
        response = api.media_upload(item)
        media_id = response.media_id_string
        media_ids.append(media_id)

    client = tweepy.Client(
        consumer_key=config['consumer_key'],
        consumer_secret=config['consumer_secret'],
        access_token=config['token'],
        access_token_secret=config['token_secret']
    )

    update = client.create_tweet(text="", media_ids=media_ids, media_tagged_user_ids=[])
    print(update)


def save_files(clip, output):
    output_path = config['save_clips'] if clip else config['save_images']
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')

    for item in output:
        shutil.move(item, output_path + timestamp + item)


if __name__ == '__main__':
    config = load_config()

    generateClip=check_generate(config['chance_clip'])
    directory = config['video_directory'] if generateClip else config['directory']
    if not directory: 
        directory=config['directory']
    filepath = get_random_filepath(directory, config['file_ending'])
    duration = get_file_length(filepath)
    useSubtitles = check_generate(config['chance_sub'])

    if generateClip:
        if config['clip_subtitles']: useSubtitles=True 
        output = generate_clip_local(filepath, duration, config['clip_count'], config['clip_seconds_apart'],
                                     config['clip_length'],useSubtitles)
    else:
        output = generate_screenshot_local(filepath, duration, config['image_count'], config['image_seconds_apart'],useSubtitles)

    post_update(output)

    if config['save']:
        save_files(check_generate(config['chance_clip']), output)
