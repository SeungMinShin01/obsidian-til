---
출처: Claude 대화
작성일: 2026-09-03
tags: [프로젝트, python]
---

# 변경이력 - main.py

`main.py`가 기능이 늘며 어떻게 변했는지의 추적. 코드 자체보다 **책임이 어떻게 옮겨갔는가**를 본다. 누적형 — 바뀔 때마다 아래에 덧붙인다.

## 줄 수로 본 궤적

| 커밋 | 무엇 | 줄 수 |
| --- | --- | --- |
| 파이썬으로 실행 기록 | 실행 기록만 | ~15 |
| SQLite 저장 계층 | store 호출 | ~30 |
| writer 추가 | 렌더 호출 | ~40 |
| sources 어댑터 분리 | `collect_all` 등장 | ~55 |
| moef 어댑터 | 로그에 계층별 숫자 | ~60 |
| Secret 주입·traceback | 예외 추적 | ~68 |
| known_ids 계약 | 수집 전 conn·id집합 | ~74 |

줄 수는 완만히 늘지만 **책임의 성격이 몇 번 바뀌었다.** 아래가 변곡점.

## 1. 시작 — main이 곧 전부였다

```python
def main() -> None:
    stamp = now_utc()
    append_run_log(f"실행: {stamp} UTC (python)")
    print(f"기록 완료: {stamp} UTC")
```

셸을 파이썬으로 옮긴 첫 형태. main이 직접 일한다. 할 일이 하나라 나눌 것도 없었다.

## 2. 저장·표현이 붙으며 — main이 지휘자로

store·writer가 생기며 main이 **직접 하던 일을 남에게 시키는 자리**가 됐다.

```python
conn = store.connect()
new_count = store.upsert_jobs(conn, FAKE_JOBS, stamp)
rendered = writer.render_jobs(conn)
```

「수집기 08」의 전환. main은 순서만 안다 — 수집은 store, 표현은 writer. 실제 일이 딴 파일로 나가며 main은 오히려 **얇아졌다.**

## 3. `collect_all` 등장 — 순회·격리가 함수로 승격

`FAKE_JOBS`를 `sources/fake.py`로 빼고 소스 순회 함수가 생겼다(「수집기 18」).

```python
def collect_all(sources: list) -> tuple[list[dict], list[str]]:
    for source in sources:
        try:
            jobs.extend(source.fetch())
        except Exception as e:
            failed.append(f"{name}({type(e).__name__})")
    return jobs, failed
```

main() 안 수집 로직이 **별도 함수로 승격.** 격벽(try/except continue)이 여기 살고, main()은 결과만 받는다. 책임이 한 겹 더 나뉘었다 — "무엇을 부를지"(main)와 "어떻게 순회·격리할지"(collect_all).

## 4. moef 어댑터 — 로그가 계층을 말하기 시작

가짜 → 진짜 API로 바뀌며 로그가 계층별 숫자를 담았다.

```python
message = f"실행 : {stamp} UTC - 수집 {len(jobs)}건 신규 {new_count}건, 누적 {total}건, 마크다운 {rendered}건"
if failed:
    message += f", 실패 소스 {' '.join(failed)}"
```

main()의 마지막 책임이 **"각 계층이 돌려준 숫자를 한 줄로 요약"**으로 정해졌다. store는 마크다운 수를, writer는 수집 수를 모른다 — 전체를 보는 자리는 지휘자뿐.

## 5. traceback — 조용한 실패에 소리를 붙였다

12일 공백·URLError를 겪고 except에 두 줄이 붙었다.

```python
    except Exception as e:
        failed.append(f"{name}({type(e).__name__})")
        print(f"[{name}] {e!r}")
        traceback.print_exc()
```

격벽은 유지하되 삼킨 실패의 상세를 Actions 로그로 흘린다. run-log엔 종류만, Actions 로그엔 전체 추적(「수집기 22」 두 층 로그). `import traceback`을 빠뜨려 except 안에서 NameError가 났던 것도 이 단계.

## 6. known_ids 계약 — main이 DB를 먼저 열게 됐다

jumpit(목록/상세 2단계)이 붙으며 **수집 순서가 뒤집혔다.**

```python
# 이전
jobs, failed = collect_all(SOURCES)
conn = store.connect()

# 이후
conn = store.connect()
known = store.all_ids(conn)
jobs, failed = collect_all(SOURCES, known)
```

지금까지 어댑터는 DB를 몰랐다. jumpit은 "아는 건 상세 안 부름"이 필요해 DB 상태를 알아야 했고, 방향(main→store, main→sources)을 지키려 **main이 id 집합을 구해 넘기는** 방식을 택했다. `conn`·`known`이 수집보다 위로 올라왔고, `collect_all`도 `(sources, known_ids)`로 늘었다.

## 관찰

### main은 늘 "안 하는" 쪽으로 갔다

| 단계 | main이 직접 하던 것 | 넘긴 곳 |
| --- | --- | --- |
| 시작 | 전부 | (자기) |
| 저장·표현 | 순서 지휘만 | store, writer |
| collect_all | 부를 목록만 | collect_all |
| 지금 | 요약·순서·id 조달 | 나머지 전부 |

기능이 늘수록 줄 수는 조금 늘지만 **하는 일은 추상적**이 된다. 구체적 일(HTTP·SQL·파싱)은 아래 계층으로 내려갔다. 지휘자가 실무를 안 할수록 소스를 갈아끼우기 쉽다 — 좋은 신호.

### 계약이 바뀌면 main도 바뀐다

`fetch()` → `fetch(known_ids)` 한 번의 계약 변경이 main의 순서까지 바꿨다. 덕 타이핑이라 컴파일러가 안 막아주니 조정은 사람 몫이고, `collect_all() missing 1 argument`·`UnboundLocalError`로 두 번 걸렸다.

### 리팩터 신호

main이 다시 뚱뚱해지면(구체적 일이 돌아오면) 계층을 하나 더 팔 때다.
