import os
import random
import shutil
import datetime
import subprocess

import config
import twitter


# config
script_dir = os.path.dirname(os.path.abspath(__file__))

try:
    cfg = config.Config(os.path.join(script_dir, 'settings.cfg'))
except config.ConfigFormatError:
    print('Error: Check settings.cfg')
    exit()

# settings
directory = cfg['general.directory']
save = cfg['general.save']
multi_chance = cfg['general.multi.chance']
img_num = cfg['general.multi.img_num']
sec_apart = cfg['general.multi.sec_apart']
image_directory = cfg['general.image.directory']
video_directory = cfg['general.video.directory']
clip_length = cfg['general.video.length']
video_chance = cfg['general.video.chance']

# twitter keys
CONSUMER_KEY_INPUT = cfg['keys.consumer.key']
CONSUMER_SECRET_INPUT = cfg['keys.consumer.secret']
ACCESS_TOKEN_KEY_INPUT = cfg['keys.access.key']
ACCESS_TOKEN_SECRET_INPUT = cfg['keys.access.secret']

# etc.
now = datetime.datetime.now()
tmpfile_img = os.path.join(script_dir, cfg['etc.tmpfile.img'])
tmpfile_vid = os.path.join(script_dir, cfg['etc.tmpfile.vid'])
tmpfile_img_alt = os.path.join(script_dir, cfg['etc.tmpfile_alt.img'], now.strftime('%Y%m%d-%H%M%S.jpg'))
tmpfile_vid_alt = os.path.join(script_dir, cfg['etc.tmpfile_alt.vid'], now.strftime('%Y%m%d-%H%M%S.mp4'))


# randomly select a mkv video from input directory
# look at help diagram to understand which use cases are supported
def get_random_video_filepath(directory):
    outdir = ''
    direc = directory
    while os.path.isdir(direc):
        outdir += random.choice(os.listdir(direc))
        if outdir.endswith(('mkv', 'mp4', 'avi', 'webm')):
            break
        else:
            outdir += '/'
            direc += outdir
    return outdir


# use ffmpeg to generate screenshot at timestamp
def generate_random_screenshot_locally(filepath, random_time, tmpfile_img):
    command_img = [
        'ffmpeg', '-y',
        '-ss', str(random_time),
        '-i', filepath,
        '-vframes', '1',
        '-vf', 'scale=1920:-1',
        '-q:v', '1',
        '-qmin', '1',
        tmpfile_img
    ]
    subprocess.call(command_img)
    return tmpfile_img


# use ffmpeg to generate clip at timestamp
def generate_random_clip_locally(filepath):
    random_time = random.uniform(0.00, get_length(filepath) - float(clip_length))
    command_vid = [
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
        tmpfile_vid
    ]
    subprocess.call(command_vid)
    return tmpfile_vid


# using normal image generation multiple times
def generate_multi_screenshots_locally(filepath, tmpfile_img, img_num):
    if img_num < 1 or img_num > 4:
        print('Error: Check img_num in settings')
        exit()
    elif img_num == 1:
        img_num = random.randint(1, 4)

    image_list = []
    random_time = random.uniform(0.00, get_length(filepath) - sec_apart * 4)
    tmpfile_img_name, extension = os.path.splitext(tmpfile_img)

    for i in range(img_num):
        counter = i
        tmpfile_img = tmpfile_img_name + str(counter) + extension
        image_list.append(generate_random_screenshot_locally(filepath, random_time, tmpfile_img))
        random_time += sec_apart
    return image_list


# use ffprobe to get the length of the video
def get_length(filepath):
    command_info = [
        'ffprobe',
        '-i', filepath,
        '-show_entries', 'format=duration',
        '-v', 'quiet',
        '-of', 'csv=%s' % 'p=0'
    ]
    duration = subprocess.check_output(command_info)
    return float(duration)


# uploads the screenshot/clip to twitter
def post_update(tmpfile):
    try:
        api = twitter.Api(consumer_key=CONSUMER_KEY_INPUT,
                          consumer_secret=CONSUMER_SECRET_INPUT,
                          access_token_key=ACCESS_TOKEN_KEY_INPUT,
                          access_token_secret=ACCESS_TOKEN_SECRET_INPUT)
        return api.PostUpdate('', tmpfile)
    except twitter.error.TwitterError:
        print('Error: Invalid key')


# checks if we should generate a screenshot or clip
def check_video():
    r = random.random()
    if r <= video_chance:
        return True
    else:
        return False


# checks if we should generate multiple screenshots
def check_multi():
    r = random.random()
    if r <= multi_chance:
        return True
    else:
        return False


if __name__ == '__main__':
    # determine if we should generate a video or screenshot
    should_generate_video = check_video()

    # determine if multiple images should generate
    should_generate_multi = check_multi()

    # if we are generating a video, set our working directory to the video directory if one exists.
    if should_generate_video and video_directory:
        directory = video_directory
    # and if we are generating an image, set our working directory to the image directory if one exists.
    elif not should_generate_video and image_directory:
        directory = image_directory

    # find our random video by parsing directory
    try:
        filepath = directory + get_random_video_filepath(directory)
    except IndexError:
        print('Error: No video file')
        exit()

    # generate output file
    try:
        if should_generate_video:
            output = generate_random_clip_locally(filepath)
        elif image_directory:
            output = filepath
        elif should_generate_multi:
            output_list = generate_multi_screenshots_locally(filepath, tmpfile_img, img_num)
        else:
            random_time = random.uniform(0.00, get_length(filepath))
            output = generate_random_screenshot_locally(filepath, random_time, tmpfile_img)
    except subprocess.CalledProcessError:
        print('Error: Invalid file path')
        exit()

    # post to twitter
    if should_generate_multi and not should_generate_video:
        post_update(output_list)
    else:
        post_update(output)

    # save the image/video clip
    if should_generate_video and save:
        shutil.move(output, tmpfile_vid_alt)
    elif should_generate_multi and save:
        for output in output_list:
            now = datetime.datetime.now()
            tmpfile_img_alt = os.path.join(script_dir, cfg['etc.tmpfile_alt.img'], now.strftime('%Y%m%d-%H%M%S%f.jpg'))
            shutil.move(output, tmpfile_img_alt)
    elif save:
        shutil.move(output, tmpfile_img_alt)
