import requests, json, os

WEBHOOK = os.environ["WEBHOOK"]
STATE = "last_seen.txt"
LANGS = {"ko": "Manhwa", "zh": "Manhua", "ja": "Manga"}  # remove a line to skip that type

r = requests.get(
    "https://api.mangadex.org/chapter",
    params={
        "limit": 100,
        "order[publishAt]": "desc",
        "translatedLanguage[]": "en",
        "includes[]": "manga",
        "includeFutureUpdates": 0,
    },
    headers={"User-Agent": "discord-chapter-feed/1.0"},
    timeout=30,
)
chapters = r.json()["data"]

last = open(STATE).read().strip() if os.path.exists(STATE) else None
new = []
for c in chapters:
    if c["id"] == last:
        break
    new.append(c)

for c in reversed(new):
    manga = next((x for x in c["relationships"] if x["type"] == "manga"), None)
    if not manga or "attributes" not in manga:
        continue
    kind = LANGS.get(manga["attributes"].get("originalLanguage"))
    if not kind:
        continue
    titles = manga["attributes"]["title"]
    title = titles.get("en") or next(iter(titles.values()))
    ch = c["attributes"].get("chapter") or "?"
    requests.post(WEBHOOK, json={
        "content": f"**{kind}** | {title}, Chapter {ch}\nhttps://mangadex.org/chapter/{c['id']}"
    })

if chapters:
    open(STATE, "w").write(chapters[0]["id"])
