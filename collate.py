#!/usr/bin/env python3

import copy
import json
import os
import re

from bs4 import BeautifulSoup
import yaml

# location of 1.htm, 2.htm, etc.
PAGES_DIRECTORY = 'qposts.online/page'

# when False, trim stray whitepaces from links in posts+refs; see explanation in clean_up_raw_text()
KEEP_ORIGINAL_WHITESPACE = False


def extract_metadata_block(meta_container):
    """
    Extracts author + tripcode, source site + board, and link if applicable.
    Returns an object of what it finds.
    """

    collated_metadata = {}

    # extract the span with the name+tripcode in it
    author_container = meta_container.find('span', 'name')

    # extract the bold/strong text -- i.e. the main name
    author = author_container.find('strong').getText()
    assert len(author) > 0, 'Author name not found!!'
    collated_metadata['author'] = author

    # remove the main name, leaving only the tripcode if applicable (and strip l/r whitespace)
    author_container.find('strong').decompose()
    maybe_tripcode = author_container.getText().strip()
    if maybe_tripcode:
        collated_metadata['tripcode'] = maybe_tripcode

    # extract source board + site block
    source_container = meta_container.find('span', 'source')

    # extract the bold/strong text -- i.e. the board name
    board = source_container.find('strong').getText()
    assert len(board) > 0, 'Board name not found!!'
    collated_metadata['source'] = {}
    collated_metadata['source']['board'] = board

    # remove the board name, leaving only the site (and maybe link if applicable)
    source_container.find('strong').decompose()

    # get thread link if we have it
    maybe_thread_link = source_container.find('a')
    if maybe_thread_link:
        collated_metadata['source']['link'] = maybe_thread_link['href']
        maybe_thread_link.decompose()

    # we've extracted board name and link if we have it; all that's left is the site
    site = source_container.getText().strip()
    assert site, 'Site not found!!'
    collated_metadata['source']['site'] = site

    # attach timestamp
    collated_metadata['time'] = int(meta_container.find('span', 'time').getText())

    # attach id
    collated_metadata['id'] = int(meta_container.find('span', 'num').getText())

    return collated_metadata


def extract_images(post_block):
    """
    Extracts image filename + uploaded image name for all images in a post/reference.
    Returns a list of objects containing filename + uploaded name
    """

    images_container = post_block.find('div', 'images', recursive=False)
    if not images_container:
        return None

    # well laid out figs + figcaptions make life easy for images + image names
    images = images_container.findAll('figure', recursive=False)
    return [{
        'file': os.path.split(image.find('a')['href'])[1],  # filename on disk
        'name': image.find('figcaption').getText()  # filename as posted
    } for image in images]


def extract_body(post_block, is_ref=False):
    """
    Extracts the main body text as plaintext less any referenced divs, images, html tags, etc.
    Returns a string; newlines indicated by literal \n.
    """

    """
    During body extraction, I decompose a number of elements (including divs, which contain post
    references) which basically vaporizes them. Since we need the (post) references later to extract
    and python is pass by reference*, we need to duplicate the object.

    * if you pull an https://xkcd.com/386/ and say something like "ackchyually in python, object
    references are passed by value..." I will find you and smack you
    """
    post_block_copy = copy.copy(post_block)

    # just attempt to find the main text content; some main posts have a div for this, some
    # don't, and no references have it so try/catch
    try:
        content_div = post_block_copy.find('div', 'text')
        if content_div:
            post_block_copy = content_div
    except AttributeError:
        pass

    # this is random div noise (unlikely) or a referenced post (almost always); regardless, we don't
    # want it/them
    divs = post_block_copy.findAll('div')
    for div in divs:
        div.decompose()

    # bs4 thinks these tags need a separator when rendering with get_text(); who knows why...
    # Unwrapping them seems to solve it. If any other tags that need to be unwrapped pop up, throw
    # them in tags_to_unwrap
    tags_to_unwrap = ['abbr', 'em']
    for tag_to_unwrap in tags_to_unwrap:
        instances_to_unwrap = post_block_copy.findAll(tag_to_unwrap)
        for instance_to_unwrap in instances_to_unwrap:
            instance_to_unwrap.unwrap()

    # Get your pitchforks ready. I don't know why bs4 behaves this way but for some reason it's
    # throwing separators where there shouldn't be after unwrapping the abbrs but extracting and
    # reparsing seems to fix it. I hate it; I don't understand it; it works; it stays.
    post_block_copy_duplicate = BeautifulSoup(str(post_block_copy), 'html.parser')

    raw_post_text = post_block_copy_duplicate.get_text(separator="\n")

    return clean_up_raw_text(raw_post_text)


