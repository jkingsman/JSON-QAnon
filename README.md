# QAnon is a dangerous cult. This archive is for research purposes only, and I do _not_ endorse any material in this repo.

# QAnon Post Dataset

`posts.json` contains all QAnon posts as scraped from https://qposts.online as of 2022-12-19. The JSON has been dumped with `ensure_ascii=False` so should be UTF-8 but there may be some encoding gotchas I haven't caught (`text` fields contain text with line breaks as literal `\n`). I did my best in terms of avoiding capture glitches/bad logic but I didn't read through all 4k posts so caveat emptor; I make no guarantees of data integrity.

## Important Note

https://qposts.online appears to be offline as of 2024. However, in the event of future drops, this repo will be kept up to date and potentially have its codebase updated to support future scraping. As-is, this represents an up-to-date snapshot of Q-Anon posts as of 2024-10 despite the generation code no longer functioning. If you archived the whole site to capture images, those references will still work with your local copy and `viewer.html`. If you did not capture the images, you can generally find them on various sites around the web that archive Q content.

## Documentation and Context

Posts reference images which I have opted not to include in this repo due to their distasteful content; the text is already quite enough and then some. ~~You should be able to download the images with the mirror script below if you so desire; the `file` in `images` refers to the filename of the image as referred to by https://qposts.online at the time of indexing. There are about 800MB of images.~~ As the original site is down, you may no longer scrape the images directly. If you are an academic researcher and can prove it (a university email is table stakes; a university email with a link to your page on a sociology department webpage or equivalant, all the better), you may contact me and I may, at my discretion, provide you with my archive. Emails which do not unequivocally establish academic credentials and a reasonable, contextualized need for the content will not receive a response.

_N.B.: The script as-is will consolidate links with spaces in the middle (making them invalid) into links without spaces (for example `https:// twitter. com/` becomes `https://twitter.com/`). As far as I can tell, Q's original posts contained these spaces; I elected to remove them for the sake of functioning links. If you want this whitespace left untouched, you can set `KEEP_ORIGINAL_WHITESPACE` to `True` and the script will make no attempts at coercing them into well-formed links._

### HTML Viewer

`viewer.html` will render a simple display of all posts with their basic information. This dynamically generates the page from `posts.json`, so __needs to be actively served by a web server that can also handle requests for the JSON__ (and optionally the images if you've scraped them). Python can do a simple web server of its current folder, so quick and dirty is to open a terminal in this repo's folder and run `python3 -m http.server 8000` which will make it accessible at http://localhost:8000.

If you have the images scraped, the location the script expects to find them in is in `IMAGE_BASE`.  If your location isn't `./images`, change it in the JS. If you don't have images, they'll just fail to render and not affect the rest of the display.

The resulting HTML can be then saved as a complete webpage with most web browsers, or printed to PDF for more visual analysis.

## Schema

Actual JSON schemas give me a headache, so here it is in markdown form. If someone is really desperate for a JSON schema, I can probably scrape something together. This schema assumes all keys are mandatory unless labeled as optional.

The JSON takes the form of an array of `post` objects under the `posts` key. A post consists of:

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

If the `filename` key in `post_metadata`, the metadata will contain the `filename` key which is a string indicating the HTML file that particular post was pulled from; this can be combined with the other commented-out blocks containing `helpful for debugging` which can restrict the parsing to a single post from a single file wich is helpful for debugging extraction/formatting/etc.

## Misc. Analysis Snippets

### Extract all Q posts to file

To extract all of Q and only Q's posts without regard to images, referenced posts, etc., this `jq` command can be used (the `| select(.)` carves out `null` values generated by extracting the non-existent text key from posts with images only):

```
cat posts.json | jq --raw-output '.posts[].text | select(.)' > aggregated.txt
```

### Get top ten most linked-to domains in Q posts (and count of links)

To get the top ten domains, we'll first extract the post body and `grep` for all URL-like structures. Then we'll use `awk` to set both `:` and `/` as field separators and extract the fourth field (the domain). Then we'll use the common idiom of `sort | uniq -c | sort -nr`: `sort` will alphabetically sort the posts so that `uniq -c` can count the number of unique occurrences (in actuality `uniq -c` only provides a count of line repeats, but since it's sorted the number of repeats will be the number of times the unique line occurred) and then `sort -nr` will sort `n`umerically in `r`everse order, giving us occurences listed by descending count. Finally, `head -10` will extract the first ten lines from the results.

```bash
cat posts.json |
    jq --raw-output '.posts[].text | select(.)' |
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

for post in data['posts']:
  # do things here

  # example of printing all post texts where they exist
  if 'text' in post:
    print(post['text'])
```

## Do it Yourself

> *Note that this is mostly irrelevant now as the original site that the scraper was build on is down!*

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
# note that you'll need to remove the rejected image formats if you also want to archive the images
wget --wait=1 --level=inf --recursive --page-requisites --no-parent --reject css,js,json,ico,svg,jpg,jpeg,png --convert-links --adjust-extension --no-clobber --restrict-file-names=windows -e robots=off https://qposts.online/

# collation; results in posts.json
# remember to update DIRECTORY if the posts aren't in ./qposts.online/page relative to the script
./collate.py
```

## Fine Print

I provide this data for data analysis use only; the content is distasteful and misleading to put it charitably and I do not endorse it.

~~The site itself is laid out mostly logically in terms of HTML and formatting so I have high hopes for consistency over time as it pertains to the screen scraping, but should it change dramatically, this extraction script will obviously break. I've tried to lay the script out as modularly as I can so that updates can be made with a reasonable amount of effort but I make no guarantees of durability, nor that I will have time or interest to update the script to stay current, to be brutally honest.~~ The extraction script is permanently broken because the source site went down.

The code in my extraction script and any other original components of this repo are licensed under MIT (and please cite me if my script or its results is utilized as part of academic research -- I'd love to read a preprint!); as the extracted posts are not my content, I cannot license them in any degree.

## Cite this work

If you use JSON-QAnon in a paper, check out the CITATION.cff file for the correct citation.

```bibtex
@misc{JSON-QANON,
title={JSON-QAnon},
author={Kingsman, Jack},
year={2023},
url={https://github.com/jkingsman/JSON-QAnon},
month={Jan},
doi="10.13140/RG.2.2.28778.32964",
note={{\url{https://www.kaggle.com/datasets/jkingsman/qanondrops}}}
}
```
