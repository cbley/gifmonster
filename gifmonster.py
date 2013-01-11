import os
import requests
import redis

reddit_gifs = "http://www.reddit.com/r/gifs.json?limit=100"
output_dir = "images"

domain_whitelist = [
    'i.imgur.com',
    'imgur.com',
    'bukk.it',
    'media.tumblr.com',
    'i.minus.com'
]

r = redis.StrictRedis()


def should_download(post):
    # domain in in whitelist
    in_whitelist = post['domain'] in domain_whitelist

    # filename is gif
    is_gif = post['url'][-3:].lower() == 'gif'

    # hasn't already been downloaded
    filename = get_file_name(post['url'])
    is_downloaded = r.sismember('gifmonster:downloads', filename)

    return in_whitelist and is_gif and not is_downloaded


def get_file_name(url):
    return url.split(os.path.sep)[-1]


def download(post):
    url = post['url']
    filename = get_file_name(url)

    req = requests.get(url)
    output_path = os.path.join(output_dir, filename)
    print output_path

    r.sadd('gifmonster:downloads', filename)

    with open(output_path, 'wb') as output_file:
        output_file.write(req.content)


def get_gifs():
    req = requests.get(reddit_gifs)
    data = req.json()

    for post in [child['data'] for child in data['data']['children']]:
        if should_download(post):
            download(post)


if __name__ == '__main__':
    get_gifs()
