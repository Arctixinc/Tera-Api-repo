from requests import Session
from urllib.parse import urlparse, parse_qs
from os import path
from http.cookiejar import MozillaCookieJar
from re import findall
import re
import os
from pySmartDL import SmartDL

# Define SIZE_UNITS and DirectDownloadLinkException here if they're not defined in your script file
SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']

class DirectDownloadLinkException(Exception):
    pass

def download_image(url):
    obj = SmartDL(url, progress_bar=False)
    obj.start()
    obj.wait()
    if obj.isSuccessful():
        new_filename = "thumb.png"
        os.rename(obj.get_dest(), new_filename)
        return new_filename
    else:
        return None
    
def get_readable_file_size(size_in_bytes):
    if size_in_bytes is None:
        return '0B'
    index = 0
    while size_in_bytes >= 1024 and index < len(SIZE_UNITS) - 1:
        size_in_bytes /= 1024
        index += 1
    return f'{size_in_bytes:.2f}{SIZE_UNITS[index]}' if index > 0 else f'{size_in_bytes}B'    
    
def terabox(url):
    if not path.isfile('cookies.txt'):
        raise DirectDownloadLinkException("cookies.txt not found")
    try:
        jar = MozillaCookieJar('cookies.txt')
        jar.load()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    cookies = {}
    for cookie in jar:
        cookies[cookie.name] = cookie.value
    details = {'contents':[], 'title': '', 'total_size': 0, 'thumb': ''}
    details["header"] = ' '.join(f'{key}: {value}' for key, value in cookies.items())

    def __fetch_links(session, dir_='', folderPath=''):
        params = {
            'app_id': '250528',
            'jsToken': jsToken,
            'shorturl': shortUrl
            }
        if dir_:
            params['dir'] = dir_
        else:
            params['root'] = '1'
        try:
            _json = session.get("https://www.1024tera.com/share/list", params=params, cookies=cookies).json()
        except Exception as e:
            raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
        if _json['errno'] not in [0, '0']:
            if 'errmsg' in _json:
                raise DirectDownloadLinkException(f"ERROR: {_json['errmsg']}")
            else:
                raise DirectDownloadLinkException('ERROR: Something went wrong!')

        if "list" not in _json:
            return
        contents = _json["list"]
        for content in contents:
            if content['isdir'] in ['1', 1]:
                if not folderPath:
                    if not details['title']:
                        details['title'] = content['server_filename']
                        newFolderPath = path.join(details['title'])
                    else:
                        newFolderPath = path.join(details['title'], content['server_filename'])
                else:
                    newFolderPath = path.join(folderPath, content['server_filename'])
                __fetch_links(session, content['path'], newFolderPath)
            else:
                if not folderPath:
                    if not details['title']:
                        details['title'] = content['server_filename']
                    folderPath = details['title']
                item = {
                    'url': content['dlink'],
                    'filename': content['server_filename'],
                    'path' : path.join(folderPath),
                    'thumb': content.get('thumbs', {}).get('url3', '')                
                }
                if 'size' in content:
                    size = content["size"]
                    if isinstance(size, str) and size.isdigit():
                        size = float(size)
                    details['total_size'] += size
                details['contents'].append(item)
    with Session() as session:
        try:
            _res = session.get(url, cookies=cookies)
        except Exception as e:
            raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
        if jsToken := findall(r'window\.jsToken.*%22(.*)%22', _res.text):
            jsToken = jsToken[0]
        else:
            raise DirectDownloadLinkException('ERROR: jsToken not found!.')
        shortUrl = parse_qs(urlparse(_res.url).query).get('surl')
        if not shortUrl:
            raise DirectDownloadLinkException("ERROR: Could not find surl")
        try:
            __fetch_links(session)
        except Exception as e:
            raise DirectDownloadLinkException(e)

    # Modify the link
    details['contents'][0]['url'] = details['contents'][0]['url'].replace("d.1024tera.com", "d3.terabox.app").replace("&reg", "%26reg")
    thumb = details['contents'][0]['thumb'].replace("data.1024tera.com", "d3.terabox.app")
    file_name = details['title']
    file_size = get_readable_file_size(details['total_size'])
    download_link = details['contents'][0]['url'] 
    return (
            download_link,
            file_name,
            file_size,
            thumb
        )
        