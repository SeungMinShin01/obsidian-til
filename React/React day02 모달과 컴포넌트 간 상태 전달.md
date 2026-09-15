---
출처: Claude 분석
원본: KDT_2026/2026_React/src/example/day02/practice2
작성일: 2026-09-14
tags: [학습, react]
---

# React day02 — 모달과 컴포넌트 간 상태 전달

> 실습 파일: `src/example/day02/practice2/ProductManager.jsx` · `practice2/ReviewManager.jsx`
> 허브: [[React MOC]] · 이전: [[React day02 useEffect와 fetch로 서버 CRUD]] · 다음: [[React day03 JSX 스타일링과 이미지 경로]]

실습 2의 나머지 절반이다. `ProductManager`가 화면 전체를 쥐고, 카테고리 관리·제품 수정·리뷰 세 개의 **모달**을 상태로 열고 닫으며, 자식 컴포넌트(`CategoryManager`·`ReviewManager`)와 콜백 props로 소식을 주고받는다. 서버 통신 자체는 앞 노트와 같은 패턴이므로, 이 노트는 **여러 상태를 한 컴포넌트에서 다루는 법**과 **컴포넌트끼리 값을 주고받는 법**에 집중한다.

## 1. 배운 내용

### 1-1. ProductManager의 상태 목록

```jsx
// src/example/day02/practice2/ProductManager.jsx
const [products, setProducts] = useState([]);
const [categories, setCategories] = useState([]);

// 모달 상태
const [iscategorymodalopen, setIscategorymodalopen] = useState(false);
const [iseditmodalopen, setIseditmodalopen] = useState(false);
const [selectedproductforreview, setSelectedproductforreview] = useState(null);

// 폼 상태
const [form, setForm] = useState({ name: '', price: '', cno: '' });
const [editform, setEditform] = useState({ bno: null, name: '', price: '', cno: '' });
```

| 묶음 | 상태 | 타입 | 역할 |
| --- | --- | --- | --- |
| 서버 데이터 | `products`, `categories` | 배열 | 목록 두 개. 제품 등록 폼의 `<select>`에 카테고리가 필요해서 둘 다 받는다 |
| 모달 열림 | `iscategorymodalopen`, `iseditmodalopen` | boolean | `true`면 모달을 그린다 |
| 모달 + 대상 | `selectedproductforreview` | 객체 또는 `null` | "어느 제품의 리뷰인가"까지 담아야 해서 boolean이 아니라 제품 객체 자체를 넣는다. `null`이면 닫힘 |
| 폼 | `form`, `editform` | 객체 | 입력창 여러 개를 객체 하나로 묶었다 |

앞 노트의 `CategoryManager`가 상태 2개였다면 여기는 7개다. 상태가 늘어나도 원리는 같다 — **화면에 보이는 것은 전부 상태에서 나오고, 바꾸려면 `setXXX`를 부른다.**

### 1-2. 객체 상태와 스프레드 갱신

```jsx
<input value={form.name}  onChange={(e) => setForm({ ...form, name: e.target.value })} />
<input value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} />
<select value={form.cno}  onChange={(e) => setForm({ ...form, cno: e.target.value })}>
```

입력창이 세 개면 상태를 세 개 만들 수도 있지만, 여기서는 `{ name, price, cno }` 객체 하나로 묶었다. 그 대신 한 필드만 바꿀 때 **객체를 새로 만들어야** 한다. `{ ...form, name: 값 }`은 기존 필드를 전부 복사한 뒤 `name`만 덮어쓴 새 객체다.

[[React day02 useState와 상태 갱신]]에서 정리한 "배열·객체는 주소값이 바뀌어야 재렌더링"이 그대로 적용된다. `form.name = 값`처럼 직접 고치면 주소가 같아서 화면이 안 바뀐다.

| 시도 | 결과 |
| --- | --- |
| `form.name = e.target.value` | 값은 바뀌지만 재렌더링 없음 — 입력창이 안 움직인다 |
| `setForm({ ...form, name: e.target.value })` | 새 객체 → 재렌더링 → 입력창 갱신 |
| `setForm({ name: e.target.value })` | 재렌더링은 되지만 `price`·`cno`가 사라진다 |

