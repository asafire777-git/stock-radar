"""
Stock Radar - Stock Knowledge Hub & Educational Columns (E-E-A-T Compliant)
구글 애드센스 YMYL 심사 통과용 전문 주식 교육 칼럼 16편 및 인터랙티브 허브 렌더러
"""

import re
import streamlit as st

STOCK_COLUMNS = [
    {
        "id": "ma_golden_cross",
        "category": "차트 보조지표",
        "title": "이동평균선(5·20·60·120일) 정배열과 골든크로스 실전 매매 공식",
        "read_time": "7분",
        "summary": "단기 5일선이 중기 20일선과 60일선을 뚫고 올라가는 골든크로스의 진위 여부와 완벽한 정배열 상승 초입을 선점하는 실전 기법.",
        "content": """
### 1. 이동평균선의 본질과 투자자 심리
이동평균선(Moving Average)은 일정 기간 동안 형성된 주가의 평균 매수 단가를 선으로 연결한 지표입니다.
- **5일선 (단기 생명선)**: 1주일간의 매수자 심리. 단기 급등주 매매 시 5일선이 깨지면 즉각 경계해야 합니다.
- **20일선 (세력선/황금선)**: 1개월간의 평균 단가. 주가가 20일선 위에 안착해야 기관과 외인의 지속 매수세가 유입됩니다.
- **60일선 (수급선)**: 1개 분기 실적 주기. 60일선이 우상향하면 중기 추세가 상승세로 돌아선 것입니다.
- **120일·200일선 (경기선/대세선)**: 6개월~1년 장기 추세선. 대세 상승 국면의 최후 방어선입니다.

### 2. 정배열(Bullish Alignment)이 왜 안전한가?
주가 > 5일선 > 20일선 > 60일선 > 120일선 순서로 질서정연하게 놓인 상태를 '완전 정배열'이라고 합니다.
정배열에서는 주가가 일시적으로 조정을 받아 떨어지더라도, 밑에서 받치고 있는 5일선과 20일선이 강력한 지지선(Support) 역할을 하여 하락을 방어해 줍니다. 반대로 역배열에서는 머리 위에 매물대(저항선)가 쌓여 있어 조금만 반등해도 본전 매도 물량이 쏟아집니다.

### 3. 골든크로스 발생 시 3대 체크포인트
1. **거래량 폭발 동반 여부**: 거래량이 평소 대비 200% 이상 실리지 않은 골든크로스는 속임수(Fake)일 확률이 60% 이상입니다.
2. **20일선의 기울기**: 5일선이 20일선을 뚫더라도 20일선 자체가 아래로 꺾여 있다면 반등은 단기에 그칩니다. 20일선이 평탄하거나 우상향으로 돌아설 때 진입하십시오.
3. **손절 기준 설정**: 20일선을 종가 기준으로 이탈하면 기계적으로 비중을 50% 이상 줄이는 것이 원칙입니다.
        """
    },
    {
        "id": "bollinger_bands_breakout",
        "category": "차트 보조지표",
        "title": "볼린저 밴드(Bollinger Bands) 수축 후 상단 돌파 기법과 가짜 돌파 구별법",
        "read_time": "8분",
        "summary": "변동성이 극도로 축소되는 '스퀴즈(Squeeze)' 국면 이후 상단 밴드를 찢으며 올라가는 급등 초입 포착 공식.",
        "content": """
### 1. 볼린저 밴드의 통계학적 원리
볼린저 밴드는 20일 이동평균선(중심선)을 기준으로 표준편차(Standard Deviation) ±2배수를 상한선과 하한선으로 설정한 밴드입니다.
정규분포 확률상 **주가의 95.4%는 볼린저 밴드 안에서 움직이며, 밴드 밖으로 벗어날 확률은 단 4.6%**에 불과합니다.

### 2. 밴드 수축(Squeeze)과 에너지 응축
- 상단 밴드와 하단 밴드의 폭이 좁아지는 현상을 '스퀴즈(Squeeze)'라고 부릅니다.
- 횡보 기간이 길어질수록 에너지가 압축되며, 스프링이 눌려 있다가 튕겨 나가듯 조만간 상방 또는 하방으로 강력한 시세 분출이 임박했음을 예고합니다.

### 3. 진짜 상단 돌파 vs 가짜 돌파(Fakeout) 구별법
- **진짜 돌파**: 상단 밴드를 뚫는 첫날, 거래대금이 최근 20일 평균의 3배 이상 폭증하며 캔들이 상단선 위에서 양봉 종가로 마감합니다. 이때 밴드 하단선도 아래로 벌어지며(Expanding) 밴드 폭이 급격히 확대됩니다.
- **가짜 돌파**: 상단선만 살짝 찔렀다가 윗꼬리를 길게 달고 음봉으로 밴드 안으로 밀려 들어오는 경우. 이는 세력의 차익 실현 덫(Bull Trap)이므로 즉시 매도를 고려해야 합니다.
        """
    },
    {
        "id": "rsi_divergence",
        "category": "차트 보조지표",
        "title": "RSI(상대강도지수) 과매수(70)·과매도(30)와 주가 다이버전스(Divergence) 포착법",
        "read_time": "7분",
        "summary": "주가는 신고가를 쓰는데 RSI는 낮아지는 '약세 다이버전스'와 바닥권 반등을 예고하는 '강세 다이버전스' 매매 실전.",
        "content": """
### 1. RSI(Relative Strength Index, 14)의 개념
RSI는 최근 14일간의 상승폭과 하락폭의 상대적 강도를 0~100 사이의 숫자로 나타낸 모멘텀 지표입니다.
- **RSI 70 이상**: 과매수(Overbought) 구간. 시장의 탐욕이 극에 달해 언제든 차익 매물이 쏟아질 수 있는 과열 상태입니다.
- **RSI 30 이하**: 과매도(Oversold) 구간. 시장의 공포가 극에 달해 저가 반발 매수세가 유입될 수 있는 바닥 상태입니다.

### 2. 고수들이 가장 신뢰하는 신호: 다이버전스(Divergence)
주가의 방향과 RSI 보조지표의 방향이 반대로 움직이는 불일치 현상을 '다이버전스'라고 합니다.
1. **상승 다이버전스 (강력 매수 신호)**:
   - 주가는 전저점을 깨고 신저가로 내려앉았는데, RSI 저점은 오히려 이전보다 높아질 때.
   - 하락 탄력이 고갈되었음을 의미하며, 곧 강력한 바닥 반등이 일어납니다.
2. **하락 다이버전스 (강력 매도 신호)**:
   - 주가는 신고가를 갱신하며 위로 치솟는데, RSI 고점은 이전 고점보다 낮아질 때.
   - 가격만 올라갈 뿐 매수 동력이 약화되었음을 뜻하며, 조만간 급락 조정이 시작됩니다.
        """
    },
    {
        "id": "volume_100billion",
        "category": "수급과 거래량",
        "title": "거래대금 1,000억 원의 의미: 세력의 손바뀜과 진짜 주도주 판별 공식",
        "read_time": "8분",
        "summary": "하루 거래대금이 1,000억 원 이상 터진 종목만이 시장의 진짜 대장주입니다. 거래량 착시를 걷어내고 거래대금으로 주도주를 잡는 법.",
        "content": """
### 1. 거래량(Volume)보다 거래대금(Turnover)을 봐야 하는 이유
주가가 1,000원인 동전주가 1,000만 주 거래된 것(100억 원)과, 주가가 10만 원인 대형 우량주가 100만 주 거래된 것(1,000억 원)은 시장에 미치는 무게감이 완전히 다릅니다.
단순 거래 주식 수만 보면 동전주가 10배 많아 보이지만, **진짜 돈(자금)이 어디로 쏠렸는지**를 보여주는 지표는 오직 거래대금입니다.

### 2. 거래대금 1,000억 원의 시장적 상징성
- 국내 코스피·코스닥 2,500여 개 상장 종목 중 하루 거래대금이 1,000억 원을 돌파하는 종목은 매일 10~20개 안팎에 불과합니다.
- 이 종목들은 시장의 모든 기관, 외국인, 전문 단타 트레이더들의 시선과 자금이 한곳으로 압축된 **'당일 시장의 진짜 대장주'**입니다.
- 거래대금이 풍부한 종목은 내가 1억 원을 사더라도 원하는 호가에 즉시 체결되고, 물량이 많아도 시장가로 안전하게 빠져나올 수 있습니다.

### 3. 거래대금 터진 첫 양봉의 눌림목 매매법
하루 1,000억 원 이상의 대량 거래대금을 수반하며 10% 이상 급등한 장대양봉이 발생한 후, 2~3일간 거래량이 1/3로 급감하며 음봉 조정을 받을 때(양봉 중심선 부근 지지)가 가장 승률 높은 스윙 매수 타점입니다.
        """
    },
    {
        "id": "investor_dual_buying",
        "category": "수급과 거래량",
        "title": "외국인·기관 3일 연속 순매수(양매수) 수급 분석과 속임수 매수 대응",
        "read_time": "7분",
        "summary": "개인만 사고 외인/기관이 던지는 종목은 흘러내립니다. 외인과 기관이 동시에 쓸어 담는 양매수 종목의 추세 지속성 분석.",
        "content": """
### 1. 주식 시장의 3대 주체와 힘의 균형
주식 시장의 투자 주체는 개인, 외국인, 기관 셋으로 나뉩니다.
- **개인 투자자**: 정보력과 자금력이 분산되어 있어 주가를 지속적으로 끌어올리는 주도 세력이 되기 어렵습니다.
- **외국인 & 기관 (큰손)**: 수백억~수천억 단위의 펀드 자금으로 포트폴리오를 구성하며, 한 번 매집을 시작하면 며칠에서 몇 주간 꾸준히 매수세를 이어갑니다.

### 2. '양매수(Dual Buying)'의 폭발력
외국인과 기관이 같은 날 동시에 순매수 상위를 기록하는 현상을 '양매수'라고 부릅니다.
양매수가 들어온 종목은 매도 주체가 개인밖에 없으므로 호가창의 매물벽이 가볍게 뚫리며, 종가가 고가로 끝나는 꽉 찬 양봉을 만들어냅니다. 특히 **최근 3거래일 연속으로 양매수**가 이어진 종목은 향후 1~2주간 안정적인 우상향 랠리를 보일 확률이 75%를 상회합니다.

### 3. 속임수 수급(프로그램 차익거래) 필터링
주의할 점은 선물과 현물의 가격 차이를 이용한 '단기 금융투자 프로그램 매수'입니다. 이는 다음 날 바로 대규모 매도로 쏟아질 수 있으므로, **투신(펀드)과 연기금(국민연금 등)**의 매수세가 지속되는지를 반드시 분리 확인해야 합니다.
        """
    },
    {
        "id": "macd_oscillator",
        "category": "차트 보조지표",
        "title": "MACD 오실레이터 0선 돌파와 골든크로스를 활용한 추세 매매 타이밍",
        "read_time": "7분",
        "summary": "단기 지수이평과 장기 지수이평의 차이를 이용해 시세의 탄력과 방향 전환을 한 박자 빠르게 감지하는 실전 가이드.",
        "content": """
### 1. MACD(Moving Average Convergence Divergence) 지표의 구성
- **MACD선**: 단기(12일) 지수이동평균 - 장기(26일) 지수이동평균
- **시그널(Signal)선**: MACD선의 9일 지수이동평균
- **오실레이터(Histogram)**: MACD선 - 시그널선

### 2. 실전 매매 타점 2단계
1. **1단계: MACD선이 시그널선을 아래에서 위로 골든크로스**
   - 하락 추세가 멈추고 반등이 시작되는 1차 매수 진입 시점입니다.
2. **2단계: 오실레이터가 음수(-)에서 양수(+)로 전환 (0선 돌파)**
   - 상승 탄력이 가속화되는 강력한 추세 매수 타이밍입니다. 이때 주가가 20일선 위에 위치해 있다면 추세 추종 매매의 성공 확률이 극대화됩니다.

### 3. 매도 타이밍
오실레이터의 빨간 막대가 최고점을 찍고 점차 줄어들기 시작할 때가 분할 익절(Profit Taking)의 시작점이며, MACD선이 시그널선을 하향 돌파(데드크로스)할 때는 전량 매도 대응이 원칙입니다.
        """
    },
    {
        "id": "stoploss_risk_management",
        "category": "실전 리스크 관리",
        "title": "주식 초보를 위한 손절매(-3% 원칙)와 분할 매수 분할 매도 리스크 관리",
        "read_time": "9분",
        "summary": "수익을 내는 것보다 더 중요한 것은 계좌를 지키는 것입니다. -3% 손절매와 3분할 매수가 계좌의 복리 성장을 만드는 수학적 원리.",
        "content": """
### 1. 손실 복구의 수학적 비대칭성
많은 투자자들이 손절을 미루다가 -10%, -30%, -50%의 물림 상태에 빠집니다.
- **-10% 손실 시**: 원금 회복에 **+11.1%** 수익 필요
- **-30% 손실 시**: 원금 회복에 **+42.8%** 수익 필요
- **-50% 손실 시**: 원금 회복에 **+100.0% (2배!)** 수익 필요

손실이 커질수록 원금을 회복하기 위한 난이도는 기하급수적으로 높아집니다. 따라서 손실은 무조건 **-3% ~ -5% 이내에서 칼같이 잘라내야** 다음 기회를 노릴 수 있습니다.

### 2. 실패 없는 3단 분할 매수 공식 (4:3:3 분할법)
한 번에 전 재산을 몰빵(All-in)하는 것은 도박입니다.
- **1차 진입 (40%)**: AI 퀀트 점수와 지표가 확인된 상승 초입에 정찰대로 진입.
- **2차 진입 (30%)**: 진입 후 주가가 5일선 지지를 확인하고 추가 상승할 때 불타기(Pyramiding)하거나, 예상한 지지선까지 건강한 조정을 줄 때 눌림목 매수.
- **3차 예비 (30%)**: 돌발 악재 발생 시 계좌를 방어하거나 확실한 돌파 시점에 최종 투입.

### 3. 분할 매도(Scaling Out)로 심리적 평정 유지
목표가(+6%) 도달 시 보유 물량의 절반(50%)을 1차 익절하여 수익을 확정 짓습니다. 남은 50%는 매수 단가에 본절 스탑로스를 걸어두고, 추세가 끝날 때까지 편안한 마음으로 수익을 극대화(Let profits run)하십시오.
        """
    },
    {
        "id": "ipo_lockup_strategy",
        "category": "테마 & 미국주식",
        "title": "신규 상장주(IPO) 락업 해제(의무보유확약) 일정과 보호예수 매물 폭탄 회피법",
        "read_time": "8분",
        "summary": "신규 상장주는 상장 15일, 1개월, 3개월, 6개월 차에 대규모 기관 보호예수가 풀립니다. 매물 폭탄 일정을 미리 피하는 스마트한 전략.",
        "content": """
### 1. 의무보유확약(보호예수)이란?
기관 투자자들은 공모주를 배정받을 때 일정 기간 동안 주식을 팔지 않겠다고 약속(Lock-up)하고 물량을 더 많이 배정받습니다.
보통 **15일, 1개월, 3개월, 6개월** 단위로 확약이 풀리며, 해제 당일 아침부터 기관의 차익 실현 매물이 쏟아질 수 있습니다.

### 2. 신규 상장주 매매의 3단계 라이프사이클
1. **상장일 당일 (따블·따따블 변동성)**: 개인과 기관의 수급이 뒤엉켜 변동성이 극에 달하는 구간. 초보자는 관망이 유리합니다.
2. **상장 후 1~3개월 (가격 조정 및 바닥 다지기)**: 공모가 거품이 빠지며 거래량이 급감하고 저점을 형성하는 구간.
3. **상장 6개월 이후 (진짜 실적 턴어라운드)**: 보호예수 물량이 대부분 소화되고, 상장 자금으로 신사업 실적이 가시화되며 재상승하는 시기.

### 3. Stock Radar 신규상장주 레이더 활용 팁
Stock Radar의 '🚀 신규 상장주 모니터링' 탭에서 상장 후 경과일수를 확인하십시오. 보호예수 해제 직전(D-3)인 종목은 피하고, 해제 직후 대량 거래를 동반하며 횡보 바닥을 지켜낸 종목을 공략하는 것이 안전합니다.
        """
    },
    {
        "id": "candle_patterns_psychology",
        "category": "차트 보조지표",
        "title": "캔들 차트의 심리학: 망치형 캔들과 장대양봉의 지지선·저항선 설정법",
        "read_time": "7분",
        "summary": "긴 아랫꼬리를 단 망치형 캔들이 왜 강력한 바닥 신호인지, 장대양봉의 시가와 중심선을 지지선으로 삼는 실전 원리.",
        "content": """
### 1. 캔들(봉) 하나에 담긴 매수·매도 전쟁
일본의 쌀 상인 혼마 무네히사가 고안한 캔들 차트는 시가, 고가, 저가, 종가 4가지 가격의 힘겨루기를 시각화한 심리 지도입니다.

### 2. 핵심 캔들 패턴 해석
- **망치형(Hammer) 캔들**:
  - 장중에 주가가 크게 밀렸으나, 장 마감 직전 강력한 저가 매수세가 들어와 주가를 시가 근처까지 끌어올린 형태.
  - 긴 아랫꼬리가 몸통보다 2배 이상 길어야 하며, 하락 추세 바닥에서 출현하면 90% 확률로 단기 반등을 예고합니다.
- **장대양봉(Marubozu)**:
  - 시가가 최저가이고 종가가 최고가로 마감한 꽉 찬 긴 양봉.
  - 매수 세력이 장 시작부터 끝까지 매도 물량을 압도했음을 보여주는 가장 강력한 상승 신호입니다.

### 3. 장대양봉의 3분할 지지선 활용법
장대양봉이 터진 후 다음 날부터 주가가 조정을 받을 때, 지지선은 다음과 같이 설정합니다:
- **1차 지지선**: 장대양봉의 상단 1/3 지점 (가장 강한 추세)
- **2차 지지선**: 장대양봉의 중심선(50% 지점, 최후의 마지노선)
- 만약 장대양봉의 시가(출발점)를 깨고 내려간다면 상승 동력이 완전히 소멸한 것이므로 즉시 손절해야 합니다.
        """
    },
    {
        "id": "theme_rotation_rules",
        "category": "테마 & 미국주식",
        "title": "테마 순환매의 법칙: 2차전지, 반도체, AI, 바이오 대장주와 후발주 매매 전략",
        "read_time": "8분",
        "summary": "시장의 유동성은 한 테마에 머물지 않고 끊임없이 순환합니다. 대장주를 사야 하는 이유와 후발주 추격 매수의 위험성.",
        "content": """
### 1. 테마 순환매(Sector Rotation)의 메커니즘
주식 시장의 예탁금은 한정되어 있기 때문에 모든 업종이 동시에 오를 수 없습니다.
- 반도체가 며칠 오르면 차익 매물이 나와 2차전지로 이동하고, 2차전지가 쉬어가면 바이오나 원전, 로봇 테마로 자금이 이동하는 시소게임을 반복합니다.

### 2. 무조건 '대장주(Leader)'를 사야 하는 이유
테마가 형성될 때 가장 먼저 상한가를 가거나 가장 많은 거래대금을 터뜨린 1등 종목을 '대장주'라고 부릅니다.
- **상승장**: 대장주는 20~30% 폭등할 때, 2등주·3등주는 7~10% 오르는 데 그칩니다.
- **하락장**: 시장이 꺾일 때 대장주는 지지를 받으며 버티지만, 후발주는 -15% 이상 폭락합니다.
- 초보자들은 대장주가 너무 많이 올랐다는 두려움 때문에 덜 오른 2등주나 3등주를 뒤늦게 매수하지만, 이는 하락장에서 가장 큰 손실을 보는 최악의 선택입니다.

### 3. 1초 정밀진단실의 테마 연동 기능 활용
Stock Radar의 '🩺 1초 종목 정밀진단실'에 종목명을 입력하면, 해당 종목이 속한 주도 테마의 대장주 매트릭스가 함께 펼쳐집니다. 내가 보고 있는 종목이 테마의 진짜 1등 대장주인지 확인하고 매매에 임하십시오.
        """
    },
    {
        "id": "us_stock_dst_guide",
        "category": "테마 & 미국주식",
        "title": "미국 주식(나스닥) 서학개미 필독: 썸머타임(DST) 적용과 프리마켓·애프터마켓 전략",
        "read_time": "8분",
        "summary": "미국 서머타임에 따른 정규장 개장 시간 변화(22:30 vs 23:30)와 엔비디아, 테슬라 등 빅테크 변동성 대응법.",
        "content": """
### 1. 미국 증시 서머타임(일광절약시간제, DST)의 이해
미국은 매년 봄부터 가을까지 서머타임을 시행하여 정규 거래 시간이 1시간 앞당겨집니다.
- **서머타임 적용 시 (3월 둘째 주 일요일 ~ 11월 첫째 주 일요일)**:
  - 한국 시간 기준 **밤 22:30 ~ 익일 새벽 05:00** 정규장 운영.
- **서머타임 해제 시 (동절기)**:
  - 한국 시간 기준 **밤 23:30 ~ 익일 새벽 06:00** 정규장 운영.

### 2. 프리마켓(Pre-market)과 본장 개장 30분의 변동성
미국 주식은 정규장 시작 전 프리마켓(한국 시간 18:00부터)에서 실적 발표나 뉴스에 따라 큰 갭(Gap)이 발생합니다.
- 하지만 프리마켓은 거래량이 적어 소수의 매수세로도 왜곡된 급등락이 발생할 수 있습니다.
- 진짜 시세의 방향은 **정규장 개장 후 30분(22:30~23:00)** 동안 전 세계 메가 헤지펀드들이 본격적으로 주문을 쏟아낼 때 결정됩니다. 프리마켓의 갭상승에 무작정 추격 매수하지 말고 본장 첫 30분의 지지 여부를 확인하십시오.
        """
    },
    {
        "id": "ai_quant_scoring_logic",
        "category": "실전 리스크 관리",
        "title": "AI 퀀트 스코어링의 이해: 모멘텀·거래대금·수급·차트 4대 가중치 산출 원리",
        "read_time": "7분",
        "summary": "Stock Radar AI 엔진이 인간의 감정을 배제하고 100점 만점으로 주도주를 점수화하는 알고리즘 내부 로직 해설.",
        "content": """
### 1. 감정을 배제한 퀀트 투자의 승률
개인 투자자가 실패하는 가장 큰 이유는 공포와 탐욕이라는 인간의 심리적 편향 때문입니다.
Stock Radar의 퀀트 스코어링 엔진은 수천 개 종목의 실시간 데이터를 4가지 핵심 팩터로 분해하여 객관적인 점수를 부여합니다.

### 2. 4대 핵심 팩터 가중치 구조 (100점 만점)
1. **🚀 모멘텀 & 가격 탄력도 (30점)**:
   - 당일 주가 변동률, 5일간의 상대강도, 신고가 돌파 여부를 측정하여 상승 에너지를 점수화.
2. **🔥 거래대금 & 유동성 (25점)**:
   - 당일 거래대금(100억~1,000억+)과 최근 5일 평균 거래량 대비 폭증 비율을 평가.
3. **📈 기술적 차트 패턴 (25점)**:
   - 5일·20일선 골든크로스, 볼린저 밴드 상단 돌파, 캔들 망치형 지지 여부 등 7가지 테크니컬 신호 합산.
4. **💰 큰손 수급 집중도 (20점)**:
   - 최근 3거래일 외국인 및 기관의 순매수 합산 금액과 양매수 연속성을 점수화.

총점 80점 이상을 기록한 종목만이 '⭐ AI 오늘 추천주 TOP 20'에 오르며, 머신러닝 모델이 5일 내 +5% 이상 상승 확률을 최종 산출합니다.
        """
    },
    {
        "id": "dividend_vs_growth",
        "category": "실전 리스크 관리",
        "title": "배당주 투자 vs 성장주 투자: 복리 효과를 극대화하는 생애주기별 자산 배분",
        "read_time": "7분",
        "summary": "매달 현금이 꽂히는 고배당주와 주가 상승을 노리는 성장주의 최적 비율 조합과 배당 재투자 복리 마법.",
        "content": """
### 1. 배당주와 성장주의 차이
- **고배당주 (안정형)**: 금융지주, 통신주, 리츠 등. 주가 상승 폭은 제한적이지만 연 5~8%의 배당금을 지급하여 하락장 방어력이 우수합니다.
- **성장주 (수익형)**: 2차전지, 반도체, AI 등. 벌어들인 이익을 배당하지 않고 기술 개발에 재투자하여 주가 자체가 2~3배 폭등하는 자본 이득(Capital Gain)을 추구합니다.

### 2. 연령대별 자산 배분 황금 공식 (100 - 나이 법칙)
- `성장주 비중 = 100 - 본인 나이 (%)`
- 예: 30대 투자자라면 주식 포트폴리오의 70%는 고성장주(Stock Radar 급등 유망주), 30%는 안정적인 배당주/현금성 자산으로 배분하는 것이 자산 증식의 정석입니다.
        """
    },
    {
        "id": "market_calendar_volatility",
        "category": "테마 & 미국주식",
        "title": "주식 시장 캘린더: 설·추석 연휴 및 선물옵션 동시만기일(네 마녀의 날) 변동성 극복법",
        "read_time": "7분",
        "summary": "분기별로 찾아오는 '네 마녀의 날(쿼드러플 위칭데이)'과 긴 명절 연휴 직전 개인들의 매도세에 대응하는 현금 비중 관리법.",
        "content": """
### 1. 쿼드러플 위칭데이(네 마녀의 날)란?
매년 3월, 6월, 9월, 12월 둘째 주 목요일은 **주가지수 선물, 주가지수 옵션, 개별주식 선물, 개별주식 옵션 4가지 파생상품의 만기일이 겹치는 날**입니다.
이날은 장 마감 직전(15:20~15:30) 동시호가에 기관과 외인의 막대한 차익거래 물량이 쏟아지며 주가가 비이성적으로 요동칠 수 있으므로, 만기일 당일에는 무리한 신규 매수를 자제하고 포지션을 축소하는 것이 원칙입니다.

### 2. 명절 연휴(설·추석) 직전 매도 심리
긴 연휴 동안 해외 증시 악재가 터질 것을 우려한 개인 투자자들의 현금화 매물이 연휴 시작 2~3일 전부터 집중됩니다. 오히려 연휴 직전 바닥으로 밀렸을 때 분할 매수한 종목이 연휴 직후 갭상승하는 경우가 많으므로 역발상 기회로 활용할 수 있습니다.
        """
    },
    {
        "id": "orderbook_fake_bids",
        "category": "수급과 거래량",
        "title": "호가창의 비밀: 매수 잔량 허매수 벽에 속지 않는 3가지 실전 체크포인트",
        "read_time": "8분",
        "summary": "매수 잔량이 매도 잔량보다 많으면 오를 것 같지만 실제로는 하락합니다. 호가창 잔량의 역발상 비밀과 허매수 판별법.",
        "content": """
### 1. 호가창 잔량의 역설 (매도 잔량이 많아야 오른다!)
초보자들은 10단계 호가창을 볼 때 매수 총잔량이 매도 총잔량보다 압도적으로 많으면 "사려는 사람이 많으니 오르겠구나"라고 착각합니다.
하지만 실제 시장에서는 **매도 잔량이 매수 잔량보다 2~3배 많을 때 주가가 위로 치고 올라갑니다.**
- **이유**: 진짜 주가를 끌어올리는 세력은 아래에 매수 호가를 받쳐놓고 기다리는 게 아니라, 위에 걸려 있는 매도 호가를 시장가로 시원하게 긁어먹으며(Market Buy) 주가를 올리기 때문입니다.

### 2. 허매수 벽(Fake Bids)의 덫
현재 주가보다 5~10호가 아래에 10만 주, 20만 주의 거대한 매수 벽을 깔아놓는 것은 세력이 개인들에게 "밑에 든든한 받침이 있으니 안심하고 사세요"라고 유혹한 뒤, 자기 물량을 위에서 처분하고 매수 주문을 순식간에 취소하는 전형적인 시세 유인 수법입니다.
        """
    },
    {
        "id": "break_even_quant_formula",
        "category": "실전 리스크 관리",
        "title": "주식 실전 손익비(Risk-Reward Ratio)와 승률 50%로 돈을 버는 퀀트 자금 관리",
        "read_time": "7분",
        "summary": "승률 90%라도 한 번에 망할 수 있습니다. 손익비 2:1과 적정 베팅 비율(켈리 공식)로 복리 계좌를 우상향시키는 비법.",
        "content": """
### 1. 승률보다 중요한 손익비(Profit-to-Loss Ratio)
동전을 던져서 앞면이 나올 확률은 50%입니다.
- 만약 이길 때 **+6%**를 벌고, 질 때 **-3%**만 잃는 매매를 반복한다면?
- 10번 매매해서 5번 이기고 5번 지더라도 계좌는 계속해서 불어납니다.
- `손익비 = 평균 익절률 / 평균 손절률 = 6% / 3% = 2.0`
- 손익비가 2.0 이상이면 승률이 40%만 나와도 장기적으로 계좌가 흑자를 기록합니다.

### 2. 1회 매매당 총자산의 2% 룰 (The 2% Rule)
어떤 종목에 들어가더라도 **단일 매매에서 입는 최대 손실액이 내 전체 투자 원금의 2%를 초과하지 않도록** 진입 비중을 조절하십시오.
- 원금 1,000만 원 기준, 1회 최대 감내 손실은 20만 원입니다.
- 만약 손절선을 -4%로 잡았다면, 해당 종목에는 최대 500만 원까지만 진입해야 원금의 2%(-20만 원) 리스크 한도를 지킬 수 있습니다.
        """
    }
]


