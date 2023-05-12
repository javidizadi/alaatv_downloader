from pathlib import Path, PurePath
from re import compile
from bs4 import BeautifulSoup
from enum import Enum
from requests import request
from sys import exit
from signal import signal, SIGINT


class Resolution(Enum):
    p720 = 'HD_720p'
    p480 = 'hq'
    p240 = '240p'


def sigint_handler(sig, frame):
    print('\nexiting...')
    exit(0)


def main():
    signal(SIGINT, sigint_handler)
    main_list_url = input('Please enter main list link: ').strip()
    if not check_url(main_list_url):
        print('Link is not in valid format.')
        main()

    resolution_pat = compile(r"720|480|240")
    while True:
        resolution_input = input('Enter video quality (720,480,240): ').strip()
        if not resolution_pat.fullmatch(resolution_input):
            print('Quality is not valid.')
            continue
        break
    resolution = Resolution[f'p{resolution_input}']
    while True:
        result_file_name = input('Please enter result file name: ').strip()
        if result_file_name is not None:
            result_file_name += '.txt'
            break
    video_links = []
    set_num = get_set(main_list_url)
    main_list_page = request('GET', main_list_url).content
    soup = BeautifulSoup(main_list_page, 'html.parser')
    for name in get_file_names(soup):
        video_link = generate_video_link(name, set_num, resolution)
        video_links.append(f'{video_link}\n')
    with open(result_file_name, 'w') as f:
        f.writelines(video_links)
    result_path = PurePath(Path(__file__), result_file_name)
    print(f'result saved to {result_path}')


BASE_LINK = "https://nodes.alaatv.com/media/@set@/@res@/@name@"


def get_set(url: str) -> str:
    return url.split('/')[-1]


def check_url(url: str)-> bool:
    base_url_pat = compile(r"https:\/\/alaatv.com\/set\/(0|[1-9]\d*)")
    if base_url_pat.fullmatch(url) is None:
        return False
    return True


def get_file_names(bs: BeautifulSoup) -> list:
    file_names = []
    thumbnail_link_pat = compile(
        r"https:\/\/nodes.alaatv.com\/media\/thumbnails\/")
    for link in bs.find_all('img'):
        src = link.get('src')
        if src is None or thumbnail_link_pat.match(src) is None:
            continue
        file_name = src.replace('https://', '') \
            .replace('.jpg', '.mp4')\
            .split('/')[4]
        file_names.append(file_name)
    return file_names


def generate_video_link(video_name: str, set: str, resolution: Resolution) -> str:
    return BASE_LINK.replace('@set@', set)\
        .replace('@res@', resolution.value)\
        .replace('@name@', video_name)


if __name__ == '__main__':
    main()