폼을 비울 때도 `setForm({ name: '', price: '', cno: '' })`처럼 초기 모양 그대로 새 객체를 넣는다.

### 1-3. select도 제어 컴포넌트

```jsx
<select value={form.cno} onChange={(e) => setForm({ ...form, cno: e.target.value })}>
  <option value="">카테고리 선택</option>
  {categories?.map((c) => (
    <option key={c.cno} value={c.cno}>{c.name}</option>
  ))}
</select>
```

`<select>`는 HTML에서 `<option selected>`로 고르지만 React에서는 **`<select value={…}>`** 로 고른다. 옵션 목록은 서버에서 받은 `categories`를 `map`으로 찍고, 첫 줄에 빈 값 옵션을 두어 "아직 안 골랐음"을 표현한다. `e.target.value`는 항상 **문자열**이라 서버에 보낼 때 `Number(form.cno)`로 바꾼다.

`categories?.map`의 `?.`는 옵셔널 체이닝이다 — `categories`가 `undefined`·`null`이면 `map`을 부르지 않고 `undefined`를 돌려준다. 초기값이 `[]`라 실제로는 필요 없지만, 응답이 이상할 때를 대비한 방어다.

### 1-4. 숫자로 바꿔 보내기

```jsx
body: JSON.stringify({
  name: form.name,
  price: Number(form.price),
  cno: Number(form.cno),
}),
```

`<input type="number">`라도 `e.target.value`는 `"89000"` 같은 문자열이다. `JSON.stringify`는 문자열은 `"89000"`(따옴표 포함), 숫자는 `89000`으로 다르게 직렬화한다. 서버의 DTO 필드가 `int`면 문자열로 보내도 대개 변환되지만, 타입을 맞춰 보내는 편이 안전하다. 화면에 보일 때는 반대로 `Number(p.price || 0).toLocaleString()`으로 `89,000` 같은 표기를 만든다.

### 1-5. 모달 = 조건부 렌더링 + 고정 배경

```jsx
{iscategorymodalopen && (
  <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                backgroundColor: 'rgba(0,0,0,0.4)', display: 'flex',
                justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
    <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', width: '420px' }}>
      <h3>카테고리 관리</h3>
      <CategoryManager oncategoryupdated={(newlist) => setCategories(newlist)} />
      <button onClick={() => setIscategorymodalopen(false)}>닫기</button>
    </div>
  </div>
)}
```

모달에 특별한 API는 없다. **`상태 && <JSX>`** 로 상태가 `true`일 때만 그리고, 바깥 `div`를 `position: fixed`로 화면 전체에 깔아 반투명 배경을 만들고, 안쪽 `div`를 flex로 가운데 두는 것뿐이다.

| 동작 | 코드 |
| --- | --- |
| 열기 | 헤더 버튼 `onClick={() => setIscategorymodalopen(true)}` |
| 닫기 | ✕ 버튼·닫기 버튼 `onClick={() => setIscategorymodalopen(false)}` |
| 그리기 | `{iscategorymodalopen && (...)}` — `false && X`는 `false`라 아무것도 안 그린다 |

`&&` 조건부 렌더링은 [[React day02 useState와 상태 갱신]]의 "JSX를 변수에 담아 `if`로 갈아끼우기"를 한 줄로 줄인 것이다. 왼쪽이 `false`·`null`·`undefined`면 React가 그 자리를 비운다. 단 왼쪽이 숫자 `0`이면 `0`이 화면에 찍히므로 `length && ...`보다 `length > 0 && ...`로 쓴다.

### 1-6. 인라인 style은 객체 두 겹

```jsx
<div style={{ display: 'flex', gap: '8px', marginBottom: '14px' }}>
```

JSX의 `style`은 문자열이 아니라 **객체**를 받는다. 바깥 `{}`는 "JS 표현식", 안쪽 `{}`는 "객체 리터럴"이다. 속성명은 `margin-bottom`이 아니라 카멜케이스 `marginBottom`, 값은 문자열(`'8px'`)이거나 숫자(`zIndex: 1000`)다. 실습 2는 CSS 파일 없이 전부 이 방식으로 꾸며서, 컴포넌트 하나에 화면과 모양이 함께 들어 있다.

### 1-7. 자식 → 부모 — oncategoryupdated

