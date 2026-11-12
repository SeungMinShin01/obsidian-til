---
출처: Claude 대화
작성일: 2026-11-12
tags: [프로젝트, java]
---

# AiOps - 로그인과 권한 (B)

> 허브: [[AiOps 프로젝트 MOC]]

**PR #31 `[AI-76][AI-78~81] 12단계 로그인·권한: GitHub 로그인, 보안 체인, MembershipGuard, RequireOwner·AdminGuard`** — 브랜치 `feat/server-AI-81-role-admin`. 커밋 15개(일반 11 + 브랜치 합치기 4). 2026-11-10 12:07(KST) develop에 머지. 하위 작업 5개: AI-76 권한 E2E·뼈대(설계자 선행 6커밋), AI-78 GitHub 로그인, AI-79 보안 체인 2개, AI-80 MembershipGuard, AI-81 역할 검사·관리자 지정. 브랜치를 78 → 79 → 80 → 81로 계단처럼 쌓고 마지막 브랜치 하나로 PR을 열었다. 44파일, +1839 −92.

## 1. 배운 내용

### 1-1. 요청이 지나가는 길

```
Starter ── POST /v1/events (X-AIOPS-KEY) ─▶ [체인 1: apiKeyChain, @Order(1), /v1/**]
              ApiKeyAuthFilter → ApiKeyResolver.resolve → TenantContext.set(키의 팀)
              STATELESS(세션 안 만듦), CSRF 끔 → IngestController → RLS

브라우저 ── /oauth2/authorization/github ─▶ GitHub 동의 ─▶ /login/oauth2/code/github
              [체인 2: sessionChain, @Order(2), /api/** /oauth2/** /login/** /logout]
              GithubLoginSuccessHandler → app_user upsert → 세션에 AppUserPrincipal → "/"

브라우저 ── /api/teams/7/... (AIOPS_SESSION 쿠키 + X-XSRF-TOKEN) ─▶ 체인 2: 세션 없으면 401
              ─▶ 인터셉터 MembershipGuard: URL의 7 → DB에서 멤버 확인 → 정지 팀? → TenantContext.set(7)
              ─▶ RequireOwnerInterceptor: @RequireOwner면 역할이 OWNER인지
              ─▶ 컨트롤러 → 트랜잭션 시작 시 set_config → RLS
              ─▶ afterCompletion: TenantContext.clear()

브라우저 ── /api/admin/** ─▶ 체인 2 ─▶ AdminGuard: 환경변수 GitHub id 목록에 있나? 아니면 403
```

입구는 둘(키, 세션)이지만 끝은 같은 `TenantContext → RLS`다. 11단계의 `TenantFilter`는 지우고 그 일을 `ApiKeyAuthFilter`가 넘겨받았다.

### 1-2. 코드로 보기: 보안 체인 2개 (`SecurityConfig`)

`SecurityFilterChain`은 "이 경로의 요청은 이 필터 묶음을 지난다"는 설정이다. 여러 개면 `@Order` 순서로 `securityMatcher`를 보고 **처음 맞는 체인 하나만** 탄다.

```java
@Configuration
@ConditionalOnWebApplication(type = ConditionalOnWebApplication.Type.SERVLET)  // ①
public class SecurityConfig {

    @Bean
    @Order(1)
    SecurityFilterChain apiKeyChain(HttpSecurity http, ApiKeyResolver apiKeyResolver) throws Exception {
        http.securityMatcher("/v1/**")  // ②
                .csrf(c -> c.disable())
                // Starter 요청마다 세션이 생기면 메모리가 샌다
                .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))  // ③
                .requestCache(r -> r.requestCache(new NullRequestCache()))
                .addFilterBefore(new ApiKeyAuthFilter(apiKeyResolver), UsernamePasswordAuthenticationFilter.class)  // ④
                .authorizeHttpRequests(a -> a.anyRequest().authenticated())
                .exceptionHandling(e -> e.authenticationEntryPoint((req, res, ex) -> res.sendError(401)));
        return http.build();
    }

    @Bean
    @Order(2)
    SecurityFilterChain sessionChain(HttpSecurity http, GithubLoginSuccessHandler successHandler,
            GithubLoginFailureHandler failureHandler) throws Exception {
        http.securityMatcher("/api/**", "/oauth2/**", "/login/**", "/logout")  // ⑤
                ...
                .authorizeHttpRequests(a -> a
                        .requestMatchers("/oauth2/**", "/login/**").permitAll()
                        .anyRequest().authenticated())
                // 미인증 /api 요청을 세션에 저장하지 않는다 (401만 주고 끝)
                .requestCache(r -> r.requestCache(new NullRequestCache()))
                // 로그인 페이지 redirect가 아니라 401. 콘솔이 401을 보고 로그인 화면으로 보낸다
                .exceptionHandling(e -> e.authenticationEntryPoint((req, res, ex) -> res.sendError(401)));  // ⑥
        return http.build();
    }
}
```

