---
출처: 내가 작성
작성일: 2026-08-11
tags: [학습]
  - 디자인패턴
  - repository
  - MVVM
  - DI
---

# Repository Pattern 분석

## 1. Repository Pattern이란?

**데이터 레이어를 앱의 나머지 부분에서 분리하는 디자인 패턴.**

→ 데이터 레이어는 UI와 별도로 앱의 데이터와 비즈니스 로직을 "처리"하는 앱 레이어 부분이다.
다른 레이어에서는 데이터 레이어가 제공하는 API를 통해서만 이 데이터에 액세스할 수 있습니다.

UI가 사용자에게 정보를 제공하는 동안, 데이터 레이어에는 네트워킹 코드, Room 데이터베이스, 데이터 관련 오류 및 예외 처리, 데이터를 읽거나 조작하는 코드 등이 포함된다.

![[Pasted image 20260811181411.png|257]]

공식문서의 그림 — Activity와 Fragment 같은 앱 구성요소가 ViewModel로, Repositories를 통해 데이터 소스에 접근하는 계층을 보여줍니다.

## 2. Repository Pattern 사용의 이점이란?

Repository 모듈은 데이터 작업을 처리하고 여러 백엔드 API 사용을 한 곳에서 가능하게 합니다.

일반적인 앱에서 저장소(Repository가 아니더라도 data 계층에 접근하는 것들)는 네트워크에서 데이터를 가져올지, 아니면 로컬 데이터베이스에 캐시된 결과를 사용할지 결정하는 로직을 구현한다. MVVM의 경우 뷰 모델이 위와 같은 역할을 하게 된다.

![[Pasted image 20260811181732.png|700]]

1. MVVM에서 Repository와 DI 라이브러리를 같이 사용하게 된다면 뷰 모델에서 Data 관련한 구현 세부정보를 교체할 수 있습니다. 이는 코드를 모듈식으로, 테스트 가능하게 만들 수 있습니다. 쉽게 Repository에 Test 코드를 작성해서 Data를 활용하는 코드의 나머지 부분을 테스트할 수 있습니다.

2. Repository는 앱 데이터의 특정 부분에 관한 **단일 정보 소스(Single Source of Truth)** 역할을 해야 합니다. 네트워크 리소스와 오프라인 캐시 등 여러 데이터 소스로 작업할 때, Repository는 앱이 오프라인 상태일 때도 받아놓은 데이터를 사용할 수 있게 합니다. 캐싱의 경우 Room 라이브러리를 통해서 저장했다가 꺼내서 쓰기도 합니다.

## 3. Repository Pattern 구현 (Java)

> 원문은 안드로이드(Kotlin + Hilt) 예제였는데, 같은 구조를 **Java**로 옮겨서 정리한다.
> 식당 지도 앱을 예로, "식당 데이터 담당 사서(Repository)를 만들어서 화면에 붙이는" 4단계다. [[Java day09 MVC 종합예제]] 에서 만든 구조의 다음 단계이기도 하다.

### 3-1. 약속과 실체를 나눈다 — interface / Impl

```java
// 약속: "식당 데이터를 준다"는 명세만 존재. 내용이 없다
public interface RestaurantRepository {
    List<Restaurant> findAll();
    Restaurant findByName(String name);
}
```

```java
// 실체: 약속을 실제로 지키는 구현
public class RestaurantRepositoryImpl implements RestaurantRepository {

    private final RestaurantDataSource restaurantDataSource;  // 식당 API 담당
    private final MapDataSource mapDataSource;                // 지도 API 담당

    // 재료를 내가 new 하지 않고 생성자로 받는다 = 생성자 주입
    public RestaurantRepositoryImpl(RestaurantDataSource rds, MapDataSource mds) {
        this.restaurantDataSource = rds;
        this.mapDataSource = mds;
    }

    @Override
    public List<Restaurant> findAll() {
        return restaurantDataSource.fetchAll();   // 어디서 가져오는지는 여기만 안다
    }

    @Override
    public Restaurant findByName(String name) { ... }
}
```

읽는 법:

- `interface` — "이런 기능을 제공하겠다"는 **약속만** 있고 구현이 없다. [[Java 오버로딩 오버라이딩과 인터페이스(이관)]] 의 인터페이스 그대로
- `implements` — 약속을 실제로 이행하는 실체
- 생성자에서 DataSource를 **받는 것**(주입)이 핵심이다. 클래스 안에서 `new RestaurantDataSource()`를 해버리면 실체가 고정돼서 갈아끼울 수 없다
- `private final` — 받은 재료를 바꿔치기할 수 없게 잠근다. [[Java day08 접근제한자와 static]] 의 `final` 성질

> 왜 나누나? 상위 계층을 테스트할 때 진짜 Impl 대신 가짜(Fake)를 꽂기 위해서다. 아래 "쉽게 설명하면"의 interface 항목 참고.

### 3-2. 약속과 실체를 연결한다 — 조립 담당자

"누가 `RestaurantRepository`를 달라고 하면 `RestaurantRepositoryImpl`을 줘라"는 연결을 **한 곳에서** 담당한다. 순수 Java로는 조립 클래스를 직접 만든다.

