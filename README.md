# QAnon is a dangerous cult. This archive is for research purposes only, and I do _not_ endorse any material in this repo.

# QAnon Post Dataset

In `posts.json` is an archive of all QAnon posts as scraped from https://qposts.online as of Jan 25 2020. The JSON has been dumped with `ensure_ascii=False` so should be UTF-8 but there may be some encoding gotchas I haven't caught. I did my best in terms of avoiding capture glitches/bad logic but I didn't read through all 4k posts so caveat emptor; I make no guarantees of data integrity.

Posts reference images which I have opted not to include in this repo due to their distasteful content; the text is already quite enough and then some. You should be able to download the images with the mirror script below if you so desire; the `file` in `images` refers to the filename of the image as referred to by https://qposts.online at the time of indexing. I cannot speak to the durability of these references but they will be accurate if you run the extraction yourself (i.e. if the file naming scheme is changed, this script will pick it up).

## Do it Yourself

Took me about two hours for a total mirror on a terrible hotel wifi using a one second pause between requests; yours will probably go much faster on good internet (but remember to be a good netizen and rate limit requests, especially to a non-API. Depending on how low of a profile you want to keep, bump up the `--wait=1` option higher to wait more than one second between each request).

To run your own extraction, mirorr the site, update `DIRECTORY` in `collate.py` to point at the HTML location after mirroring, enter a `venv` and install the `requirements.txt`, then let it rip. It will dump the results as a JSON array to `posts.json` (should take a few seconds).

```bash
# repo clone
git clone git@github.com:jkingsman/JSON-QAnon.git
cd JSON-QAnon

# setup + installation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x collate.py

# site mirroring
wget --wait=1 --level=inf --recursive --page-requisites --no-parent --convert-links --adjust-extension --no-clobber --restrict-file-names=windows -e robots=off https://qposts.online/

# collation; results in posts.json
# remember to update DIRECTORY if the posts aren't in ./qposts.online/page relative to the script
./collate.py
```

## Schema

Actual JSON schemas give me a headache, so here it is in markdown form. If someone is really desperate for a JSON schema, I can probably scrape something together. This schema assumes all keys are on all objects unless it is stated as optional.

The JSON takes the form of an array of `post` objects. A post consists of:

* `post_metadata`: an object containing misc. information about the post (object)
  * `author`: the author of the post; usually `Q` or `Anonymous` (string)
  * `source`: an object containing information about the post's origin
    * `board`: the chan board the post came from (string)
    * `site`: one of `4ch`, `8ch`, or `8kun`, indicating the site the post is from (4chan, 8chan, or 8kun) (string)
    * `link`: link to the original post (optional) (string)
  * `time`: epoch timestamp of posting time (integer/timestamp)
* `text`: the text of the post with newlines delimited by literal `\n` (string, optional)
* `images`: an array of objects indicating images used in the post (object, optional)
  * `file`: the name of the image file itself as archived from https://qposts.online (string)
  * `name`: the name of the image as it was named when posted to the image board (string)
* `referenced_posts`: an array of objects indicating replied-to posts within Q's post (i.e. `>>8251669`) (object, optional)
  * `reference`: the string within the `text` of the main post that referred to this one (string)
  * `text`: the textual content of the referenced post (string, optional)
  * `images`: an array of objects indicating images used in the post (object, optional)
    * `file`: the name of the image file itself as archived from https://qposts.online (string)
    * `name`: the name of the image as it was named when posted to the image board (string)


## Fine Print

I provide this data for data analysis use only; the content is distasteful and misleading to put it charitably and I do not endorse it.

The site itself is laid out mostly logically in terms of HTML and formatting so I have high hopes for consistency over time as it pertains to the screen scraping, but should it change dramatically, this extraction script will obviously break. I've tried to lay the script out as modularly as I can so that updates can be made with a reasonable amount of effort but I make no guarantees of durability, nor that I will have time or interest to update the script to stay current, to be brutally honest.

The code in my extraction script is licensed under MIT (and please cite me if my script or its results is utilized as part of academic research -- I'd love to read a preprint!); as the extracted posts are not my content, I cannot license them in any degree.