(번호 주석은 내가 붙였다.)

| 번호 | 이유 |
|---|---|
| ① | `WebEnvironment.NONE` 테스트(웹 서버 없이 뜨는 테스트)에는 `HttpSecurity`가 없다. 서블릿 웹일 때만 켠다 |
| ② | 경로로 나눈다(D-021). "헤더가 있으면 키, 없으면 세션"처럼 한 체인 안에서 분기하지 않는다. 그래서 `/api`에 키만 보내면 401, `/v1`에 세션 쿠키만 보내도 401 |
| ③ | Starter는 쿠키를 안 들고 다닌다. 요청마다 세션을 만들면 버려지는 세션이 쌓인다. E2E 2번이 `Set-Cookie`가 없는지 본다 |
| ④ | 키 필터를 기본 로그인 필터 자리 앞에 끼운다. 이 필터는 일부러 `@Component`가 아니다(1-3) |
| ⑤ | GitHub 로그인 경로(`/oauth2/**`, `/login/**`)도 세션 체인에 넣어야 로그인 결과가 세션에 저장된다 |
| ⑥ | 기본값은 로그인 페이지로 302. SPA(한 페이지 앱, React 콘솔)는 302를 받으면 HTML을 받아 버린다. 401만 주고 화면 이동은 콘솔이 한다 |

두 체인 어디에도 안 걸리는 경로(`/health`, `/_test/**`)는 보안 필터를 아예 안 탄다. 의도된 것이지만 리뷰 메모에 적었다.

### 1-3. 코드로 보기: API 키 필터 (`ApiKeyAuthFilter`)

```java
/**
 ...
 * 빈(@Component)으로 만들지 않는다: Filter 빈은 Spring Boot가 모든 경로의 서블릿 필터로 자동 등록해서
 * /api/**에도 타게 된다. SecurityConfig의 /v1 체인에만 직접 끼운다.
 */
public class ApiKeyAuthFilter extends OncePerRequestFilter {
    ...
        ResolvedKey key;
        try {
            key = apiKeyResolver.resolve(request.getHeader(ProtocolConstants.HEADER_API_KEY));  // ①
        } catch (InvalidApiKeyException e) {
            // 키 없음·없는 키·폐기 키를 구분하지 않는다 (IngestExceptionHandler와 같은 응답)
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            ...
            return;
        }

        try {
            SecurityContext context = holder.createEmptyContext();
            context.setAuthentication(new ApiKeyAuthentication(key.tenantId(), key.env()));  // ②
            holder.setContext(context);
            TenantContext.set(key.tenantId());
            request.setAttribute(ENV_ATTRIBUTE, key.env());
            chain.doFilter(request, response);
        } finally {
            TenantContext.clear();  // ③
            holder.clearContext();
        }
```

| 번호 | 이유 |
|---|---|
| ① | 키 검증은 `ApiKeyResolver` 한 곳(규칙 2). 필터는 부르기만 한다. 폐기 키 캐시 무효화도 거기 있다(AI-74) |
| ② | `ApiKeyAuthentication`은 "팀 번호 + env"만 든 인증 객체다. 키 원문은 들고 있지 않다. 이걸 넣어야 체인의 `anyRequest().authenticated()`를 통과한다 |
| ③ | set한 곳이 finally에서 clear(v0.2 규칙 10). 톰캣 스레드는 재사용되므로 안 지우면 다음 요청이 이전 팀을 물려받는다 |

