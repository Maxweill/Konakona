## Konakona - An Automated Twitter Screenshot/Video Bot
Konakona is a generic twitter screenshot / video posting bot written in Python. This project was originally developed for [@LuckyStarPicBot](https://twitter.com/LuckyStarPicBot).

### What is this?
This bot was written in order to generate a constant stream of content for a Twitter bot that avoids the overhead of manual uploads or pre-clipping images and video files.

It works by first parsing through a directory and selecting a video. It then uses ffmpeg to generate a screenshot at a random time from that video, then uploads it to twitter.

The bot also has the ability to parse through multiple directories, so you can give it a larger organized selection of videos to choose from. 

Take note that if you have a directory in the same hierarchical level as video files, it is significantly more likely that you will pull from the videos rather than parse the directory, since the bot stops parsing once it finds a video.

Additionally, rather than a screenshot, the bot can also generate videos from the source material.

Currently, the bot is capable of finding and parsing MKV, MP4, and AVI video files. 


### How To Use

#### Linux

**First**, you will need FFMPEG. This is tested with version n4.4, but will probably work fine with older versions.

**Second**, get the python requirements with:

```
pip install -r requirements.txt
```

**Third**, you will need a method of running the script at your specified intervals. 
I personally run the bot as a cronjob on my home server. My job config is set to run at 30 minute intervals and looks something like this:

```
*/30 * * * * python3 konakona.py
```

**Finally**, set up the configuration file.

#### Configuration
In the same directory as the konakona.py script is a configuration file, **config.yaml**. You will need to modify this file in order for the bot to function.
##### Config Variables
The settings.cfg file contains a number of variables.

| 'general' tree  | data-type | description                                                  |
| --------------- | --------- | ------------------------------------------------------------ |
| twitter.consumerKey       | string | See [twitter docs](https://developer.twitter.com/en/docs/authentication/oauth-1-0a) for more information. |
| twitter.consumerSecret      | string | See [twitter docs](https://developer.twitter.com/en/docs/authentication/oauth-1-0a) for more information. |
| twitter.token       | string |S ee [twitter docs](https://developer.twitter.com/en/docs/authentication/oauth-1-0a) for more information. |
| twitter.tokenSecret      | string | See [twitter docs](https://developer.twitter.com/en/docs/authentication/oauth-1-0a) for more information. |
| directory       | string | The main directory to pull your source video files from. |
| altVidDirectory       | string | An alternate directory to source video files from. Falls back to directory if empty. |
| fileEnding       | string | The filetype we should look for when choosing a source video. |
| save       | yes/no | Whether we should save your outputs into a folder for later. |
| saveDirectory.images       | string | The folder where we save generated images. |
| saveDirectory.clips       | string | The folder where we save generated videos.  |
| screenshot.imageCount       | integer | The number of images to send per tweet.|
| screenshot.secondsApart       | integer | The gap time between images in a given tweet. |
| clip.clipCount       | integer | The number of clips to send per tweet. |
| clip.secondsApart       | integer | The gap time between clips in a given tweet. |
| clip.clipLength       | integer  | The length of a single clip within a tweet. |
| clip.forceSubTrack       | 0/1 | If we should force videos to always display the sub track. |
| chance.clip       | decimal | The odds of generating a video clip instead of a single image. |
| chance.subtitleChance       | decimal | The odds of generating a clip/image withe the primary subtitle track burned in.|

### Future Enhancements
* GUI setup tool.
* Konakona OC ＼(^o^)／

### Licensing
This software is free and open-source software, licensed under the GPLv3. For more information, see the LICENSE file in the repository, or check out https://www.fsf.org/

### Thanks
Mevon, for his help with development and ability organize my pastebins and discord messages of ffmpeg commands. Check out his instance of this bot: [@MonogatariBotto](https://twitter.com/MonogatariBotto).

auranoir, for recommending that I pick Lucky Star as the source anime for the original bot.
