# makefun-newsimage-20261118

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/arzss-code/makefun-newsimage-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/arzss-code/makefun-newsimage-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

Sum up 18 November's world news in one image: a dark editorial infographic — Trump in Asia ahead of the Xi-Putin summit, Ukraine strikes the Kerch Bridge, Nvidia rejects Huang's return + global tech outages, GTA VI lands Thursday — with a markets & mood panel (NVIDIA revenue bars, fear gauge, flashpoints). The artwork is generated offline by a deterministic Python (PIL) program and shipped as `entry.png`.

## Run it

```sh
python3 main.py   # copies entry.png to $MAKEFUN_OUTPUT_DIR (default /output)
```

`main.py` is standard-library only and never draws at run time. To regenerate the artwork (requires Pillow):

```sh
python3 tools/build_image.py   # writes MAKEFUN_OUT or /output/entry.png
```

Rebuilds are byte-identical only with the same fonts (DejaVu/Liberation) and Pillow version; the committed `entry.png` is the submitted artwork.

---
<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