옛 `TenantFilter`는 `chain.doFilter`까지 같은 try 안에 있었다. 새 코드는 **키 해석 실패만** 401로 바꾸고, 컨트롤러 예외는 그대로 위로 보낸다. 더 정확해졌다.

### 1-4. 코드로 보기: GitHub 로그인 성공 → app_user upsert

OAuth2 로그인은 "신원 확인을 GitHub에 맡기는 것"이다. 우리 서버는 비밀번호를 갖지 않는다. 범위는 `scope: read:user`뿐이다(이메일·레포 권한 없음).

```java
if (!(authentication.getPrincipal() instanceof OAuth2User github)
        || !(github.getAttribute("id") instanceof Number id)
        || !(github.getAttribute("login") instanceof String login)) {  // ①
    log.warn("github login without id/login");
    holder.clearContext();
    request.getSession().invalidate();
    response.sendRedirect(GithubLoginFailureHandler.FAILURE_URL);
    return;
}
String name = github.getAttribute("name");

AppUserEntity user = appUserService.upsertFromGithub(id.longValue(), login, name);  // ②
AppUserPrincipal principal = new AppUserPrincipal(user.getId(), user.getGithubId(), user.getLogin());

SecurityContext context = holder.createEmptyContext();
context.setAuthentication(UsernamePasswordAuthenticationToken.authenticated(principal, null, List.of()));  // ③
holder.setContext(context);
repository.saveContext(context, request, response);  // ④

response.sendRedirect("/");
```

```java
@Transactional
public AppUserEntity upsertFromGithub(long githubId, String login, String name) {
    return users.findByGithubId(githubId)
            .map(user -> {
                user.updateProfile(login, name);  // ⑤
                return user;
            })
            .orElseGet(() -> users.save(new AppUserEntity(githubId, login, name)));
}
```

| 번호 | 이유 |
|---|---|
| ① | 패턴 매칭 `instanceof`로 타입 확인과 변수 선언을 한 번에. 필수 값이 없으면 저장하지 않고 실패 화면으로 |
| ② | upsert = 있으면 갱신, 없으면 생성. 사용자 식별은 숫자 `github_id`다. `login`(아이디 문자열)은 GitHub에서 바꿀 수 있다 |
| ③ | 세션의 인증을 GitHub 객체에서 **우리 `AppUserPrincipal(appUserId, githubId, login)`** 으로 바꾼다. 이후 코드는 GitHub 속성을 몰라도 된다. 테스트 로그인도 같은 record를 쓰므로 `CurrentUser`가 두 경우를 똑같이 꺼낸다 |
| ④ | 성공 핸들러에서 컨텍스트를 새로 만들었으니 세션에 직접 저장해야 다음 요청에 남는다 |
| ⑤ | 다시 로그인하면 login·name만 갱신. 팀에 자동 가입시키지 않는다(팀 합류는 초대로만) |

실패 핸들러는 예외 **클래스 이름만** 로그에 남긴다. 메시지에 OAuth `code` 같은 값이 섞일 수 있기 때문이다(규칙 10).

`AppUserPrincipal`이 `Serializable`인 이유: 세션에 들어가는 객체는 세션 저장소가 직렬화(바이트로 바꿔 저장)할 수 있어야 한다.

### 1-5. 코드로 보기: 세션 쿠키와 CSRF

```yaml
server:
  port: 8080
  servlet:
    session:
      cookie:                   # 콘솔 세션 쿠키 (AI-79). 같은 도메인이라 Lax로 충분, None 금지
        name: AIOPS_SESSION
        http-only: true
        secure: true            # 로컬(http)은 application-local.yml에서 false
        same-site: lax
```

- `HttpOnly`: 자바스크립트가 쿠키를 못 읽는다. XSS(남의 스크립트가 페이지에서 실행되는 공격)로 세션을 훔치기 어렵다.
- `Secure`: https에서만 보낸다.
- `SameSite=Lax`: 다른 사이트에서 시작한 POST 같은 요청에는 쿠키를 안 붙인다. 링크 클릭(GET)에는 붙인다.