def extract_references(post_block):
    """
    Extracts the referenced posts from the main post block and returns a list of posts, which always
    contains the text that referred to it in the original post (e.g. >>123456) and can contain image
    objects + text objects.
    Returns a list of post objects.
    """

    refs = post_block.findAll('div', 'op')
    if not refs:
        return None

    collated_refs = []
    for ref in refs:
        collated_ref = {}

        # the referring text is always the immediately previous sibling of the reference
        collated_ref['reference'] = ref.previous_sibling.getText()

        # extract reference text if we have it
        maybe_text = extract_body(ref, is_ref=True)
        if maybe_text:
            collated_ref['text'] = clean_up_raw_text(maybe_text)

        # extract the reference's image if we have any
        maybe_images = extract_images(ref)
        if maybe_images:
            collated_ref['images'] = maybe_images

        collated_refs.append(collated_ref)

    return collated_refs


def clean_up_emails(post):
    """
    This a dumb way to handle this but the post site uses a server-side email protection script (I
    guess for anti-spam) and it's a little overzealous (note this does not show up in the original
    Q posts; these are an artifact introduced by the current host I'm scraping from). Thankfully,
    usage is minimal so I just wrote a function to slot them in from the known list. If
    significantly more posts are added that trip the protection system or it changes (or the
    timestamps are changed but I assume those to be immutable) this will need additional TLC.
    """

    if post['post_metadata']['time'] == 1526767434:
        post['post_metadata']['author'] = 'NowC@mesTHEP@in—-23!!!'

    # Q sure liked this link; three separate posts using it
    if post['post_metadata']['time'] in [1588693786, 1585242439, 1553795409]:
        post['text'] = post['text'].replace('email\xa0protected]',
                                            'https://uscode.house.gov/view.xhtml?path=/prelim@title'
                                            '18/part1/chapter115&edition=prelim')

    return post


def clean_up_raw_text(text):
    """
    This corrects some minor oddities in spacing/link text. These show up in the original posts
    (as far as I can tell) so removing them technically changes the content of original or
    referenced posts. If this is an issue, set KEEP_ORIGINAL_WHITESPACE to True and this will be
    short-circuited.
    """

    if KEEP_ORIGINAL_WHITESPACE:
        return text

    # eliminate spaces after http://
    http_whitespace_regex = re.compile(r"http:\/\/\s+")
    text = http_whitespace_regex.sub('http://', text)

    # eliminate spaces after https://
    https_whitespace_regex = re.compile(r"https:\/\/\s+")
    text = https_whitespace_regex.sub('https://', text)

    # tuples of find/replace for known bad URLs
    misc_spaced_url_corrections = [
        ('twitter. com', 'twitter.com'),
        ('theguardian. com', 'theguardian.com'),
    ]

    for search, replacement in misc_spaced_url_corrections:
        text = text.replace(search, replacement)

    return text


collected_posts = []
# loop through all html files in the directory to be scanned
entry_count = len(os.listdir(PAGES_DIRECTORY))
current_entry = 1
for entry in os.scandir(PAGES_DIRECTORY):
    print(f"Processing entry {current_entry} of {entry_count}")
    current_entry += 1

    # # helpful for debugging -- skip all files but this one
    # if entry.name != '1.html':
    #     continue

    # parse the page html
    soup = BeautifulSoup(open(entry.path), 'html.parser')

    # extract all posts
    posts = soup.findAll('div', {'class': 'post', 'data-timestamp': True})

    for post in posts:
        collated_post = {}

        # yank metadata
        meta_container = post.find('div', 'meta')
        collated_post['post_metadata'] = extract_metadata_block(meta_container)

        # # helpful for debugging -- append src file to metadata
        # collated_post['post_metadata']['filename'] = entry.name

        # # helpful for debugging -- skip all posts but this ID
        # # requires scrape_metadata to be appended above
        # if collated_post['post_metadata']['id'] != 4939:
        #     continue

        # break out main meat of the post for easier manipulation
        post_body = post.find('div', 'message')

        # yank images
        extracted_images = extract_images(post_body)
        if extracted_images:
            collated_post['images'] = extracted_images

        # yank main post text
        extracted_body = extract_body(post_body)
        if extracted_body:
            collated_post['text'] = extracted_body

        # yank referenced posts
        referenced_posts = extract_references(post_body)
        if referenced_posts:
            collated_post['referenced_posts'] = referenced_posts

        # clean up emails -- see func comment; this is maximum clowntown
        collated_post = clean_up_emails(collated_post)

        # attach to big list
        collected_posts.append(collated_post)

# sort by date asc
collected_posts.sort(key=lambda post: post['post_metadata']['time'])

# pretty print and dump it
# if you're desperate, removing indent=2 shaves a half meg off
keyed_list = {"posts": collected_posts}

with open('posts.yml', 'w') as outfile:
    yaml.dump(keyed_list, outfile, allow_unicode=True)

with open('posts.json', 'w') as outfile:
    json.dump(keyed_list, outfile, indent=2, ensure_ascii=False)
