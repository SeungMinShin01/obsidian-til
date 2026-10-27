---
출처: Claude 분석
원본: KDT_2026/2026_Python/practice/ReportPractice/Report.py, practice/ReportPractice/ddareungi_1-6.csv, practice/ReportPractice/ddareungi_7-12.csv, practice/ReportPractice/ddareungi_names.csv
작성일: 2026-10-27
tags: [학습, python]
---

# Python day07 — 넘파이로 따릉이 대여소 재배치 분석 실습

> 실습 파일: `practice/ReportPractice/Report.py`, `ddareungi_1-6.csv`, `ddareungi_7-12.csv`, `ddareungi_names.csv`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day07 넘파이로 고객 구매 데이터 분석 실습]] · 다음: (아직 없음)

고객 구매 데이터 실습에 이어 두 번째로 실제 데이터 파일에 넘파이를 꺼내 쓴 보고서 실습이다. 이번 데이터는 서울 공공자전거 따릉이의 **대여소별·월별 대여 건수와 반납 건수**다. 지난 실습이 CSV 한 장을 읽어 열을 뽑고 조건으로 거르는 데 집중했다면, 이번에는 그 앞에 **데이터를 준비하는 단계**가 붙는다 — 상·하반기로 나뉜 파일 두 장을 `vstack`으로 이어 붙이고, 월별로 흩어진 3만 행을 대여소 2,812곳 단위로 합산해 새 표를 만들고, 숫자 ID뿐인 표 옆에 문자열 이름표를 따로 읽어 붙인다. 그 위에서 "자전거가 빠져나가기만 하는 대여소는 어디인가"를 불균형 지수와 순유출 정규화로 찾는다. 코드 곳곳의 주석에 어느 날 어느 파일에서 배운 도구인지(`DAY07 n-03 vstack`, `DAY06 n-01 dtype`)를 적어 두었는데, 지난 노트들의 문법이 실전에서 어디에 꽂히는지 확인하는 용도로 그대로 따라가 본다.

## 1. 배운 내용

### 1-1. 데이터 준비 — 파일 두 장을 읽고 `vstack`으로 이어 붙이기

```python
import numpy as np
# [0] ID  [1] 기준년월  [2] 대여건수  [3] 반납건수
data1 = np.genfromtxt('./practice/ReportPractice/ddareungi_1-6.csv',
                      delimiter=',', skip_header=1, encoding='utf-8-sig')
data2 = np.genfromtxt('./practice/ReportPractice/ddareungi_7-12.csv',
                      delimiter=',', skip_header=1, encoding='utf-8-sig')
print(f"상반기: {data1.shape}, 하반기: {data2.shape}")   # (16403, 4), (16567, 4)

data = np.vstack([data1, data2])
print(f"1~12월 데이터 형태: {data.shape}")               # (32970, 4)
```

`genfromtxt`의 `delimiter`·`skip_header`는 지난 실습과 같고, 인자 하나가 새로 붙었다.

| 인자 | 뜻 |
| --- | --- |
| `encoding='utf-8-sig'` | 파일 맨 앞의 **BOM**(Byte Order Mark, `﻿`)을 떼고 읽는다. 엑셀이 UTF-8로 저장한 CSV에 흔히 붙어 있다 |
| `skip_header=1` | 첫 줄 `ID,기준년월,대여건수,반납건수`는 글자라 건너뜀 |

BOM은 보이지 않는 3바이트 표식이라 그냥 `utf-8`로 읽으면 첫 열 이름 앞에 유령 문자가 붙는다. 지금은 헤더를 건너뛰니 숫자 표에는 영향이 없지만, 아래 1-3의 이름표 파일처럼 **문자열로 읽을 때**는 첫 값이 `'﻿102'`가 되어 버리므로 `utf-8-sig`로 통일해 두는 편이 안전하다. 한글이 든 공공데이터 CSV는 대부분 이 옵션이 필요하다고 보면 된다.

읽힌 표는 `float64` 4열이다. `기준년월`도 `202501.`처럼 실수로 들어오고, 상반기 파일은 1~6월, 하반기 파일은 7~12월이다. 두 표는 **열 구성이 같고 행만 다르니** `np.vstack([data1, data2])`로 세로로 쌓는다 — day07 첫 노트의 "행이 늘어나는 병합, 열 개수가 맞아야 한다"가 정확히 이 경우다. 32,970행이 되었고, 한 행은 "어느 대여소의 어느 달 대여·반납"이다.

