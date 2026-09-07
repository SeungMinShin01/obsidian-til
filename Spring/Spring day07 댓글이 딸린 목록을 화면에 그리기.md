---
출처: Claude 분석
원본: KDT_2026/2026B_Spring/springweb/src/main/resources/static/day07/index.html, springweb/src/main/resources/static/day07/index.js, springweb/src/main/resources/static/day07/index.css, springweb/src/main/resources/sql/practice5.sql
작성일: 2026-09-07
tags: [학습, javascript]
---

# Spring day07 — 댓글이 딸린 목록을 화면에 그리기

> 실습 파일: `resources/static/day07/index.html`, `resources/static/day07/index.js`, `resources/static/day07/index.css`, `resources/sql/practice5.sql`
> 허브: [[Spring MOC]] · 이전: [[Spring day07 FK 번호를 엔티티로 바꿔 저장하기]]

여기까지는 계속 서버 쪽만 쌓아 왔습니다. 관계를 엔티티로 잡고, DTO로 펴고, 계층을 나누고, 번호를 객체로 바꿔 저장하는 자리까지 왔는데 그것을 **실제로 부르는 화면**은 day02 이후로 손대지 않았습니다. 이번에는 게시글과 그에 딸린 댓글을 한 화면에 그리는 피드를 붙입니다.

day02에서 다룬 화면은 표 한 줄 = 레코드 한 줄이라 관계가 없었습니다. 이번 화면은 **응답 한 줄 안에 목록이 또 들어 있는 모양**이라, 그리는 코드도 한 겹 중첩됩니다. 그리고 목록을 통째로 다시 그리는 방식이 처음으로 문제를 일으키는 자리가 나옵니다.

## 1. 배운 내용

### 1-1. 화면이 기대하는 응답 모양

`index.js` 가 `/api/board` 에서 받아 쓰는 프로퍼티를 그대로 모으면 화면이 요구하는 계약이 나옵니다.

```js
res.data.forEach(post => {
    const commentList = post.comments || [];
    ...
    post.author, post.content, post.createdAt, post.id
    ...
    commentList.map(c => `... ${c.author} ... ${c.content} ... ${c.id} ...`)
});
```

| 자리 | 모양 | 화면에서 쓰는 곳 |
| --- | --- | --- |
| 응답 전체 | JSON 배열 | `forEach` 로 카드 하나씩 |
| 게시글 한 벌 | 객체 | 작성자·내용·작성시각·번호 |
| `post.comments` | 중첩된 JSON 배열 | 카드 안쪽 댓글 목록 |

**게시글 DTO가 댓글 DTO 목록을 필드로 들고 있어야 이 모양이 나옵니다.** 앞에서 정리한 "관계를 평평하게 편 DTO"의 한 갈래인데, 여기서는 완전히 평평하게 펴는 것이 아니라 **한 겹은 남겨 둔 채로** 내보냅니다. 게시글과 댓글은 화면에서 항상 같이 보이니 한 번의 요청으로 함께 오는 편이 자연스럽습니다.

여기서 화면 쪽 코드가 서버 쪽 이름을 그대로 쓴다는 점이 다시 드러납니다. `post.createdAt` 은 DB의 `created_at` → 자바 필드 `createdAt` → JSON 키 `createdAt` 을 거쳐 온 이름입니다. **컬럼 이름 하나가 화면 코드까지 관통합니다.**

### 1-2. 목록 안의 목록 — 그리는 코드가 한 겹 중첩된다

```js
const commentsHtml = commentList.length > 0
    ? commentList.map(c => `
        <div class="comment-item">
            <div class="cmt-author">${c.author || ''}</div>
            <div class="cmt-text">${c.content || ''}</div>
            <button onclick="removeComment(${post.id}, ${c.id})">삭제</button>
        </div>
    `).join('')
    : '<div>첫 번째 댓글을 남겨보세요.</div>';
```

바깥은 `forEach` 로 돌면서 DOM에 붙이고, 안쪽은 `map` 으로 **문자열을 만들어 돌려받습니다.** 두 반복의 성격이 다릅니다.

