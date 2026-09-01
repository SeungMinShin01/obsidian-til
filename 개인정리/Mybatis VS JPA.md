
레거시(과거 - 현재) - Mybatis
미래 - JPA

시장에서는 여전히 Mybatis를 사용중에 있다.
JPA에 맞춰서 DB를 설계하면 가능하지만, 레거시를 컨버젼하는 프로젝트, 혹은 고도화 하는 프로젝트 훨씬 많기 때문에 현장에서는 Mybatis를 많이 사용한다.

#### ORM (Object Relational Mapping)이란?
- 객체와 관계형 데이터베이스 간 불일치 문제를 해결하기 위한 기술
- 자바 클래스 <--> DB 테이블 간 자동 매핑
- 대표 기술 : 'JPA', 'Hibernate'
--- ORM 을 사용하면 SQL을 직접 작성하지 않고 자바 객체 중심으로 개발 가능 ---

### SQL Mapper란?
- 개발자가 작성한 SQl에 자바 객체를 수동으로 매핑하는 방식
- SQL은 명확하게 제어할 수 있지만, 코드량이 많아진다.
- 대표 프레임워크: 'MyBatis'

### JPA (Java Persistence API)
개념
	- 자바 ORM 기술에 대한 표준 인터페이스
	- DB 테이블과 자바 객체를 자동으로 매핑
	- SQL 대신 'JPQL' 사용
	- 대표 구현체: 'Hibernate'
주요 어노테이션
  ``` java
  @Entity
	@Table(name="user")
	public class User{
	@Id
	@GeneratedValue
	 private Long id;
	private String name;
    } 
  ```
	
특징
	- SQL을 직접 작성하지 않고도 DB 연동 가능
	- 객체 중심 프로그래밍에 최적화
	- 트랜잭션 관리, 캐싱, 지연 로딩, Dirty Checking 등의 고급 기능 제공
	- Spring Data JPA와 결합 시 생산성 극대화
	- Spring Data JPA와 결합 시 생산성 극대화
### MyBatis
개념
	- SQL Mapper 기반 프레임워크
	- SQL을 개발자가 직접 작성하고, 결과를 자바 객체에 수동 매핑
	- XML 또는 어노테이션 기반으로 SQL을 구성함
사용 예시
  ``` java
  <select id = "findById" resultType="User">
	   Select * FROM users WHERE id = #{id}
  </select>
  ```

**MyBatis 프레임워크**는 반복적인 **JDBC 프로그래밍을 단순화하여, 불필요한 Boilerplate 코드를 제거하고, Java 소스코드에서 SQL 문을 분리하여 별도의 XML 파일로 저장하고, 이 둘을 서로 연결시켜주는 기능을 제공**합니다.

특징
	- SQL이 명확하게 보이고, 디버깅이 쉬움
	- 복잡한 조건과 조인 쿼리에 강함
	- SQL과 비즈니스 로직을 명확히 분리 가능
	- 객체 매핑을 수동으로 제어 가능
	- 동적 쿼리

공통점
	- Java 기반 백엔드 프레임워크
	- DB와 자바 객체 간 매핑을 지원
	- CRUD, JOIN, 트랜잭션 등 DB 관련 작업을 처리 가능
	- Spring Boot 와 잘 통합됨
차이점
	- JPA는 SQL을 자동 생성하고, MyBatis는 SQL을 직접 작성함
	- JPA는 ORM 기반으로 객체 지향적인 설계를 지향하고, MyBatis는 SQL 중심 설계에 가까움
	- JPA는 ORM 기반으로 객체 지향적인 설계를 지향하고, MyBatis는 복잡한 쿼리 제어에 유리
	- JPA는 러닝 커브가 높고, MyBatis는 복잡한 쿼리 제어에 유리