### 1-2. 대여소별 12개월 합계 — `np.unique`와 마스크로 그룹 합산

```python
ids = np.unique(data[:, 0])            # 중복 없는 대여소번호 (오름차순) → 2812개
rows = []
for i in ids:
    m = data[:, 0] == i                # 이 대여소의 행만 True
    rows.append([i, np.sum(data[m, 2]), np.sum(data[m, 3])])
station = np.array(rows)
print(f"대여소별 데이터 형태: {station.shape}")   # (2812, 3)
```

이 실습의 가장 중요한 단계다. 월별 3만 행을 **대여소 하나당 한 행**으로 눌러야 "어느 대여소가" 문제라는 질문에 답할 수 있기 때문이다. 세 조각으로 나눠 읽는다.

| 조각 | 하는 일 |
| --- | --- |
| `np.unique(data[:, 0])` | 0번 열(ID)의 **중복을 없애고 오름차순으로** 정렬한 1차원 배열. 2,812개의 대여소 번호가 나온다 |
| `m = data[:, 0] == i` | ID 열을 번호 하나와 비교 → 3만 개의 참·거짓. 그 대여소의 달만 `True` |
| `np.sum(data[m, 2])` | 참인 행의 2번 열(대여건수)만 골라 합산. 행은 불리언·열은 정수로 동시 지정 |

`for`가 다시 등장한 점이 눈에 띈다. 지난 실습에서는 `for`를 한 번도 안 썼는데, "같은 키를 가진 행끼리 묶어 집계"하는 **group by**는 순수 넘파이에 한 줄짜리 함수가 없어서 키마다 마스크를 만드는 반복문이 가장 읽기 쉬운 방법이다. 반복은 대여소 수(2,812번)만큼만 돌고, 각 회차 안의 비교·합산은 넘파이가 C로 처리하니 3만 행 전체를 파이썬 `for`로 도는 것과는 속도가 다르다. 판다스가 `groupby('ID').sum()` 한 줄로 해 주는 일이 바로 이것이고, 그 안에서 벌어지는 일을 손으로 한 번 풀어 본 셈이다(3-1 참고).

`rows`는 `[ID, 대여합계, 반납합계]` 리스트 2,812개를 담은 **리스트 안의 리스트**이고, 마지막에 `np.array(rows)`로 감싸 `(2812, 3)` 2차원 배열이 된다. day06 첫 노트의 "리스트 안의 리스트 → 2차원 배열"이 실제 데이터에서 쓰인 자리다. 이렇게 만든 `station`이 이후 모든 단계의 표이고, 열 지도는 코드 주석대로 `[0] ID [1] 대여합계 [2] 반납합계`로 바뀐다 — 원본 `data`의 열 번호와 다르니 어느 표를 보고 있는지 늘 확인해야 한다.

`np.unique`가 **오름차순으로 돌려준다**는 성질은 다음 단계에서 중요해진다. `station`의 행 순서가 ID 오름차순으로 고정되기 때문이다. 참고로 대여소마다 행 수는 1~12개로 제각각이다(연중 운영된 곳은 12행, 중간에 생기거나 없어진 곳은 그보다 적다). 마스크로 합산하면 행 수가 달라도 그 대여소에 있는 달만 더해지니 따로 손볼 것이 없다.

### 1-3. 이름표 파일 — `dtype=str`로 문자열 배열 읽기

```python
names = np.genfromtxt('./practice/ReportPractice/ddareungi_names.csv',
                      delimiter=',', skip_header=1, encoding='utf-8-sig', dtype=str)
print(f"이름표 형태: {names.shape}")   # (2812, 2)
print(station[:3])      # [[  102. 34540. 36332.] [  103. 26170. 29316.] [  104. 15621. 13526.]]
print(names[:3, 1])     # ['망원역 1번출구 앞' '망원역 2번출구 앞' '합정역 1번출구 앞']
```

`station`에는 대여소 번호만 있어서 결과를 사람이 읽을 수 없다. 이름은 별도 파일(`ID,이름`)에 있고, 이름은 숫자가 아니니 `genfromtxt`에 `dtype=str`을 준다. 이러면 ID 열까지 **전부 문자열**(`'102'`)인 `(2812, 2)` 배열이 된다 — 넘파이 배열은 자료형이 하나라서 숫자와 글자를 한 표에 섞을 수 없고, 그래서 **숫자 표와 이름 표를 따로 두고 행 순서로 맞추는** 구조가 된다. `dtype`이 `<U41`로 찍히는데, "유니코드 최대 41글자"라는 뜻이고 가장 긴 이름에 맞춰 잡힌다.