```java
// 앱에서 조립을 담당하는 유일한 곳
public class AppConfig {

    // 싱글톤 — day09에서 getInstance()로 만들던 것과 같은 목적
    private static final RestaurantRepository repository =
            new RestaurantRepositoryImpl(
                    new RestaurantDataSource(),
                    new MapDataSource()
            );

    public static RestaurantRepository restaurantRepository() {
        return repository;    // 반환 타입이 interface라는 게 포인트
    }
}
```

한 문장으로: **"new는 여기서만 한다."**

- 반환 타입이 `RestaurantRepositoryImpl`(실체)이 아니라 `RestaurantRepository`(약속)이다 — 받아가는 쪽은 실체의 존재를 모른다
- 실체를 `FakeRestaurantRepository`로 바꾸고 싶으면 **이 파일 한 곳만** 고친다
- [[Java day10 상속과 다형성]] 의 업캐스팅이 정확히 이 자리에서 쓰인다: `RestaurantRepository r = new RestaurantRepositoryImpl(...)`

### 3-3. 주문한다 — 상위 계층이 Repository를 받는다

화면 로직을 담당하는 클래스(안드로이드의 ViewModel 자리, 콘솔 앱이면 Controller)도 실체가 아니라 약속을 받는다.

```java
public class MapController {

    private final RestaurantRepository repository;   // 약속(interface) 타입으로 보관

    public MapController(RestaurantRepository repository) {   // 생성자 주입
        this.repository = repository;
    }

    public void showRestaurants() {
        List<Restaurant> list = repository.findAll();   // 출처는 모른 채 쓴다
        // 화면 출력...
    }
}
```

- **이 파일에 `Impl`이라는 글자가 등장하지 않는다** — 그래서 실체를 바꿔도 이 파일은 그대로다
- [[Java day09 MVC 종합예제]] 의 `BoardController → BoardDAO` 연결과 같은 모양인데, 차이는 DAO를 `getInstance()`로 직접 부르는 대신 **생성자로 받는다**는 것. 직접 부르면 갈아끼우기가 안 되고, 받으면 된다

### 3-4. 조립해서 실행한다 — main

```java
public class AppStart {
    public static void main(String[] args) {
        // 조립: AppConfig에서 완성품을 받아 Controller에 꽂는다
        MapController controller =
                new MapController(AppConfig.restaurantRepository());

        controller.showRestaurants();
    }
}
```

테스트할 때는 같은 자리에 가짜를 꽂는다.

```java
// DB도 네트워크도 없이 Controller 로직만 검사할 수 있다
MapController controller = new MapController(new FakeRestaurantRepository());
```

### 3-5. 전체 흐름 한 줄 요약

```
AppStart(main)
  └─ AppConfig ── new는 여기서만 ──▶ RestaurantRepositoryImpl
  │                                     ├─ RestaurantDataSource
  │                                     └─ MapDataSource
  └─ MapController(약속 타입으로 받음) ──▶ repository.findAll()
                                            (출처는 Impl만 안다)
```

이 "조립 담당(AppConfig)"을 사람이 직접 쓰는 대신 프레임워크가 대신해 주는 것이 **Spring의 `@Autowired`**, 안드로이드의 **Hilt `@Inject`**(원문의 Kotlin 예제)다. 어노테이션이 하는 일은 결국 3-2의 AppConfig를 자동 생성하는 것 — 손으로 먼저 만들어봤으면 프레임워크가 무엇을 대신해주는지 정확히 보인다. [[Java day09 MVC 종합예제]] 3-3의 결론과 같다.

### 3-6. 같은 구조를 JS로

JS에는 interface 문법이 없지만 **"같은 이름의 함수를 가진 객체"가 곧 약속**이다. 게시판 프로젝트( [[JS day14 게시판 CRUD]] )에 그대로 붙일 수 있는 형태로 쓰면:

```javascript
// 실체 1 — localStorage 버전 (지금 게시판이 쓰는 것)
const localBoardRepository = {
  findAll() {
    return JSON.parse(localStorage.getItem("posts") ?? "[]");
  },
  save(post) {
    const posts = this.findAll();
    posts.push(post);
    localStorage.setItem("posts", JSON.stringify(posts));
  },
};

// 실체 2 — 서버 버전 (백엔드가 생기면)
const apiBoardRepository = {
  async findAll() {
    const res = await fetch("/api/posts");
    return res.json();
  },
  async save(post) {
    await fetch("/api/posts", { method: "POST", body: JSON.stringify(post) });
  },
};
```

```javascript
// 조립 담당 — Java의 AppConfig 자리. 갈아끼우는 곳은 여기 한 줄
const boardRepository = localBoardRepository;   // ← apiBoardRepository로 교체 가능

// 상위 계층 — 출처를 모른 채 쓴다 (Java의 Controller 자리)
async function renderBoard() {
  const posts = await boardRepository.findAll();   // localStorage인지 서버인지 모름
  // 화면 그리기...
}
```

