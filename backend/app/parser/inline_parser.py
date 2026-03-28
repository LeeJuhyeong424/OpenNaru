"""3단계: 인라인 파서 — 텍스트 내부의 인라인 문법을 처리한다.

처리 우선순위 (설계 문서 기준):
  1. {{{...}}}  — 이스케이프 / 색상 / 크기 블록
  2. '''...'''  — 굵은 글씨
  3. ''...''    — 기울임
  4. __...__    — 밑줄
  5. ~~...~~    — 취소선
  6. ^^...^^    — 위첨자
  7. ,,..,,     — 아래첨자
  8. `...`      — 인라인 코드
  9. [[...]]    — 내부 링크 / 파일 / 분류
  10. [http...] — 외부 링크
  11. [* ...]   — 각주
  12. $...$     — 수식 (KaTeX)
  13. 나머지     — 일반 텍스트
"""

import re
from urllib.parse import urlparse

from .nodes import (
    BaseNode,
    BoldNode,
    ColorNode,
    ExternalLinkNode,
    FootnoteNode,
    InlineCodeNode,
    ItalicNode,
    LinkNode,
    MathNode,
    SizeNode,
    StrikeNode,
    SubNode,
    SupNode,
    TextNode,
    UnderlineNode,
)

# 허용된 외부 링크 프로토콜
_ALLOWED_SCHEMES = {'http', 'https', 'mailto', 'ftp'}


def parse_inline(text: str, footnotes: list[str] | None = None) -> list[BaseNode]:
    """텍스트를 인라인 노드 목록으로 변환한다."""
    if footnotes is None:
        footnotes = []
    nodes: list[BaseNode] = []
    _parse_span(text, nodes, footnotes)
    return nodes


def _parse_span(text: str, out: list[BaseNode], footnotes: list[str]) -> None:
    """텍스트를 우선순위대로 순차 파싱해 out에 노드를 추가한다."""
    if not text:
        return

    # 1순위: {{{...}}} 색상/크기/이스케이프 블록
    m = _find_brace_block(text)
    if m:
        _flush_text(text[:m.start()], out)
        inner = m.group(1)
        _parse_brace_block(inner, out, footnotes)
        _parse_span(text[m.end():], out, footnotes)
        return

    # 2순위: '''굵기'''
    m = _match_pair(text, "'''")
    if m:
        _flush_text(text[:m[0]], out)
        node = BoldNode()
        _parse_span(m[1], node.children, footnotes)
        out.append(node)
        _parse_span(text[m[2]:], out, footnotes)
        return

    # 3순위: ''기울임''
    m = _match_pair(text, "''")
    if m:
        _flush_text(text[:m[0]], out)
        node = ItalicNode()
        _parse_span(m[1], node.children, footnotes)
        out.append(node)
        _parse_span(text[m[2]:], out, footnotes)
        return

    # 4순위: __밑줄__
    m = _match_pair(text, "__")
    if m:
        _flush_text(text[:m[0]], out)
        node = UnderlineNode()
        _parse_span(m[1], node.children, footnotes)
        out.append(node)
        _parse_span(text[m[2]:], out, footnotes)
        return

    # 5순위: ~~취소선~~
    m = _match_pair(text, "~~")
    if m:
        _flush_text(text[:m[0]], out)
        node = StrikeNode()
        _parse_span(m[1], node.children, footnotes)
        out.append(node)
        _parse_span(text[m[2]:], out, footnotes)
        return

    # 6순위: ^^위첨자^^
    m = _match_pair(text, "^^")
    if m:
        _flush_text(text[:m[0]], out)
        node = SupNode()
        _parse_span(m[1], node.children, footnotes)
        out.append(node)
        _parse_span(text[m[2]:], out, footnotes)
        return

    # 7순위: ,,아래첨자,,
    m = _match_pair(text, ",,")
    if m:
        _flush_text(text[:m[0]], out)
        node = SubNode()
        _parse_span(m[1], node.children, footnotes)
        out.append(node)
        _parse_span(text[m[2]:], out, footnotes)
        return

    # 8순위: `인라인 코드`
    m = _match_pair(text, "`")
    if m:
        _flush_text(text[:m[0]], out)
        out.append(InlineCodeNode(content=m[1]))
        _parse_span(text[m[2]:], out, footnotes)
        return

    # 9순위: [[내부 링크]]
    m = re.search(r'\[\[(.+?)\]\]', text)
    if m:
        _flush_text(text[:m.start()], out)
        out.append(_parse_internal_link(m.group(1)))
        _parse_span(text[m.end():], out, footnotes)
        return

    # 10순위: [http... 텍스트] 외부 링크
    m = re.search(r'\[(https?://\S+)(?:\s+([^\]]*))?\]', text)
    if m:
        _flush_text(text[:m.start()], out)
        url = _sanitize_url(m.group(1))
        label = m.group(2) or m.group(1)
        out.append(ExternalLinkNode(url=url, label=label))
        _parse_span(text[m.end():], out, footnotes)
        return

    # 11순위: [* 각주]
    m = re.search(r'\[\*\s*(.*?)\]', text)
    if m:
        _flush_text(text[:m.start()], out)
        footnotes.append(m.group(1))
        out.append(FootnoteNode(content=m.group(1), index=len(footnotes)))
        _parse_span(text[m.end():], out, footnotes)
        return

    # 12순위: $수식$ (KaTeX 인라인)
    m = re.search(r'\$([^$\n]+?)\$', text)
    if m:
        _flush_text(text[:m.start()], out)
        out.append(MathNode(content=m.group(1), display=False))
        _parse_span(text[m.end():], out, footnotes)
        return

    # 나머지: 일반 텍스트
    _flush_text(text, out)