두 표가 **같은 행 순서**라는 전제가 핵심이다. `station`은 `np.unique`가 ID 오름차순으로 만들었고, 이름표 파일도 ID 오름차순으로 적혀 있으며 둘 다 2,812행이라, `station[k]`의 대여소 이름이 `names[k, 1]`이다. `station[:3]`과 `names[:3, 1]`을 나란히 찍어 102·103·104가 망원역·합정역으로 맞는지 눈으로 확인하는 줄이 그래서 들어가 있다. 이 전제가 깨지면(이름표에 한 곳이 빠져 있다든지) 그다음 결과가 전부 엉뚱한 이름을 달고 나오므로, 순서를 믿고 쓸 때는 이런 확인을 한 번 거치는 편이 안전하다. 키로 맞추는 더 튼튼한 방법은 2-2에 적어 둔다.

### 1-4. 지표 만들기 — 열 꺼내기와 불균형 지수

```python
rent  = station[:, 1]      # 대여합계
ret   = station[:, 2]      # 반납합계
ratio = rent / ret         # 불균형 지수 (Step 3에서 만드는 값)
```

`station[:, 1]`·`station[:, 2]`로 열을 1차원으로 뽑아 이름을 붙여 두면 뒤 코드가 `station[:, 1]` 대신 `rent`로 읽힌다. `ratio`는 두 배열의 같은 위치끼리 나눈 **파생 변수**다. 1이면 대여와 반납이 같고, 1보다 크면 **빌려 가는 사람이 돌려놓는 사람보다 많아 자전거가 빠져나가는 유출형**, 1보다 작으면 쌓이는 유입형 대여소다. 지난 실습의 "구매 금액 ÷ 방문 횟수"와 같은 모양이고, 나누는 쪽(반납)이 0인 대여소가 있으면 `inf`가 나온다는 주의점도 같다(이 데이터에서는 반납 0인 곳이 없어 무사했다).

### 1-5. Step 1~3 — 기술 통계, 분위 기준선, 가장 불균형한 대여소

Step 4·5의 복합 조건과 정규화에 들어가기 전에, 기본 통계로 데이터의 윤곽을 잡고 단순 조건으로 "관리 대상"을 먼저 걸러 보는 세 단계가 앞에 붙어 있다. 지난 실습에서 `max`·`argmax`·`sort`를 하나씩 썼던 것을 이 데이터 위에서 다시 꺼내 쓰는 과정이다.

**Step 1 — 평균·최대·최소와 그 자리의 이름**

```python
print(f"1년 평균 대여수: {np.mean(rent):,.1f}")                                 # 13,290.6
print(f"1년 최대 대여수: {np.max(rent):,.1f} 대여소명: {names[np.argmax(rent), 1]}")  # 162,990.0 마곡나루역 2번 출구
print(f"1년 최소 대여수: {np.min(rent)} 대여소명: {names[np.argmin(rent), 1]}")      # 0.0 고덕역 4번출구
print(f"1년 평균 반납수: {np.mean(ret):,.1f}")                                  # 13,219.9
```

`np.max`는 **값**을, `np.argmax`는 **그 값이 있는 위치(행 번호)**를 돌려준다. 값만으로는 "어느 대여소인지"를 알 수 없으니, `argmax`로 얻은 행 번호를 이름표 `names`의 같은 행에 넣어 `names[np.argmax(rent), 1]`로 이름을 꺼낸다. 이것이 가능한 이유는 1-3에서 확인한 대로 `station`과 `names`의 행 순서가 같기 때문이다 — 숫자 표에서 찾은 위치를 문자열 표에 그대로 꽂는 패턴이고, 1-7의 "같은 `order`를 세 배열에" 쓰는 것과 같은 원리다. 최소 대여수가 0인 대여소가 있다는 것도 여기서 드러나는데, 뒤의 `ratio = rent / ret`에서 분자가 0이면 지수가 0이 될 뿐 오류는 나지 않는다(분모 `ret`가 0인 경우와는 다르다). 평균 대여 13,290건과 평균 반납 13,220건은 거의 같다 — 전체로 보면 빌린 만큼 돌려놓는 것이 당연하고, 문제는 대여소 **사이**의 쏠림이라는 점을 이 두 숫자가 미리 말해 준다.

