This repository contains a script for syncing music between a Subsonic provider and a Garmin running watch.

I wrote this script to keep music in sync between my Navidrome server and my Garmin Forerunner. When run the script does the following:

1. Gets the songs on a playlist I designated for my watch
2. Gets the songs currently in the `Music` folder on the watch
3. Deletes any songs that are on the watch, but not on the playlist
4. Adds any songs from the playlist that are missing from the watch

## Getting started

My Garmin smartwatch uses MTP to add/remove files. The python script shells out to `mtp-tools` to make this happen. As a result you'll need to install `libmtp` to ensure `mtp-tools` are available for it:

```shell
brew install libmtp
```

Python dependencies can be installed with pip:

```shell
pip install -r requirements.txt
```

Now you can setup your environment by copying `.env.example` to `.env` and updating the configs:

```shell
cp .env.example .env
vim .env
```

Finally, you can run the script like so:

```shell
python -m garmin_music_sync
```