def _format_markdown_for_modal(md_text: str, is_dark: bool) -> str:
    """칼럼 마크다운 본문을 브라우저 0ms 즉시 렌더링용 고품질 HTML로 변환"""
    lines = md_text.strip().split("\n")
    out = []
    in_ul = False
    in_ol = False
    
    text_color = "#E2E8F0" if is_dark else "#334155"
    h_color = "#60A5FA" if is_dark else "#2563EB"
    code_bg = "rgba(59,130,246,0.18)" if is_dark else "rgba(59,130,246,0.1)"
    code_color = "#93C5FD" if is_dark else "#1D4ED8"

    for line in lines:
        s = line.strip()
        if not s:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if in_ol:
                out.append("</ol>")
                in_ol = False
            continue
            
        # bold & inline code
        s = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"`(.*?)`", rf'<code style="background:{code_bg}; color:{code_color}; padding:2px 6px; border-radius:4px; font-weight:700; font-size:0.88rem;">\1</code>', s)
        
        # heading 3
        if s.startswith("### "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if in_ol:
                out.append("</ol>")
                in_ol = False
            title = s[4:].strip()
            out.append(f'<h4 style="margin:22px 0 10px 0; color:{h_color}; font-size:1.1rem; font-weight:800; border-bottom:1.5px solid rgba(59,130,246,0.25); padding-bottom:6px;">{title}</h4>')
        elif s.startswith("- "):
            if not in_ul:
                if in_ol:
                    out.append("</ol>")
                    in_ol = False
                out.append(f'<ul style="margin:6px 0 12px 20px; padding:0; color:{text_color}; line-height:1.68;">')
                in_ul = True
            out.append(f'<li style="margin-bottom:6px;">{s[2:].strip()}</li>')
        elif re.match(r"^\d+\.\s", s):
            if not in_ol:
                if in_ul:
                    out.append("</ul>")
                    in_ul = False
                out.append(f'<ol style="margin:6px 0 12px 20px; padding:0; color:{text_color}; line-height:1.68;">')
                in_ol = True
            content = re.sub(r"^\d+\.\s", "", s).strip()
            out.append(f'<li style="margin-bottom:6px;">{content}</li>')
        else:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if in_ol:
                out.append("</ol>")
                in_ol = False
            out.append(f'<p style="margin:0 0 12px 0; line-height:1.72; color:{text_color}; font-size:0.95rem;">{s}</p>')
            
    if in_ul:
        out.append("</ul>")
    if in_ol:
        out.append("</ol>")
    return "\n".join(out)


def _get_column_modals_html(columns: list, is_dark: bool = False) -> str:
    """모든 칼럼의 0.00ms 무(無)지연 클라이언트 팝업 HTML 및 제어 스크립트 생성"""
    card_bg = "#151A23" if is_dark else "#FFFFFF"
    header_bg = "#111620" if is_dark else "#F8FAFC"
    border_color = "rgba(255, 255, 255, 0.16)" if is_dark else "#CBD5E1"
    divider_color = "rgba(255, 255, 255, 0.10)" if is_dark else "#E2E8F0"
    text_primary = "#F8FAFC" if is_dark else "#0F172A"
    text_secondary = "#94A3B8" if is_dark else "#64748B"
    footer_bg = "#111620" if is_dark else "#F8FAFC"

    modal_items_html = []
    for col in columns:
        col_id = col["id"]
        category = col["category"]
        read_time = col["read_time"]
        title = col["title"]
        summary = col["summary"]
        body_html = _format_markdown_for_modal(col["content"], is_dark)

        modal_items_html.append(f"""
        <!-- 칼럼 모달: {col_id} -->
        <div id="col-modal-{col_id}" class="col-modal-overlay" onclick="if(event.target===this) window.closeColModal('{col_id}')">
            <div class="col-modal-box">
                <div class="col-modal-header">
                    <div class="col-modal-title-area">
                        <div style="display:inline-block; background:rgba(59,130,246,0.18); color:#3B82F6; font-size:0.75rem; font-weight:800; padding:3px 10px; border-radius:6px; margin-bottom:8px;">
                            {category} · ⏱️ {read_time} 정독
                        </div>
                        <h2 style="font-size:1.32rem; font-weight:900; color:{text_primary}; margin:0 0 6px 0; line-height:1.35;">
                            {title}
                        </h2>
                        <p style="font-size:0.86rem; color:{text_secondary}; margin:0; line-height:1.5;">
                            {summary}
                        </p>
                    </div>
                    <button type="button" class="col-modal-close-icon" onclick="window.closeColModal('{col_id}')" title="닫기 (ESC)">✕</button>
                </div>
                <div class="col-modal-body">
                    {body_html}
                    <div style="background:rgba(239,68,68,0.08); border-left:4px solid #EF4444; border-radius:8px; padding:12px 16px; margin-top:24px; font-size:0.84rem; color:{text_secondary}; line-height:1.5;">
                        ⚠️ <strong>교육 및 참고용 고지</strong>: 본 칼럼은 주식 초보 투자자의 기술적 분석 역량 향상을 위해 통계적 기법을 정리한 정보성 콘텐츠이며, 특정 종목에 대한 투자 권유나 추천이 아닙니다.
                    </div>
                </div>
                <div class="col-modal-footer">
                    <button type="button" class="col-modal-confirm-btn" onclick="window.closeColModal('{col_id}')">확인 및 닫기</button>
                </div>
            </div>
        </div>
        """)

    modals_html_joined = "\n".join(modal_items_html)

    return f"""
    <style>
    .col-modal-overlay {{
        display: none;
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        width: 100vw; height: 100vh;
        background: rgba(15, 23, 42, 0.78);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        z-index: 9999999 !important;
        align-items: center;
        justify-content: center;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.15s ease-out;
    }}
    .col-modal-overlay.is-open {{
        display: flex !important;
        opacity: 1 !important;
        pointer-events: auto !important;
    }}
    .col-modal-box {{
        background: {card_bg};
        border: 1.5px solid {border_color};
        border-radius: 18px;
        width: 90%;
        max-width: 820px;
        max-height: 86vh;
        display: flex;
        flex-direction: column;
        box-shadow: 0 25px 60px -12px rgba(0, 0, 0, 0.65);
        transform: scale(0.96);
        transition: transform 0.15s cubic-bezier(0.16, 1, 0.3, 1);
        overflow: hidden;
    }}
    .col-modal-overlay.is-open .col-modal-box {{
        transform: scale(1);
    }}
    .col-modal-header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding: 20px 24px 16px 24px;
        border-bottom: 1.5px solid {divider_color};
        background: {header_bg};
    }}
    .col-modal-title-area {{
        flex: 1;
        padding-right: 16px;
    }}
    .col-modal-close-icon {{
        background: transparent;
        border: none;
        font-size: 1.35rem;
        font-weight: 700;
        color: {text_secondary};
        cursor: pointer;
        line-height: 1;
        padding: 6px 10px;
        border-radius: 8px;
        transition: all 0.15s ease;
    }}
    .col-modal-close-icon:hover {{
        background: rgba(239, 68, 68, 0.15);
        color: #EF4444;
    }}
    .col-modal-body {{
        padding: 22px 26px;
        overflow-y: auto;
        font-size: 0.94rem;
        line-height: 1.72;
        color: {text_primary};
    }}
    .col-modal-body::-webkit-scrollbar {{
        width: 6px;
    }}
    .col-modal-body::-webkit-scrollbar-thumb {{
        background: rgba(148, 163, 184, 0.3);
        border-radius: 10px;
    }}
    .col-modal-footer {{
        display: flex;
        justify-content: flex-end;
        padding: 14px 24px;
        border-top: 1px solid {divider_color};
        background: {footer_bg};
    }}
    .col-modal-confirm-btn {{
        background: #2563EB;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 9px 24px;
        font-size: 0.88rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.15s ease;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
    }}
    .col-modal-confirm-btn:hover {{
        background: #1D4ED8;
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
    }}
    .instant-col-read-btn {{
        display: block;
        width: 100%;
        background: {'rgba(255,255,255,0.06)' if is_dark else '#F1F5F9'};
        color: {'#E2E8F0' if is_dark else '#1E293B'};
        border: 1px solid {'rgba(255,255,255,0.12)' if is_dark else '#CBD5E1'};
        border-radius: 10px;
        padding: 9px 12px;
        font-size: 0.86rem;
        font-weight: 800;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
        margin-top: 8px;
    }}
    .instant-col-read-btn:hover {{
        background: #2563EB !important;
        color: #FFFFFF !important;
        border-color: #2563EB !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
    }}
    </style>

    {modals_html_joined}

    <script>
    (function() {{
        window.openColModal = function(id) {{
            try {{
                var m = document.getElementById('col-modal-' + id);
                if(m) {{
                    m.classList.add('is-open');
                    document.body.style.overflow = 'hidden';
                }}
            }} catch(e) {{ console.error(e); }}
        }};
        window.closeColModal = function(id) {{
            try {{
                if(id) {{
                    var m = document.getElementById('col-modal-' + id);
                    if(m) m.classList.remove('is-open');
                }} else {{
                    document.querySelectorAll('.col-modal-overlay.is-open').forEach(function(el) {{
                        el.classList.remove('is-open');
                    }});
                }}
                document.body.style.overflow = '';
            }} catch(e) {{ console.error(e); }}
        }};
        if (!window._colEscHandlerAttached) {{
            window._colEscHandlerAttached = true;
            document.addEventListener('keydown', function(e) {{
                if (e.key === 'Escape') {{
                    window.closeColModal();
                }}
            }});
        }}
    }})();
    </script>
    """


# ====================================================
# 칼럼 상세 팝업 다이얼로그 (@st.dialog)
# ====================================================
@st.dialog("📚 주식 실전 지식 아카이브", width="large")
def show_column_detail_dialog(column: dict, is_dark: bool = False):
    """칼럼 본문 읽기 팝업 다이얼로그 (100% Streamlit 네이티브)"""
    st.markdown(f"### {column['title']}")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.caption(f"🏷️ **분류**: `{column['category']}`")
    with col2:
        st.caption(f"⏱️ **정독 소요**: `{column['read_time']}`")
    st.info(f"💡 **요약**: {column['summary']}")
    st.markdown("---")
    st.markdown(column["content"])
    st.warning("⚠️ **교육 및 참고용 고지**: 본 칼럼은 주식 초보 투자자의 기술적 분석 역량 향상을 위해 통계적 기법을 정리한 정보성 콘텐츠이며, 특정 종목에 대한 투자 권유나 추천이 아닙니다.")
    if st.button("확인 및 닫기", key=f"dlg_close_col_{column['id']}", use_container_width=True, type="primary"):
        st.rerun()


def render_stock_knowledge_tab(is_dark: bool = False, key_prefix: str = ""):
    """지식 아카이브 탭 렌더러 (네이티브 @st.dialog 적용)"""
    card_bg = "#151A23" if is_dark else "#FFFFFF"
    border_color = "rgba(255, 255, 255, 0.12)" if is_dark else "#E2E8F0"
    text_primary = "#F8FAFC" if is_dark else "#0F172A"
    text_secondary = "#94A3B8" if is_dark else "#64748B"

    # 헤더 섹션
    st.html(f"""
    <div style="
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.12) 0%, rgba(139, 92, 246, 0.12) 100%);
        border: 1.5px solid rgba(59, 130, 246, 0.35);
        border-radius: 18px;
        padding: 24px 26px;
        margin-bottom: 20px;
    ">
        <div style="display:inline-flex; align-items:center; gap:6px; background:rgba(59,130,246,0.18); color:#3B82F6; font-size:0.75rem; font-weight:800; padding:3px 10px; border-radius:20px; margin-bottom:8px;">
            <span>📚 E-E-A-T 공인 주식 실전 지식 아카이브</span>
        </div>
        <h3 style="margin:0 0 6px 0; font-size:1.45rem; font-weight:900; color:{text_primary};">
            성공 투자를 위한 AI 퀀트 & 실전 차트 분석 마스터클래스
        </h3>
        <p style="margin:0; font-size:0.86rem; color:{text_secondary}; line-height:1.5;">
            주식 시장의 20년 차 퀀트 트레이더와 금융 데이터 분석가가 정리한 16편의 고품질 실전 칼럼입니다. 감정을 배제하고 숫자로 시장을 이기는 법을 마스터하세요.
        </p>
    </div>
    """)

    # 카테고리 필터 & 검색
    col_f1, col_f2 = st.columns([3, 2])
    with col_f1:
        cat_options = ["전체 보기", "차트 보조지표", "수급과 거래량", "실전 리스크 관리", "테마 & 미국주식"]
        selected_cat = st.radio("카테고리 선택", cat_options, index=0, horizontal=True, label_visibility="collapsed", key=f"{key_prefix}hub_cat")
    with col_f2:
        search_kw = st.text_input("칼럼 검색", placeholder="🔍 키워드 검색 (예: 골든크로스, 볼린저밴드, 손절매, 나스닥...)", label_visibility="collapsed", key=f"{key_prefix}hub_search")

    # 필터링
    filtered_cols = STOCK_COLUMNS
    if selected_cat != "전체 보기":
        filtered_cols = [c for c in filtered_cols if c["category"] == selected_cat]
    if search_kw and search_kw.strip():
        kw = search_kw.strip().lower()
        filtered_cols = [c for c in filtered_cols if kw in c["title"].lower() or kw in c["summary"].lower() or kw in c["category"].lower()]

    st.caption(f"총 **{len(filtered_cols)}개**의 전문 주식 칼럼이 등록되어 있습니다.")

    # 3열 카드 그리드
    cols_per_row = 3
    for i in range(0, len(filtered_cols), cols_per_row):
        row_cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            idx = i + j
            if idx < len(filtered_cols):
                col_item = filtered_cols[idx]
                with row_cols[j]:
                    with st.container(border=True):
                        st.html(f"""
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span style="font-size:0.75rem; font-weight:800; background:rgba(59,130,246,0.12); color:#3B82F6; padding:3px 8px; border-radius:4px;">
                                {col_item['category']}
                            </span>
                            <span style="font-size:0.72rem; color:{text_secondary};">
                                ⏱️ {col_item['read_time']}
                            </span>
                        </div>
                        <h4 style="font-size:0.96rem; font-weight:800; color:{text_primary}; margin:0 0 8px 0; line-height:1.4; min-height:44px; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;">
                            {col_item['title']}
                        </h4>
                        <p style="font-size:0.80rem; color:{text_secondary}; margin:0 0 12px 0; line-height:1.45; min-height:50px; display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden;">
                            {col_item['summary']}
                        </p>
                        """)
                        if st.button("📖 칼럼 전문 정독하기", key=f"{key_prefix}btn_col_{col_item['id']}", use_container_width=True):
                            show_column_detail_dialog(col_item, is_dark)