**Step 2 — 정렬한 배열의 위치로 상위 10%·하위 10% 기준선 잡기**

```python
n = len(station)                           # 2812
rent_sorted = np.sort(rent)                # 오름차순 복사본
ret_sorted  = np.sort(ret)

top10 = rent_sorted[int(n * 0.9)]          # 대여 상위 10% 기준: 27938.0
low10 = ret_sorted[int(n * 0.1)]           # 반납 하위 10% 기준: 2017.0

group = (rent >= top10) | (ret <= low10)
print("관리가 필요한 대여소: ", station[group].shape[0], "곳")   # 564곳
```

"상위 10%"를 `np.percentile` 없이 손으로 구하는 방법이다. 오름차순으로 정렬한 배열에서 **90% 지점의 위치** `int(n * 0.9)`(= 2,530번째)에 있는 값이 곧 상위 10%가 시작되는 기준값이고, 10% 지점 `int(n * 0.1)`(= 281번째)의 값이 하위 10%의 끝 기준값이다. `np.sort`는 원본을 건드리지 않는 정렬된 복사본을 주므로 `rent` 자체의 순서(= `names`와의 행 대응)는 그대로 남는다 — 정렬본은 기준값을 읽는 데만 쓰고, 조건은 원래 순서의 `rent`·`ret`에 건다.

| 조각 | 뜻 |
| --- | --- |
| `int(n * 0.9)` | 2812 × 0.9 = 2530.8 → 2530. 정수 인덱스가 필요하니 `int`로 자른다 |
| `rent_sorted[2530]` | 정렬본에서 그 위치의 값. 이 값 이상이면 "대여 상위 10%" |
| `(rent >= top10) \| (ret <= low10)` | **또는** — 많이 빌려 가는 곳이거나, 거의 돌려놓지 않는 곳이거나 |

Step 4가 `&`로 두 조건을 **모두** 만족하는 좁은 집합(75곳)을 만든다면, Step 2는 `\|`로 **둘 중 하나**라도 걸리는 넓은 집합(564곳)을 만든다. 상위 10%가 약 282곳, 하위 10%가 약 282곳인데 합이 정확히 564인 것은 두 집합이 겹치지 않았다는 뜻이다 — 대여가 많은 곳은 반납도 많아서 "반납 하위 10%"에 들지 않는 것이 자연스럽다. 같은 데이터에서 `|`와 `&` 중 무엇을 고르느냐로 "관리 대상"의 뜻이 완전히 달라진다.

**Step 3 — 불균형 지수의 최댓값 자리**

```python
ratio = rent / ret
worst = np.argmax(ratio)
print("대여 반납이 가장 불균형한 대여소: ", names[worst, 1])   # 길음뉴타운푸르지오아파트 3단지
print(f"불균형 지수: {ratio[worst]:,.1f} 배")                   # 21.6 배
```

Step 1의 `argmax` 패턴을 파생 변수에 적용한 것이다. 대여가 반납의 21.6배인 대여소가 1위인데, 이 숫자는 이용량이 적은 곳에서 분모가 작아 튀어 오른 값일 가능성이 크다. 바로 이 한계 때문에 Step 4에서 `rent >= np.median(rent)`라는 이용량 조건을 **추가로** 거는 것이고, Step 5에서는 비율 대신 대수 차이 `rent - ret`로 지표를 바꾼다. 단계가 앞으로 갈수록 "가장 극단적인 하나"에서 "실제로 조치할 만한 집단"으로 질문이 옮겨 가는 흐름이다.

### 1-6. Step 4 — 복합 위험군: 유출형이면서 이용도 많은 대여소

```python
cond = (ratio >= 1.2) & (rent >= np.median(rent))
risk = station[cond]
print(f"대여건수 중앙값: {np.median(rent):,.0f}건")                       # 9,957건
print(f"복합 위험 대여소: {risk.shape[0]}곳")                               # 75곳
print(f"전체 대비 비율: {risk.shape[0] / station.shape[0] * 100:.1f}%")   # 2.7%
```