| 반복 | 표기 | 하는 일 |
| --- | --- | --- |
| 바깥 (게시글) | `forEach` | 카드를 만들어 `appendChild` — 돌려주는 값이 필요 없다 |
| 안쪽 (댓글) | `map(...).join('')` | 조각 문자열을 모아 하나로 이어 붙인다 |

`map` 은 배열을 배열로 바꿉니다. 그대로 템플릿 리터럴에 박으면 원소 사이에 쉼표가 끼므로 `join('')` 으로 이어 붙여야 합니다. 이 두 줄이 짝이라고 외워 두는 편이 편합니다.

빈 목록일 때 다른 문구를 내보내는 삼항 연산자도 같은 자리에 있습니다. 배열이 비어 있으면 `map` 은 빈 배열을, `join('')` 은 빈 문자열을 돌려주므로 **아무것도 안 그려지고 끝납니다.** 그것을 그대로 두면 화면이 텅 비어 보이니 대신 안내 문구를 넣습니다.

### 1-3. `removeComment(${post.id}, ${c.id})` — 안쪽에서 바깥 값을 함께 넘긴다

댓글 삭제 버튼은 값을 둘 받습니다. 댓글 번호만 있으면 서버 쪽 삭제는 되는데, **게시글 번호를 같이 넘기는 이유는 화면 쪽 사정입니다.** 삭제 후 목록을 다시 그릴 때 "어느 카드의 댓글창을 다시 열어야 하는가"를 알아야 하기 때문입니다.

안쪽 `map` 콜백 안에서 바깥 `forEach` 의 `post` 를 그대로 쓸 수 있는 것은 **클로저** 덕분입니다. 화살표 함수가 자기가 만들어진 자리의 변수를 계속 볼 수 있어서, 중첩이 늘어도 바깥 값을 따로 넘겨 줄 필요가 없습니다.

다만 그 값이 `onclick` 문자열 안으로 들어가는 순간 성질이 달라집니다. 템플릿 리터럴은 값을 **코드 조각**으로 박아 넣습니다.

```js
onclick="removeComment(${post.id}, ${c.id})"   // → removeComment(3, 7)
```

숫자라 그대로 박아도 유효한 코드가 되지만, 문자열이었다면 따옴표로 감싸야 합니다. 박아 넣는 값의 타입에 따라 적는 모양이 갈립니다.

### 1-4. 통째로 다시 그리면 열려 있던 것이 닫힌다

이 화면의 갱신 방식은 앞에서 쓰던 것과 같습니다. 등록·삭제가 끝나면 `getPosts()` 를 다시 불러 **목록 영역을 통째로 비우고 새로 그립니다.**

```js
feedContainer.innerHTML = '';   // 다 지우고
res.data.forEach(post => { ... appendChild(card); });   // 다시 만든다
```

간단하고 서버 상태와 어긋날 일이 없다는 것이 이 방식의 장점입니다. 그런데 이번 화면에는 **DOM에만 있고 서버에는 없는 상태**가 하나 생겼습니다. 댓글창이 열려 있는지 닫혀 있는지입니다.

`innerHTML = ''` 로 지우는 순간 그 `open` 클래스도 같이 사라집니다. 댓글을 하나 달았더니 방금까지 보고 있던 댓글창이 접혀 버리는 모양이 됩니다.

### 1-5. 사라질 상태를 바깥에 기억해 두기

`index.js` 맨 위의 한 줄이 그 대응입니다.

```js
// 펼쳐진 댓글 창의 boardId를 기록하여 목록 갱신 시 상태 유지
const openCommentSet = new Set();
```

토글할 때 DOM의 클래스와 이 집합을 **함께** 고칩니다.

```js
if (drawer.classList.contains('open')) {
    drawer.classList.remove('open');
    openCommentSet.delete(boardId);
} else {
    drawer.classList.add('open');
    openCommentSet.add(boardId);
}
```

그리고 다시 그릴 때 이 집합을 보고 클래스를 되돌려 줍니다.

```js
const isOpen = openCommentSet.has(post.id);
...
<div class="comment-drawer ${isOpen ? 'open' : ''}" id="comments-${post.id}">
```