쿠키 세션은 브라우저가 자동으로 쿠키를 붙이므로 CSRF(다른 사이트가 내 브라우저로 몰래 요청을 보내는 공격) 방어가 필요하다.

```java
.csrf(c -> c
        .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())  // ①
        .csrfTokenRequestHandler(new SpaCsrfTokenRequestHandler()))
```

```java
@Override
public void handle(HttpServletRequest request, HttpServletResponse response, Supplier<CsrfToken> csrfToken) {
    xor.handle(request, response, csrfToken);
    csrfToken.get(); // 첫 GET에서 XSRF-TOKEN 쿠키 발급  // ②
}

@Override
public String resolveCsrfTokenValue(HttpServletRequest request, CsrfToken csrfToken) {
    String header = request.getHeader(csrfToken.getHeaderName());
    return (StringUtils.hasText(header) ? plain : xor).resolveCsrfTokenValue(request, csrfToken);  // ③
}
```

| 번호 | 이유 |
|---|---|
| ① | 토큰을 `XSRF-TOKEN` 쿠키로 준다. 콘솔 JS가 읽어서 `X-XSRF-TOKEN` 헤더로 돌려보내야 하므로 **이 쿠키만** HttpOnly가 아니다. 다른 사이트는 우리 쿠키 값을 읽을 수 없으니 헤더를 못 만든다 |
| ② | Spring Security 6부터 토큰 생성이 "쓸 때까지" 미뤄진다. 그러면 첫 GET에 쿠키가 안 나간다. 매번 `get()`을 불러 쿠키를 발급시킨다 |
| ③ | 헤더로 온 값(SPA)은 원문 비교, 폼 파라미터면 XOR 비교. XOR은 BREACH(압축 길이로 비밀을 추측하는 공격) 대비로 토큰을 매번 다르게 섞는 방식이다. Spring 공식 문서의 SPA 예제 그대로다 |

로그아웃은 `POST /api/logout` + CSRF 헤더 → 세션 무효화, `AIOPS_SESSION` 삭제, 204.

### 1-6. 코드로 보기: MembershipGuard → TenantContext → RLS

인터셉터(`HandlerInterceptor`)는 DispatcherServlet 안에서 컨트롤러 직전·직후에 끼어드는 장치다. 필터보다 안쪽이라 세션 인증이 이미 끝난 상태다.

```java
Optional<Long> teamId = teamIdOf(request);  // ①
if (teamId.isEmpty()) {
    response.sendError(HttpServletResponse.SC_NOT_FOUND);
    return false;
}

AppUserPrincipal user = CurrentUser.get(); // 세션 없으면 /api 체인이 이미 401
Optional<MembershipEntity> membership = memberships.findByUserIdAndTenantId(user.appUserId(), teamId.get());  // ②
if (membership.isEmpty()) {
    response.sendError(HttpServletResponse.SC_FORBIDDEN);
    return false;
}

boolean suspended = tenants.findById(teamId.get())
        .map(t -> t.getStatus() == TenantStatus.SUSPENDED)
        .orElse(true); // 팀이 없으면 통과시키지 않는다
if (suspended) {
    ...
    response.getWriter().write("{\"reason\":\"SUSPENDED\"}");  // ③
    return false;
}

TenantContext.set(teamId.get());
request.setAttribute(ROLE_ATTRIBUTE, membership.get().getRole());  // ④
return true;
}

@Override
public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler,
        Exception ex) {
    TenantContext.clear(); // 예외·403 무관하게 (preHandle이 true였던 요청은 항상 여기로 온다)  // ⑤
}
```

