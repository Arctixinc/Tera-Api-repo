import requests
import os
import asyncio
from urllib.parse import urlparse, parse_qs
from typing import Optional


COOKIE = """csrfToken=q18O5aIk_SiKb5MzjfVXayx0; browserid=R5w6xd3x3JYQ3UK9rvcQ6_8DTzeVcjG-LqSsAtvAoZRYNj-C-0jiIeH1s=; lang=en; bid_n=18f6c0745c17f8f7ae4207; _ga=GA1.1.834669620.1715504373; g_state={"i_l":0}; ndus=YfVURCyteHuiLa-mHTQ61D3wvw08a2KCKNEdqKgY; TSID=6BDhcYeJm6gCwI5EJxY2bAz7uhZHUbd3; ab_ymg_result={"data":"50842c6b7cc2ae966a3c4cd0cc4ef519e391b40f2c6b662f00f5c72d67ff6a67cbb859d73ee18285a31556e8e35d5b93b33cc55bd9d795780d1920040a39a2d8a57997bbb19b84e8d9bbffaaf1243160849959eaaf2b08142f1dde43d753b1d32a34ef6095bff282ec4d8ba0feceedc84f53d0860c525a9117466e78eb7f9d5f","key_id":"66","sign":"360ee784"}; ndut_fmt=9B88EC9E4206635FED27B984DF21237B4DFCD031D6D8958E4EFB7A7165017D59; ab_sr=1.0.1_ODBkYTdhMjMyNjdjZDA4ZTk1MGZjYWUwZTIyZjdiYjMxM2Y4N2NhMDcxYzQ4OTUyNTNiYTRmNWQyMGUzOWFiOWNkMDIxYmE3MjEyNjA3Nzg0YjVlZDJiMjMwYjZhMjU3Yzg2ZmU5YzFlMWNlZmI3OTc2YzEyOTIwOWUxMjgzMjc0OWViY2RmYjc3MjZiN2Q3ODNmYmZkNTdjMDYzNjBiMA==; _ga_06ZNKL8C2E=GS1.1.1715504373.1.1.1715504886.50.0.0"""

def find_between(data: str, first: str, last: str) -> Optional[str]:
    try:
        start = data.index(first) + len(first)
        end = data.index(last, start)
        return data[start:end]
    except ValueError:
        return None

def extract_surl_from_url(url: str) -> Optional[str]:
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    surl = query_params.get("surl", [])

    if surl:
        return surl[0]
    else:
        return False

def get_formatted_size(size_bytes: int) -> str:
    if size_bytes >= 1024 * 1024:
        size = size_bytes / (1024 * 1024)
        unit = "MB"
    elif size_bytes >= 1024:
        size = size_bytes / 1024
        unit = "KB"
    else:
        size = size_bytes
        unit = "b"

    return f"{size:.2f} {unit}"

async def get_data(url: str):
    r = requests.Session()
    headersList = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
        "Connection": "keep-alive",
        "Cookie": COOKIE,
        "DNT": "1",
        "Host": "www.terabox.app",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }

    payload = ""

    response = r.get(url, data=payload, headers=headersList)
    response = r.get(response.url, data=payload, headers=headersList)
    logid = find_between(response.text, "dp-logid=", "&")
    jsToken = find_between(response.text, "fn%28%22", "%22%29")
    bdstoken = find_between(response.text, 'bdstoken":"', '"')
    shorturl = extract_surl_from_url(response.url)
    if not shorturl:
        return False

    reqUrl = f"https://www.terabox.app/share/list?app_id=250528&web=1&channel=0&jsToken={jsToken}&dp-logid={logid}&page=1&num=20&by=name&order=asc&site_referer=&shorturl={shorturl}&root=1"

    headersList = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
        "Connection": "keep-alive",
        "Cookie": COOKIE,
        "DNT": "1",
        "Host": "www.terabox.app",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }

    payload = ""

    response = r.get(reqUrl, data=payload, headers=headersList)

    if not response.status_code == 200:
        return False
    r_j = response.json()
    #print("Response JSON:", r_j)
    if r_j["errno"]:
        return False
    if not "list" in r_j and not r_j["list"]:
        return False

    response = r.head(r_j["list"][0]["dlink"], headers=headersList)
    direct_link = response.headers.get("location")
    data = {
        "file_name": r_j["list"][0]["server_filename"],
        "direct_link": direct_link.replace('https://data.terabox.app', 'https://d8.freeterabox.com'),
        "thumb": r_j["list"][0]["thumbs"]["url3"].replace("data.terabox.app", "d3.terabox.app"),
        "size": get_formatted_size(int(r_j["list"][0]["size"])),
    }
    return data