```jsx
// 부모 (ProductManager)
<CategoryManager oncategoryupdated={(newlist) => setCategories(newlist)} />

// 자식 (CategoryManager)
export default function CategoryManager({ oncategoryupdated }) {
  const fetchcategories = async () => {
    // ... 조회 성공 시
    setCategories(list);
    if (oncategoryupdated) oncategoryupdated(list);
  };
}
```

카테고리 목록은 두 컴포넌트가 각자 들고 있다 — 모달 안 `CategoryManager`의 표, 그리고 `ProductManager`의 제품 등록 `<select>`. 모달에서 카테고리를 추가했는데 `<select>`에 안 뜨면 곤란하다. 그래서 자식이 조회를 마칠 때마다 **부모가 넘겨준 함수를 새 목록과 함께 부른다.** 부모는 그 함수 안에서 자기 상태를 갱신한다.

| 방향 | 수단 | 예 |
| --- | --- | --- |
| 부모 → 자식 (데이터) | props 값 | `product={selectedproductforreview}` |
| 자식 → 부모 (이벤트) | props 함수 | `oncategoryupdated={(list) => setCategories(list)}` |

[[React day02 컴포넌트 분리와 콜백 props]]의 "데이터는 내려가고 이벤트는 올라간다"에 **올라가는 값이 배열**인 경우다. `if (oncategoryupdated)`로 감싼 것은 이 컴포넌트를 부모 없이(콜백 없이) 써도 터지지 않게 하는 방어다.

### 1-8. 부모 → 자식 → 부모 — ReviewManager

```jsx
// 부모
<button onClick={() => setSelectedproductforreview(p)}>리뷰</button>
{selectedproductforreview && (
  <ReviewManager product={selectedproductforreview}
                 onclose={() => setSelectedproductforreview(null)} />
)}

// 자식 (ReviewManager)
export default function ReviewManager({ product, onclose }) {
  const [reviews, setReviews] = useState([]);
  useEffect(() => { fetchreviews(); }, [product?.bno]);
  // ...
  <button onClick={onclose}>✕</button>
}
```

리뷰 모달은 자식 컴포넌트가 **모달 껍데기까지 통째로** 그린다(`position: fixed` 배경이 `ReviewManager` 안에 있다). 부모는 "어느 제품인지"(`product`)와 "닫는 법"(`onclose`)만 넘긴다.

| 흐름 | 코드 |
| --- | --- |
| ① 리뷰 버튼 클릭 | `setSelectedproductforreview(p)` — 제품 객체가 상태에 들어감 |
| ② 모달 등장 | `selectedproductforreview && <ReviewManager … />` — `null`이 아니므로 그림 |
| ③ 자식이 조회 | `useEffect(…, [product?.bno])` — 마운트 직후 `fetch(…/reviews?bno=${product.bno})` |
| ④ 닫기 | `onclose()` → 부모의 `setSelectedproductforreview(null)` → `null && …`이라 사라짐 |

`useEffect`의 의존성이 `[]`가 아니라 `[product?.bno]`인 점이 앞 노트와 다르다. 같은 모달이 열린 채로 다른 제품이 들어오면(`bno`가 바뀌면) 리뷰를 다시 받아오게 한 것이다. 닫았다 다시 열면 컴포넌트가 새로 마운트되니 어차피 다시 조회되지만, 의존성을 적어 두면 "이 효과는 `bno`에 달려 있다"는 의도가 코드에 남는다.

### 1-9. 수정 모달 — 기존 값으로 폼 채우기

```jsx
const openeditmodal = (product) => {
  setEditform({
    bno: product.bno,
    name: product.name,
    price: product.price,
    cno: product.cno || (product.category ? product.category.cno : ''),
  });
  setIseditmodalopen(true);
};

const handleupdateproduct = async (e) => {
  e.preventDefault();
  const res = await fetch('http://localhost:8080/api/products', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ bno: editform.bno, name: editform.name,
                           price: Number(editform.price), cno: Number(editform.cno) }),
  });
  if (res.ok) { setIseditmodalopen(false); fetchproducts(); }
};
```

