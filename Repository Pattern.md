---
출처: 내가 작성
작성일: 2026-08-11
tags: [디자인패턴, repository, android, MVVM, DI]
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

## 3. Repository Pattern 구현 (with Hilt)

> 언어는 **Kotlin**(안드로이드 공식 언어, Java 계승)이다. `@어노테이션` · 클래스 · 생성자 구조가 Java와 거의 대응되므로 [[Java day09 MVC 종합예제]] 를 만들었다면 읽을 수 있다.
> 식당 지도 앱을 예로, "식당 데이터 담당 사서(Repository)를 만들어서 화면에 붙이는" 4단계다.

### 3-1. 약속과 실체를 나눈다 — interface / Impl

```kotlin
interface RestaurantRepository          // 약속: "식당 데이터를 준다"는 명세만 존재

@Singleton                              // 앱 전체에 1개만 만든다
class RestaurantRepositoryImpl @Inject constructor(
    private val restaurantDataSource: RestaurantDataSource,   // 식당 API 담당
    private val mapDataSource: MapDataSource                  // 지도 API 담당
) : RestaurantRepository {              // 약속의 실제 구현
```

읽는 법:

- `interface RestaurantRepository` — Java의 인터페이스와 같다. "이런 기능을 제공하겠다"는 **약속만** 있고 내용이 없다
- `RestaurantRepositoryImpl : RestaurantRepository` — Java의 `implements`. 콜론(`:`)이 그 역할이다
- `@Inject constructor(...)` — "이 클래스를 만들 때 필요한 재료(DataSource 2개)는 **내가 new 하지 않고 받아온다**"는 선언. 이게 DI(의존성 주입)의 전부다 — `new`를 직접 안 쓰고 밖에서 넣어주는 것
- `@Singleton` — [[Java day09 MVC 종합예제]] 에서 `getInstance()`로 직접 만들던 싱글톤을 어노테이션 한 줄로 대신한다

> 왜 나누나? 나중에 ViewModel을 테스트할 때 진짜 Impl 대신 가짜(Fake)를 꽂기 위해서다. 아래 "쉽게 설명하면"의 interface 항목 참고.

### 3-2. 약속과 실체를 연결한다 — Hilt 모듈

이제 Hilt(안드로이드의 DI 라이브러리)에게 "누가 `RestaurantRepository`를 달라고 하면 `RestaurantRepositoryImpl`을 줘라"라고 **연결 규칙을 등록**한다.

```kotlin
@Module                                  // "여기 연결 규칙이 있다"
@InstallIn(SingletonComponent::class)    // 이 규칙을 앱 전역에서 쓴다
abstract class RepositoryBindModule {
    @Binds                               // 연결: Impl(실체) → interface(약속)
    abstract fun bindFoodApiRepository(
        restaurantRepositoryImpl: RestaurantRepositoryImpl   // 이걸 주면
    ): RestaurantRepository                                  // 이 타입으로 받는다
}
```

한 문장으로: **"RestaurantRepository 주문이 들어오면 RestaurantRepositoryImpl로 배달해라."**

- `@Module` + `@InstallIn(SingletonComponent)` — 이 배달 규칙표를 앱 전역 범위에 게시한다
- `@Binds` — 규칙표의 한 줄. 파라미터(Impl)가 반환 타입(interface)의 배달품이 된다

직접 `new RestaurantRepositoryImpl(...)`을 쓰는 코드가 앱 어디에도 없다는 게 포인트다. 생성은 전부 Hilt가 규칙표를 보고 대신한다.

### 3-3. 주문한다 — ViewModel이 Repository를 받는다

```kotlin
@HiltViewModel
class MapViewModel @Inject constructor(
    private val repository: RestaurantRepository    // 약속(interface) 타입으로 주문
) : ViewModel() {
```

- ViewModel의 생성자가 `RestaurantRepository`(약속)를 달라고 요청한다
- Hilt가 3-2의 규칙표를 보고 `RestaurantRepositoryImpl`(실체)을 만들어 넣어준다
- **ViewModel 코드에는 Impl이라는 글자가 등장하지 않는다** — 그래서 나중에 실체를 바꿔도 이 파일은 그대로다

### 3-4. 화면에서 쓴다 — Fragment

```kotlin
@AndroidEntryPoint                       // "이 화면에서 Hilt 주입을 쓴다"
class MapFragment : BaseFragment<FragmentMapBinding>() {

    private val viewModel: MapViewModel by viewModels()   // 필요해질 때 생성(지연 초기화)
}
```

- `by viewModels()` — ViewModel을 처음 쓰는 순간에 만들어주는 지연 초기화. 이때 3-3의 주입이 연쇄적으로 일어난다
- 결과: 화면 → ViewModel → Repository → DataSource 체인이 전부 자동 조립된 상태로 도착한다

### 3-5. 전체 흐름 한 줄 요약

```
MapFragment ──(by viewModels)──▶ MapViewModel
                                   └─ RestaurantRepository 주문
                                        └─ Hilt 규칙표(@Binds) 확인
                                             └─ RestaurantRepositoryImpl 생성
                                                  ├─ RestaurantDataSource 주입
                                                  └─ MapDataSource 주입
```

`new`가 한 번도 등장하지 않았다. **조립을 사람이 아니라 도구가 한다** — [[Java day09 MVC 종합예제]] 3-3에서 "지금 손으로 만든 싱글톤과 계층 연결을 스프링이 대신해 준다"고 했던 것의 안드로이드판이 정확히 이것이다(Spring의 `@Autowired` ≒ Hilt의 `@Inject`).

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
