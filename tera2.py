import requests
import os
import asyncio
from urllib.parse import urlparse, parse_qs
from typing import Optional


COOKIE = """csrfToken=9HpHISugzdSuOHxnwlp_7hEg; browserid=pEKq9yCroSyLuWiL13swe-ry1xEVIrV23wd7l2Qu9cpFyOjbFevNP1MD-G4YIfoLjrEajJXH1MjnaKXN; lang=en; __bid_n=18f81b88633b3d4e854207; _ga=GA1.1.903314936.1715868327; __stripe_mid=8693ce74-2b6f-482d-87ae-559781a364ec34c195; ndus=YQvOcCYteHuiMW0ZUme6PL_YmyK_awyI238-BSGY; TSID=YCb7JmuZ3QCblNhZJcWcJdiq3Q1goV9M; ab_ymg_result={"data":"ca91c55a9d05a2fcbd186bc79ea13a1a5fb9fbaf6b3fab080ea616c3cd54959b5d9d0be42a45049123576b75b7957e068fe31aea81ce3555029dd84331f344525f85a738f73b289994a322d8e76d912dbdac036505feb0a4c4be86dc18350d8e64c368c3482d50a700aec4d56fd0c75de05a820d354a0d4326b4b1aefa722e19","key_id":"66","sign":"e7dc8dc1"}; ab_sr=1.0.1_YTE2ODk3MDA0MmYxZGRmNmJlYWM5MjllN2JkYjJkMjEzYTliYWJkMTE5N2QyZGNiZjhjZjk4ZWY0NDRjZmZmNDA1NmEyZTJkMGZiNWQyMzgyMzA3ZjlhMWFkM2I3MzMwODcwNDk0NDFlMDQ4NDVlZjg1Y2I3YmMyNzFjNzM3NzMwNzc4ZDFhYzJkOWExMDYwY2MwYjE0MjFhOWZmNjE2NA==; ndut_fmt=0A679721A4378C650A99405FD095F6D2D5DFC176DBCF2C1EBB283A2C1DB77FFE; _ga_06ZNKL8C2E=GS1.1.1715868326.1.1.1715870242.60.0.0"""

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