- `findAll` / `save`라는 **메소드 이름의 일치**가 interface를 대신한다 (덕 타이핑)
- 상위 계층이 `await`로 통일해서 부르면, 동기(localStorage)든 비동기(fetch)든 같은 코드로 동작한다
- localStorage 게시판을 백엔드로 옮기는 날, 고치는 곳은 **조립 한 줄**이다 — [[JS day13 웹 스토리지와 인터벌]] 에서 "localStorage의 한계 때문에 백엔드가 필요하다"고 했던 그 전환을 이 구조가 무통증으로 만든다

### 참고 — 원문(Kotlin + Hilt)과의 대응

| Java (이 노트) | JS (3-6) | Kotlin + Hilt (원문) |
| --- | --- | --- |
| `interface` + `implements` | 메소드 이름 일치 (덕 타이핑) | `interface` + `:` (콜론) |
| `AppConfig`에서 손조립 | `const boardRepository = ...` 한 줄 | `@Module` + `@Binds` 규칙표 |
| `private static final` 싱글톤 | 모듈 스코프 객체 1개 | `@Singleton` |
| 생성자 주입 | 변수 교체 | `@Inject constructor` (자동) |
| `main`에서 조립 | 스크립트 최상단에서 조립 | `@AndroidEntryPoint` + `by viewModels()` |

---

## 쉽게 설명하면 (보충)

### 도서관 사서 비유

Repository는 **도서관 사서**다.

```
손님(ViewModel/Controller): "해리포터 주세요"
사서(Repository):           서고에서 꺼내든, 창고에서 가져오든, 옆 도서관에서 빌려오든
                            알아서 구해다 준다
```

손님은 책이 **어디서 왔는지 모른다.** 그냥 "달라"고만 하면 된다. 책의 위치가 바뀌어도(서고 → 창고), 조달 방식이 바뀌어도(구매 → 대여) 손님의 요청 방법은 그대로다.

코드로 옮기면: 상위 계층은 `repository.getRestaurants()`만 호출하고, 그 데이터가 **네트워크에서 왔는지 / Room 캐시에서 왔는지 / 테스트용 가짜인지 모른다.** 이 "모른다"가 이 패턴의 핵심 가치다 — 데이터 출처를 바꿔도 상위 계층 코드가 한 줄도 안 바뀐다.

### interface가 왜 필요한가

3번 구현에서 `RestaurantRepository`(인터페이스)와 `RestaurantRepositoryImpl`(구현체)을 굳이 나눈 이유:

```
ViewModel이 아는 것:   RestaurantRepository (약속/명세)
실제로 주입되는 것:     RestaurantRepositoryImpl (진짜 구현)
테스트 때 주입하는 것:  FakeRestaurantRepository (가짜 구현)
```

ViewModel은 "약속"만 알기 때문에, 뒤에서 진짜↔가짜를 갈아끼워도 모른다. DI(Hilt)는 이 갈아끼우기를 자동으로 해주는 도구다. **"타입은 부모(인터페이스)로, 실제 객체는 자식으로"** — [[Java day10 상속과 다형성]] 의 `Car`가 `Tire` 타입만 알고 한국타이어든 금호타이어든 갈아끼우는 구조와 정확히 같은 원리다.

### 이미 만들어 본 적이 있다

이 패턴은 처음이 아니다. 언어와 이름만 달랐다.

| | 역할 | 상위 계층이 모르는 것 |
| --- | --- | --- |
| Java `BoardDAO` — [[Java day09 MVC 종합예제]] | 게시글 저장·조회 담당 | ArrayList인지 DB인지 |
| JS 게시판의 저장 함수 묶음 — [[JS day14 게시판 CRUD]] | localStorage 읽기/쓰기 담당 | localStorage인지 서버인지 |
| 보드게임카페 프로젝트의 `models/` — [[controllers와 models 분석]] | SQL 담당 (만들다 중단됨) | 어떤 쿼리를 쓰는지 |
| Android `Repository` (이 노트) | 네트워크/Room 조달 담당 | 어느 데이터 소스인지 |

전부 같은 한 문장으로 요약된다: **"데이터를 어디서 어떻게 가져오는지는 한 계층만 알고, 나머지는 모르게 한다."**

보드게임카페 프로젝트에서 `models/`를 만들다 만 것이 "이 패턴을 반만 적용하면 없느니만 못하다"는 반례였고, 이 노트의 Hilt 구조가 그걸 끝까지 완성한 형태다.

### 한 장 요약

```
[UI/ViewModel]  ──"데이터 줘"──▶  [Repository]  ──▶  네트워크 (Retrofit)
     ▲                              │              ──▶  로컬 캐시 (Room)
     └───────── 데이터만 받음 ◀──────┘              ──▶  테스트용 가짜
                                (출처는 Repository만 안다)
```

- 상위 계층: **무엇**이 필요한지만 안다
- Repository: **어디서 어떻게** 가져올지를 안다
- DI: 그 "어떻게"를 상황(운영/테스트)에 맞게 갈아끼워 준다

## 관련 노트

[[Java day09 MVC 종합예제]] · [[Java day10 상속과 다형성]] · [[JS day14 게시판 CRUD]] · [[controllers와 models 분석]] · [[전문용어 정리]] · [[더 나아가기 - 테스트와 배포]]
