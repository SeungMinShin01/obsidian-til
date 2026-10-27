---
출처: Claude 분석
원본: KDT_2026/2026_Python/practice/practice2.py, practice/customer_purchase_data.csv
작성일: 2026-10-27
tags: [학습, python]
---

# Python day07 — 넘파이로 고객 구매 데이터 분석 실습

> 실습 파일: `practice/practice2.py`, `practice/customer_purchase_data.csv`
> 허브: [[Python 정리본 인덱스]] · 이전: [[Python day07 넘파이 통계 함수와 axis]] · 다음: (아직 없음)

day06~07에서 익힌 넘파이 도구를 **실제 데이터 파일 하나에 처음으로 전부 꺼내 쓴** 실습이다. 고객 1,000명의 방문·체류·장바구니·구매 금액이 든 CSV를 `genfromtxt`로 읽어 2차원 배열로 만들고, 다섯 단계 미션을 반복문 없이 풀었다. 열 하나 뽑아 통계 내기(Step 1), `|`로 충성 고객 걸러 ID만 꺼내기(Step 2), 열끼리 나눠 새 지표를 만들고 `argmax`로 1등 찾기(Step 3), `&`로 이탈 위험군 행 전체 추출하고 세기(Step 4), Min-Max 정규화로 VVIP를 고른 뒤 `argsort`로 금액순 상위 5명 뽑기(Step 5). 한 단계마다 "어떤 도구를 꺼내는가"를 정리해 두면 넘파이 문법이 어디에 쓰이는 것인지 한눈에 들어온다.

## 1. 배운 내용

### 1-1. 데이터 준비 — CSV를 2차원 배열로

```python
import numpy as np
# [기본 제공 코드] CSV 파일 로드 (헤더 제외, 콤마 구분)
data = np.genfromtxt('./practice/customer_purchase_data.csv', delimiter=',', skip_header=1)
print(f"데이터 형태: {data.shape}")   # 데이터 형태: (1000, 5)
```

| 인자 | 뜻 |
| --- | --- |
| `'./practice/…csv'` | 파일 경로 — 실행하는 폴더(`2026_Python`) 기준 상대 경로 |
| `delimiter=','` | 칸 구분 문자. CSV(Comma-Separated Values)니까 쉼표 |
| `skip_header=1` | 첫 줄(`Customer_ID,Visits,…` 열 이름)은 숫자가 아니라서 건너뜀 |

결과는 **1000행 5열의 2차원 배열**이고 자료형은 전부 `float64`다. 넘파이 배열은 한 가지 자료형만 담으니 고객ID `1001`도 `1001.`로 들어온다. 열 번호와 뜻은 파일 머리의 주석대로다.

| 열 | 이름 | 뜻 |
| --- | --- | --- |
| `[0]` | ID | 고객ID |
| `[1]` | Visits | 방문 횟수 |
| `[2]` | Stay_Time | 평균 체류 시간(분) |
| `[3]` | Cart_Items | 장바구니 담은 횟수 |
| `[4]` | Purchase_Amount | 최종 구매 금액($) |

이 표가 이후 모든 단계의 지도다. `data[:, 4]`가 보이면 "모든 행의 구매 금액", `data[:, 1]`이면 "모든 행의 방문 횟수"로 읽는다. 열 이름이 숫자 인덱스로만 남는 것이 넘파이의 불편한 점이고, 판다스가 이름으로 열을 부르게 해 주는 이유다.

### 1-2. Step 1 — 열 하나 뽑아 기초 통계

```python
sales = data[:, 4]                     # 모든 행(:)의 4번 열 → 1차원 (1000,)
print(f"평균 구매 금액: {np.mean(sales):,}원")   # 1,319.483
print(f"총 매출액: {np.sum(sales):,}원")         # 1,319,483.0
```

`data[:, 4]`는 day06의 2차원 슬라이싱이다. 행 자리에 `:`(전부), 열 자리에 정수 `4` — 정수로 고르면 그 축이 사라지므로 결과는 2차원이 아니라 **길이 1000의 1차원 배열**이 된다. 이 배열이 `sales`이고, 지난 노트의 `np.mean`·`np.sum`을 바로 걸 수 있다.

f-문자열 안의 `:,`는 천 단위 쉼표 서식이다. `{값:,}`은 `1319483.0`을 `1,319,483.0`으로 찍는다. 평균이 `1,319.483`처럼 소수가 길게 나오면 `{np.mean(sales):,.0f}`로 소수 자리를 잘라 줄 수 있다 — 서식 지정자는 `:`뒤에 `,`(쉼표) 다음 `.0f`(소수 0자리 고정) 순서로 이어 붙인다.