정리하면 **화면을 지웠다 다시 그리는 방식에서는, DOM에만 살아 있는 상태를 DOM 바깥에 한 벌 더 들고 있어야 합니다.** 그 한 벌이 "진짜"이고 DOM은 그것을 비춘 결과가 됩니다.

`Set` 을 고른 것도 맞는 자리입니다. 담는 것이 번호 목록이고, 같은 번호가 두 번 들어갈 일이 없고, 물어보는 것이 "들어 있나"뿐입니다.

| 필요 | `Set` | 배열 |
| --- | --- | --- |
| 중복 없이 담기 | 자동 | 넣기 전에 검사해야 함 |
| 들어 있나 | `has()` | `includes()` / `indexOf()` |
| 빼기 | `delete()` | `splice()` 로 자리를 찾아 제거 |
| 순서 | 보장하지 않음(쓸 일 없음) | 유지 |

댓글 등록·삭제 함수에서 `openCommentSet.add(boardId)` 를 한 번 더 부르는 것도 같은 이야기입니다. 댓글을 방금 건드렸으면 그 카드는 **열린 채로 다시 그려지는 편이** 자연스럽습니다.

### 1-6. 값을 어디에 싣는가 — 이 화면의 네 요청

```js
axios.post('/api/board', payload);                       // 본문
axios.delete('/api/board', { params: { id, password } }); // 쿼리스트링
axios.post('/api/board/comments', payload);              // 본문
axios.delete('/api/board/comments', { params: { commentId, password } });
```

| 갈래 | 싣는 곳 | 서버 쪽 표시 |
| --- | --- | --- |
| 등록 | 요청 본문(JSON) | `@RequestBody` |
| 삭제 | 쿼리스트링 | `@RequestParam` |

기준은 앞에서 정리한 것과 같습니다. **여러 값을 한 벌로 보내면 본문, 값 한둘이면 쿼리스트링**입니다. `axios.delete` 는 두 번째 인자가 설정 객체라 값을 `params` 안에 넣어야 하는 점만 모양이 다릅니다. `axios.post` 는 두 번째 인자가 곧 본문이라 객체를 그대로 넘깁니다. 같은 라이브러리인데 메소드마다 인자 자리가 갈리는 자리라 헷갈리기 쉽습니다.

주소 설계도 눈여겨볼 만합니다. 댓글은 `/api/board/comments` 로 **게시글 주소 아래에 붙었습니다.** 댓글이 게시글에 딸린 것이라는 관계가 주소에 드러납니다.

### 1-7. 삭제 앞에 비밀번호를 물어보기

```js
async function removePost(id) {
    const password = prompt('비밀번호를 입력하세요:');
    ...
}
```

`prompt` 는 값을 문자열로 돌려주고, 취소하면 `null` 을 돌려줍니다. `confirm` 이 `true`/`false` 만 주는 것과 갈리는 자리입니다.

여기서 비밀번호는 로그인 개념이 아니라 **글마다 붙은 값 하나**입니다. 익명 게시판에서 자기 글만 지우게 하는 오래된 방식이고, 시드 SQL에도 그대로 값이 들어 있습니다.

```sql
INSERT INTO board (author, password, content, created_at, updated_at)
VALUES ('유재석', '1234', '안녕하세요! 첫 번째 게시글입니다.', NOW(), NOW());
```

실습용이라 이렇게 두지만, 비밀번호를 표에 그대로 두는 것은 연습 범위 안에서만 성립하는 모양입니다. 실제로는 해시해서 저장하고 원문은 어디에도 남기지 않습니다.

시드 SQL을 보면 게시글 셋을 먼저 넣고 댓글을 나중에 넣습니다. 댓글의 `board_id` 가 게시글 번호를 가리키니 **부모가 먼저 들어가야 합니다.** 관계가 있는 표의 시드에서 늘 나오는 순서입니다. 감사 컬럼에 `NOW()` 를 직접 적는 것도 SQL로 바로 나가는 INSERT가 JPA 리스너를 안 거치기 때문입니다.

### 1-8. 모달 — 클래스 하나로 열고 닫기

```css
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(4px);
  display: none;
  align-items: flex-end;
}
.modal-overlay.active {
  display: flex;
}
```

```js
function openPostModal() {
    document.querySelector('.modal-post').classList.add('active');
}
```

