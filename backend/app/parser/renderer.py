"""4단계: 렌더러 — AST 트리를 HTML 문자열로 변환한다.

이 단계에서 XSS 방어를 위한 HTML 이스케이프를 적용한다.
모든 사용자 입력 텍스트는 escape() 처리 후 출력한다.
"""

import re
from html import escape

from .inline_parser import parse_inline
from .nodes import (
    BaseNode,
    BoldNode,
    CalloutNode,
    CodeBlockNode,
    ColorNode,
    ExternalLinkNode,
    FoldingNode,
    FootnoteNode,
    HeadingNode,
    HorizontalNode,
    HtmlBlockNode,
    InlineCodeNode,
    ItalicNode,
    LinkNode,
    ListItemNode,
    ListNode,
    MathNode,
    ParagraphNode,
    QuoteNode,
    RedirectNode,
    RenderResult,
    SizeNode,
    StrikeNode,
    SubNode,
    SupNode,
    TableNode,
    TextNode,
    TocEntry,
    UnderlineNode,
)

# 크기 등급 → rem 매핑
_SIZE_MAP = {
    "+5": "2.0", "+4": "1.75", "+3": "1.5", "+2": "1.25", "+1": "1.1",
    "-1": "0.9", "-2": "0.8", "-3": "0.7", "-4": "0.6", "-5": "0.5",
}

# Callout 종류 → 표시 이름
_CALLOUT_LABEL = {
    "note": "📝 노트",
    "tip": "💡 팁",
    "warning": "⚠️ 주의",
    "danger": "🚨 경고",
}


