# pandabye
Export your thumbs / likes from pandora to CSV

## What
A python script which logs into your pandora profile and exports your thumbed up tracks history

## Why
On July 31, 2017, Australian and NZ subscribers will no longer be able to access Pandora. Despite the fact that there are over a million of us, Pandora doesn't seem to have provided any means by which to export our history so we can take it with us to Spotify or similar.

This script lets you download your entire thumb-up history and save it to CSV. From there you can use one of the many online tools already available to import your tracks as you see fit.

## Usage
You'll need Python 3 and the requets library installed.
```
pip3 install requests
```

The script can then be run as follows:
```
python3 export_from_pandora.py \
  --email email@email.com \
  --password super-secret-password \
  --csv_file my-likes.csv \
  --batch_size 100
```
The last two options (`batch_size` and `csv_file`) are optional.