| 번호 | 이유 |
|---|---|
| ① | 팀 번호는 **URL 경로에서만** 읽는다(쿠키·세션·헤더 X). `@PathVariable`을 안 쓰고 `PathPattern`으로 직접 파싱한다. 컨트롤러 맵핑이 없는 경로(`/api/teams/{남의팀}/아무거나`)도 404가 아니라 403을 줘야 "그 경로가 있는지"가 드러나지 않는다(E2E 3번) |
| ② | **요청마다 DB 조회.** 세션에 소속을 캐시하지 않아서 내보낸 사람은 바로 다음 요청부터 403(E2E 6번). membership은 RLS가 없는 테이블이라 `user_id + tenant_id` 고정 조건 메서드만 쓴다(D-023) |
| ③ | 정지된 팀은 멤버라도 403. 콘솔이 안내를 띄우도록 이유를 준다 |
| ④ | 역할을 Spring Security 권한(`GrantedAuthority`)에 넣지 않는다. 역할은 **팀마다** 다르다(A팀 OWNER, B팀 MEMBER). 요청 속성에 넣고 다음 인터셉터가 읽는다 |
| ⑤ | `postHandle`은 컨트롤러가 예외를 던지면 안 불린다. `afterCompletion`은 preHandle이 true였으면 항상 불린다. 뒤 인터셉터가 403으로 끊어도 불린다 |

여기서 `TenantContext.set(7)`을 하면 서비스의 트랜잭션이 시작될 때 바인더가 `set_config('app.tenant_id', '7', true)`를 하고, RLS가 7번 팀 행만 보여 준다. 가드가 뚫려도 RLS로 0건 = **이중 방어**. 관리자도 이 가드에서 예외가 없다. 관리자는 `/api/admin/**`로만 다른 팀을 본다(D-024).

### 1-7. 코드로 보기: @RequireOwner와 AdminGuard

```java
registry.addInterceptor(membershipGuard).addPathPatterns("/api/teams/**");
registry.addInterceptor(requireOwnerInterceptor).addPathPatterns("/api/teams/**");  // ①
registry.addInterceptor(adminGuard).addPathPatterns("/api/admin/**");
```

```java
if (!(handler instanceof HandlerMethod method) || !requiresOwner(method)) {  // ②
    return true;
}
if (request.getAttribute(MembershipGuard.ROLE_ATTRIBUTE) != MemberRole.OWNER) {  // ③
    response.sendError(HttpServletResponse.SC_FORBIDDEN);
    return false;
}
```

```java
@ConfigurationProperties("aiops.admin")
public record AdminProperties(Set<Long> githubIds) {

    public AdminProperties {
        githubIds = githubIds == null ? Set.of() : Set.copyOf(githubIds);  // ④
    }

    public boolean isAdmin(long githubId) {
        return githubIds.contains(githubId);
    }
}
```

| 번호 | 이유 |
|---|---|
| ① | 등록 순서 = 실행 순서. 역할 검사가 가드보다 먼저면 역할 속성이 아직 없어서 항상 403 |
| ② | 핸들러가 컨트롤러 메서드(`HandlerMethod`)일 때만 본다. 정적 리소스 등은 그냥 통과 |
| ③ | enum은 객체가 하나뿐이라 `!=`로 비교해도 된다. 속성이 없으면(null) 역시 403 → 안전한 쪽으로 실패 |
| ④ | 환경변수 `AIOPS_ADMIN_GITHUB_IDS=1,2,3`이 `Set<Long>`으로 바인딩된다. 비어 있으면 빈 집합 = 관리자 없음. `/api/me`의 `isAdmin`과 `AdminGuard`가 이 record 하나를 같이 쓴다(따로 파싱 X). DB 컬럼·하드코딩 없음 |

`AdminGuard`는 세션 사용자의 `githubId`가 목록에 있으면 통과, 아니면 403. 목록이 비면 생성자에서 경고 로그를 한 번 남긴다. "첫 로그인 사용자를 관리자로" 같은 편의 기능은 일부러 없다.

### 1-8. 테스트: 설계자가 먼저 쓴 빨간 테스트 (D-080)

AI-76 6커밋은 설계자가 먼저 올렸다(구현 전 빨강). 담당자 B는 테스트를 고치지 않고 초록으로 만들었다(규칙 9).

