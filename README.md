## Konakona - An Automated Twitter Screenshot/Video Bot
Konakona is a generic twitter screenshot / video posting bot written in Python. This project was originally developed for [@LuckyStarPicBot](https://twitter.com/LuckyStarPicBot).

### What is this?
This bot was written in order to generate a constant stream of content for a Twitter bot that avoids the overhead of manual uploads or pre-clipping images and video files.

It works by first parsing through a directory and selecting a video. It then uses ffmpeg to generate a screenshot at a random time from that video, then uploads it to twitter.

The bot also has the ability to parse through multiple directories, so you can give it a larger organized selection of videos to choose from. 

Take note that if you have a directory in the same hierarchical level as video files, it is significantly more likely that you will pull from the videos rather than parse the directory, since the bot stops parsing once it finds a video.

![Explanation](/konakona/data/help_diagram.png)

Additionally, rather than a screenshot, the bot can also generate videos from the source material.

Currently, the bot is capable of finding and parsing MKV, MP4, and AVI video files. 

Other filetypes can be manually added in the function **get_random_video_filepath** at your own risk.

### How To Use

**First**, you will need FFMPEG. This is tested with version n4.4, but will probably work fine with older versions.

**Second**, get the python requirements with:
`pip install -r requirements.txt`

**Third**, you will need a method of running the script at your specified intervals. 
I personally run the bot as a cronjob on my home server. My job config is set to run at 30 minute intervals and looks something like this:

`*/30 * * * * python3 konakona.py`


**Finally**, set up the configuration file.

#### Configuration
In the same directory as the konakona.py script is a configuration file, **settings.cfg**. You will need to modify this file in order for the bot to function.
##### Config Variables
The settings.cfg file contains a JSON-like structure of variables. Of these variables, please note:

*directory* - Located in the 'general' tree. String. The path to your videos, or your folder of (folders of...) videos. Should end with a '/'.

*save* - Located in the 'general' tree. Boolean. Choose whether images/clips should be saved or not. Output files get renamed and moved to the media folder. The format of the filename is %Y%m%d-%H%M%S(year,month,day-hour,minute,second).

*multi.chance* - Located in the 'general.multi' tree. Integer. A number between 0 and 1, representing the percentage of the time the bot will produce multiple images. Set to 0 to never produce multiple images. Set to 1 to produce multiple images every time.

*multi.img_num* - Located in the 'general.multi' tree. Integer. Goes up to 4 images. Generates multiple images that get posted as one tweet. Not working with videos.

*multi.sec_apart* - Located in the 'general.multi' tree. Integer. Chooses how many seconds apart the multiple generated images should be.

*image.directory* - Located in the 'general.image' tree. An alternate image tree. It works like the base tree, but, if filled out, will be the source folder for all videos. Useful for pre-generated images, for instance.

*video.directory* - Located in the 'general.video' tree. An alternate video tree. It works like the base tree, but, if filled out, will be the source folder for all videos. Useful for guaranteeing that videos have subtitles, for instance.

*video.length* - Located in the 'general.video' tree. Integer. This is what the length of an outputted video clip will be, in seconds.

*video.chance* - Located in the 'general.video' tree. A number between 0 and 1, representing the percentage of the time the bot will produce a video instead of producing a screenshot. Set to 0 to never produce a video. Set to 1 to produce a video every time.

##### API Keys
There are also API keys that you must fill out. You will need to sign up for a Twitter developer account in order to gain access to these. For more info, see Twitter's website. https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api

These keys & secrets should be placed in the corresponding variables in the 'keys.consumer' and 'keys.access' trees.

### Future Enhancements
* Burn in subtitles. (Currently soft-subtitles are not supported).
 
### Licensing
This software is free and open-source software, licensed under the GPLv3. For more information, see the LICENSE file in the repository, or check out https://www.fsf.org/

### Thanks
Mevon, for his help with development and ability organize my pastebins and discord messages of ffmpeg commands. Check out his instance of this bot: [@MonogatariBotto](https://twitter.com/MonogatariBotto).

Ophelia, for recommending that I pick Lucky Star as the source anime for the original bot.
