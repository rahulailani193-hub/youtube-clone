# YouTube Clone (Gaming / Learning / Sports)

## Run
Open the folder with VS Code **Live Server**, or from this folder run:

    python3 -m http.server 8000

then visit http://localhost:8000

## Videos (all under 5 minutes, stored in /media)
| File | Category | Length |
|------|----------|--------|
| gaming-pong.mp4 | Gaming | 2:00 |
| gaming-snake.mp4 | Gaming | 2:00 |
| gaming-breakout.mp4 | Gaming | 1:30 |
| learning-times-tables.mp4 | Learning | 0:56 |
| learning-pythagoras.mp4 | Learning | 1:00 |
| learning-binary.mp4 | Learning | 0:50 |
| sports-basketball.mp4 | Sports | 1:40 |
| sports-sprint.mp4 | Sports | 1:20 |
| sports-penalty.mp4 | Sports | 1:28 |

Thumbnails are in /media/thumbs.

## Swapping in your own videos
1. Put your .mp4 in /media (keep it <= 5:00) and a thumbnail .jpg in /media/thumbs.
2. Edit the matching entry in `VIDEO_SOURCES` in `data.js` (title, category, url, poster, duration).
That's it - cards, hover previews, search and categories update automatically.

`make_videos.py` is the script that rendered the demo clips (needs Python, OpenCV, NumPy, ffmpeg).
