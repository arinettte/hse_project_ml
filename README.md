# Listen Your Emotion

<div style="display: flex; flex-wrap: wrap;">
    <img src="https://github.com/AKBAPEL/hse_project_ml/blob/main/Listen_Your_Emotion/resources/image_files/LYEE.jpg" alt="Diagram 2.1" style="width: 81%; margin: 5px;">
</div>

- Receive your image from the computer camera, determine the mood and produce a suitable track.
- A unique interface and the ability to listen to music by genre, mood and activity at the current moment in time
- The recommendation system is based on the user's favorite music in Yandex music, current mood and heuristics.

## Demo Image

![Screenshot1](https://github.com/AKBAPEL/hse_project_ml/blob/main/Listen_Your_Emotion/resources/image_files/for_read.jpg) 

## Content

- [Features](#features)
- [Download](#download)
- [Themes](#themes)
- [Support chat](#Support-chat)
- [Human evolution](#Human-evoluation)
- [FAQ](#faq)

## Features:

- **User authorization** 
The user can not only log into their account, but also fill out his profile. 
This will also be necessary when using tg-bot (more details [below](#Support-chat))

- **Playlists** Added playlists sorted by genre and by user action at the current time

- **Personal music** Added the ability to listen to user's favourite music from Yandex Music. This database can be updated at any time with the music classification algorithm that uses Machine Learning. Machine Learning algorithms are also used for heuristics so that each subsequent track is in harmony with the next one.

- **Efficient music storage** We don't storage all .mp3 locally. There are 3 queues (Happy, Sad, Calm). At any given time, each one stores 7 tracks. The queues are updated (that is, the old track is deleted and the new one is downloaded) with the most suitable tracks. Each track has an ID on Yandex music. We store these IDs locally in text format, next to the predicted mood.

- **Emotional recognition** Onboard implementation of a quantized Neural Network to predict the current emotion of the user to reccomend him the relevant track. 

## Download

We have made our application available for download!
To do this, you need to follow the link and download the project.

[Link](https://drive.google.com/file/d/1PwEhHlbpH2-E3iqb75g9oV1D1xsFXYyT/view?usp=drive_link)

## Before start

You need to get a Yandex Music token. Here is more information how to get it: [Link](https://yandex-music.readthedocs.io/en/main/token.html#)

Run music_storage\before_starting.py. Insert your token and wait for the algorithm to finish classifying the music.

## Start

Run main.exe and enjoy!

## Themes

**Welcome! Dark theme**

![](https://github.com/AKBAPEL/hse_project_ml/blob/main/Listen_Your_Emotion/resources/image_files/for_read_dark.jpg) 

## Support chat

As a full-fledged application, we decided that we needed our users to be able to connect with our team and offer something new and interesting.

[TG-bot](https://t.me/LyeLyesupportBot)
![](https://github.com/AKBAPEL/hse_project_ml/blob/main/Listen_Your_Emotion/resources/image_files/tg_bot.jpg) 

For this purpose, we have implemented a telegram bot in which <span style="color:purple">users*</span> can rate our application according to three criteria, leave a review and write to technical support to receive feedback

There are also some bonuses, one of which is on your birthday! 🎂

<span style="color:purple">*to use tg-bot you must register in the application</span>


## Human evaluation

As part of our project, we conducted a comprehensive survey among users to gather valuable feedback and insights. Here are the links to the survey and their corresponding statistics as of 05/31/2024:

[Survey about the interface](https://forms.gle/Jn33xH1AZ8u8M5bU7)
![](https://github.com/AKBAPEL/hse_project_ml/blob/main/Listen_Your_Emotion/resources/image_files/maindiag1.jpg?raw=true)

(From left to right are people's results about three possible interfaces. The study was conducted with a rating from 1 to 3, 1 variant won, which became the final one (it received the highest rating from 86 people).)

[General survey after installing the application](https://forms.gle/Z7M8XFjqk3ALbRS76)

<div style="display: flex; flex-wrap: wrap;">
    <img src="https://github.com/AKBAPEL/hse_project_ml/blob/main/Listen_Your_Emotion/resources/image_files/diagram2.1.jpg" alt="Diagram 2.1" style="width: 51%; margin: 5px;">
    <img src="https://github.com/AKBAPEL/hse_project_ml/blob/main/Listen_Your_Emotion/resources/image_files/giagram2.2.jpg" alt="Photo 1" style="width: 51%; margin: 5px;">
    <img src="https://github.com/AKBAPEL/hse_project_ml/blob/main/Listen_Your_Emotion/resources/image_files/diagram2.3.jpg" alt="Photo 2" style="width: 50%; margin: 5px;">
</div>

1. Changing user opinion with the introduction of heuristics)
Feel free to explore the surveys and delve into the fascinating data we've collected!
2. Comparability of track and human emotions
3. Сomparison with popular music apps


## FAQ

### What inspired us?

- In our world, it is very important not to lose composure and be able to cope with the most difficult life situations. That is why we decided that we could help people hear their emotions and become even happier for at least a minute