**`TestOnlyController` (`src/test`, `@Profile("test")`)** — 운영 jar에는 아예 안 들어간다. GitHub를 거치지 않고 세션을 만든다.

```java
@PostMapping("/_test/login/{userId}")
ResponseEntity<Void> login(@PathVariable long userId, HttpServletRequest request) {
    ...
    SecurityContext context = SecurityContextHolder.createEmptyContext();
    context.setAuthentication(UsernamePasswordAuthenticationToken.authenticated(principal, null, List.of()));
    request.getSession(true).setAttribute(
            HttpSessionSecurityContextRepository.SPRING_SECURITY_CONTEXT_KEY, context);
    return ResponseEntity.ok().build();
}
```

`/_test/**`는 어느 체인에도 안 걸리므로 로그인 없이 부를 수 있다. 세션에 넣는 키가 Spring Security 기본 저장 위치와 같아서, 다음 요청에서 세션 체인이 그대로 읽는다. 그 밖에 `_test/ping`(가드 통과 시 팀 번호 반환), `_test/owner-action`(`@RequireOwner`), `/api/admin/_test/ping`, `/api/_test/tenant`(남은 팀 확인)가 있다.

**`TestLogin`** — 브라우저 흉내. `Set-Cookie`를 모아 두고, POST 전에 `XSRF-TOKEN`이 없으면 `GET /api/me`로 받아 와서 `X-XSRF-TOKEN` 헤더로 되돌린다. redirect를 따라가지 않아서 302를 그대로 볼 수 있다.

**`AuthorizationE2ETest` 7개** (톰캣 스레드 1개로 고정 → 모든 요청이 같은 스레드)

| # | 테스트 | 기대 |
|---|---|---|
| 1 | 세션 없이 `/api/me` | 401, `Location` 헤더 없음(redirect 아님) |
| 2 | 키 없이 `POST /v1/events` | 401, `Set-Cookie` 없음(STATELESS) |
| 3 | 팀원이 남의 팀 URL / 맵핑 없는 남의 팀 경로 / 자기 팀 / 소속 없는 사람 | 403 / 403 / 200 + 본문=자기 팀 번호 / 403 |
| 4 | 팀원·조장이 `owner-action` POST | 403 / 201 |
| 5 | 조장·관리자가 `/api/admin/_test/ping` | 403 / 200 |
| 6 | 같은 세션으로 200 → DB에서 membership 삭제 → 다시 | 바로 403 |
| 보조 | 가드 통과 요청 뒤, 403 요청 뒤 `/api/_test/tenant` | 둘 다 `"none"` |

스레드를 1개로 묶는 이유: 스레드가 여러 개면 다음 요청이 다른 스레드로 가서 "앞 요청의 팀이 남았나"를 확인할 수 없다.

그 밖에 `SecurityChainTest` 8개(키·세션 섞임, CSRF 없는 POST 403, 위조 헤더 403, 로그아웃 204), `MembershipGuardTest` 7개(숫자 아닌 팀 번호 404, 정지 팀 `reason`), `AdminGuardTest` 4개, `ApiKeyAuthFilterTest` 6개(옛 `TenantFilterTest` 이름 변경), `AppUserServiceTest` 4개, `GithubLoginSuccessHandlerTest` 2개, `MeControllerTest` 3개, `RequireOwnerTest` 3개.

**`PostgresContainerSupport` max_connections=300**

```java
// 테스트 클래스마다 설정이 다르면 스프링 컨텍스트(=커넥션 풀)가 따로 떠서 기본 상한 100을 넘는다
// ("remaining connection slots are reserved"). 테스트용 DB만 상한을 올린다. fsync=off는 Testcontainers 기본값 유지
.withCommand("postgres", "-c", "fsync=off", "-c", "max_connections=300")
```

Spring 테스트는 설정이 같은 클래스끼리 컨텍스트를 캐시해 재사용한다. 이번 PR은 `properties = {...}`가 다른 `@SpringBootTest`를 여럿 만들어서 컨텍스트가 늘었다. 컨텍스트마다 Hikari 풀(기본 최대 10)이 살아 있어서 Postgres 기본 상한 100을 넘었다. `withCommand`를 덮어쓰면 Testcontainers가 기본으로 넣던 `fsync=off`가 빠지므로 직접 다시 적었다.