조건 두 개를 `&`로 겹친다. `ratio >= 1.2`는 "반납보다 대여가 20% 이상 많다", `rent >= np.median(rent)`는 "대여 건수가 **중앙값 이상**, 즉 상위 절반"이다. 불균형만 보면 이용이 거의 없는 외곽 대여소가 비율 때문에 튀어 오르니, 이용량 조건을 하나 더 걸어 "실제로 많은 사람이 겪는 불균형"만 남기는 설계다. 비율 지표의 분모가 작은 쪽이 튀는 성질을 `&` 조건 하나로 눌렀다는 점에서 지난 노트 3-3의 처방을 그대로 쓴 셈이다.

중앙값을 쓴 이유도 적어 둘 만하다. 대여 건수 평균은 13,290건인데 중앙값은 9,957건이다 — 몇몇 대형 대여소가 평균을 끌어올리는 **오른쪽으로 치우친 분포**라, "절반 지점"을 뜻하려면 평균이 아니라 중앙값이 맞다. `station[cond]`로 행 전체를 꺼내고 `shape[0]`으로 세는 것, 전체 대비 비율을 `shape[0]`끼리 나누는 것은 지난 실습과 같다. `:,.0f`는 천 단위 쉼표에 소수 0자리, `:.1f`는 소수 1자리 서식이다.

### 1-7. Step 5 — 순유출 Min-Max 정규화로 재배치 최우선 대여소

```python
net  = rent - ret                                          # 순유출 대수
norm = (net - np.min(net)) / (np.max(net) - np.min(net))   # Min-Max Scaling → 0~1
mask = norm >= 0.9
vip  = station[mask]
print(f"재배치 최우선 대여소: {vip.shape[0]}곳")              # 5곳

order = np.argsort(net[mask])[::-1]        # 순유출 많은 순
print(vip[order])                          # [ID, 대여, 반납]
print(names[mask, 1][order])               # 대여소 이름
print(net[mask][order])                    # 순유출 대수
```

Step 4의 `ratio`가 비율이었다면 `net = rent - ret`은 **대수 그 자체**다. 1년 동안 그 대여소에서 몇 대가 순수하게 빠져나갔는지이고, 재배치 트럭이 실제로 옮겨야 하는 양에 가까운 숫자다. 이 값의 범위는 −15,253 ~ +10,637로, 음수는 자전거가 쌓이는 곳이다. Min-Max 정규화를 걸면 가장 많이 쌓인 곳이 0, 가장 많이 빠져나간 곳이 1이 되고, `norm >= 0.9`는 "최대 유출의 90% 지점 이상"이라 5곳만 남는다. 지난 실습 Step 5와 공식·흐름이 같은데, 정규화 대상이 금액에서 **음수를 포함한 차이값**으로 바뀌었을 뿐이다. 최솟값을 빼 주는 공식이라 음수가 섞여 있어도 0~1로 잘 눌린다.

마지막 네 줄이 이번 실습에서 새로 보는 모양이다. **같은 `mask`와 같은 `order`를 서로 다른 세 배열에 똑같이 적용**한다.

| 식 | 뜻 |
| --- | --- |
| `np.argsort(net[mask])[::-1]` | 5곳의 순유출을 내림차순으로 세웠을 때의 **순번** (길이 5) |
| `vip[order]` | 숫자 표 5행을 그 순서로 |
| `names[mask, 1][order]` | 이름표에서 **같은 mask로 같은 5행**의 이름 열을 뽑고, 같은 순서로 |
| `net[mask][order]` | 순유출 5개를 같은 순서로 |

`mask`는 길이 2,812의 참·거짓이라 `station`에도 `names`에도 `net`에도 똑같이 걸 수 있고(세 배열의 행이 같은 대여소를 가리키니까), `order`는 길이 5의 순번이라 걸러진 5개짜리 배열 어디에나 똑같이 걸 수 있다. 결과는 상왕십리역 1번출구(10,637대), 아차산역 4번출구(9,978대), 신일해피트리아파트 앞(9,888대) 순이다. 지난 노트에서 "정렬 위치 순번으로 **다른 배열**을 같은 순서로 재배열한다"고 적어 둔 `argsort`의 용도가 여기서 숫자 표·이름표·지표 세 곳에 동시에 쓰였다 — `np.sort`로 `net`만 정렬했다면 어느 대여소인지 알 길이 없었을 것이다.

### 1-8. 단계별로 다시 보기 — 지난 실습과 달라진 점

