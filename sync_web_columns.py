"""
Sync all published full-length AdSense-grade columns from nstock-web/columns/*.html
into stock-radar/data/columns_full.json so the Streamlit Knowledge Hub displays
the exact same rich editorial articles (tables, SVG diagrams, checklists, Q&As).
"""
import json
import os
import re
from bs4 import BeautifulSoup

WEB_DIR = r"c:\AIproject\Sample\nstock-web\columns"
OUT_PATH = r"c:\AIproject\Sample\stock-radar\data\columns_full.json"


def map_cat(raw: str) -> str:
    r = (raw or "").strip()
    if any(k in r for k in ["차트", "보조지표", "캔들", "기술적", "이동평균", "볼린저", "RSI", "MACD"]):
        return "차트 보조지표"
    if any(k in r for k in ["수급", "거래", "호가", "외국인", "기관", "체결강도", "주도주"]):
        return "수급과 거래량"
    if any(k in r for k in ["리스크", "심리", "자산", "손절", "손익", "배당", "공모", "IPO", "포트폴리오", "펀더멘털", "재무", "PBR", "PER", "ROE"]):
        return "실전 리스크 관리"
    return "테마 & 미국주식"


def sync_columns():
    items = []
    for num in range(1, 200):
        fp = os.path.join(WEB_DIR, f"{num}.html")
        if not os.path.exists(fp):
            continue
        with open(fp, encoding="utf-8") as f:
            html = f.read()
        soup = BeautifulSoup(html, "lxml")

        h1 = soup.find("h1")
        title = h1.get_text(" ", strip=True) if h1 else f"칼럼 #{num}"

        meta_desc = soup.find("meta", attrs={"name": "description"})
        summary = meta_desc["content"].strip() if (meta_desc and meta_desc.get("content")) else ""

        badge = soup.select_one(".badge-cat, .cat-badge, .category-badge, .article-badge, .meta-badge")
        raw_cat = badge.get_text(" ", strip=True) if badge else ""
        cat = map_cat(raw_cat + " " + title)

        rt_m = re.search(r"(\d+)\s*분", soup.get_text())
        read_time = f"{rt_m.group(1)}분" if rt_m else "8분"

        body = soup.select_one(".article-content") or soup.select_one(".article-body") or soup.select_one("article")
        if not body:
            continue

        for sel in [
            ".radar-cta-box",
            ".cta-box",
            ".related-columns",
            ".related-grid",
            ".related-section",
            ".article-nav",
            ".back-link",
            ".article-header",
            ".article-meta",
            "header",
            "nav",
            "footer",
            "script",
            "h1",
        ]:
            for el in body.select(sel):
                el.decompose()

        content_html = body.decode_contents().strip()
        plain_text = body.get_text(" ", strip=True)
        items.append({
            "num": num,
            "id": f"col_{num}",
            "category": cat,
            "raw_category": raw_cat or cat,
            "title": title,
            "read_time": read_time,
            "summary": summary or (plain_text[:135] + "..."),
            "web_url": f"https://nstock.kr/columns/{num}",
            "char_count": len(plain_text),
            "content_html": content_html,
        })

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"TOTAL_SYNCED: {len(items)}")
    for it in items:
        print(f"#{it['num']:02d} [{it['category']}] ({it['char_count']}자) {it['title'][:46]}")


if __name__ == "__main__":
    sync_columns()