## 2. 리뷰 메모

| 항목 | 내용 | 심각도 |
|---|---|---|
| GitHub access token이 메모리에 남음 | `GithubLoginSuccessHandler` 주석은 "access token은 꺼내지도 저장하지도 않는다". 하지만 Spring의 `oauth2Login()` 기본 설정은 성공 핸들러보다 **먼저** `OAuth2AuthorizedClient`(access token 포함)를 `OAuth2AuthorizedClientRepository`에 저장한다. Boot 기본 빈은 `InMemoryOAuth2AuthorizedClientService`라서 서버 메모리 맵에 남고, 로그아웃해도 지워지지 않는다. DB·로그에는 안 남는다. `SecurityConfig`에 `authorizedClientRepository`를 따로 설정한 곳이 없다. 실행해서 확인하지는 못 했다. 확인 방법: 로그인 후 `OAuth2AuthorizedClientService.loadAuthorizedClient("github", <github id>)`가 null인지 보기. 고치려면 아무것도 저장하지 않는 저장소를 넣거나 성공 핸들러에서 지운다 | 중간 |
| 운영 프록시 뒤 OAuth 콜백 | Spring은 GitHub에 보낼 `redirect_uri`를 요청 주소(`{baseUrl}/login/oauth2/code/github`)로 만든다. `server.forward-headers-strategy` 설정이 없어서, Caddy가 https를 풀고 http로 넘기면 `http://...` 콜백이 만들어져 GitHub 앱의 https 콜백과 안 맞을 수 있다. 또 v0.3 문서 그림은 Caddy가 `/api/*`만 서버로 보낸다. `/oauth2/**`, `/login/oauth2/**`도 서버로 보내야 한다. Caddyfile이 아직 저장소에 없어서 확인 못 함. 10단계 배포 전에 확인 필요 | 중간 |
| 체인 밖 경로는 무방비 | 두 체인의 `securityMatcher`에 안 걸리는 경로는 보안 필터를 전혀 안 탄다. 사용자 체인 빈이 있으면 Boot 기본 체인도 꺼진다. 누가 `/admin/...`, `/console-api/...` 같은 다른 접두사로 컨트롤러를 만들면 로그인 없이 열린다. `WebMvcConfig` 주석("다른 접두사 금지")에만 의존한다. 마지막 순서에 `/health`만 열고 나머지는 `denyAll`인 체인을 두면 실수를 막을 수 있다 | 중간 |
| 규칙 15 (관리자 접근 기록) | 이 PR 시점의 `AdminGuard`는 통과·거부를 기록하지 않는다. 주석대로 13단계로 미뤘고, 이후 AI-87(`468b29b`)이 `adminAccessLogInterceptor`를 `/api/admin/**`에 붙였다. 머지 시점에는 실제 관리자 API가 `_test` 하나뿐이라 규칙 위반은 아니다 | 메모 |
| `@RequireOwner` 대상 | `@Target(ElementType.METHOD)`뿐이다(머지 시점·현재 develop 둘 다). 그런데 인터셉터는 `AnnotatedElementUtils.hasAnnotation(method.getBeanType(), ...)`로 **클래스**에 붙은 것도 본다. 클래스에는 붙일 수 없어 컴파일 오류가 나므로 이 분기는 실행될 일이 없다. 명세 3-5는 "메서드 단위"라 METHOD만인 게 맞다. 주석 "(또는 클래스)"와 분기를 지우거나, TYPE을 허용할지 정해야 한다. (11/10에 B가 "명세는 METHOD+TYPE인데 추가할까요"라고 물었고 추가하기로 답했지만 아직 반영되지 않았다) | 낮음 |
| `XSRF-TOKEN` 쿠키 Secure | `CookieCsrfTokenRepository`는 Secure를 `request.isSecure()`로 정한다. 프록시 뒤에서 forward 헤더를 안 믿으면 false → 이 쿠키만 Secure 없이 나간다. 세션 쿠키는 yml로 `secure: true` 고정이라 괜찮다. 위 프록시 설정을 고치면 같이 해결된다 | 낮음 |
| `/api/teams` (번호 없음) | 인터셉터 패턴 `/api/teams/**`는 `/api/teams` 자체도 잡는데, `teamIdOf`가 빈 값이라 404가 된다. 지금은 팀 목록을 `/api/me`가 주고 팀 생성은 `/api/admin` 아래라 문제없다. 나중에 `GET /api/teams`를 만들면 막힌다 | 낮음 |
| 테스트 빈칸: 쿠키 속성 | `HttpOnly`·`Secure`·`SameSite=Lax`(A-02)는 yml 설정뿐이고 검사하는 테스트가 없다. `SecurityChainTest`는 MockMvc라 실제 톰캣 쿠키 설정이 안 붙는다. RANDOM_PORT 테스트에서 `Set-Cookie: AIOPS_SESSION=...; HttpOnly; SameSite=Lax`를 확인하면 된다. GitHub 실제 왕복도 수동 확인 항목이다 | 낮음 |
| 테스트 빈칸: 실제 조장 API | E2E 4번 이름은 `memberIssuingKeyIs403`이지만 `_test/owner-action`으로 대신 검사한다. 실제 API에 `@RequireOwner`를 빠뜨리면 이 테스트는 못 잡는다. 이후 14단계 `InvitationController`·`MemberController`에는 붙어 있는 것을 확인했다. 키 발급 API는 확인 못 함 | 메모 |
| 정지 응답 이유 | `tenants.findById`가 비면 `orElse(true)` → `{"reason":"SUSPENDED"}`. 실제 이유는 "팀 없음"이다. membership이 tenant를 참조하므로 현실적으로는 생기기 어렵다 | 메모 |
| `/logout` 매처 | `securityMatcher`에 `/logout`이 있지만 로그아웃 주소는 `/api/logout`이다. `/logout`은 쓰이지 않는다 | 메모 |
| 세션 고정 | 실제 GitHub 로그인은 Spring 기본 전략(로그인 시 세션 id 교체)이 성공 핸들러 전에 돈다. `TestOnlyController`는 교체하지 않지만 테스트 전용이라 괜찮다 | 메모 |
| 비밀값·로그 (규칙 10) | `client-secret`은 환경변수만, 실패 로그는 예외 클래스 이름만, `/api/me` 응답에 토큰·이메일 없음. `client-id` 기본값 `local-unset`은 기동용 자리표시자(비밀 아님). 문제 못 찾음 | 메모 |