| 단계 | 질문 | 꺼낸 도구 | 지난 실습 대비 |
| --- | --- | --- | --- |
| 준비 1 | 파일 두 장을 한 표로 | `genfromtxt(encoding='utf-8-sig')` → `vstack` | **새로움** — 병합, BOM |
| 준비 2 | 월별 행을 대여소별 한 행으로 | `np.unique` → `for`+마스크 → `np.sum` → `np.array(rows)` | **새로움** — group by를 손으로 |
| 준비 3 | 번호에 이름 붙이기 | `genfromtxt(dtype=str)` + 행 순서 맞추기 | **새로움** — 문자열 배열 |
| 지표 | 유출형인가 | `rent / ret` | 같음 (파생 변수) |
| Step 1 | 평균·최대·최소는, 그곳은 어디인가 | `mean`·`max`·`min` + `argmax`/`argmin` → `names[idx, 1]` | 같음 + **위치를 이름표에 꽂기** |
| Step 2 | 상위 10%·하위 10%에 드는 곳 | `np.sort` 복사본의 `int(n * 0.9)` 위치값 → `\|` 조건 | 같음 (분위 기준·`\|`) |
| Step 3 | 가장 불균형한 한 곳 | `np.argmax(ratio)` → `names[worst, 1]` | 같음 (`argmax`) |
| Step 4 | 유출형 **그리고** 많이 쓰는 곳 | `&` + `np.median` → `station[cond]` → `shape[0]` | 같음 (`&` 행 추출) |
| Step 5 | 가장 급한 곳 N개를 순서대로 | 정규화 → `mask` → `argsort[::-1]` → 세 배열에 같은 `order` | 같음 + **여러 배열 동기 정렬** |

뒤쪽 분석은 지난 실습의 반복이고, 앞쪽 준비가 이번에 늘어난 부분이다. 실제 데이터는 늘 "분석하기 좋은 한 장"으로 오지 않고, 파일이 나뉘어 있고 단위가 다르고(월 vs 대여소) 이름은 딴 파일에 있다. 그걸 한 표로 만드는 전처리가 분석 코드보다 길어지는 것이 보통이라는 점을 이 실습이 보여 준다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `np.unique(return_counts=True)` — 대여소별 행 수 확인

```python
ids, counts = np.unique(data[:, 0], return_counts=True)
print(counts.min(), counts.max())      # 1 12  — 12달 다 있는 곳부터 한 달만 있는 곳까지
print((counts < 12).sum())             # 연중 운영이 아닌 대여소 수
```

`np.unique`에 `return_counts=True`를 주면 값마다 몇 번 나왔는지도 함께 돌려준다. 1-2의 합계가 "12개월 합"이라는 전제가 모든 대여소에 맞는지 이렇게 먼저 확인하면, 운영 기간이 짧은 대여소를 월평균으로 바꿔 비교할지 제외할지를 결정할 수 있다. 데이터를 합치기 전에 키의 분포를 보는 습관이다.

### 2-2. 행 순서 대신 키로 이름 맞추기 — 딕셔너리와 `np.searchsorted`

```python
name_of = dict(zip(names[:, 0].astype(int), names[:, 1]))     # {102: '망원역 1번출구 앞', …}
print([name_of[int(i)] for i in vip[order][:, 0]])

# 또는 정렬된 ID 배열에서 위치를 찾는 넘파이식
pos = np.searchsorted(names[:, 0].astype(int), vip[order][:, 0].astype(int))
print(names[pos, 1])
```

1-3은 두 파일의 행 순서가 같다는 전제에 기댔다. 이름표에 한 줄이 빠지거나 순서가 다르면 조용히 틀리는 구조라, **ID를 키로 직접 찾는** 쪽이 튼튼하다. day02 딕셔너리의 `dict(zip(키들, 값들))`이 넘파이 배열에도 그대로 먹히고, 넘파이 안에서 끝내고 싶으면 `searchsorted`가 정렬된 배열에서 각 값의 위치를 이진 탐색으로 돌려준다. 판다스라면 `merge`(SQL JOIN)가 이 일을 한다.

### 2-3. 반복문 없는 그룹 합산 — `np.add.at`·`np.bincount`

```python
idx = np.searchsorted(ids, data[:, 0])         # 각 행이 ids의 몇 번째인지 (길이 32970)
rent_sum = np.bincount(idx, weights=data[:, 2]) # 같은 idx끼리 대여건수를 더함
ret_sum  = np.bincount(idx, weights=data[:, 3])
station2 = np.column_stack([ids, rent_sum, ret_sum])
print(np.array_equal(station, station2))        # True
```