수정은 등록과 두 가지가 다르다. **열 때 폼을 채운다** — 클릭한 제품의 값을 `editform`에 복사해 두고 모달을 연다. **보낼 때 `bno`를 함께 보낸다** — 서버가 어느 행을 고칠지 알아야 하므로 본문에 키가 들어간다. 메소드는 `PUT`이다. 삭제가 쿼리 스트링으로 키를 보냈다면 수정은 본문으로 보낸다.

`product.cno || (product.category ? product.category.cno : '')`는 서버 응답이 `cno`를 평평하게 줄 수도, `category: { cno, name }` 객체로 줄 수도 있어서 둘 다 받아 주는 코드다. 목록 표의 `p.categoryname || (p.category ? p.category.name : …)`도 같은 이유다. 백엔드 DTO 모양이 정해지면 한쪽만 남기면 된다.

| 요청 | 메소드 | 키 전달 | 본문 |
| --- | --- | --- | --- |
| 등록 | POST | 없음 (서버가 발급) | `{ name, price, cno }` |
| 수정 | PUT | 본문 안 `bno` | `{ bno, name, price, cno }` |
| 삭제 | DELETE | 쿼리 스트링 `?bno=` | 없음 |

### 1-10. 별점 — 문자열 반복으로 그리기

```jsx
{'★'.repeat(r.rating || 5)}{'☆'.repeat(5 - (r.rating || 5))}
```

`String.prototype.repeat(n)`으로 채운 별 `rating`개, 빈 별 `5 - rating`개를 이어 붙인다. 이미지나 아이콘 라이브러리 없이 숫자 하나를 시각화하는 간단한 방법이다. `r.rating || 5`는 값이 없을 때 5로 두는 기본값 처리다.

## 2. 추가로 알면 좋은 활용법

### 2-1. 폼 onChange 하나로 합치기

입력창마다 `setForm({ ...form, name: … })`을 따로 쓰는 대신 `name` 속성으로 묶을 수 있다.

```jsx
const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

<input name="name"  value={form.name}  onChange={onChange} />
<input name="price" value={form.price} onChange={onChange} />
<select name="cno"  value={form.cno}   onChange={onChange}>…</select>
```

`[e.target.name]`은 계산된 프로퍼티명이다 — 이벤트가 온 입력창의 `name` 속성을 키로 쓴다. 필드가 늘어도 핸들러는 하나다.

### 2-2. 모달을 컴포넌트로 뽑기

카테고리 모달과 수정 모달의 배경·가운데 정렬 코드가 똑같다. 껍데기를 하나로 만든다.

```jsx
function Modal({ open, onClose, children }) {
  if (!open) return null;
  return (
    <div style={overlay} onClick={onClose}>
      <div style={box} onClick={(e) => e.stopPropagation()}>{children}</div>
    </div>
  );
}

<Modal open={iscategorymodalopen} onClose={() => setIscategorymodalopen(false)}>
  <CategoryManager oncategoryupdated={setCategories} />
</Modal>
```

`children`은 여는 태그와 닫는 태그 사이에 넣은 JSX가 자동으로 들어오는 특별한 props다. 배경 클릭으로 닫히게 하려면 안쪽 상자에서 `stopPropagation`으로 클릭이 배경까지 올라가지 않게 막는다. `oncategoryupdated={setCategories}`처럼 세터를 그대로 넘겨도 된다 — `(list) => setCategories(list)`와 같다.

### 2-3. 모달 상태 하나로 줄이기

boolean 두 개 + 객체 하나 대신 "지금 열린 모달이 무엇인가"를 상태 하나에 담는 방법도 있다.

```jsx
const [modal, setModal] = useState(null);   // null | 'category' | { type: 'edit', product } | { type: 'review', product }
{modal === 'category' && <CategoryManager … />}
{modal?.type === 'edit' && <EditForm product={modal.product} … />}
```

모달이 동시에 두 개 열리는 일이 없다면 이쪽이 상태 충돌을 원천 차단한다. 지금처럼 세 개까지는 따로 두어도 읽기 쉽다.

### 2-4. 인라인 style 대신 CSS 파일