비교
|항목|JPA|MyBatis|
|---|---|---|
|SQL 작성 방식|자동 생성 (JPQL)|직접 작성 (SQL/XML)|
|쿼리 제어권|프레임워크가 관리|개발자가 직접 관리|
|복잡한 쿼리 대응|어려움 (native query 필요)|유리함|
|성능 튜닝|내부 구조 이해 필요|SQL 수준에서 직접 가능|
|학습 난이도|높음 (ORM 개념 필요)|낮음 (SQL만 알면 됨)|
|유지보수|구조적으로 간결|쿼리 많아지면 복잡도 상승|
|객체지향 설계|우수함|낮음|

## 어떤 걸 선택해야 할까?

### JPA가 적합한 상황

- 단순한 CRUD 위주의 프로젝트
- 도메인 중심 설계를 지향하는 경우
- 유지보수성과 확장성이 중요한 경우
- 빠른 MVP, 초기 개발에 집중할 경우

###  MyBatis가 적합한 상황

- 복잡한 SQL 쿼리, 통계, 집계가 많은 서비스
- 성능 제어가 중요한 대용량 트래픽 처리 환경
- SQL 튜닝과 로그 추적이 중요한 경우
- 기존 DB 구조를 그대로 활용해야 하는 경우

### 혼합 사용이 필요한 상황

- 단순 CRUD는 JPA로 처리하고
- 복잡한 조회, 성능 중심 쿼리는 MyBatis로 처리하는 구조가 필요할 때
	 
## 실무 사용 사례

###  대기업/중견기업 예시

- 쿠팡 → MyBatis 중심, 일부 JPA 사용
- 배달의민족 → JPA 기반 도메인 설계
- 네이버 → MyBatis 중심
- 토스 → Hibernate(JPA 구현체) 기반 설계

###  스타트업/중소기업 경향

- 빠른 개발과 제어력을 이유로 MyBatis 선호
- 팀원 역량이나 데이터 복잡도에 따라 혼용 구조 적용


###  JPA

- ORM 기반의 자동화된 SQL 처리
- 객체 중심 개발에 적합
- 코드가 간결하고 유지보수가 쉬움
- 복잡한 쿼리에는 불리함

###  MyBatis

- SQL 직접 제어로 복잡한 쿼리에 강함
- 성능 튜닝과 디버깅이 쉬움
- 코드량이 많고 유지보수는 어려울 수 있음

---

## 누가 더 빠른가?

**MyBatis**
MyBatis는 단순히 개발자가 작성한 쿼리를 그대로 실행하기 때문에 오버헤드가 적다. 반면 JPA는 영속성 컨텍스트(Persistence Context)라는 1차 캐시를 관리하고, 엔티티의 변화를 추적하며, 트랜잭션을 관리하는 등 여러 추상화 계층을 거친다 . 이 과정에서 미세한 병목이 발생한다.

실제로 CRUD 기반의 특정 성능 비교 연구에서는 **MyBatis가 JPA 대비 최대 30% 더 높은 성능**을 보인 사례도 존재

**하지만 여기서 함정이다.** 성능은 ‘SQL 실행 속도’만으로 결정되지 않는다. JPA는 1차 캐시를 활용해 같은 트랜잭션 내에서 동일한 엔티티를 조회할 때는 DB에 접근조차 하지 않는다. 이는 MyBatis가 따라올 수 없는 강력한 장점이다.

##  마무리

JPA와 MyBatis는 서로 **보완 관계**.  
프로젝트의 특성과 요구 사항에 따라 적절히 선택하거나, **혼용하는 전략**도 좋다.

- 복잡한 조회나 성능 중심이라면 **MyBatis**
- 도메인 중심 개발과 생산성이 중요하다면 **JPA**


 ** 다음 노트 JPA 정리 - 로딩(EAGER LOADING), 지연 로딩(LASY LOADING), 영속성 전이(CascadeType), 복합키 매핑(@EmbededId, @IdClass) 등에 대한 해결

출처 : https://www.elancer.co.kr/blog/detail/231 
https://hiteksoftware.co.kr/blog/jpa-vs-mybatis/