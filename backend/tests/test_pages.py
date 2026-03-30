"""문서 API 통합 테스트 — /api/v1/wikis/{slug}/pages 엔드포인트"""


# --- 공통 헬퍼 ---

def setup_wiki(client, slug: str = "test-wiki", name: str = "테스트 위키") -> dict:
    """테스트용 위키 생성 후 응답 반환"""
    resp = client.post("/api/v1/wikis", json={"slug": slug, "name": name})
    assert resp.status_code == 201
    return resp.json()


def create_page_payload(
    slug: str = "hello-world",
    title: str = "Hello World",
    content: str = "'''안녕하세요''' 위키입니다.",
    namespace: str = "main",
) -> dict:
    """문서 생성 요청 페이로드 헬퍼"""
    return {"namespace": namespace, "slug": slug, "title": title, "content": content, "comment": ""}


# --- 테스트 케이스 ---

class TestCreatePage:
    """POST /api/v1/wikis/{slug}/pages — 문서 생성"""

    def test_create_page(self, client):
        """정상 생성 시 201 반환, uuid 형식 확인"""
        setup_wiki(client, slug="mywiki")
        payload = create_page_payload(slug="first-page", title="첫 번째 문서")
        resp = client.post("/api/v1/wikis/mywiki/pages", json=payload)

        assert resp.status_code == 201
        body = resp.json()

        # uuid 필드 형식 확인
        assert "id" in body
        assert len(body["id"]) == 36
        assert isinstance(body["id"], str)

        # 필수 필드 확인
        assert body["namespace"] == "main"
        assert body["slug"] == "first-page"
        assert body["title"] == "첫 번째 문서"
        assert body["wiki_slug"] == "mywiki"
        assert body["is_redirect"] is False

    def test_create_page_wiki_not_found(self, client):
        """존재하지 않는 위키에 문서 생성 시 404 반환"""
        payload = create_page_payload()
        resp = client.post("/api/v1/wikis/nonexistent/pages", json=payload)
        assert resp.status_code == 404
        assert resp.json()["detail"]["code"] == "WIKI_NOT_FOUND"

    def test_create_page_duplicate(self, client):
        """동일 위키/네임스페이스/slug 문서 중복 생성 시 409 반환"""
        setup_wiki(client, slug="dup-wiki")
        payload = create_page_payload(slug="dup-page")

        resp1 = client.post("/api/v1/wikis/dup-wiki/pages", json=payload)
        assert resp1.status_code == 201

        resp2 = client.post("/api/v1/wikis/dup-wiki/pages", json=payload)
        assert resp2.status_code == 409
        assert resp2.json()["detail"]["code"] == "PAGE_ALREADY_EXISTS"

    def test_create_page_different_namespace(self, client):
        """같은 slug라도 네임스페이스가 다르면 별개 문서로 생성"""
        setup_wiki(client, slug="ns-wiki")
        payload_main = create_page_payload(slug="shared-slug", namespace="main")
        payload_talk = create_page_payload(slug="shared-slug", namespace="talk")

        resp1 = client.post("/api/v1/wikis/ns-wiki/pages", json=payload_main)
        resp2 = client.post("/api/v1/wikis/ns-wiki/pages", json=payload_talk)

        assert resp1.status_code == 201
        assert resp2.status_code == 201
        # 두 문서의 uuid가 달라야 함
        assert resp1.json()["id"] != resp2.json()["id"]


class TestGetPage:
    """GET /api/v1/wikis/{slug}/pages/{namespace}/{page_slug} — 문서 조회"""

    def test_get_page(self, client):
        """정상 조회 시 200 반환, content_html 포함 확인"""
        setup_wiki(client, slug="view-wiki")
        client.post(
            "/api/v1/wikis/view-wiki/pages",
            json=create_page_payload(
                slug="test-doc",
                content="'''굵은 글씨''' 테스트",
            ),
        )

        resp = client.get("/api/v1/wikis/view-wiki/pages/main/test-doc")
        assert resp.status_code == 200
        body = resp.json()

        # content_html은 파서가 렌더링한 HTML을 담고 있어야 함
        assert body["content_html"] is not None
        assert "<strong>" in body["content_html"] or "strong" in body["content_html"]

        # 기본 필드 확인
        assert body["slug"] == "test-doc"
        assert body["namespace"] == "main"
        # latest_revision_id는 정수여야 함
        assert body["latest_revision_id"] is not None
        assert isinstance(body["latest_revision_id"], int)

    def test_get_page_not_found(self, client):
        """존재하지 않는 문서 조회 시 404 + exists/can_create 필드 반환"""
        setup_wiki(client, slug="nf-wiki")

        resp = client.get("/api/v1/wikis/nf-wiki/pages/main/no-such-page")
        assert resp.status_code == 404
        body = resp.json()

        # 설계 스펙: 없는 문서 조회 시 exists=false, can_create=true 반환
        detail = body["detail"]
        assert detail["exists"] is False
        assert detail["can_create"] is True
        assert detail["code"] == "PAGE_NOT_FOUND"

    def test_get_page_wiki_not_found(self, client):
        """존재하지 않는 위키의 문서 조회 시 404 반환"""
        resp = client.get("/api/v1/wikis/ghost-wiki/pages/main/some-page")
        assert resp.status_code == 404
        assert resp.json()["detail"]["code"] == "WIKI_NOT_FOUND"


