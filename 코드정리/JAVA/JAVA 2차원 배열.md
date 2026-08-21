---
출처: Claude 분석
작성일: 2026-08-21
tags: [코드정리]
---

# JAVA 2차원 배열

> 상위: [[JAVA 배열과 String]]

## 선언과 접근

```java
int[][] grid = new int[3][4];
int[][] init = { {1, 2}, {3, 4}, {5, 6} };

grid[0][2] = 7;
int rows = grid.length;
int cols = grid[0].length;
```

- `new int[3][4]`는 3행 4열이다. 실제로는 "배열 3개를 담은 배열"이라 `grid.length`는 행 수, `grid[0].length`는 열 수다
- 접근은 `[행][열]` 순서다. 좌석표·시간표·2차원 맵이 전부 이 구조다

## 순회

```java
for (int i = 0; i < grid.length; i++) {
    for (int j = 0; j < grid[i].length; j++) {
        System.out.print(grid[i][j] + " ");
    }
    System.out.println();
}

for (int[] row : grid) {
    for (int cell : row) { }
}
```

- 바깥 루프가 줄, 안쪽 루프가 칸이다. 별점·피라미드·구구단 출력과 같은 뼈대다
- 인덱스가 필요 없으면 향상된 for 이중으로 쓴다. 출력은 `Arrays.deepToString(grid)`(1차원용 toString은 주소가 나온다)

## 행마다 길이가 다른 배열 ※

```java
int[][] jagged = new int[3][];
jagged[0] = new int[2];
jagged[1] = new int[5];
```

- 열 크기를 비워 두면 행마다 다른 길이를 붙일 수 있다(가변 배열)

## 활용 — 좌석표

```java
boolean[][] seat = new boolean[5][6];

if (!seat[r][c]) {
    seat[r][c] = true;
} else {
    System.out.println("이미 예약된 좌석입니다.");
}
```

- boolean 2차원 배열이 "자리 있음/없음" 표가 된다. 영화관 예매·강의실 배치의 기본형이고, DB로 가면 이 표가 좌석 테이블이 된다
