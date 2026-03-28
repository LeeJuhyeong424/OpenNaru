"""나무마크 파서 오케스트레이터 — 4단계 파이프라인을 순서대로 실행한다.

파이프라인:
  입력 텍스트 → [토크나이저] → [블록 파서] → [인라인 파서] → [렌더러] → RenderResult
"""

from .block_parser import parse_blocks
from .nodes import RenderResult
from .renderer import HtmlRenderer
from .tokenizer import tokenize


def parse(text: str, allow_raw_html: bool = False) -> RenderResult:
    """
    나무마크 텍스트를 HTML로 변환한다.

    Args:
        text: 나무마크 원문
        allow_raw_html: True이면 {{{#!html}}} 원시 HTML 허용 (관리자 전용)

    Returns:
        RenderResult (html, toc, categories, links, footnotes, redirect_to)
    """
    tokens = tokenize(text)
    blocks = parse_blocks(tokens)
    renderer = HtmlRenderer(allow_raw_html=allow_raw_html)
    return renderer.render(blocks)