class TestUpdatePage:
    """PATCH /api/v1/wikis/{slug}/pages/{namespace}/{page_slug} — 문서 편집"""

    def test_update_page(self, client):
        """편집 시 새 revision 생성, latest_revision_id 변경 확인"""
        setup_wiki(client, slug="edit-wiki")
        client.post(
            "/api/v1/wikis/edit-wiki/pages",
            json=create_page_payload(slug="edit-doc", content="원본 내용"),
        )

        # 초기 latest_revision_id 확인
        get_resp = client.get("/api/v1/wikis/edit-wiki/pages/main/edit-doc")
        first_rev_id = get_resp.json()["latest_revision_id"]
        assert first_rev_id is not None

        # 편집
        edit_resp = client.patch(
            "/api/v1/wikis/edit-wiki/pages/main/edit-doc",
            json={"content": "수정된 내용", "comment": "첫 번째 편집"},
        )
        assert edit_resp.status_code == 200
        body = edit_resp.json()

        # latest_revision_id가 증가했는지 확인
        assert body["latest_revision_id"] > first_rev_id

    def test_update_page_title(self, client):
        """title 변경 시 문서 제목 업데이트 확인"""
        setup_wiki(client, slug="title-wiki")
        client.post(
            "/api/v1/wikis/title-wiki/pages",
            json=create_page_payload(slug="title-doc", title="원래 제목"),
        )

        resp = client.patch(
            "/api/v1/wikis/title-wiki/pages/main/title-doc",
            json={"content": "수정 내용", "title": "바뀐 제목"},
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "바뀐 제목"

    def test_update_page_multiple_revisions(self, client):
        """여러 번 편집 시 latest_revision_id가 매번 증가"""
        setup_wiki(client, slug="multi-wiki")
        client.post(
            "/api/v1/wikis/multi-wiki/pages",
            json=create_page_payload(slug="multi-doc"),
        )

        prev_rev_id = 0
        for i in range(2, 5):
            resp = client.patch(
                "/api/v1/wikis/multi-wiki/pages/main/multi-doc",
                json={"content": f"편집 {i}", "comment": f"{i}번째 편집"},
            )
            assert resp.status_code == 200
            new_rev_id = resp.json()["latest_revision_id"]
            assert new_rev_id > prev_rev_id
            prev_rev_id = new_rev_id

    def test_update_page_not_found(self, client):
        """존재하지 않는 문서 편집 시 404 반환"""
        setup_wiki(client, slug="missing-wiki")
        resp = client.patch(
            "/api/v1/wikis/missing-wiki/pages/main/ghost-doc",
            json={"content": "내용"},
        )
        assert resp.status_code == 404
        assert resp.json()["detail"]["code"] == "PAGE_NOT_FOUND"


class TestListRevisions:
    """GET /api/v1/wikis/{slug}/pages/{ns}/{slug}/revisions — 편집 이력 목록"""

    def test_list_revisions(self, client):
        """편집 이력 목록 정상 반환"""
        setup_wiki(client, slug="rev-wiki")
        client.post(
            "/api/v1/wikis/rev-wiki/pages",
            json=create_page_payload(slug="rev-doc", content="초기 내용"),
        )
        # 2번 편집
        client.patch(
            "/api/v1/wikis/rev-wiki/pages/main/rev-doc",
            json={"content": "두 번째 편집", "comment": "2차"},
        )
        client.patch(
            "/api/v1/wikis/rev-wiki/pages/main/rev-doc",
            json={"content": "세 번째 편집", "comment": "3차"},
        )

        resp = client.get("/api/v1/wikis/rev-wiki/pages/main/rev-doc/revisions")
        assert resp.status_code == 200
        body = resp.json()

        # 총 3개 이력 (최신 순)
        assert body["total"] == 3
        assert len(body["items"]) == 3

        # 최신 순 정렬 확인 (id 내림차순)
        rev_ids = [item["id"] for item in body["items"]]
        assert rev_ids == sorted(rev_ids, reverse=True)

    def test_list_revisions_pagination(self, client):
        """편집 이력 페이지네이션 동작 확인"""
        setup_wiki(client, slug="page-rev-wiki")
        client.post(
            "/api/v1/wikis/page-rev-wiki/pages",
            json=create_page_payload(slug="page-doc"),
        )
        # 4번 추가 편집 (총 5개 이력)
        for i in range(2, 6):
            client.patch(
                "/api/v1/wikis/page-rev-wiki/pages/main/page-doc",
                json={"content": f"편집 {i}"},
            )

        resp = client.get(
            "/api/v1/wikis/page-rev-wiki/pages/main/page-doc/revisions?limit=2"
        )
        body = resp.json()
        assert body["total"] == 5
        assert len(body["items"]) == 2


class TestGetSpecificRevision:
    """GET /api/v1/wikis/{slug}/pages/{ns}/{slug}/revisions/{rev_id} — 특정 revision 조회"""

    def test_get_specific_revision(self, client):
        """특정 revision ID의 원본 내용 정상 확인"""
        setup_wiki(client, slug="spec-rev-wiki")
        create_resp = client.post(
            "/api/v1/wikis/spec-rev-wiki/pages",
            json=create_page_payload(slug="spec-doc", content="첫 번째 내용"),
        )
        first_rev_id = create_resp.json()["latest_revision_id"]

        edit_resp = client.patch(
            "/api/v1/wikis/spec-rev-wiki/pages/main/spec-doc",
            json={"content": "두 번째 내용", "comment": "2차 편집"},
        )
        second_rev_id = edit_resp.json()["latest_revision_id"]

        # 첫 번째 revision 조회
        resp1 = client.get(
            f"/api/v1/wikis/spec-rev-wiki/pages/main/spec-doc/revisions/{first_rev_id}"
        )
        assert resp1.status_code == 200
        body1 = resp1.json()
        assert body1["id"] == first_rev_id
        assert body1["content"] == "첫 번째 내용"

        # 두 번째 revision 조회
        resp2 = client.get(
            f"/api/v1/wikis/spec-rev-wiki/pages/main/spec-doc/revisions/{second_rev_id}"
        )
        assert resp2.status_code == 200
        body2 = resp2.json()
        assert body2["id"] == second_rev_id
        assert body2["content"] == "두 번째 내용"
        assert body2["comment"] == "2차 편집"

    def test_get_specific_revision_not_found(self, client):
        """존재하지 않는 revision ID 조회 시 404 반환"""
        setup_wiki(client, slug="no-rev-wiki")
        client.post(
            "/api/v1/wikis/no-rev-wiki/pages",
            json=create_page_payload(slug="no-rev-doc"),
        )

        resp = client.get(
            "/api/v1/wikis/no-rev-wiki/pages/main/no-rev-doc/revisions/999999"
        )
        assert resp.status_code == 404
        assert resp.json()["detail"]["code"] == "REVISION_NOT_FOUND"

    def test_get_revision_fields(self, client):
        """revision 응답 필드 구조 확인"""
        setup_wiki(client, slug="fields-wiki")
        create_resp = client.post(
            "/api/v1/wikis/fields-wiki/pages",
            json={**create_page_payload(slug="fields-doc", content="내용"), "comment": "최초 작성"},
        )
        rev_id = create_resp.json()["latest_revision_id"]

        resp = client.get(
            f"/api/v1/wikis/fields-wiki/pages/main/fields-doc/revisions/{rev_id}"
        )
        assert resp.status_code == 200
        body = resp.json()

        # 필수 필드 존재 확인
        assert "id" in body
        assert "content" in body
        assert "comment" in body
        assert "editor_username" in body
        assert "editor_ip" in body
        assert "is_suppressed" in body
        assert "byte_size" in body
        assert "byte_diff" in body
        assert "created_at" in body

        # 인증 미구현 단계 — editor_username은 None
        assert body["editor_username"] is None
        assert body["is_suppressed"] is False
        assert body["comment"] == "최초 작성"
