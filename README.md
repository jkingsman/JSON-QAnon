# QAnon is a dangerous cult. This archive is for research purposes only, and I do _not_ endorse any material in this repo.

# QAnon Post Dataset

`posts.json` contains all QAnon posts as collated from multiple sources, up to the most recent drop on 2022-11-27. The JSON has been dumped with `ensure_ascii=False` so should be UTF-8 but there may be some encoding gotchas I haven't caught (`text` fields contain text with line breaks as literal `\n`). I did my best in terms of avoiding capture glitches/bad logic but I didn't read through all 5k posts so caveat emptor; I make no guarantees of data integrity.

## Important Notes

Posts reference images which I have opted not to include in this repo due to their distasteful content; the text is already quite enough and then some. As the original site I scraped the images from is down, you may no longer scrape the images directly yourself. The original filenames of the images are included in the dump, and they can often be found around the web.

If you are an academic researcher and can prove it (a university email is table stakes; a university email with a link to your page on a sociology department webpage or equivalant, all the better), you may contact me and I may, at my discretion, provide you with my image scrape archive. Emails which do not unequivocally establish academic credentials and a reasonable, contextualized need for the content will not receive a response. I'm in the business of helping science understand whatever this mess was and what it did to our culture, not in spreading the word to acolytes.

The `collate.py` script *prior to this commit* consolidated links with spaces in the middle (making them invalid) into links without spaces (for example `https:// twitter. com/` became `https://twitter.com/`). As far as I can tell, Q's original posts contained these spaces; I previously elected to remove them for the sake of functioning links. As the source material is becoming increasingly difficult to find, I've elected to represent these links faithfully to the original, although they result in broken links. If you want to fix them yourself, the following regexes (provided for bash/shell) should do it.

```bash
# Remove spaces after http://
sed -i 's|http://\s\+|http://|g' posts.json

# Remove spaces after https://
sed -i 's|https://\s\+|https://|g' posts.json

# Fix specific spaced URLs
sed -i 's|twitter\. com|twitter.com|g' posts.json
sed -i 's|theguardian\. com|theguardian.com|g' posts.json
```

Prior to the commit introducing this change, there were instructions for running the scrape yourself. As the source site has gone down, those instructions have been removed from the README; please view them in the git history if they are relevant to your work.

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

## Fine Print

I provide this data for data analysis use only; the content is distasteful and misleading to put it charitably and I do not endorse it.

There are no warranties of fitness for purpose or correctness of the this data -- I've done a best effort collation, and I make no guarantees my work is correct or complete.

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