### 1-3. Step 2 — `|`로 충성 고객 걸러 ID만 꺼내기

```python
loyal = (data[:, 1] >= 20) | (data[:, 4] >= 2000)   # 방문 20회 이상 이거나 구매 2000달러 이상
loyal_ids = data[loyal, 0]                           # 조건이 참인 행의 0번 열
print(f"충성고객: {loyal}")       # [ True  True False  True …]  — 참·거짓 1000개
print(f"충성고객 ID: {loyal_ids}") # [1001. 1002. 1004. 1006. …]  — 642명
```

이 단계가 실습의 핵심 문법이다. 두 줄에 지난 두 노트의 내용이 다 들어 있다.

| 조각 | 하는 일 | 어디서 배웠나 |
| --- | --- | --- |
| `data[:, 1] >= 20` | 방문 횟수 열을 20과 비교 → 참·거짓 1000개 | 배열 ↔ 스칼라 비교는 모든 요소에 |
| `(…) \| (…)` | 두 조건 중 하나라도 참이면 참 — `or` 대신 `\|`, 소괄호 필수 | 다수 조건 `&`·`\|`·`~` |
| `data[loyal, 0]` | **행 자리에 불리언 배열, 열 자리에 정수** | 불리언 인덱싱 + 2차원 쉼표 인덱싱 |

`data[loyal, 0]`의 모양을 눈여겨볼 만하다. 행 자리에 참·거짓 배열을 넣으면 "참인 행만", 열 자리에 `0`을 넣으면 "그 행들의 0번 열만" — 두 가지 고르기를 **쉼표 하나로 동시에** 한다. `data[loyal][:, 0]`으로 두 번에 나눠도 결과는 같은데, 한 번에 쓰는 쪽이 넘파이 관용구다. 조건을 `loyal`이라는 이름의 변수에 먼저 담아 두는 것도 지난 노트에서 본 습관이다. 변수 이름이 "이게 조건이다"를 말해 주고, 참인 개수를 `loyal.sum()`으로 바로 셀 수 있다(642명).

### 1-4. Step 3 — 열끼리 나눠 새 지표 만들고 `argmax`로 1등 찾기

```python
arpv = data[:, 4] / data[:, 1]        # 구매 금액 ÷ 방문 횟수 = 방문당 평균 매출
best_idx = np.argmax(arpv)            # 가장 큰 값의 위치 → 516
print(best_idx, data[best_idx, 0])    # 516 1517.0
```

`data[:, 4] / data[:, 1]`은 길이 1000짜리 배열 두 개의 나눗셈이다. **같은 위치끼리** 나뉘어 고객마다 "방문 한 번에 얼마 썼나"가 계산된다 — 반복문으로 1000번 돌 일을 한 줄로 끝내는 벡터 연산이다. 결과 배열 `arpv`(Average Revenue Per Visit)는 **원본 표에는 없던 새 열**인데, 이렇게 기존 열들을 조합해 새 지표를 만드는 것을 데이터 분석에서 파생 변수라고 부른다.

`np.argmax(arpv)`는 지난 노트의 "arg = 위치"다. 가장 높은 값이 아니라 **가장 높은 사람이 몇 번째 행인지**(516)를 받아, 그 행 번호로 `data[best_idx, 0]`에서 고객ID(1517)를 꺼낸다. 값이 필요하면 `arpv[best_idx]`(525.0), 그 고객의 모든 정보가 필요하면 `data[best_idx]`다. "최댓값 → 그 위치 → 그 위치의 다른 열"로 이어 가는 세 단계가 `argmax`가 존재하는 이유다.

이 고객의 행을 보면 방문 1회에 525달러를 쓴 사람이다. 방문당 매출은 방문이 적을수록 커지는 성질이 있어서 "충성 고객"과는 다른 지표라는 점도 같이 적어 둔다. 비율 지표를 만들 때는 분모가 작은 쪽이 튀어 오를 수 있다는 걸 염두에 둬야 한다.

### 1-5. Step 4 — `&`로 이탈 위험군 행 전체 추출하고 세기

```python
risk = data[(data[:, 1] <= 3) & (data[:, 3] <= 1)]   # 방문 3회 이하 이면서 장바구니 1회 이하
print(risk.shape[0])                                  # 23
```