**보이고 안 보이고를 자바스크립트가 직접 정하지 않고, 클래스를 붙였다 뗄 뿐입니다.** 어떻게 보일지는 전부 CSS가 정합니다. 이 갈라 두기가 있으면 나중에 모달 모양을 바꿀 때 자바스크립트를 안 봐도 됩니다. 댓글 드로어(`.comment-drawer.open`)도 같은 구조입니다.

`position: fixed` + `inset: 0` 은 화면 네 변에 딱 붙이는 관용 표기입니다. `top/right/bottom/left: 0` 네 줄을 한 줄로 줄인 것입니다.

배경 클릭으로 닫는 처리에도 한 가지 요령이 있습니다.

```js
document.querySelector('.modal-post').addEventListener('click', (e) => {
    if (e.target === document.querySelector('.modal-post')) closePostModal();
});
```

클릭은 안쪽 요소에서 바깥으로 거슬러 올라오므로(버블링), 시트 안을 눌러도 오버레이의 처리기가 불립니다. 그래서 **실제로 눌린 것이 오버레이 자기 자신인지** `e.target` 으로 확인합니다. 이 한 줄이 없으면 입력칸을 누를 때마다 모달이 닫힙니다.

### 1-9. 하단 바가 클릭을 통과시키는 자리

```css
.bottom-bar {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  background: linear-gradient(to top, rgba(15, 20, 25, 0.95) 70%, transparent);
  pointer-events: none;
}
.write-fab {
  pointer-events: auto;
}
```

하단 바는 화면 폭 전체를 덮는데, 그 위로 그라데이션만 깔고 실제로 누를 것은 가운데 버튼 하나입니다. 부모에 `pointer-events: none` 을 걸어 클릭을 통과시키고 버튼에만 `auto` 로 되살립니다. **덮개는 있는데 클릭은 막지 않는** 모양을 만드는 표기입니다.

### 1-10. `<script>` 를 body 끝에 두고 마지막 줄에서 시작하기

```html
<script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
<script src="index.js"></script>
```

```js
// 초기 실행
getPosts();
```

순서가 둘 다 의미가 있습니다. axios를 먼저 불러야 `index.js` 안에서 그 이름을 쓸 수 있고, `<script>` 가 body 끝에 있어야 `document.querySelector('.modal-post')` 가 실제 요소를 찾습니다. `index.js` 마지막 줄의 `addEventListener` 도 같은 사정입니다.

`getPosts()` 를 마지막 줄에서 한 번 부르는 것이 화면의 시작점입니다. 이후로는 등록·삭제가 끝날 때마다 같은 함수가 다시 불립니다. **화면을 그리는 통로가 하나뿐**이라 "어디서 그렸더라"를 찾을 일이 없습니다.

## 2. 추가로 알면 좋은 활용법

### 2-1. `innerHTML` 에 남의 글을 넣는다는 것

```js
<div class="post-content">${post.content || ''}</div>
```

`post.content` 는 사용자가 입력한 문자열입니다. 그것을 `innerHTML` 로 넣으면 **글자가 아니라 마크업으로 해석됩니다.** 내용에 태그가 들어 있으면 그대로 문서에 붙습니다. 게시판처럼 남이 쓴 글을 그리는 화면에서는 이것이 XSS가 열리는 자리입니다.

대응은 값이 들어가는 자리만 `textContent` 로 넣는 것입니다.

```js
const p = document.createElement('div');
p.className = 'post-content';
p.textContent = post.content;   // 태그가 있어도 글자로 들어간다
```

틀은 템플릿 리터럴로 만들고 사용자 값만 따로 채우는 절충도 흔합니다. 라이브러리를 쓴다면 값을 자동으로 이스케이프해 주는 쪽을 고릅니다.

### 2-2. `${post.content || ''}` — 값이 없을 때를 미리 막기

`||` 는 왼쪽이 거짓 같은 값(`undefined`·`null`·빈 문자열·`0`)이면 오른쪽을 돌려줍니다. 그래서 서버가 안 보낸 필드가 `undefined` 로 찍히는 것을 막습니다.