class HtmlRenderer:
    """블록 노드 목록을 받아 HTML + 메타데이터를 반환한다."""

    def __init__(self, allow_raw_html: bool = False):
        # allow_raw_html: True이면 {{{#!html}}} 원시 HTML 허용 (관리자 전용)
        self.allow_raw_html = allow_raw_html

    def render(self, nodes: list[BaseNode]) -> RenderResult:
        result = RenderResult()
        parts: list[str] = []

        for node in nodes:
            # 넘겨주기 문서는 HTML 없이 redirect_to만 설정
            if isinstance(node, RedirectNode):
                result.redirect_to = node.target
                return result
            parts.append(self._render_block(node, result))

        # 각주 섹션 추가
        if result.footnotes:
            parts.append(self._render_footnotes(result.footnotes))

        result.html = "".join(parts)
        return result

    # ── 블록 노드 렌더링 ────────────────────────────────────────────────────

    def _render_block(self, node: BaseNode, result: RenderResult) -> str:
        if isinstance(node, HeadingNode):
            return self._render_heading(node, result)
        if isinstance(node, ParagraphNode):
            return self._render_paragraph(node, result)
        if isinstance(node, TableNode):
            return self._render_table(node, result)
        if isinstance(node, ListNode):
            return self._render_list(node, result)
        if isinstance(node, QuoteNode):
            return self._render_quote(node, result)
        if isinstance(node, HorizontalNode):
            return '<hr>\n'
        if isinstance(node, CodeBlockNode):
            return self._render_code_block(node)
        if isinstance(node, FoldingNode):
            return self._render_folding(node, result)
        if isinstance(node, CalloutNode):
            return self._render_callout(node, result)
        if isinstance(node, HtmlBlockNode):
            # 관리자 권한이 없으면 원시 HTML 출력 차단
            if self.allow_raw_html:
                return node.content + '\n'
            return ''
        return ''

    def _render_heading(self, node: HeadingNode, result: RenderResult) -> str:
        anchor = _make_anchor(node.content)
        node.anchor = anchor
        result.toc.append(TocEntry(level=node.level, text=node.content, anchor=anchor))
        inner = self._render_inline_text(node.content, result)
        return f'<h{node.level} id="{escape(anchor)}">{inner}</h{node.level}>\n'

    def _render_paragraph(self, node: ParagraphNode, result: RenderResult) -> str:
        # 줄바꿈은 <br>로 처리 (나무마크 한 줄 개행 원칙)
        lines_html = []
        for line in node.lines:
            lines_html.append(self._render_inline_text(line, result))
        return '<p>' + '<br>\n'.join(lines_html) + '</p>\n'

    def _render_table(self, node: TableNode, result: RenderResult) -> str:
        rows_html: list[str] = []
        for row in node.rows:
            cells_html = ''.join(
                f'<td>{self._render_inline_text(cell, result)}</td>'
                for cell in row
            )
            rows_html.append(f'<tr>{cells_html}</tr>')
        return '<table>\n' + '\n'.join(rows_html) + '\n</table>\n'

    def _render_list(self, node: ListNode, result: RenderResult) -> str:
        return self._render_list_items(node.items, result, depth=1,
                                       ordered=node.ordered)

    def _render_list_items(
        self, items: list[ListItemNode], result: RenderResult,
        depth: int, ordered: bool
    ) -> str:
        tag = 'ol' if ordered else 'ul'
        parts = [f'<{tag}>\n']
        i = 0
        while i < len(items):
            item = items[i]
            if item.depth == depth:
                content_html = self._render_inline_text(item.content, result)
                # 다음 항목이 더 깊으면 중첩 목록 생성
                sub_items = []
                j = i + 1
                while j < len(items) and items[j].depth > depth:
                    sub_items.append(items[j])
                    j += 1
                if sub_items:
                    sub_html = self._render_list_items(
                        sub_items, result, depth + 1, sub_items[0].ordered
                    )
                    parts.append(f'<li>{content_html}\n{sub_html}</li>\n')
                    i = j
                else:
                    parts.append(f'<li>{content_html}</li>\n')
                    i += 1
            else:
                # 깊이가 맞지 않는 항목은 건너뜀
                i += 1
        parts.append(f'</{tag}>\n')
        return ''.join(parts)

    def _render_quote(self, node: QuoteNode, result: RenderResult) -> str:
        inner = '<br>\n'.join(
            self._render_inline_text(line, result) for line in node.lines
        )
        return f'<blockquote>{inner}</blockquote>\n'

    def _render_code_block(self, node: CodeBlockNode) -> str:
        lang_attr = f' class="language-{escape(node.language)}"' if node.language else ''
        return f'<pre><code{lang_attr}>{escape(node.content)}</code></pre>\n'

    def _render_folding(self, node: FoldingNode, result: RenderResult) -> str:
        summary = escape(node.summary) if node.summary else '접기/펼치기'
        inner = ''.join(self._render_block(child, result) for child in node.children)
        return (
            f'<details class="folding">\n'
            f'<summary>{summary}</summary>\n'
            f'{inner}'
            f'</details>\n'
        )

    def _render_callout(self, node: CalloutNode, result: RenderResult) -> str:
        label = _CALLOUT_LABEL.get(node.kind, node.kind)
        inner = ''.join(self._render_block(child, result) for child in node.children)
        return (
            f'<div class="callout callout-{escape(node.kind)}">\n'
            f'<div class="callout-label">{label}</div>\n'
            f'{inner}'
            f'</div>\n'
        )

    def _render_footnotes(self, footnotes: list[str]) -> str:
        items = ''.join(
            f'<li id="fn-{i}">{escape(text)} '
            f'<a href="#fn-ref-{i}">↩</a></li>\n'
            for i, text in enumerate(footnotes, start=1)
        )
        return f'<div class="footnotes"><ol>{items}</ol></div>\n'

    # ── 인라인 노드 렌더링 ──────────────────────────────────────────────────

    def _render_inline_text(self, text: str, result: RenderResult) -> str:
        """텍스트를 인라인 파싱한 뒤 HTML로 변환한다."""
        nodes = parse_inline(text, result.footnotes)
        return ''.join(self._render_inline(node, result) for node in nodes)

    def _render_inline(self, node: BaseNode, result: RenderResult) -> str:
        if isinstance(node, TextNode):
            return escape(node.content)
        if isinstance(node, BoldNode):
            inner = self._render_children(node.children, result)
            return f'<strong>{inner}</strong>'
        if isinstance(node, ItalicNode):
            inner = self._render_children(node.children, result)
            return f'<em>{inner}</em>'
        if isinstance(node, UnderlineNode):
            inner = self._render_children(node.children, result)
            return f'<u>{inner}</u>'
        if isinstance(node, StrikeNode):
            inner = self._render_children(node.children, result)
            return f'<s>{inner}</s>'
        if isinstance(node, SupNode):
            inner = self._render_children(node.children, result)
            return f'<sup>{inner}</sup>'
        if isinstance(node, SubNode):
            inner = self._render_children(node.children, result)
            return f'<sub>{inner}</sub>'
        if isinstance(node, InlineCodeNode):
            return f'<code>{escape(node.content)}</code>'
        if isinstance(node, ColorNode):
            inner = self._render_children(node.children, result)
            return f'<span style="color:{escape(node.color)}">{inner}</span>'
        if isinstance(node, SizeNode):
            rem = _SIZE_MAP.get(node.size, "1.0")
            inner = self._render_children(node.children, result)
            return f'<span style="font-size:{rem}rem">{inner}</span>'
        if isinstance(node, LinkNode):
            return self._render_link(node, result)
        if isinstance(node, ExternalLinkNode):
            label = escape(node.label) if node.label else escape(node.url)
            return (f'<a href="{escape(node.url)}" target="_blank" '
                    f'rel="noopener noreferrer">{label}</a>')
        if isinstance(node, FootnoteNode):
            ref_id = f'fn-ref-{node.index}'
            fn_id = f'fn-{node.index}'
            return (f'<sup id="{ref_id}">'
                    f'<a href="#{fn_id}">[{node.index}]</a></sup>')
        if isinstance(node, MathNode):
            # KaTeX 렌더링은 프론트엔드에서 처리하므로 raw 수식을 data 속성에 보존
            tag = 'div' if node.display else 'span'
            css = 'katex-display' if node.display else 'katex-inline'
            return f'<{tag} class="{css}" data-math="{escape(node.content)}"></{tag}>'
        if isinstance(node, MathNode):
            return f'<span class="katex" data-math="{escape(node.content)}"></span>'
        return ''

    def _render_link(self, node: LinkNode, result: RenderResult) -> str:
        if node.is_category:
            result.categories.append(node.target)
            return ''  # 분류는 HTML에 직접 출력하지 않음
        if node.is_file:
            # 파일 링크는 img 태그로 변환
            alt = escape(node.label or node.target)
            src = f'/files/{escape(node.target)}'
            return f'<img src="{src}" alt="{alt}">'
        # 일반 내부 링크
        href = f'/w/{_slugify(node.target)}'
        label = escape(node.label or node.target)
        result.links.append(node.target)
        return f'<a href="{href}">{label}</a>'

    def _render_children(self, children: list[BaseNode], result: RenderResult) -> str:
        return ''.join(self._render_inline(child, result) for child in children)


# ── 유틸 ───────────────────────────────────────────────────────────────────────

def _make_anchor(text: str) -> str:
    """제목 텍스트를 HTML id 속성에 사용할 수 있는 앵커로 변환한다."""
    # 공백 → 하이픈, 특수문자 제거
    anchor = re.sub(r'\s+', '-', text.strip())
    anchor = re.sub(r'[^\w\-가-힣]', '', anchor)
    return anchor or 'section'


def _slugify(text: str) -> str:
    """내부 링크 URL에 사용할 슬러그를 생성한다."""
    # 공백 → 언더스코어 (나무위키 방식)
    return re.sub(r'\s+', '_', text.strip())
