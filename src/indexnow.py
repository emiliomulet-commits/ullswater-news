#!/usr/bin/env python3
"""Notify IndexNow (Bing, Yandex, Seznam, Naver…) about changed pages.

Usage: python3 src/indexnow.py <git-range>      e.g. HEAD~1..HEAD
Takes the HTML files changed under docs/ in that range, maps them to URLs and submits them.
"""
import json, subprocess, sys, urllib.request

HOST = "news.ullswaterinvestments.com"
KEY = "655f9b42f378102edcd81d680d0fe004"

def urls_from_git(rng):
    out = subprocess.run(["git", "diff", "--name-only", rng, "--", "docs"], capture_output=True, text=True).stdout.split()
    urls = set()
    for f in out:
        p = f[len("docs"):]
        if p.endswith("/index.html"): urls.add(f"https://{HOST}{p[:-len('index.html')]}")
        elif p.endswith((".xml", ".txt")) and not p.endswith(KEY + ".txt"): urls.add(f"https://{HOST}{p}")
    return sorted(urls)

def submit(urls):
    if not urls: print("IndexNow: nothing to submit"); return
    body = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"https://{HOST}/{KEY}.txt", "urlList": urls[:10000]}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r: print("IndexNow:", r.status, len(urls), "URLs")
    except Exception as e:
        print("IndexNow warning:", e)  # never fail the build for this

if __name__ == "__main__":
    submit(urls_from_git(sys.argv[1] if len(sys.argv) > 1 else "HEAD~1..HEAD"))