다만 `0` 도 걸린다는 점은 알아 두는 편이 좋습니다. 숫자를 다룰 때는 `??`(널 병합)를 쓰면 `null`·`undefined` 일 때만 대체합니다.

```js
const count = post.commentCount ?? 0;   // 0은 0으로 남는다
```

`post.comments || []` 도 같은 관용입니다. 서버가 목록을 안 보냈을 때 `undefined.map(...)` 으로 터지는 것을 막습니다.

### 2-3. `onclick` 속성 대신 이벤트 위임

지금은 마크업 문자열에 `onclick` 을 박아 넣습니다. 짧아서 읽기 쉬운데, 함수가 전역에 있어야 하고 값을 문자열로 박아야 하는 제약이 따라옵니다.

목록이 커지면 부모 하나에 처리기를 걸고 눌린 자리를 찾아가는 방식으로 바꿉니다.

```js
feedContainer.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-action]');
    if (!btn) return;
    const { action, id } = btn.dataset;
    if (action === 'delete-post') removePost(Number(id));
});
```

처리기가 하나뿐이라 카드를 아무리 늘려도 그대로이고, 값은 `data-*` 속성으로 넘기니 따옴표를 신경 쓸 일이 없습니다. `closest` 는 눌린 요소에서 위로 올라가며 조건에 맞는 조상을 찾아 줍니다.

### 2-4. 실패를 화면에 알리기

지금은 모든 요청이 이 모양입니다.

```js
} catch (err) {
    console.error(err);
}
```

콘솔에만 남으므로 화면에서는 **아무 일도 안 일어난 것처럼 보입니다.** 비밀번호가 틀려서 삭제가 안 된 것과 서버가 죽은 것이 화면에서 똑같이 보입니다.

axios는 2xx가 아닌 응답을 예외로 던지고, 그 안에 서버가 준 정보가 들어 있습니다.

```js
} catch (err) {
    if (err.response) {
        alert(`실패 (${err.response.status})`);   // 서버가 답은 했다
    } else {
        alert('서버에 연결하지 못했습니다.');       // 요청 자체가 못 갔다
    }
}
```

`err.response` 가 있는지로 **서버까지 갔다 왔는가**가 갈립니다. 이 둘을 나눠 두면 화면에서 볼 수 있는 정보가 확 늘어납니다.

### 2-5. 보내기 전에 값 확인하기

```js
const payload = {
    author: document.querySelector('.input-post-author').value,
    ...
};
```

`.value` 는 언제나 문자열이고, 비어 있으면 빈 문자열입니다. 그대로 보내면 `@Column(nullable = false)` 는 통과하고(빈 문자열은 `null` 이 아닙니다) 내용 없는 글이 저장됩니다.

```js
if (!payload.author.trim() || !payload.content.trim()) {
    alert('닉네임과 내용을 입력해 주세요.');
    return;
}
```

`trim()` 으로 공백만 있는 입력도 함께 거릅니다. **화면 검사는 사용자에게 빨리 알려 주는 몫이고, 진짜 방어는 서버 쪽 `@Valid` 와 DB 제약이 합니다.** 어느 한쪽만 두지 않습니다.

### 2-6. 요청이 도는 동안 버튼 잠그기

등록 버튼을 빠르게 두 번 누르면 요청이 두 번 나가고 글이 두 벌 생깁니다.

```js
async function writePost() {
    const btn = document.querySelector('.btn-submit');
    btn.disabled = true;
    try {
        await axios.post('/api/board', payload);
        ...
    } finally {
        btn.disabled = false;
    }
}
```

`finally` 에 되돌리기를 두면 실패해도 버튼이 잠긴 채 남지 않습니다. 되돌릴 수 없는 요청 앞에서는 이런 잠금이 `confirm` 만큼이나 실질적입니다.

### 2-7. 시각을 사람이 읽는 모양으로

`post.createdAt` 은 `2026-09-07T16:20:31` 같은 문자열로 옵니다. 그대로 찍으면 가운데 `T` 가 그대로 보입니다.

```js
const d = new Date(post.createdAt);
const text = d.toLocaleString('ko-KR', { dateStyle: 'short', timeStyle: 'short' });
```

