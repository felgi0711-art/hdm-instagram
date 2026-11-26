"""Veröffentlicht freigegebene Posts aus posts/<name>/ auf Instagram.

Jeder Post-Ordner enthält:
  image.jpg     Bild (JPEG, 4:5, max. 8 MB)
  caption.txt   Text inkl. Hashtags
Nach dem Posten wird published.json in den Ordner geschrieben.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

API = "https://graph.facebook.com/v23.0"
TOKEN = os.environ["IG_ACCESS_TOKEN"]
IG_USER_ID = os.environ["IG_USER_ID"]
REPO = os.environ["GITHUB_REPOSITORY"]
SHA = os.environ["GITHUB_SHA"]


def call(method, path, **params):
    params["access_token"] = TOKEN
    data = urllib.parse.urlencode(params).encode()
    url = f"{API}/{path}"
    if method == "GET":
        req = urllib.request.Request(f"{url}?{data.decode()}")
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace").replace(TOKEN, "***")
        raise SystemExit(f"API-Fehler {e.code} bei {path}: {body}")


def publish(folder):
    if os.path.exists(os.path.join(folder, "published.json")):
        print(f"{folder}: schon veröffentlicht, übersprungen")
        return None
    with open(os.path.join(folder, "caption.txt"), encoding="utf-8") as f:
        caption = f.read().strip()
    image_url = f"https://raw.githubusercontent.com/{REPO}/{SHA}/{folder}/image.jpg"

    container = call("POST", f"{IG_USER_ID}/media", image_url=image_url, caption=caption)["id"]
    for _ in range(30):
        status = call("GET", container, fields="status_code").get("status_code")
        if status == "FINISHED":
            break
        if status == "ERROR":
            raise SystemExit(f"{folder}: Instagram konnte das Bild nicht verarbeiten")
        time.sleep(5)
    if os.path.exists(os.path.join(folder, "dryrun")):
        print(f"{folder}: Probelauf ok, Bild von Instagram angenommen (nicht veröffentlicht)")
        return None
    media_id = call("POST", f"{IG_USER_ID}/media_publish", creation_id=container)["id"]
    info = call("GET", media_id, fields="permalink,timestamp")
    result = {"media_id": media_id, **info}
    with open(os.path.join(folder, "published.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"{folder}: veröffentlicht -> {info.get('permalink')}")
    return result


if __name__ == "__main__":
    folders = [a.rstrip("/") for a in sys.argv[1:]]
    if not folders:
        print("Keine neuen Posts gefunden.")
    for folder in folders:
        publish(folder)
