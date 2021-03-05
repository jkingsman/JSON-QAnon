# QAnon is a dangerous cult. This archive is for research purposes only, and I do _not_ endorse any material in this repo.

# QAnon Post Dataset

`posts.json` contains all QAnon posts as scraped from https://qposts.online as of Jan 25 2021. The JSON has been dumped with `ensure_ascii=False` so should be UTF-8 but there may be some encoding gotchas I haven't caught (`text` fields contain text with line breaks as literal `\n`). I did my best in terms of avoiding capture glitches/bad logic but I didn't read through all 4k posts so caveat emptor; I make no guarantees of data integrity.

Posts reference images which I have opted not to include in this repo due to their distasteful content; the text is already quite enough and then some. You should be able to download the images with the mirror script below if you so desire; the `file` in `images` refers to the filename of the image as referred to by https://qposts.online at the time of indexing. There are about 800MB of images. I cannot speak to the durability of these image filename references but they will be accurate if you run the extraction yourself (i.e. if the file naming scheme is changed, this script will pick it up).

_N.B.: The script as-is will consolidate links with spaces in the middle (making them invalid) into links without spaces (for example `https:// twitter. com/` becomes `https://twitter.com/`). As far as I can tell, Q's original posts contained these spaces; I elected to remove them for the sake of functioning links. If you want this whitespace left untouched, you can set `KEEP_ORIGINAL_WHITESPACE` to `True` and the script will make no attempts at coercing them into well-formed links._

## Do it Yourself

Took me about two hours for a total mirror on a terrible hotel wifi using a one second pause between requests; yours will probably go much faster on good internet (but remember to be a good netizen and rate limit requests, especially to a non-API. Depending on how low of a profile you want to keep, bump up the `--wait=1` option higher to wait more than one second between each request).

To run your own extraction, mirror the site, update `DIRECTORY` in `collate.py` to point at the HTML location after mirroring, enter a `venv` and install the `requirements.txt`, then let it rip. It will dump the results as a JSON array to `posts.json` (should take a few seconds).

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

Actual JSON schemas give me a headache, so here it is in markdown form. If someone is really desperate for a JSON schema, I can probably scrape something together. This schema assumes all keys are mandatory unless labeled as optional.

The JSON takes the form of an array of `post` objects. A post consists of:

* `post_metadata`: an object containing misc. information about the post (object)
  * `id`: the numerical ID of the post (sequentially up from 1) (integer)
  * `author`: the author of the post; usually `Q` or `Anonymous` (string)
  * `source`: an object containing information about the post's origin (object)
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
  * `text`: the text of the referenced post with newlines delimited by literal `\n` (string, optional) (string, optional)
  * `images`: an array of objects indicating images used in the post (object, optional)
    * `file`: the name of the image file itself as archived from https://qposts.online (string)
    * `name`: the name of the image as it was named when posted to the image board (string)

### Debugging

If the `scrape_metadata` key is enabled (handy for debugging as it tells you the post ID and the HTML file that particular post was pulled from), that is a mandatory object (when the addition lines are uncommented) containing `file` (string of the filename the post was pulled from) and `id` (integer of the numerical ID of the post, sequentially from the first post -- open the HTML and you'll see what I mean). These can be combined with the other commented-out blocks containing `helpful for debugging` which can restrict the parsing to a single post from a single file, helpful for debugging extraction/formatting/etc.

## Misc. Analysis Snippets

### Extract all Q posts to file

To extract all of Q and only Q's posts without regard to images, referenced posts, etc., this `jq` command can be used (the `| select(.)` carves out `null` values generated by extracting the non-existent text key from posts with images only):

```
cat posts.json | jq --raw-output '.[].text | select(.)' > aggregated.txt
```

### Get top ten most linked-to domains in Q posts (and count of links)

To get the top ten domains, we'll first extract the post body and `grep` for all URL-like structures. Then we'll use `awk` to set both `:` and `/` as field separators and extract the fourth field (the domain). Then we'll use the common idiom of `sort | uniq -c | sort -nr`: `sort` will alphabetically sort the posts so that `uniq -c` can count the number of unique occurrences (in actuality `uniq -c` only provides a count of line repeats, but since it's sorted the number of repeats will be the number of times the unique line occurred) and then `sort -nr` will sort `n`umerically in `r`everse order, giving us occurences listed by descending count. Finally, `head -10` will extract the first ten lines from the results.

```bash
cat posts.json |
    jq --raw-output '.[].text | select(.)' |
    grep -Eo "(http\S*)" |
    awk -F[/:] '{print $4}' |
    sort | uniq -c | sort -nr |
    head -10
```

### Iterate with python

```python
import json

with open('posts.json') as f:
  data = json.load(f)

for post in data:
  # do things here

  # example of printing all post texts where they exist
  if 'text' in post:
    print(post['text'])
```

## Fine Print

I provide this data for data analysis use only; the content is distasteful and misleading to put it charitably and I do not endorse it.

The site itself is laid out mostly logically in terms of HTML and formatting so I have high hopes for consistency over time as it pertains to the screen scraping, but should it change dramatically, this extraction script will obviously break. I've tried to lay the script out as modularly as I can so that updates can be made with a reasonable amount of effort but I make no guarantees of durability, nor that I will have time or interest to update the script to stay current, to be brutally honest.

The code in my extraction script is licensed under MIT (and please cite me if my script or its results is utilized as part of academic research -- I'd love to read a preprint!); as the extracted posts are not my content, I cannot license them in any degree.