"3분 전" 같은 상대 시각이 필요하면 `Intl.RelativeTimeFormat` 이 있습니다. 서버에서 포맷해 보내는 갈래도 있는데, **화면마다 원하는 모양이 다르므로 값은 표준 모양으로 보내고 꾸미기는 화면에서 하는 편**이 손이 덜 갑니다.

## 3. 더 나아가 알면 좋은 것

### 3-1. 전부 다시 그리기와 부분만 고치기

지금 방식은 무슨 일이 있어도 목록 전체를 다시 그립니다. 서버 상태와 어긋날 일이 없다는 것이 가장 큰 값어치입니다. 대신 요청이 한 번 더 나가고, 스크롤 위치나 열린 상태 같은 것을 따로 챙겨야 합니다(1-5가 그 대응이었습니다).

| 갈래 | 방식 | 손익 |
| --- | --- | --- |
| 전체 재조회 | 갱신 후 목록을 다시 받아 그린다 | 어긋날 일 없음 / 요청 한 번 더, 상태 유실 |
| 부분 갱신 | 바뀐 카드만 손으로 고친다 | 빠름 / 서버 상태와 어긋날 여지 |
| 낙관적 갱신 | 응답을 기다리지 않고 먼저 그리고, 실패하면 되돌린다 | 즉각 반응 / 되돌리기 코드가 붙는다 |

규모가 작을 때는 지금 방식이 제일 안전합니다. 화면이 커지고 상태가 늘어나면 "DOM 바깥에 상태를 들고 있다가 그것으로 화면을 그린다"는 1-5의 발상이 점점 커져서 결국 상태 관리 라이브러리나 프레임워크가 하는 일이 됩니다.

### 3-2. 댓글을 언제 함께 보낼 것인가

지금은 목록 응답에 댓글이 다 실려 옵니다. 게시글이 세 개일 때는 문제가 없는데, 백 개가 되면 대부분 펼치지도 않을 댓글까지 전부 실어 보내게 됩니다.

- 목록에는 댓글 **개수만** 담고, 펼칠 때 `/api/board/{id}/comments` 로 따로 받아 오기
- 목록은 그대로 두되 댓글을 최근 몇 개만 담기
- 게시글 목록 자체에 페이징 걸기

서버 쪽으로는 이것이 곧 N+1 이야기와 이어집니다. 게시글을 읽고 각 게시글의 댓글을 따로 읽으면 쿼리가 1+N이 되고, `join fetch` 나 `@EntityGraph` 로 한 번에 읽는 갈래가 있습니다. 컬렉션을 페치하면 결과 줄이 늘어 `distinct` 와 페이징 제약이 따라오는 것도 앞에서 정리한 그대로입니다.

### 3-3. 비밀번호를 값으로 다루는 것의 한계

글마다 비밀번호를 두는 방식은 요청마다 비밀번호가 함께 오갑니다. 다음 단계는 **한 번 확인하고 그 사실을 들고 다니는** 구조입니다.

- 세션 — 서버가 로그인 상태를 기억하고 브라우저는 세션 ID만 들고 다닌다
- 토큰(JWT) — 서버가 상태를 안 들고, 브라우저가 서명된 증표를 들고 다닌다
- Spring Security — 인증·인가를 필터 층에서 처리해 컨트롤러가 그것을 몰라도 되게 한다

저장 쪽도 같이 봅니다. 비밀번호는 원문이 아니라 해시(BCrypt 등)로 저장하고, 확인은 "해시가 같은가"로 합니다. 되돌릴 수 없는 방향으로 한 번 바꿔 두는 것이라 표를 통째로 들여다봐도 원문을 알 수 없습니다.

### 3-4. 정적 파일이 두 자리에 있는 이유

빌드 폴더 아래에도 `static/day07` 이 그대로 한 벌 있습니다. `src/main/resources` 에 둔 것을 그레이들이 빌드 결과물로 복사한 것이라, **손대는 것은 언제나 `src` 쪽 하나뿐입니다.** 화면을 고쳤는데 안 바뀌어 보이면 빌드가 다시 돌았는지, 브라우저가 캐시를 물고 있는지 순서로 봅니다.

### 3-5. 다음에 볼 키워드

