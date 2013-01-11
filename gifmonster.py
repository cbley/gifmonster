import os
import requests
import redis
import praw

output_dir = "gifs"

domain_whitelist = [
    'i.imgur.com',
    'imgur.com',
    'bukk.it',
    'media.tumblr.com',
    'i.minus.com'
]

r = redis.StrictRedis()
p = praw.Reddit(user_agent='gifmonster')


def should_download(post):
    # domain in in whitelist
    in_whitelist = post.domain in domain_whitelist

    # filename is gif
    is_gif = post.url[-3:].lower() == 'gif'

    # hasn't already been downloaded
    filename = get_file_name(post.url)
    is_downloaded = r.sismember('gifmonster:downloads', filename)

    return in_whitelist and is_gif and not is_downloaded


def get_file_name(url):
    return url.split(os.path.sep)[-1]


def download(post):
    url = post.url
    filename = get_file_name(url)

    req = requests.get(url)
    output_path = os.path.join(output_dir, filename)
    print output_path

    r.sadd('gifmonster:downloads', filename)

    with open(output_path, 'wb') as output_file:
        output_file.write(req.content)


def get_gifs(sub_reddit):
    submissions = p.get_subreddit(sub_reddit).get_hot(limit=100)

    for post in submissions:
        if should_download(post):
            download(post)


if __name__ == '__main__':
    gif_sub_reddits = ['gifs', 'reactiongifs']

    for sub_reddit in gif_sub_reddits:
        get_gifs(sub_reddit)
