import requests
import os
import asyncio
from urllib.parse import urlparse, parse_qs
from typing import Optional


COOKIE = """csrfToken=CtaTyhN71o6m4SbIqaVD60Ei; browserid=dq1iAgZuV4yKXm06ZyuiuRLj84QjU2o4jlUbJuUIQ37peQYzEwtj1q_4T0o=; lang=en; TSID=b8RtRDpicYQCQEJmwyybbBj4GJnShdab; __bid_n=18ef9ee1ec765517634207; _ga=GA1.1.1991953586.1713760087; g_state={"i_l":0}; ndus=YdDqqKxteHui7gHufHe82l0exhUaKFWTx2MHwKmo; ndut_fmt=6D981AFF47C5BC72E6D5102E07B7B9F133E821FB36E915B51E5F6A016E7F5D20; _ga_06ZNKL8C2E=GS1.1.1713760086.1.1.1713761677.18.0.0"""

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
        "direct_link": direct_link,
        "thumb": r_j["list"][0]["thumbs"]["url3"].replace("data.terabox.app", "d3.thumb.app"),
        "size": get_formatted_size(int(r_j["list"][0]["size"])),
    }
    return data
