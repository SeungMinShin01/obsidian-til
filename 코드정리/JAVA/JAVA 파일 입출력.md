---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA 파일 입출력

> 상위: [[JAVA 예외와 유틸]]

전부 ※. 프로그램을 꺼도 데이터가 남게 하는 가장 가벼운 방법이다(DB 전 단계).

## 읽기 — Files.readAllLines

```java
import java.nio.file.*;
import java.util.List;

Path path = Path.of("books.txt");

if (Files.exists(path)) {
    List<String> lines = Files.readAllLines(path);
    for (String line : lines) {
        String[] cols = line.split(",");
    }
}
```

- `Path.of("파일명")`이 경로 객체, `readAllLines`가 전체를 줄 단위 리스트로 읽는다
- 한 줄을 `split(",")`으로 잘라 DTO로 복원하는 것까지가 세트다(CSV 읽기)
- 없는 파일을 읽으면 예외가 나므로 `Files.exists`로 먼저 확인하거나 try-catch로 감싼다. `IOException` 처리가 필수다

## 쓰기 — Files.write

```java
List<String> lines = new ArrayList<>();
for (BookDto b : list) {
    lines.add(b.getNo() + "," + b.getTitle() + "," + b.getAuthor());
}
Files.write(path, lines);

Files.writeString(path, "한 덩어리 문자열");
Files.write(path, lines, StandardOpenOption.APPEND);
```

- 리스트를 넘기면 줄 단위로 저장된다. 기본은 덮어쓰기, `APPEND` 옵션이면 이어쓰기(로그에 적합)
- DTO→한 줄 문자열(저장), 한 줄→DTO(복원) 변환을 짝으로 만들어 두면 그게 파일 버전 DAO다

## 프로그램에 끼우는 자리

```java
public class BookDao {
    private ArrayList<BookDto> list = load();

    public boolean save(BookDto dto) {
        list.add(dto);
        persist();
        return true;
    }
}
```

- 시작할 때 파일→리스트로 불러오고(load), 변경 때마다 리스트→파일로 내린다(persist)
- 저장 위치가 ArrayList(메모리)→파일→MySQL로 올라가는 동안 DAO 바깥은 그대로다 — 계층 분리의 이득이 여기서도 반복된다
