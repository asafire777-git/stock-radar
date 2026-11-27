"""
Stock Radar - Real-Time AI News & Risk Sentiment Filter (Gemini + Google News RSS)
매수 직전 최종 통과 종목의 최근 뉴스·공시 헤드라인을 실시간 수집하고
Gemini AI(및 키워드 백업 필터)로 치명적 악재(유상증자·횡령·소송·어닝쇼크 등)를 자동 차단합니다.
"""

import json
import re
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
import requests

from src.gemini_engine import call_gemini_api

_NEWS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

# Gemini 호출 불가/지연 시에도 치명적 악재를 즉시 차단하는 백업 리스크 키워드
_CRITICAL_RISK_KR = [
    "유상증자", "횡령", "배임", "거래정지", "상장폐지", "감사의견 거절",
    "관리종목", "불성실공시", "압수수색", "분식회계", "파산", "회생절차",
]
_CRITICAL_RISK_EN = [
    "bankruptcy", "chapter 11", "sec investigation", "fraud", "delisting",
    "accounting scandal", "secondary offering", "indictment", "subpoena",
]
_BULLISH_KW = [
    "수주", "호실적", "어닝서프라이즈", "신고가", "흑자전환", "임상 성공", "fda 승인",
    "목표가 상향", "자사주 매입", "배당 확대", "beat", "upgrade", "record revenue",
    "partnership", "contract win", "ai demand", "surge", "buyback",
]


def fetch_recent_news_headlines(query: str, is_us: bool = False, max_items: int = 6) -> List[str]:
    """Google News RSS에서 종목 관련 최신 뉴스 헤드라인 수집 (무료·안정)"""
    try:
        q_enc = urllib.parse.quote(query)
        if is_us:
            url = f"https://news.google.com/rss/search?q={q_enc}&hl=en-US&gl=US&ceid=US:en"
        else:
            url = f"https://news.google.com/rss/search?q={q_enc}&hl=ko&gl=KR&ceid=KR:ko"
        resp = requests.get(url, headers=_NEWS_HEADERS, timeout=5)
        if resp.status_code != 200 or not resp.text:
            return []
        root = ET.fromstring(resp.text)
        headlines = []
        for item in root.findall(".//item")[:max_items]:
            title_el = item.find("title")
            if title_el is not None and title_el.text:
                clean_t = re.sub(r"\s+-\s+[^-]+$", "", title_el.text.strip())
                if clean_t and clean_t not in headlines:
                    headlines.append(clean_t)
        return headlines
    except Exception:
        return []


def _keyword_fallback_sentiment(headlines: List[str], is_us: bool = False) -> Dict[str, Any]:
    """Gemini API 미설정 또는 타임아웃 시 결정론적 키워드 리스크 판독"""
    if not headlines:
        return {
            "verdict": "NEUTRAL",
            "label": "⚪ 중립 (뉴스 없음)",
            "score": 0,
            "reason": "최근 특이 악재 뉴스 미감지",
            "engine": "RSS 키워드 필터",
            "headlines": [],
        }

    joined = " ".join(headlines).lower()
    risk_list = _CRITICAL_RISK_EN if is_us else (_CRITICAL_RISK_KR + _CRITICAL_RISK_EN)
    hit_risks = [kw for kw in risk_list if kw.lower() in joined]
    if hit_risks:
        return {
            "verdict": "CRITICAL_RISK",
            "label": "🚨 치명적 악재 (매수 차단)",
            "score": -85,
            "reason": f"악재 키워드 감지({', '.join(hit_risks[:2])}) — 매수 자동 보류",
            "engine": "RSS 키워드 필터",
            "headlines": headlines[:3],
        }

    hit_bull = [kw for kw in _BULLISH_KW if kw.lower() in joined]
    if hit_bull:
        return {
            "verdict": "BULLISH",
            "label": "🟢 호재 우세",
            "score": 65,
            "reason": f"긍정 모멘텀 뉴스 감지({', '.join(hit_bull[:2])})",
            "engine": "RSS 키워드 필터",
            "headlines": headlines[:3],
        }

    return {
        "verdict": "NEUTRAL",
        "label": "⚪ 중립 (특이 악재 없음)",
        "score": 10,
        "reason": f"최신 뉴스 {len(headlines)}건 검토 완료 — 치명적 악재 없음",
        "engine": "RSS 키워드 필터",
        "headlines": headlines[:3],
    }


def analyze_stock_news_risk(code: str, name: str, is_us: bool = False) -> Dict[str, Any]:
    """
    종목의 최신 뉴스 헤드라인을 수집하고 Gemini AI로 악재·호재 판독
    반환 verdict: 'BULLISH' | 'NEUTRAL' | 'CRITICAL_RISK'
    """
    query = f"{code} stock" if is_us else f"{name} 주식"
    headlines = fetch_recent_news_headlines(query, is_us=is_us, max_items=6)
    if not headlines:
        return _keyword_fallback_sentiment([], is_us=is_us)

    # 1. Gemini AI 정밀 판독 시도
    hl_text = "\n".join(f"- {h}" for h in headlines)
    prompt = (
        f"종목: {name} ({code})\n"
        f"최신 뉴스 헤드라인:\n{hl_text}\n\n"
        "위 뉴스들을 분석해 단기 주식 매수 관점에서 치명적 악재(유상증자, 횡령/배임, 상장폐지/거래정지, "
        "대규모 어닝쇼크, SEC 조사/소송 등)가 있는지 판별하고, 반드시 아래 JSON 형식으로만 답하라:\n"
        '{"verdict": "BULLISH" 또는 "NEUTRAL" 또는 "CRITICAL_RISK", "score": -100~100 정수, "reason": "한국어 35자 이내 핵심 요약"}'
    )
    sys_inst = "너는 보수적인 퀀트 리스크 매니저다. 오직 유효한 JSON 한 줄만 출력하라."
    raw = call_gemini_api(prompt, system_instruction=sys_inst, temperature=0.1, max_tokens=220)
    if raw:
        try:
            m = re.search(r"\{.*\}", raw, flags=re.DOTALL)
            if m:
                parsed = json.loads(m.group(0))
                verdict = str(parsed.get("verdict", "NEUTRAL")).upper().strip()
                if verdict not in ("BULLISH", "NEUTRAL", "CRITICAL_RISK"):
                    verdict = "NEUTRAL"
                score = int(parsed.get("score", 0))
                reason = str(parsed.get("reason", "최신 뉴스 검토 완료")).strip()[:60]
                label_map = {
                    "BULLISH": "🟢 AI 호재 판독",
                    "NEUTRAL": "⚪ AI 중립 (안전)",
                    "CRITICAL_RISK": "🚨 AI 악재 차단",
                }
                return {
                    "verdict": verdict,
                    "label": label_map[verdict],
                    "score": score,
                    "reason": reason,
                    "engine": "Gemini AI",
                    "headlines": headlines[:3],
                }
        except Exception:
            pass

    # 2. Gemini 미연동/실패 시 키워드 백업 필터
    return _keyword_fallback_sentiment(headlines, is_us=is_us)
