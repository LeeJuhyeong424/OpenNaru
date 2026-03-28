"""AST 노드 정의 — 모든 노드는 BaseNode를 상속한다."""

from dataclasses import dataclass, field
from typing import Optional

# ── 기본 노드 ─────────────────────────────────────────────────────────────────

@dataclass
class BaseNode:
    type: str


# ── 블록 노드 (문서 최상위 구조) ──────────────────────────────────────────────

@dataclass
class DocumentNode(BaseNode):
    type: str = "document"
    children: list = field(default_factory=list)


@dataclass
class HeadingNode(BaseNode):
    type: str = "heading"
    level: int = 1          # 1~5
    content: str = ""
    anchor: str = ""        # id 속성용 슬러그


@dataclass
class ParagraphNode(BaseNode):
    type: str = "paragraph"
    lines: list[str] = field(default_factory=list)


@dataclass
class TableNode(BaseNode):
    type: str = "table"
    rows: list[list[str]] = field(default_factory=list)  # rows[행][열] = 셀 원문


@dataclass
class ListNode(BaseNode):
    type: str = "list"
    ordered: bool = False   # True = <ol>, False = <ul>
    items: list = field(default_factory=list)  # ListItemNode 목록


@dataclass
class ListItemNode(BaseNode):
    type: str = "list_item"
    depth: int = 1          # 중첩 깊이
    ordered: bool = False
    content: str = ""


@dataclass
class QuoteNode(BaseNode):
    type: str = "quote"
    lines: list[str] = field(default_factory=list)


@dataclass
class HorizontalNode(BaseNode):
    type: str = "horizontal"


@dataclass
class CodeBlockNode(BaseNode):
    type: str = "code_block"
    language: str = ""
    content: str = ""


@dataclass
class FoldingNode(BaseNode):
    """접기/펼치기 블록 {{{#!folding [제목]}}}"""
    type: str = "folding"
    summary: str = ""
    children: list = field(default_factory=list)


@dataclass
class CalloutNode(BaseNode):
    """{{{#!note}}}, {{{#!tip}}}, {{{#!warning}}}, {{{#!danger}}}"""
    type: str = "callout"
    kind: str = "note"      # note / tip / warning / danger
    children: list = field(default_factory=list)


@dataclass
class HtmlBlockNode(BaseNode):
    """{{{#!html}}} — 관리자 전용 원시 HTML 삽입"""
    type: str = "html_block"
    content: str = ""


@dataclass
class RedirectNode(BaseNode):
    type: str = "redirect"
    target: str = ""


# ── 인라인 노드 (블록 내부 인라인 문법) ───────────────────────────────────────

@dataclass
class TextNode(BaseNode):
    type: str = "text"
    content: str = ""


@dataclass
class BoldNode(BaseNode):
    """'''굵은 글씨'''"""
    type: str = "bold"
    children: list = field(default_factory=list)


@dataclass
class ItalicNode(BaseNode):
    """''기울임''"""
    type: str = "italic"
    children: list = field(default_factory=list)


@dataclass
class UnderlineNode(BaseNode):
    """__밑줄__"""
    type: str = "underline"
    children: list = field(default_factory=list)


@dataclass
class StrikeNode(BaseNode):
    """~~취소선~~"""
    type: str = "strike"
    children: list = field(default_factory=list)


@dataclass
class SupNode(BaseNode):
    """^^위첨자^^"""
    type: str = "sup"
    children: list = field(default_factory=list)


@dataclass
class SubNode(BaseNode):
    """,,아래첨자,,"""
    type: str = "sub"
    children: list = field(default_factory=list)


@dataclass
class InlineCodeNode(BaseNode):
    """`인라인 코드`"""
    type: str = "inline_code"
    content: str = ""


@dataclass
class ColorNode(BaseNode):
    """{{{#FF0000 텍스트}}} 또는 {{{#red 텍스트}}}"""
    type: str = "color"
    color: str = ""
    children: list = field(default_factory=list)


@dataclass
class SizeNode(BaseNode):
    """{{{+1 텍스트}}} ~ {{{+5 텍스트}}}, {{{-1 텍스트}}} ~ {{{-5 텍스트}}}"""
    type: str = "size"
    size: str = ""          # "+1" ~ "+5", "-1" ~ "-5"
    children: list = field(default_factory=list)


@dataclass
class LinkNode(BaseNode):
    """[[문서명]] 또는 [[문서명|표시텍스트]]"""
    type: str = "link"
    target: str = ""
    label: Optional[str] = None
    namespace: str = "main"     # main / 분류 / 파일 / 틀 등
    is_category: bool = False
    is_file: bool = False


@dataclass
class ExternalLinkNode(BaseNode):
    """[https://example.com 텍스트]"""
    type: str = "external_link"
    url: str = ""
    label: str = ""


@dataclass
class FootnoteNode(BaseNode):
    """[* 각주 내용]"""
    type: str = "footnote"
    content: str = ""
    index: int = 0          # 렌더링 시 순서 번호 부여


@dataclass
class MathNode(BaseNode):
    """$수식$ (KaTeX)"""
    type: str = "math"
    content: str = ""
    display: bool = False   # True = $$블록 수식$$


@dataclass
class TemplateNode(BaseNode):
    """{{틀이름|인수1=값1|인수2=값2}}"""
    type: str = "template"
    name: str = ""
    args: dict = field(default_factory=dict)
    positional_args: list[str] = field(default_factory=list)


# ── 렌더링 결과 ────────────────────────────────────────────────────────────────

@dataclass
class TocEntry:
    level: int
    text: str
    anchor: str


@dataclass
class RenderResult:
    html: str = ""
    toc: list[TocEntry] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)          # 내부 링크 목록 (역링크 계산용)
    footnotes: list[str] = field(default_factory=list)
    redirect_to: Optional[str] = None
