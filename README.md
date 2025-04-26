# QAnon is a dangerous cult. This archive is for research purposes only, and I do _not_ endorse any material in this repo.

# QAnon Post Dataset

`posts.json` contains all QAnon posts as collated from multiple sources, up to the most recent drop on 2022-11-27. The JSON has been dumped with `ensure_ascii=False` so should be UTF-8 but there may be some encoding gotchas I haven't caught (`text` fields contain text with line breaks as literal `\n`). I did my best in terms of avoiding capture glitches/bad logic but I didn't read through all 5k posts so caveat emptor; I make no guarantees of data integrity.

## Where is this data from?

There are a variety of sites around the web which collate historical Q drops, as well as, of course, archived and still-live primary sources for the posts. This dataset is an amalgamation of data from various archival sites to enrich the data. It has been spot checked against the original posts, but not exhaustively validated against primary sources -- however, for better or worse, archival efforts are near-fanatical in their attention to detail, so I have strong confidence in this dataset. If you spot an error of substance (e.g. beyond simple unicode encoding errors, which I'm sure there are a few of), please open an issue.

The `collate.py` script originally parsed a scraped copy of https://qposts.online; that site has since gone down. I retained the site's Q drop content, and also utilize other archives of sites to enrich that data. The script is now useless without a copy of the site, and I've chosen not to publicize the other sites and scripts that I retain archival copies of and use to enrich the `qposts` data with additional primary-source information.

## Important Notes

### Images

Posts reference images which I have opted not to include in this repo due to their distasteful content; the text is already quite enough and then some. As the original site I scraped the images from is down, you may no longer scrape the images directly yourself. The original filenames of the images both as published by Q and as found on the original source archive are included in the dump, and they can often be found around the web.

If you are an academic researcher and can prove valid research interest (a university email is table stakes; a university email with a link to your page on a sociology department webpage, current relevant research focus, or equivalent proof of research beyond "I'm a college student please give me Q content", all the better), you may contact me and I may, at my discretion, provide you with my image scrape archive. Emails which do not unequivocally establish academic credentials and a reasonable, contextualized need for the content will not receive a response.

### `posts.json` used to fix URLS; now it doesn't

...and represents posts accurately to original posting.

The `collate.py` script *prior to the commit which introduced this paragraph* consolidated links with spaces in the middle (making them invalid) into links without spaces (for example `https:// twitter. com/` became `https://twitter.com/`). Q's original posts contained these spaces; I previously elected to remove them for the sake of functioning links. As the source material is becoming increasingly difficult to find, I've elected to currently represent these links faithfully to the original, although they result in broken links.

If you want fixed versions, use `posts.url-normalized.json` or `posts.url-normalized.yml` which have had the following regexes applied:

```bash
# Remove spaces after http://
sed -i 's|http://\s\+|http://|g' posts.json

# Remove spaces after https://
sed -i 's|https://\s\+|https://|g' posts.json

# Fix specific spaced URLs
sed -i 's|twitter\. com|twitter.com|g' posts.json
sed -i 's|theguardian\. com|theguardian.com|g' posts.json
```
### Scrape Instruction Removal

Prior to the commit introducing this paragraph, there were instructions for running the basic scrape and then collating the data from it yourself. As the source site has gone down and data has subsequently been enriched from other sources, those instructions have been removed from the README. Please view them in the git history if they are relevant to your work.

## HTML Viewer

`viewer.html` will render a simple display of all posts with their basic information. This page utilizes `posts.js` which is simply `posts.json` assigned to the variable `QPOSTS`. This page will optionally serve the images if you scraped them from https://qposts.online before it went down.

If you have the images scraped from https://qposts.online, the location the script expects to find them in is in `IMAGE_BASE`.  If your location isn't `./images`, change it in the JS. If you don't have images, they'll just fail to render and not affect the rest of the display. Again, if you didn't scrape the sources in the early days of this repo, this door is unfortunately shut for you. See above under `Important Notes` for access if you are an academic researcher.

The resulting HTML can be then saved as a complete webpage with most web browsers, or printed to PDF for more visual analysis.

## Schema

The JSON takes the form of an array of `post` objects under the `posts` key. Machine-readable JSON schema is available in `posts.schema.json`

A post consists of:

* `post_metadata`: an object containing misc. information about the post (object)
  * `id`: the ordinal ID of the post (sequentially from 1 forwards in time; generated and not present on original posts) (integer)
  * `author`: the author of the post; usually `Q` or `Anonymous` (string)
  * `author_id`: AKA "poster ID" -- a numerical identifier for a particular poster generated from a hash of the thread ID, the user's IP address, and other information by the board it was posted on (string)
  * `tripcode`: the tripcode of the post, if included (string, optional)
  * `source`: an object containing information about the post's origin (object)
    * `board`: the chan board the post came from (string)
    * `site`: one of `4ch`, `8ch`, or `8kun`, indicating the site the post is from (4chan, 8chan, or 8kun) (string)
    * `link`: link to the original post (optional) (string)
  * `time`: epoch timestamp of posting time (integer/timestamp)
* `text`: the text of the post with newlines delimited by literal `\n` (string, optional)
* `images`: an array of objects indicating images used in the post (object, optional)
  * `file`: the name of the image file itself as archived from https://qposts.online (now defunct) (string)
  * `name`: the name of the image as it was named when posted to the image board (string)
* `referenced_posts`: an array of objects indicating replied-to posts within Q's post (i.e. `>>8251669`) (object, optional)
  * `reference`: the string within the `text` of the main post that referred to this one (string)
  * `text`: the text of the referenced post with newlines delimited by literal `\n` (string, optional) (string, optional)
  * `author_id`: AKA "poster ID" -- a numerical identifier for a particular poster generated from a hash of the thread ID, the user's IP address, and other information (string)
  * `images`: an array of objects indicating images used in the post (object, optional)
    * `file`: the name of the image file itself as archived from https://qposts.online ((now defunct) (string)
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

To get the top ten domains, we'll first extract the post body and `grep` for all URL-like structures. Then we'll use `awk` to set both `:` and `/` as field separators and extract the fourth field (the domain). Then we'll use the common idiom of `sort | uniq -c | sort -nr`: `sort` will alphabetically sort the posts so that `uniq -c` can count the number of unique occurrences (in actuality `uniq -c` only provides a count of line repeats, but since it's sorted the number of repeats will be the number of times the unique line occurred) and then `sort -nr` will sort `n`umerically in `r`everse order, giving us occurrences listed by descending count. Finally, `head -10` will extract the first ten lines from the results.

Note that this will give garbled results without using the url-normalized version (`posts.url-normalized.json`).

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

## Fine Print

I provide this data for data analysis use only; the content is distasteful and misleading to put it charitably and I do not endorse it.

There are no warranties of fitness for purpose or correctness of the this data -- I've done a best effort collation, and I make no guarantees my work is correct or complete.

The code in my extraction script and any other original components of this repo are licensed under MIT (and please cite me if my script or its results are utilized as part of academic research -- I'd love to read a preprint!); as the extracted posts are not my content, I obviously cannot license them in any degree.

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