Step 2와 짝이 되는 단계다. 이번에는 `|`가 아니라 **`&`(둘 다 참)**이고, 열을 지정하지 않아 `data[조건]`만 썼으므로 참인 **행 전체**(5열 그대로)가 2차원 배열로 나온다. 조건을 변수에 담지 않고 대괄호 안에 바로 넣었는데, 괄호가 두 겹이라 읽기가 어렵지 않으면 이렇게 써도 된다.

사람 수는 `risk.shape[0]`이다. `shape`이 `(23, 5)`니까 `[0]`이 행 개수다. 같은 답을 `len(risk)`나 조건 배열의 `.sum()`으로도 얻을 수 있다.

| Step 2 (충성) | Step 4 (이탈 위험) |
| --- | --- |
| `(A) \| (B)` — 하나라도 | `(A) & (B)` — 둘 다 |
| `data[조건, 0]` — ID 열만 | `data[조건]` — 행 전체 |
| 결과 1차원 `(642,)` | 결과 2차원 `(23, 5)` |

### 1-6. Step 5 — Min-Max 정규화로 VVIP 고르고 금액순 상위 5명

```python
norm = (sales - np.min(sales)) / (np.max(sales) - np.min(sales))  # 0~1 사이로
vvip = data[norm >= 0.9]                                           # 0.9 이상 → 39명
order = np.argsort(vvip[:, 4])[::-1]                               # 구매 금액 내림차순 순번
print(vvip[order][:5])
# [[1784.   49.  125.9  23. 2740.]
#  [1828.   50.  132.6  21. 2673.]
#  [1216.   49.  131.8  22. 2639.]
#  [1154.   49.  120.5  23. 2638.]
#  [1030.   49.  123.6  23. 2630.]]
```

세 줄에 서로 다른 도구가 하나씩 들어 있다.

**정규화** — `(x - 최솟값) / (최댓값 - 최솟값)` 공식을 배열 전체에 한 번에 건다. `sales`는 배열, `np.min(sales)`는 숫자 하나라서 "스칼라를 모든 요소에" 규칙으로 1000개가 동시에 계산되고, 최솟값인 사람은 0, 최댓값인 사람은 1이 된다. 이 데이터에서는 최솟값 0, 최댓값 2740이니 `norm = sales / 2740`과 같은 셈이다. 지난 노트 2-4에서 공식만 봤던 것이 여기서 실제 데이터에 걸렸다.

**VVIP 추출** — `norm >= 0.9`는 "최댓값의 90% 이상"(2466달러 이상)이고, 그 조건을 `data`에 걸어 행 전체를 꺼낸다. `norm`은 `sales`에서 나온 배열이지만 길이가 1000으로 `data`의 행 개수와 같으니 `data`의 행 선택에 그대로 쓸 수 있다 — **조건을 만든 배열과 조건을 거는 배열이 달라도 길이만 맞으면 된다.**

**정렬** — `np.argsort(vvip[:, 4])`는 VVIP 39명의 구매 금액을 **오름차순으로 세웠을 때의 행 순번**이고, `[::-1]`로 뒤집어 내림차순 순번을 만든 뒤, `vvip[order]`로 **행 전체를 그 순서대로** 다시 꺼낸다. 지난 노트에서 "2차원 표는 `np.sort`가 아니라 `argsort` + 팬시 인덱싱으로 행을 통째로 정렬한다"고 적어 둔 바로 그 모양이다. 마지막 `[:5]`는 앞 5행 슬라이스다. 금액 열만 `np.sort`로 정렬했다면 "누구인지"가 사라졌을 텐데, `argsort`를 거쳐서 ID·방문·체류가 금액과 짝을 유지한 채 나왔다.

### 1-7. 다섯 단계를 도구별로 다시 보기

| Step | 질문 | 꺼낸 도구 |
| --- | --- | --- |
| 1 | 한 열의 평균·합은? | `data[:, j]` 열 추출 → `mean`·`sum` |
| 2 | 조건 A **또는** B인 사람의 ID는? | `(A) \| (B)` → `data[조건, 0]` |
| 3 | 두 열로 만든 지표가 가장 높은 사람은? | 배열끼리 `/` → `argmax` → `data[idx, 0]` |
| 4 | 조건 A **그리고** B인 사람 전체와 수는? | `(A) & (B)` → `data[조건]` → `shape[0]` |
| 5 | 상위 그룹을 금액순으로 N명? | 정규화(스칼라 연산) → 불리언 → `argsort[::-1]` → 팬시 인덱싱 → `[:N]` |

