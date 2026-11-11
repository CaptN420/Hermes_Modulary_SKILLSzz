#!/usr/bin/env python3
"""End-to-end itch.io free-asset downloader.

itch.io free packs are NOT served by a plain GET. The working flow:
  1. GET the game page, extract the csrf_token meta tag.
  2. POST {page_url}/file/{upload_id} with csrf_token + source=game_download
     -> JSON {"url": "<s3-direct-url>"}
  3. GET that S3 URL -> the actual file.

The download_url -> accept_nda + download_key path is a dead end (CSRF tokens
expire per attempt, key is double-URL-encoded) - do not go down it.

Finding upload_id: usually data-upload_id="<id>" on the game page. If absent
(name-your-price flow), POST to {page_url}/download_url with just the csrf, GET
the returned one-time URL, and read data-upload_id from THAT page.

The whole chain runs in ONE process with a shared cookie jar because the CSRF
token is replaced between steps and one-time URLs are single-use.

Usage:  python itch_download.py <page_url> <upload_id> <outfile>
Example: python itch_download.py https://brackeysgames.itch.io/brackeys-platformer-bundle 10224882 pack.zip
"""
import urllib.request, urllib.parse, http.cookiejar, re, json, sys

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [("User-Agent", UA)]


def csrf_of(html):
    m = re.search(r'<meta name="csrf_token" value="([^"]+)"', html)
    return m.group(1) if m else None


def find_upload_id(page_url):
    """Get upload_id from the game page, or via the one-time download_url page."""
    html = op.open(page_url).read().decode("utf-8", "ignore")
    m = re.search(r'data-upload_id="(\d+)"', html)
    if m:
        return m.group(1)
    csrf = csrf_of(html)
    if not csrf:
        return None
    body = urllib.parse.urlencode({"csrf_token": csrf}).encode()
    req = urllib.request.Request(page_url + "/download_url", data=body, headers={
        "X-CSRF-Token": csrf, "Referer": page_url,
        "Content-Type": "application/x-www-form-urlencoded"})
    j = json.loads(op.open(req).read())
    one_time = j["url"]
    dl = op.open(urllib.request.Request(one_time, headers={"User-Agent": UA, "Referer": page_url})).read().decode("utf-8", "ignore")
    m2 = re.search(r'data-upload_id="(\d+)"', dl)
    return m2.group(1) if m2 else None


def download(page_url, upload_id, outfile):
    html = op.open(page_url).read().decode("utf-8", "ignore")
    csrf = csrf_of(html)
    if not csrf:
        print("NO CSRF token on game page"); return False
    body = urllib.parse.urlencode({"csrf_token": csrf, "source": "game_download"}).encode()
    req = urllib.request.Request(page_url + "/file/" + upload_id, data=body, headers={
        "X-CSRF-Token": csrf, "Referer": page_url,
        "Content-Type": "application/x-www-form-urlencoded"})
    try:
        resp = op.open(req).read()
    except urllib.error.HTTPError as e:
        resp = e.read()
    try:
        j = json.loads(resp)
    except Exception:
        print("non-JSON response:", resp[:150]); return False
    if "url" not in j:
        print("error:", j); return False
    data = op.open(urllib.request.Request(j["url"], headers={"User-Agent": UA})).read()
    with open(outfile, "wb") as f:
        f.write(data)
    print(f"downloaded {len(data)} bytes -> {outfile}")
    return True


if __name__ == "__main__":
    if len(sys.argv) == 4:
        ok = download(sys.argv[1], sys.argv[2], sys.argv[3])
    else:  # page_url + outfile, auto-find upload_id
        ok = download(sys.argv[1], find_upload_id(sys.argv[1]), sys.argv[2])
    sys.exit(0 if ok else 1)