- `textContent` · XSS · 이스케이프 · `DOMPurify`
- 이벤트 위임 · `closest` · `dataset`(`data-*` 속성)
- `??`(널 병합) 와 `||` 의 갈림 · 옵셔널 체이닝 `?.`
- `err.response` · axios 인터셉터로 오류 처리 한 자리에 모으기
- `Intl.DateTimeFormat` · `Intl.RelativeTimeFormat`
- 낙관적 갱신(optimistic update) 과 되돌리기
- 페이징 · 무한 스크롤 · `IntersectionObserver`
- 세션 · 쿠키 · JWT · Spring Security · BCrypt
- `join fetch` · `@EntityGraph` · 컬렉션 페치의 `distinct` 와 페이징 제약
- 상태를 화면 바깥에 두는 구조 → 프레임워크(React·Vue)가 대신하는 일

## 실습 파일

- `2026B_Spring/springweb/src/main/resources/static/day07/index.js` (**화면 전체를 다시 그리는 방식과 그때 사라지는 상태** — 목록 안에 목록이 든 응답을 바깥 `forEach`·안쪽 `map().join('')` 두 겹으로 그리는 구조와 두 반복의 성격이 갈리는 자리, `innerHTML = ''` 로 지웠다 다시 그릴 때 DOM에만 있던 `open` 클래스가 함께 사라지는 문제와 `Set` 을 DOM 바깥에 두어 상태를 기억했다 되돌리는 대응, 안쪽 콜백에서 바깥 `post` 를 클로저로 그대로 쓰는 점과 그 값을 `onclick` 문자열에 박을 때 타입에 따라 따옴표가 갈리는 자리, `axios.post` 의 두 번째 인자가 본문이고 `axios.delete` 는 설정 객체의 `params` 라 인자 자리가 메소드마다 갈리는 점, `prompt` 가 문자열과 `null` 을 돌려주는 것과 `confirm` 의 대비, `|| ''` 로 안 온 값을 막는 관용, 화면을 그리는 통로를 `getPosts()` 하나로 고정해 두는 배치)
- `2026B_Spring/springweb/src/main/resources/static/day07/index.html` (**화면 골격과 스크립트 순서** — 피드 영역·하단 고정 바·모달 셋으로 나눈 구조와 빈 컨테이너 하나를 자바스크립트가 채우는 배치, axios CDN을 `index.js` 보다 먼저 두어야 하는 이유와 `<script>` 를 body 끝에 두어야 `querySelector` 가 요소를 찾는 사정, `class` 식별자와 `onclick` 으로 마크업과 코드를 잇는 표기)
- `2026B_Spring/springweb/src/main/resources/static/day07/index.css` (**보이고 안 보이고를 클래스로만 가르는 구조** — `.modal-overlay` / `.modal-overlay.active`, `.comment-drawer` / `.comment-drawer.open` 두 짝이 같은 모양인 점과 자바스크립트가 `classList` 만 건드리고 모양은 전부 CSS가 정하는 갈라 두기, `position: fixed` + `inset: 0` 으로 화면을 덮는 표기, `pointer-events: none` 을 부모에 걸고 버튼에만 `auto` 로 되살려 덮개가 클릭을 막지 않게 하는 자리, `:root` 사용자 정의 속성으로 색·반경을 한 자리에 모으기, `@media (min-width: 521px)` 로 좁은 화면은 하단 시트·넓은 화면은 가운데 모달로 갈라 두기)
- `2026B_Spring/springweb/src/main/resources/sql/practice5.sql` (**관계가 있는 표의 시드** — 게시글을 먼저 넣고 댓글을 나중에 넣어야 하는 부모 우선 순서와 댓글의 `board_id` 가 앞서 들어간 번호를 가리키는 점, 감사 컬럼에 `NOW()` 를 직접 적는 이유가 SQL로 바로 나가는 INSERT는 JPA 리스너를 안 거치기 때문인 자리, 비밀번호를 값 하나로 표에 두는 실습용 모양과 그 한계)

## 관련 노트

[[Spring MOC]] · [[Spring day07 FK 번호를 엔티티로 바꿔 저장하기]] · [[KDT_2026 학습 지도]]
