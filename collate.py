#!/usr/bin/env python3

import copy
import json
import os

from bs4 import BeautifulSoup

DIRECTORY = 'qposts.online/page'


def extract_metadata_block(meta_container):
    collated_metadata = {}

    # extract the spane with the name+tripcode in it
    author_container = meta_container.find('span', 'name')
    author = author_container.find('strong').getText()
    if not len(author):
        print('NAME NOT FOUND!', file=sys.stderr)
        exit()
    collated_metadata['author'] = author

    # remove the base name, leaving the tripcode if applicable
    author_container.find('strong').decompose()
    tripcode_or_empty = author_container.getText().strip()
    if tripcode_or_empty:
        collated_metadata['tripcode'] = tripcode_or_empty

    # extract source + board
    source_container = meta_container.find('span', 'source')
    board = source_container.find('strong').getText()
    if not len(board):
        print('BOARD NOT FOUND!', file=sys.stderr)
        exit()
    collated_metadata['source'] = {}
    collated_metadata['source']['board'] = board

    # remove the board name, leaving the site (and maybe link)
    source_container.find('strong').decompose()

    # get thread link if we have it
    thread_link_or_empty = source_container.find('a')
    if thread_link_or_empty:
        collated_metadata['source']['link'] = thread_link_or_empty['href']
        thread_link_or_empty.decompose()

    site = source_container.getText().strip()
    if site:
        collated_metadata['source']['site'] = site
    else:
        print('SITE NOT FOUND!', file=sys.stderr)
        exit()

    # attach timestamp
    collated_metadata['time'] = int(meta_container.find('span', 'time').getText())

    return collated_metadata


def extract_images(post_block):
    images_container = post_block.find('div', 'images', recursive=False)

    if not images_container:
        return None

    images = images_container.findAll('figure', recursive=False)
    return [{
        'file': os.path.split(image.find('a')['href'])[1],
        'name': image.find('figcaption').getText()
    } for image in images]


def extract_body(post_block, is_ref=False):
    # do decomposition with a local copy -- not sure if this is necessary
    post_block_copy = copy.copy(post_block)

    try:
        # just attempt to find it; some main posts have it, some don't, no references have it
        content_div = post_block_copy.find('div', 'text')
        if content_div:
            post_block_copy = content_div
    except AttributeError:
        pass

    # this is noise or embedded posts; regardless, we don't want them
    divs = post_block_copy.findAll('div')
    for div in divs:
        div.decompose()

    # unwrap abbreviations because bs4 thinks they need a separator
    abbrs = post_block_copy.findAll('abbr')
    for abbr in abbrs:
        abbr.unwrap()

    # get your pitchforks ready. I don't know why bs4 behaves this way but for some reason
    # it's throwing separators where there shouldn't be after unwrapping the abbrs
    # but extracting and reparsing seems to fix it. I hate it, I don't understand it,
    # it works, it stays.
    post_block_copy_duplicate = BeautifulSoup(str(post_block_copy), 'html.parser')
    return post_block_copy_duplicate.get_text(separator="\n")


def extract_references(post_block):
    refs = post_block.findAll('div', 'op')
    if not refs:
        return None

    collated_refs = []
    for ref in refs:
        collated_ref = {}
        collated_ref['reference'] = ref.previous_sibling.getText()
        maybe_text = extract_body(ref, is_ref=True)
        if maybe_text:
            collated_ref['text'] = maybe_text

        maybe_images = extract_images(ref)
        if maybe_images:
            collated_ref['images'] = maybe_images

        collated_refs.append(collated_ref)

    return collated_refs


# this is so dumb but the author uses a server-side email protection
# script, I guess for anti-spam, but it's a little overzealous. Thankfully, usage is
# minimal so I just wrote a function to slot them in from the known list
def clean_up_emails(post):
    if post['post_metadata']['time'] == 1526767434:
        post['post_metadata']['author'] = 'NowC@mesTHEP@in—-23!!!'

    if post['post_metadata']['time'] in [1588693786, 1585242439, 1553795409]:
        post['text'] = post['text'].replace('email\xa0protected]',
                                            'https://uscode.house.gov/view.xhtml?path=/prelim@title'
                                            '18/part1/chapter115&edition=prelim')

    return post


collected_posts = []
for entry in os.scandir(DIRECTORY):
    # helpful for debugging
    # if entry.name != '104.html':
    #     continue

    soup = BeautifulSoup(open(entry.path), 'html.parser')

    # extract all posts
    posts = soup.findAll('div', {'class': 'post', 'data-timestamp': True})

    for post in posts:
        collated_post = {}
        # helpful for debugging
        # collated_post['scrape_metadata'] = {
        #     'file': entry.name,
        #     'id': int(post.find('div', 'meta').find('span', 'num').getText())
        # }

        # yank metadata
        meta_container = post.find('div', 'meta')
        collated_post['post_metadata'] = extract_metadata_block(meta_container)

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

        # clean up emails -- see func comment
        collated_post = clean_up_emails(collated_post)

        collected_posts.append(collated_post)

# sort by date asc
collected_posts.sort(key=lambda post: post['post_metadata']['time'])

# just a little pretty printing :)
with open('posts.json', 'w') as outfile:
    json.dump(collected_posts, outfile, indent=2, ensure_ascii=False)
