자바
1. @Override: 상위 클래스/인터페이스의 메서드를 재정의함을 명시 및 검증
2. @Retention: 어노테이션의 유지 범위(SOURCE, CLASS, RUNTIME) 지정
3. @Target: 어노테이션이 적용될 대상(TYPE, METHOD, FIELD 등) 지정
롬복
4. @NoArgsConstructor: 기본 생성자 자동 생성
5. @AllArgsConstructor: 모든 필드를 포함하는 생성자 자동 생성
6. @Getter: Getter 메서드 자동 생성
7. @Setter: Setter 메서드 자동 생성
8. @ToString: toString() 메서드 자동 생성
9. @RequiredArgsConstructor: final 필드만 포함하는 생성자 자동 생성
10. @Builder: 빌더 패턴 방식의 객체 생성 메서드 자동 생성
스프링
11. @SpringBootApplication: 톰캣 자동 구성, 컴포넌트 스캔, 설정 기능을 포함한 시작점 지정
12. @Component: 스프링 빈(Bean, 객체)으로 등록
13. @Autowired: 스프링 빈(객체) 의존성 자동 주입
스프링 HTTP
14. @Controller: Spring MVC 컨트롤러 등록 (프론트엔드파일 반환용)
15. @RestController: RESTful 웹 서비스 컨트롤러 등록 (@Controller + @ResponseBody)
16. @ResponseBody: 반환 객체를 HTTP 응답 본문(JSON/XML/Text)으로 전송
17. @RequestMapping: 클래스 또는 메서드 레벨에서 공통 URI 경로 및 HTTP 속성을 정의
18. @GetMapping: HTTP GET 요청 전용 매핑
19. @PostMapping: HTTP POST 요청 전용 매핑
20. @PutMapping: HTTP PUT 요청 전용 매핑
21. @DeleteMapping: HTTP DELETE 요청 전용 매핑
22. @RequestParam: 쿼리 스트링 또는 폼 파라미터(application/x-www-form-urlencoded) 값 추출
23. @ModelAttribute: 요청 파라미터를 객체(DTO) 필드에 저장
24. @PathVariable: URI 경로 자체에 포함된 식별자 값 추출
25. @RequestBody: HTTP body(JSON, XML 등, POST/PUT에서 주로 사용) 데이터를 Java 객체로 저장