`style={{…}}`은 빠르지만 같은 모양을 여러 곳에서 반복하게 된다. Vite 프로젝트는 `import './ProductManager.css'`로 CSS를 붙일 수 있고, `className="btn btn-danger"`처럼 클래스로 정리하면 JSX가 훨씬 짧아진다. CSS 수업에서 배운 선택자·flex가 그대로 쓰인다. 인라인은 **값이 상태에 따라 계산될 때**(`style={{ color: r.rating < 3 ? 'red' : 'green' }}`)에만 남기는 편이 정리된다.

### 2-5. 목록 갱신 뒤 카테고리 삭제 확인 문구

카테고리 삭제 확인창에 "(연결된 제품 확인 필요)"가 붙어 있다. `product.cno`가 `category.cno`를 참조하는 FK라서, 제품이 딸린 카테고리를 지우면 DB가 거부하거나(제약) 제품까지 같이 지워진다(CASCADE). 어느 쪽이든 프론트는 `res.ok`가 `false`인 응답을 받으니 그때 안내를 띄우는 처리를 덧붙일 수 있다. FK와 CASCADE는 SQL 수업에서 정리한 내용이다(평문 언급).

## 3. 더 나아가 알면 좋은 것

### 3-1. 상태를 어디에 둘 것인가

카테고리 목록이 `ProductManager`와 `CategoryManager`에 **두 벌** 있고 콜백으로 맞추고 있다. 이것이 "상태 끌어올리기"의 실제 사례이자 한계다 — 같은 데이터를 쓰는 컴포넌트가 더 늘면 콜백 사슬이 길어진다. 다음 단계는 목록을 부모 한 곳에만 두고 자식은 `categories`와 `refresh` 함수를 props로 받는 방식, 그 다음은 Context나 전역 상태 라이브러리(Zustand·Redux)로 어디서든 꺼내 쓰는 방식이다.

### 3-2. 커스텀 훅으로 통신 코드 빼기

`fetchXXX`·`handlecreate`·`handledelete` 세 쌍이 세 컴포넌트에 거의 같은 모양으로 반복된다. `useResource('/api/categories', 'cno')` 같은 커스텀 훅으로 뽑으면 컴포넌트에는 화면만 남는다. 훅의 이름은 반드시 `use`로 시작한다.

### 3-3. 접근성과 포털

진짜 모달은 배경 스크롤 잠금, ESC로 닫기, 포커스 가두기 같은 처리가 필요하다. `ReactDOM.createPortal`로 모달을 `#root` 바깥에 그리면 부모의 `overflow: hidden`이나 `z-index` 문제에서 벗어난다. 라이브러리(Radix·Headless UI)를 쓰면 이런 것들이 갖춰져 있다.

### 3-4. 다음에 볼 키워드

- `children` props와 합성(composition), 재사용 가능한 `Modal` 컴포넌트
- 상태 끌어올리기의 한계 → Context API → Zustand/Redux
- 커스텀 훅(`useXXX`)으로 fetch 로직 분리
- `createPortal`, 모달 접근성(포커스 트랩·ESC)
- React Router — 모달 대신 `/products/:bno/reviews` 같은 경로로 화면 나누기
- 백엔드 쪽 `@CrossOrigin`, `@RequestBody` DTO, `@RequestParam`으로 쿼리 스트링 받기 (Spring 노트에서 다룰 내용 — 평문 언급)

## 실습 파일

- `KDT_2026/2026_React/src/example/day02/practice2/ProductManager.jsx` — 제품 목록·등록·수정(PUT)·삭제, 객체 폼 상태와 스프레드 갱신, `<select>` 제어, 모달 세 개(`&&` 조건부 렌더링 + `position: fixed`), `CategoryManager`·`ReviewManager` 조립과 콜백 props
- `KDT_2026/2026_React/src/example/day02/practice2/ReviewManager.jsx` — 제품 하나의 리뷰 조회(`useEffect` 의존성 `[product?.bno]`)·등록·삭제, 자식이 모달 껍데기까지 그리고 `onclose`로 부모 상태를 비우는 패턴, `repeat`로 별점 표시

## 관련 노트

[[React MOC]] · [[React day02 useEffect와 fetch로 서버 CRUD]] · [[React day03 JSX 스타일링과 이미지 경로]] · [[React day02 useState와 상태 갱신]] · [[React day02 컴포넌트 분리와 콜백 props]] · [[KDT_2026 학습 지도]]