`for`가 한 번도 안 나온다. "열을 뽑는다 → 조건을 만든다 → 조건으로 행을 고른다 → 집계하거나 정렬한다"의 네 동작이 반복되고, 넘파이 문법은 이 네 동작의 표기법이라고 보면 된다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 열 번호에 이름 붙이기

```python
ID, VISITS, STAY, CART, AMOUNT = range(5)
sales = data[:, AMOUNT]
loyal = (data[:, VISITS] >= 20) | (data[:, AMOUNT] >= 2000)
```

`data[:, 4]`가 늘어나면 4가 금액인지 장바구니인지 되돌아보게 된다. 열 순서대로 상수에 이름을 붙여 두면 코드가 읽히고, 열 순서가 바뀌어도 한 줄만 고치면 된다. 판다스가 `df['Purchase_Amount']`로 해 주는 일을 넘파이에서 손으로 하는 셈이다.

### 2-2. 조건 두 개를 겹쳐 분할표 만들기

```python
hi_visit = data[:, 1] >= 20
hi_amount = data[:, 4] >= 2000
print((hi_visit & hi_amount).sum(), (hi_visit & ~hi_amount).sum())
print((~hi_visit & hi_amount).sum(), (~hi_visit & ~hi_amount).sum())
```

Step 2의 두 조건을 `&`와 `~`로 네 조합으로 나누면 "많이 오고 많이 쓰는 / 많이 오지만 적게 쓰는 / …" 2×2 표가 된다. 조건을 변수에 담아 두었기에 가능한 조합이고, 고객 세분화의 가장 단순한 형태다.

### 2-3. 집계 결과를 보기 좋게 — 서식 지정자

```python
print(f"{np.mean(sales):,.1f}")   # 1,319.5   — 쉼표 + 소수 1자리
print(f"{norm[0]:.2%}")           # 73.69%    — 비율을 퍼센트로
print(f"{int(data[best_idx, 0])}") # 1517      — 1517.0 대신 정수로
```

`float64` 배열에서 꺼낸 고객ID가 `1517.0`으로 찍히는 게 어색하면 `int()`로 바꾸거나, 열 하나를 `data[:, 0].astype(int)`로 통째로 정수화한다. 전체 출력 모양은 `np.set_printoptions(precision=1, suppress=True)`로 소수 자릿수와 지수 표기(`1.5e+03`)를 끌 수 있다.

### 2-4. 읽기 옵션 — 이름·자료형 살려서

```python
d = np.genfromtxt(path, delimiter=',', names=True)    # 헤더를 열 이름으로 → d['Visits']
d = np.loadtxt(path, delimiter=',', skiprows=1)        # 결측값 없는 깨끗한 파일이면 더 빠름
```

`names=True`를 주면 구조화 배열이 되어 `d['Purchase_Amount']`처럼 이름으로 열을 부를 수 있다(단, 2차원 인덱싱 `d[:, 4]`는 더 못 쓴다). `loadtxt`는 `genfromtxt`의 가벼운 판으로, 빈 칸이 없는 파일에서 더 빠르다. 빈 칸이 있으면 `genfromtxt`가 `nan`으로 채워 주고, 지난 노트의 `nanmean`류가 필요해진다.

### 2-5. 결과 저장

```python
np.savetxt('./practice/vvip_top5.csv', vvip[order][:5], delimiter=',', fmt='%.1f',
           header='ID,Visits,Stay_Time,Cart_Items,Purchase_Amount', comments='')
```

읽은 것의 반대다. `fmt`로 숫자 서식을, `header`로 첫 줄을 넣고, `comments=''`를 주지 않으면 헤더 앞에 `#`이 붙는다. 분석 결과를 다른 사람에게 넘길 때 배열을 그대로 CSV로 내보내는 가장 짧은 길이다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 같은 분석을 판다스로

이 실습을 그대로 판다스로 옮기면 `df = pd.read_csv(path)` 한 줄로 읽고, `df['Purchase_Amount'].mean()`, `df[(df['Visits'] >= 20) | (df['Purchase_Amount'] >= 2000)]['Customer_ID']`, `df['arpv'] = df['Purchase_Amount'] / df['Visits']`, `df.loc[df['arpv'].idxmax(), 'Customer_ID']`, `df.sort_values('Purchase_Amount', ascending=False).head(5)`가 된다. 열을 이름으로 부르고 `sort_values`가 행을 통째로 정렬해 주는 것 말고는 **구조가 똑같다** — 불리언 필터에 `&`·`|`와 소괄호가 필요한 것도, `idxmax`가 `argmax`인 것도 그대로다. 판다스가 넘파이 위에 올라가 있기 때문이고, 여기서 넘파이로 한 번 손으로 풀어 본 것이 판다스 문법을 외우는 게 아니라 이해하게 만드는 바탕이 된다.