1-2의 `for`를 넘파이만으로 없애는 관용구다. `searchsorted`로 각 행을 "몇 번째 대여소"라는 정수 인덱스로 바꾼 뒤, `bincount`에 `weights`를 주면 인덱스별로 가중치(대여건수)를 더해 준다. `np.add.at(out, idx, values)`도 같은 일을 한다. 2,812번 돌던 반복이 통째로 사라지지만 읽기는 어려워지므로, 데이터가 수십만 행을 넘어 반복이 느껴질 때 꺼내면 된다.

### 2-4. 두 그룹 결과를 한 표로 — `column_stack`과 `savetxt`

```python
result = np.column_stack([vip[order], net[mask][order]])     # ID·대여·반납·순유출
np.savetxt('./practice/ReportPractice/rebalance_top.csv', result, delimiter=',',
           fmt='%d', header='ID,대여,반납,순유출', comments='', encoding='utf-8-sig')
```

1-7에서 따로 찍은 세 출력을 열로 붙이면 보고서에 넣을 표가 된다. `column_stack`은 1차원 배열을 열로 세워 가로로 붙이고, `savetxt`의 `encoding='utf-8-sig'`를 주면 엑셀에서 한글 헤더가 깨지지 않는다. 문자열 이름 열까지 같이 쓰려면 배열 자료형이 하나여야 하는 넘파이의 한계에 걸리므로, 그때는 `zip`으로 줄을 만들어 `csv` 모듈로 쓰거나 판다스로 넘어간다.

### 2-5. 임계값을 숫자가 아니라 분위수로

```python
top = net >= np.percentile(net, 99)      # 순유출 상위 1%
print(top.sum())
```

`norm >= 0.9`는 최댓값에 상대적인 기준이라, 한 대여소가 유난히 튀면 나머지가 전부 0.9 아래로 깔려 몇 곳 안 남는다(이번 데이터가 그 경우로 5곳). "상위 몇 %"가 필요하면 `np.percentile`로 분위수를 잘라 쓰는 편이 분포 모양에 덜 흔들린다. Step 4의 `np.median`이 바로 50번째 백분위수다. Step 2의 `rent_sorted[int(n * 0.9)]`도 같은 일을 손으로 한 것이라 `np.percentile(rent, 90)`으로 바꿔 쓸 수 있다 — 다만 `percentile`은 기본적으로 두 값 사이를 보간하므로 정렬본의 위치값과 소수점이 조금 다를 수 있다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 같은 분석을 판다스로

```python
import pandas as pd
df = pd.concat([pd.read_csv(f, encoding='utf-8-sig') for f in files])   # vstack
st = df.groupby('ID')[['대여건수', '반납건수']].sum().reset_index()        # 1-2의 for+마스크
st = st.merge(pd.read_csv(names_file, encoding='utf-8-sig'), on='ID')  # 1-3의 행 순서 맞추기
st['순유출'] = st['대여건수'] - st['반납건수']
st.nlargest(5, '순유출')                                                 # Step 5
```

이번 실습의 준비 단계 세 개가 판다스에서는 `concat`·`groupby().sum()`·`merge` 한 줄씩이다. 넘파이로 마스크 반복문을 돌려 본 뒤에 보면 `groupby`가 "키마다 마스크를 만들어 집계"를 대신 해 주는 함수라는 것이, `merge`가 "행 순서에 기대지 않고 키로 붙이는" 안전한 1-3이라는 것이 보인다. 판다스를 배울 때 이 대응을 기억해 두면 함수 이름이 아니라 동작으로 외워진다.

### 3-2. 재배치 문제는 어디로 이어지나

유출형·유입형 대여소를 찾는 것은 공유 자전거 운영의 **리밸런싱**(rebalancing) 문제의 첫 단계다. 실무에서는 연 단위 합계가 아니라 시간대별 흐름(출근 시간엔 주거지에서 빠져나가 역으로 몰린다)을 보고, 유출 대여소 → 유입 대여소로 트럭이 도는 경로를 짜는 최적화(차량 경로 문제, VRP)로 이어진다. 넘파이 수준에서는 월별 `기준년월` 열을 살려 대여소×월 행렬을 `reshape`로 만들고 `axis=1`로 계절성을 보는 것이 다음 실습거리다.

### 3-3. 구조화 배열과 문자열·숫자 혼합

