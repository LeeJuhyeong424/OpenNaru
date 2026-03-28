# 나무마크 파서 설계

나무마크 확장 문법을 HTML로 변환하는 파서의 구조와 동작 방식을 설명합니다.

## 처리 파이프라인

입력 텍스트는 4단계를 거쳐 HTML로 변환됩니다.

```
텍스트 입력
    ↓
[1] Tokenizer    — 줄 단위로 읽어 토큰 종류를 판별
    ↓
[2] Block Parser — 연속 토큰을 블록 노드로 묶음
    ↓
[3] Inline Parser — 블록 내 인라인 문법(굵기·링크 등) 처리
    ↓
[4] Renderer     — AST 노드를 HTML 문자열로 출력
    ↓
RenderResult (html, toc, categories, links, footnotes, redirect_to)
```

### 단계 1 — Tokenizer

텍스트를 줄 단위로 읽어 각 줄의 **종류(TokenType)** 만 판별합니다.
코드블록·나무마크 블록 상태를 추적해 중첩 구조를 올바르게 처리합니다.

| TokenType | 설명 |
|-----------|------|
| `HEADING` | `= 제목 =` ~ `====== 제목 ======` |
| `TABLE_ROW` | `\|\| 셀 \|\| 셀 \|\|` |
| `LIST_ITEM` | `* 항목` / `# 항목` (중첩: `**`, `##`) |
| `QUOTE` | `> 인용` |
| `HORIZONTAL` | `----` |
| `CODE_BLOCK_OPEN/BODY/CLOSE` | ` ```lang ` … ` ``` ` |
| `BLOCK_OPEN/BODY/CLOSE` | `{{{#!directive` … `}}}` |
| `REDIRECT` | `#넘겨주기 [[목적지]]` |
| `BLANK` | 빈 줄 |
| `PARAGRAPH` | 위 규칙에 해당하지 않는 일반 텍스트 |

### 단계 2 — Block Parser

토큰 목록을 순회하여 연속 토큰을 **블록 노드(AST)** 로 묶습니다.

- 연속 `PARAGRAPH` 토큰 → `ParagraphNode`
- 연속 `TABLE_ROW` 토큰 → `TableNode`
- `LIST_ITEM` 토큰 → 들여쓰기 깊이에 따라 중첩 `ListNode`

### 단계 3 — Inline Parser

블록 내 텍스트에서 인라인 문법을 재귀적으로 파싱합니다.
우선순위: `{{{...}}}` > `'''bold'''` > `''italic''` > `__underline__` > `~~strike~~` > `^^sup^^` > `,,sub,,` > `` `code` `` > `[[link]]` > `[external]` > `[* footnote]` > `$math$`

### 단계 4 — Renderer

AST 트리를 순회하여 HTML을 생성합니다.
**모든 텍스트 노드**에 `html.escape()` 를 적용하여 XSS를 방어합니다.

## AST 노드 구조

### 블록 노드

| 노드 | 주요 필드 |
|------|-----------|
| `HeadingNode` | `level`, `content`, `anchor` |
| `ParagraphNode` | `children` (인라인 노드 목록) |
| `TableNode` | `rows` (셀 목록의 목록) |
| `ListNode` | `ordered`, `items` |
| `CodeBlockNode` | `language`, `code` |
| `FoldingNode` | `summary`, `children` |
| `CalloutNode` | `kind` (note/warning/danger/tip) |
| `HtmlBlockNode` | `html` (관리자 전용) |
| `RedirectNode` | `target` |

### 인라인 노드

`TextNode`, `BoldNode`, `ItalicNode`, `UnderlineNode`, `StrikeNode`, `SupNode`, `SubNode`, `InlineCodeNode`, `ColorNode`, `SizeNode`, `LinkNode`, `ExternalLinkNode`, `FootnoteNode`, `MathNode`, `TemplateNode`

## 렌더링 결과 구조

```python
@dataclass
class RenderResult:
    html: str           # 최종 HTML 문자열
    toc: list[TocEntry] # 목차 (level, text, anchor)
    categories: list[str]
    links: list[str]    # 내부 링크 대상 문서 목록
    footnotes: list[str]
    redirect_to: str | None
```

## 보안 처리

### HTML 이스케이프

렌더러에서 텍스트를 HTML로 출력할 때 **반드시** `html.escape()` 를 적용합니다.
`{{{#!html}}}` 블록은 `allow_raw_html=True` (관리자 권한) 일 때만 원시 HTML을 허용합니다.

### 링크 안전성

외부 링크 URL은 `https?://` 패턴만 허용합니다.
`javascript:`, `vbscript:`, `data:` 스킴은 차단하여 클릭재킹을 방지합니다.

### 틀(Template) 처리

파서 단계에서 즉시 렌더링하지 않고 `TemplateNode` 로 AST에 보관합니다.
렌더러 단계에서 DB에서 틀 내용을 가져와 재귀적으로 파싱하여 삽입합니다.

## 공개 API

```python
from app.parser import parse, RenderResult

result: RenderResult = parse(text, allow_raw_html=False)
```

## 관련 파일

```
backend/app/parser/
├── __init__.py      # 공개 API: parse, RenderResult
├── tokens.py        # TokenType, Token
├── nodes.py         # 모든 AST 노드 + RenderResult
├── tokenizer.py     # Tokenizer
├── block_parser.py  # Block Parser
├── inline_parser.py # Inline Parser
└── renderer.py      # HtmlRenderer
```
