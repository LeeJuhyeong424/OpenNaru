"""나무마크 파서 테스트"""

from app.parser import parse

# ── 제목 ──────────────────────────────────────────────────────────────────────

def test_heading_h1():
    result = parse("= 제목 =")
    assert "<h1" in result.html
    assert "제목" in result.html

def test_heading_levels():
    result = parse("== 2단계 ==\n=== 3단계 ===")
    assert "<h2" in result.html
    assert "<h3" in result.html

def test_heading_toc():
    result = parse("== 소개 ==\n=== 배경 ===")
    assert len(result.toc) == 2
    assert result.toc[0].level == 2
    assert result.toc[0].text == "소개"
    assert result.toc[1].level == 3


# ── 인라인 문법 ───────────────────────────────────────────────────────────────

def test_bold():
    result = parse("'''굵은 글씨'''")
    assert "<strong>굵은 글씨</strong>" in result.html

def test_italic():
    result = parse("''기울임''")
    assert "<em>기울임</em>" in result.html

def test_underline():
    result = parse("__밑줄__")
    assert "<u>밑줄</u>" in result.html

def test_strikethrough():
    result = parse("~~취소선~~")
    assert "<s>취소선</s>" in result.html

def test_sup():
    result = parse("^^위첨자^^")
    assert "<sup>위첨자</sup>" in result.html

def test_sub():
    result = parse(",,아래첨자,,")
    assert "<sub>아래첨자</sub>" in result.html

def test_inline_code():
    result = parse("`코드`")
    assert "<code>코드</code>" in result.html

def test_color():
    result = parse("{{{#FF0000 빨강}}}")
    assert 'color:#FF0000' in result.html
    assert '빨강' in result.html

def test_size_up():
    result = parse("{{{+2 큰 글씨}}}")
    assert 'font-size:1.25rem' in result.html

def test_size_down():
    result = parse("{{{-1 작은 글씨}}}")
    assert 'font-size:0.9rem' in result.html


# ── 링크 ──────────────────────────────────────────────────────────────────────

def test_internal_link():
    result = parse("[[나무위키]]")
    assert 'href="/w/나무위키"' in result.html
    assert "나무위키" in result.html

def test_internal_link_with_label():
    result = parse("[[나무위키|클릭하세요]]")
    assert "클릭하세요" in result.html

def test_category_link():
    result = parse("[[분류:게임]]")
    assert "게임" in result.categories
    assert "게임" not in result.html  # 분류는 HTML에 출력 안 함

def test_internal_links_collected():
    result = parse("[[문서A]] [[문서B]]")
    assert "문서A" in result.links
    assert "문서B" in result.links

def test_external_link():
    result = parse("[https://example.com 예시]")
    assert 'href="https://example.com"' in result.html
    assert "예시" in result.html

def test_external_link_dangerous_scheme():
    # javascript: 는 외부 링크 패턴(https?://)에 매칭되지 않아 텍스트로 출력됨
    # → href 속성 자체가 생성되지 않으므로 실행 불가능 (안전)
    result = parse("[javascript:alert(1) 클릭]")
    assert 'href="javascript:' not in result.html


# ── 각주 ──────────────────────────────────────────────────────────────────────

def test_footnote():
    result = parse("[* 이것은 각주입니다]")
    assert "각주" in result.html
    assert len(result.footnotes) == 1

def test_multiple_footnotes():
    result = parse("[* 첫 번째]\n[* 두 번째]")
    assert len(result.footnotes) == 2


# ── 표 ────────────────────────────────────────────────────────────────────────

def test_table():
    result = parse("|| 이름 || 나이 ||\n|| 홍길동 || 30 ||")
    assert "<table>" in result.html
    assert "<td>" in result.html
    assert "홍길동" in result.html

def test_table_xss():
    result = parse("|| <script>alert(1)</script> ||")
    assert "<script>" not in result.html


# ── 리스트 ────────────────────────────────────────────────────────────────────

