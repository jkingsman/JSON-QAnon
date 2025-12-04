# QAnon is a dangerous cult. This archive is for research purposes only, and I do _not_ endorse any material in this repo.

# QAnon Post Dataset

`posts.json` contains all QAnon posts as collated from multiple sources, up to the most recent drop on 2022-11-27. The JSON has been dumped with `ensure_ascii=False` so should be UTF-8 but there may be some encoding gotchas I haven't caught (`text` fields contain text with line breaks as literal `\n`). I did my best in terms of avoiding capture glitches/bad logic but I didn't read through all 5k posts so caveat emptor; I make no guarantees of data integrity.

As of the commit adding this message, significant data enrichment is now available -- timestamps (including some correction for DST), post IDs, author IDs, etc. on both primary and referenced posts. These updates are backwards compatibley, but if you're doing meaningful data mining, I highly encourage using the updated version!

## Where is this data from?

There are a variety of sites around the web which collate historical Q drops, as well as, of course, archived and still-live primary sources for the posts. This dataset is an amalgamation of data from various archival sites and manual verification to enrich the data. It has been spot checked against the original posts, but not exhaustively validated against *all* primary sources -- however, for better or worse, archival efforts are near-fanatical in their attention to detail, so I have strong confidence in this dataset, and I've manually corrected places where my scripts have spotted cross-reference discrepancies. If you spot an error of substance, please open an issue.

The collation scripts I have used to synthesize my sources and apply my manual fixes to places with data integrity issues are not published, as they are useless without the source material which contain raw data and unauthorized scrapes of many sites which I do not have the rights to republish the contents of. If the provenance of my data is of concern (or, more pertinently, if you can find any errors), please contact me and we can discuss what you need to support your use case.

## Content & Formats

### Formats

  | File Name | Format | Description |
  |-----------|--------|-------------|
  | `posts.json` | JSON | Primary dataset with full post metadata, text, images, and referenced posts |
  | `posts.yml` | YAML | YAML version of the primary dataset |
  | `posts.url-normalized.json` | JSON | Same as `posts.json` but with URLs normalized (spaces removed after `http://` and `https://`; domain fixes) |
  | `posts.url-normalized.yml` | YAML | YAML version with normalized URLs |
  | `posts.line-json.jsonl` | JSONL | Line-delimited JSON with one post object per line for streaming processing |
  | `posts.url-normalized.line-json.jsonl` | JSONL | Line-delimited JSON with normalized URLs for production streaming |
  | `posts.js` | JavaScript | JSON data exported as `const QPOSTS = {...};` for usage with `viewer.html` |
  | `posts.schema.json` | JSON Schema | JSON Schema (`draft-07`) defining the structure and validation rules |

### Images

Posts reference images which I have opted not to include in this repo due to their distasteful content; the text is already quite enough and then some. The original filenames of the images both as published by Q and as found on the original source archive are included in the dump, and they can often be found around the web.

If you are an academic researcher and can prove valid research interest (a university email is table stakes; a university email with a link to your page on a sociology department webpage, current relevant research focus, or equivalent proof of research beyond "I'm a college student please give me Q content", all the better), you may contact me and I may, at my discretion, provide you with my image scrape archive and integrated post + reference + image viewing system. Emails which do not unequivocally establish academic credentials and a reasonable, contextualized need for the content will not receive a response. I appreciate thoughtful study of the Q phenomenon and what it did to USA culture, and basically no other uses of Q's content.

### HTML Viewer

`viewer.html` will render a simple display of all posts with their basic information. This page utilizes `posts.js` which is simply `posts.json` assigned to the variable `QPOSTS`. This page will optionally serve the images if you have them available with the original as-posted-to-board filenames.

The script expects to find images in the path specified by `IMAGE_BASE`, defaulting to `./images`.  If you don't have images, they'll just fail to render and not affect the rest of the display. See above under `Images` for access if you are an academic researcher.

The resulting HTML can be then saved as a complete webpage with most web browsers, or printed to PDF for more visual analysis.

## Schema

The JSON takes the form of an array of `post` objects under the `posts` key. Machine-readable JSON schema is available in `posts.schema.json`

A post consists of:

* `post_metadata`: an object containing information about the post (object)
  * `id`: the ordinal ID of the post (sequentially from 1 forwards in time; generated and not present on original posts) (integer)
  * `author`: the author of the post; usually `Q` or `Anonymous` (string)
  * `author_id`: AKA "poster ID" -- a numerical identifier for a particular poster generated from a hash of the thread ID, the user's IP address, and other information by the board it was posted on (string)
  * `post_id`: the ID of the post, sourced from the original site it was posted on (string)
  * `tripcode`: the tripcode of the post, if included (string, optional)
  * `source`: an object containing information about the post's origin (object)
    * `board`: the chan board the post came from (string)
    * `site`: one of `4ch`, `8ch`, or `8kun`, indicating the site the post is from (4chan, 8chan, or 8kun) (string)
    * `link`: link to the original post, or an archival version as available in scrape sources; some are defunct (string)
  * `time`: epoch timestamp of posting time (integer/timestamp)
* `text`: the text of the post with newlines delimited by literal `\n` (string, optional)
* `images`: an array of objects indicating images used in the post (array, optional)
  * `file`: the name of the image file itself as archived from source board (string)
  * `name`: the name of the image as it was named when posted to the image board (string)
* `referenced_posts`: an array of objects indicating replied-to posts within Q's post (i.e. `>>8251669`) (array, optional)
  * `reference`: the string within the `text` of the main post that referred to this one (typically post_id in >>12345678 format) (string)
  * `post_id`: the ID of the referenced post (string)
  * `text`: the text of the referenced post with newlines delimited by literal `\n` (string, optional)
  * `author_id`: AKA "poster ID" -- a numerical identifier for a particular poster generated from a hash of the thread ID, the user's IP address, and other information (string)
  * `time`: epoch timestamp of when the referenced post was made (integer/timestamp)
  * `link`: link to the original referenced post, or an archival version as available in scrape sources; some are defunct (string)
  * `images`: an array of objects indicating images used in the referenced post (array, optional)
    * `file`: the name of the image file itself as archived from source board (string)
    * `name`: the name of the image as it was named when posted to the image board (string)

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

The code for my extraction and collation scripts, the presentation format, and any other original components of this repo are licensed under MIT (and please cite me if my collation efforts are utilized as part of academic research -- I'd love to read a preprint!); as the extracted posts are not my content, I obviously cannot license them in any degree.

## Cite this work

If you use `JSON-QAnon` datasets/collations in a paper, check out the CITATION.cff file for the correct citation of this particular compilation.

```bibtex
@misc{JSON-QANON,
title={JSON-QAnon},
author={Kingsman, Jack},
year={2025},
url={https://github.com/jkingsman/JSON-QAnon},
month={Jan},
doi="10.13140/RG.2.2.28778.32964",
note={{\url{https://www.kaggle.com/datasets/jkingsman/qanondrops}}}
}
```

### Works this collation has been cited in

* Eames, William J., III. "Changing Tides: Online Conspiracy Theory Use by Radical Violent Extremist Groups Over Time." Master's thesis, University of North Florida, 2023.
* Olson, Liz. "From 4-chan to the Capitol: A Text-as-Data Analysis of QAnon." Student paper, Columbia School of International and Public Affairs, April 2021.
* Thuland, Tora. "01chan.org." Art and Machine Learning project, Tisch School of the Arts, New York University, 2022. Previously available at https://www.00110000chan.org/. Information available at https://itp.nyu.edu/thesis2022/?tora-thuland.