## 3. 더 나아가 알면 좋은 것

- 다음에 볼 키워드
  - `SecurityFilterChain` 여러 개와 `@Order`, `securityMatcher` vs `requestMatchers`
  - `FilterRegistrationBean`과 "Filter 빈은 자동으로 전체 경로에 등록된다"
  - `OAuth2AuthorizedClientRepository` / `OAuth2AuthorizedClientService` (토큰이 어디 저장되나)
  - `server.forward-headers-strategy`, `X-Forwarded-Proto`와 리버스 프록시
  - CSRF: `CookieCsrfTokenRepository`, 지연 토큰(Spring Security 6), BREACH와 XOR 토큰
  - 쿠키 `SameSite` Lax / Strict / None 차이
  - `HandlerInterceptor`의 `preHandle` / `postHandle` / `afterCompletion` 호출 규칙
  - `PathPattern`·`PathContainer`로 경로 직접 파싱
  - Spring 테스트 컨텍스트 캐시와 커넥션 수 (`@DirtiesContext`, 같은 설정 묶기)
- 머지 후 `.env`에 `AIOPS_GITHUB_CLIENT_ID`, `AIOPS_GITHUB_CLIENT_SECRET`, `AIOPS_ADMIN_GITHUB_IDS` 추가. GitHub OAuth 앱 콜백은 `/login/oauth2/code/github`.

## 관련 노트

[[AiOps 25 - 어펜더 AiopsLogbackAppender]] · [[AiOps 27 - 팀 API 초대와 팀원 (B)]]