### 3-2. RFM과 고객 세분화

이 미션의 "충성·이탈 위험·VVIP"는 마케팅의 RFM 분석(Recency·Frequency·Monetary — 최근성·빈도·금액)을 단순화한 것이다. 방문 횟수가 F, 구매 금액이 M에 해당한다. 실제로는 각 지표를 `np.percentile`로 등급(1~5)으로 나눈 뒤 조합해 세그먼트를 만들고, 더 나아가면 K-means 같은 군집 알고리즘이 "비슷한 고객 묶음"을 자동으로 찾는다. 그 입력으로 넣기 전에 지표마다 단위가 다르니 Step 5의 Min-Max나 z-score 표준화를 **열마다**(`axis=0`) 걸어 스케일을 맞추는 것이 전처리의 첫 단계다.

### 3-3. 비율 지표와 0으로 나누기

Step 3의 `금액 / 방문`은 이 데이터에서 방문이 최소 1회라 무사했지만, 방문 0회가 있으면 `0으로 나누기`로 `inf`(무한대)가 나오고 `RuntimeWarning`이 뜬다(파이썬 `ZeroDivisionError`와 달리 넘파이는 멈추지 않는다). `np.divide(a, b, out=np.zeros_like(a), where=b != 0)`로 분모가 0인 자리를 0으로 두거나, `np.errstate`로 경고를 제어한다. 그리고 비율 지표가 분모가 작은 쪽에서 튀는 성질(1-4의 방문 1회 고객)은 분석 결과를 해석할 때 늘 함께 봐야 하는 부분이다 — "최소 방문 n회 이상" 같은 조건을 `&`로 하나 더 거는 것이 흔한 처방이다.

### 다음에 볼 키워드

- `genfromtxt`(`delimiter`·`skip_header`·`names`)·`loadtxt`·`savetxt`·`astype`
- `data[:, j]` 열 추출·`data[mask, j]`·`data[mask]` 행 추출·`shape[0]`
- 파생 변수(열끼리 연산)·`argmax` → 행 → 다른 열
- Min-Max 정규화·z-score·`axis=0`으로 열마다 한 번에
- `argsort[::-1]` + 팬시 인덱싱으로 행 통째 정렬·`[:N]`
- 판다스 `read_csv`·불리언 필터·`idxmax`·`sort_values`·`describe`·RFM·K-means

## 실습 파일

- `KDT_2026/2026_Python/practice/practice2.py` — `np.genfromtxt(delimiter=',', skip_header=1)`로 CSV를 `(1000, 5)` 배열로 읽기, Step 1 `data[:, 4]`로 `sales` 추출과 `np.mean`·`np.sum`(f-문자열 `:,` 천 단위 서식), Step 2 `(data[:, 1] >= 20) | (data[:, 4] >= 2000)` 조건 변수 `loyal`과 `data[loyal, 0]`으로 ID만 추출(642명), Step 3 `data[:, 4] / data[:, 1]` 파생 지표 `arpv`와 `np.argmax` → `data[best_idx, 0]`(516행·ID 1517), Step 4 `data[(…<= 3) & (…<= 1)]` 행 전체 추출과 `shape[0]`(23명), Step 5 `(sales - min) / (max - min)` Min-Max 정규화 → `data[norm >= 0.9]`(39명) → `np.argsort(vvip[:, 4])[::-1]`로 행 통째 내림차순 → `[:5]`
- `KDT_2026/2026_Python/practice/customer_purchase_data.csv` — 헤더 `Customer_ID,Visits,Stay_Time,Cart_Items,Purchase_Amount` + 고객 1,000행 (ID 1001~2000)

## 관련 노트

[[Python 정리본 인덱스]] · [[Python day07 넘파이 통계 함수와 axis]] · [[Python day07 넘파이 배열 병합·정렬과 조건 필터링]] · [[Python day06 넘파이 인덱싱·슬라이싱과 배열 연산]] · [[KDT_2026 학습 지도]]