def _flush_text(text: str, out: list[BaseNode]) -> None:
    """빈 문자열이 아닌 경우에만 TextNode를 추가한다."""
    if text:
        out.append(TextNode(content=text))


def _match_pair(text: str, marker: str) -> tuple[int, str, int] | None:
    """marker로 감싸진 첫 번째 구간을 찾아 (시작위치, 내용, 끝위치)를 반환한다."""
    start = text.find(marker)
    if start == -1:
        return None
    end = text.find(marker, start + len(marker))
    if end == -1:
        return None
    inner = text[start + len(marker):end]
    return (start, inner, end + len(marker))


def _find_brace_block(text: str):
    """{{{...}}} 패턴을 찾는다. 중첩은 처리하지 않는다."""
    return re.search(r'\{\{\{((?:(?!\{\{\{).)*?)\}\}\}', text, re.DOTALL)


def _parse_brace_block(inner: str, out: list[BaseNode], footnotes: list[str]) -> None:
    """
    {{{ 내부 내용을 파싱한다.
    - {{{#FF0000 텍스트}}} → ColorNode
    - {{{+1 텍스트}}} / {{{-1 텍스트}}} → SizeNode
    - {{{텍스트}}} → 이스케이프 (그대로 출력)
    """
    # 색상 패턴: #RRGGBB 또는 색상명
    m = re.match(r'^(#[0-9a-fA-F]{3,6}|[a-zA-Z]+)\s+(.*)', inner, re.DOTALL)
    if m:
        node = ColorNode(color=m.group(1))
        _parse_span(m.group(2), node.children, footnotes)
        out.append(node)
        return

    # 크기 패턴: +1 ~ +5, -1 ~ -5
    m = re.match(r'^([+-][1-5])\s+(.*)', inner, re.DOTALL)
    if m:
        node = SizeNode(size=m.group(1))
        _parse_span(m.group(2), node.children, footnotes)
        out.append(node)
        return

    # 이스케이프: 내용을 텍스트로 그대로 출력
    out.append(TextNode(content=inner))


def _parse_internal_link(inner: str) -> BaseNode:
    """
    [[내부 링크]] 파싱.
    - [[문서명]]
    - [[문서명|표시텍스트]]
    - [[분류:게임]]
    - [[파일:이미지.png]]
    - [[틀:정보상자]]
    """
    if '|' in inner:
        target, label = inner.split('|', 1)
    else:
        target, label = inner, None

    target = target.strip()
    label = label.strip() if label else None

    # 네임스페이스 분류
    if ':' in target:
        ns, name = target.split(':', 1)
        ns_lower = ns.lower()
        if ns_lower in ('분류', 'category'):
            return LinkNode(target=name.strip(), label=label, namespace="category",
                            is_category=True)
        if ns_lower in ('파일', 'file'):
            return LinkNode(target=name.strip(), label=label, namespace="file",
                            is_file=True)
        return LinkNode(target=target, label=label, namespace=ns_lower)

    return LinkNode(target=target, label=label, namespace="main")


def _sanitize_url(url: str) -> str:
    """외부 링크 URL에서 위험한 프로토콜을 제거한다."""
    try:
        parsed = urlparse(url)
        if parsed.scheme.lower() not in _ALLOWED_SCHEMES:
            return '#'
    except Exception:
        return '#'
    return url