def test_unordered_list():
    result = parse("* 항목1\n* 항목2")
    assert "<ul>" in result.html
    assert "<li>" in result.html
    assert "항목1" in result.html

def test_ordered_list():
    result = parse("# 첫째\n# 둘째")
    assert "<ol>" in result.html

def test_nested_list():
    result = parse("* 1단계\n** 2단계")
    assert result.html.count("<ul>") >= 2


# ── 코드블록 ──────────────────────────────────────────────────────────────────

def test_code_block():
    result = parse("```python\nprint('hello')\n```")
    assert "<pre>" in result.html
    assert "language-python" in result.html
    assert "print" in result.html

def test_code_block_xss():
    result = parse("```\n<script>alert(1)</script>\n```")
    assert "<script>" not in result.html
    assert "&lt;script&gt;" in result.html


# ── 블록 구문 ─────────────────────────────────────────────────────────────────

def test_folding():
    result = parse("{{{#!folding [접기]\n내용\n}}}")
    assert "<details" in result.html
    assert "<summary>" in result.html
    assert "내용" in result.html

def test_callout_note():
    result = parse("{{{#!note\n이것은 노트입니다\n}}}")
    assert 'callout-note' in result.html
    assert "노트" in result.html

def test_callout_warning():
    result = parse("{{{#!warning\n주의하세요\n}}}")
    assert 'callout-warning' in result.html

def test_html_block_blocked_by_default():
    result = parse("{{{#!html\n<b>원시 HTML</b>\n}}}")
    assert "<b>원시 HTML</b>" not in result.html

def test_html_block_allowed_for_admin():
    result = parse("{{{#!html\n<b>원시 HTML</b>\n}}}", allow_raw_html=True)
    assert "<b>원시 HTML</b>" in result.html

def test_quote():
    result = parse("> 인용문 내용")
    assert "<blockquote>" in result.html
    assert "인용문 내용" in result.html


# ── 수평선 ────────────────────────────────────────────────────────────────────

def test_horizontal():
    result = parse("----")
    assert "<hr>" in result.html


# ── 넘겨주기 ──────────────────────────────────────────────────────────────────

def test_redirect():
    result = parse("#넘겨주기 [[목적지 문서]]")
    assert result.redirect_to == "목적지 문서"
    assert result.html == ""


# ── XSS 방어 ──────────────────────────────────────────────────────────────────

def test_xss_in_paragraph():
    result = parse("<script>alert('xss')</script>")
    assert "<script>" not in result.html
    assert "&lt;script&gt;" in result.html

def test_xss_in_bold():
    # HTML 이스케이프 처리되어 &lt;img onerror=...&gt; 로 출력됨 (실행 불가능)
    result = parse("'''<img onerror=alert(1)>'''")
    assert "<img" not in result.html          # 실제 img 태그로 파싱되면 안 됨
    assert "&lt;img" in result.html           # 이스케이프된 텍스트로 출력되어야 함

def test_xss_in_link_label():
    result = parse("[[문서|<script>xss</script>]]")
    assert "<script>" not in result.html


# ── 수식 ──────────────────────────────────────────────────────────────────────

def test_math_inline():
    result = parse("$E=mc^2$")
    assert "katex" in result.html
    assert "E=mc^2" in result.html


# ── 복합 문법 ─────────────────────────────────────────────────────────────────

def test_bold_with_link():
    result = parse("'''[[링크]]'''")
    assert "<strong>" in result.html
    assert 'href="/w/링크"' in result.html

def test_complex_document():
    doc = """= 게임 공략 =

'''굵은 글씨'''와 [[다른 문서]] 링크

[* 이것은 각주입니다]

[[분류:게임]]
"""
    result = parse(doc)
    assert "<h1" in result.html
    assert "<strong>" in result.html
    assert "게임" in result.categories
    assert len(result.footnotes) == 1
    assert len(result.toc) == 1