이번에 숫자 표와 이름표를 따로 둔 것은 넘파이 배열이 자료형 하나만 갖기 때문이다. 넘파이에도 열마다 자료형이 다른 **구조화 배열**(`dtype=[('ID', 'i4'), ('name', 'U40')]`, `genfromtxt(names=True, dtype=None)`)이 있어서 한 표에 섞을 수는 있지만, 2차원 인덱싱 `x[:, 1]`이 막히고 문법이 달라진다. 이 불편이 커지는 지점이 판다스 `DataFrame`(열마다 자료형이 다른 표)이 존재하는 이유다.

### 다음에 볼 키워드

- `encoding='utf-8-sig'`·BOM·`dtype=str`·`<U41`·구조화 배열
- `np.vstack`으로 파일 병합·`np.unique`(`return_counts`)·마스크 반복으로 group by·`np.array(rows)`
- `argmax`/`argmin` 위치를 이름표에 꽂기 `names[np.argmax(rent), 1]`·`np.sort` 복사본의 `int(n * 0.9)` 위치값으로 분위 기준선·`|` vs `&`
- `np.median` vs 평균(치우친 분포)·파생 변수 `rent / ret`·순유출 `rent - ret`
- 같은 `mask`·같은 `order`를 여러 배열에 — `names[mask, 1][order]`
- `searchsorted`·`bincount(weights=)`·`np.add.at`·`column_stack`·`percentile`
- 판다스 `concat`·`groupby().sum()`·`merge`·`nlargest`·리밸런싱·VRP

## 실습 파일

- `KDT_2026/2026_Python/practice/ReportPractice/Report.py` — `np.genfromtxt(delimiter=',', skip_header=1, encoding='utf-8-sig')`로 상반기 `(16403, 4)`·하반기 `(16567, 4)` CSV 읽기 → `np.vstack`으로 `(32970, 4)` 병합, `np.unique(data[:, 0])`로 대여소 번호 2,812개 → `for i in ids`·`m = data[:, 0] == i`·`np.sum(data[m, 2])`·`np.sum(data[m, 3])`로 대여소별 합계 `rows` → `np.array(rows)` `(2812, 3)` `station`, 이름표 `genfromtxt(dtype=str)` `(2812, 2)`와 `station[:3]`·`names[:3, 1]` 순서 확인, `rent`·`ret` 열 추출과 `ratio = rent / ret` 불균형 지수, Step 1 `np.mean`·`np.max`·`np.min`과 `names[np.argmax(rent), 1]`·`names[np.argmin(rent), 1]`(평균 13,290.6·최대 162,990 마곡나루역 2번 출구·최소 0), Step 2 `np.sort` 정렬본의 `int(n * 0.9)`·`int(n * 0.1)` 위치값으로 대여 상위 10% 기준 27,938·반납 하위 10% 기준 2,017 → `(rent >= top10) | (ret <= low10)` 564곳, Step 3 `np.argmax(ratio)` → `names[worst, 1]`(길음뉴타운푸르지오아파트 3단지·21.6배), Step 4 `(ratio >= 1.2) & (rent >= np.median(rent))` → `station[cond]`·`shape[0]`(중앙값 9,957건·75곳·2.7%), Step 5 `net = rent - ret` → Min-Max 정규화 → `mask = norm >= 0.9`(5곳) → `np.argsort(net[mask])[::-1]`을 `vip[order]`·`names[mask, 1][order]`·`net[mask][order]` 세 배열에 동일 적용
- `KDT_2026/2026_Python/practice/ReportPractice/ddareungi_1-6.csv` — 헤더 `ID,기준년월,대여건수,반납건수`(BOM 포함), 2025년 1~6월 대여소×월 16,403행
- `KDT_2026/2026_Python/practice/ReportPractice/ddareungi_7-12.csv` — 같은 구조, 2025년 7~12월 16,567행
- `KDT_2026/2026_Python/practice/ReportPractice/ddareungi_names.csv` — 헤더 `ID,이름`, 대여소 2,812행 (ID 오름차순)

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day07 넘파이로 고객 구매 데이터 분석 실습]] · [[Python day07 넘파이 배열 병합·정렬과 조건 필터링]] · [[Python day07 넘파이 통계 함수와 axis]] · [[Python day06 넘파이 인덱싱·슬라이싱과 배열 연산]] · [[KDT_2026 학습 지도]]
