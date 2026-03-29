"""위키 API 통합 테스트 — /api/v1/wikis 엔드포인트"""


# --- 공통 헬퍼 ---

def create_wiki_payload(
    slug: str = "test-wiki",
    name: str = "테스트 위키",
    **kwargs,
) -> dict:
    """위키 생성 요청 페이로드 생성 헬퍼"""
    payload = {"slug": slug, "name": name}
    payload.update(kwargs)
    return payload


# --- 테스트 케이스 ---

class TestCreateWiki:
    """POST /api/v1/wikis — 위키 생성"""

    def test_create_wiki(self, client):
        """정상 생성 시 201 반환, uuid 노출 및 내부 id 미노출 확인"""
        payload = create_wiki_payload(slug="my-wiki", name="내 위키")
        resp = client.post("/api/v1/wikis", json=payload)

        assert resp.status_code == 201
        body = resp.json()

        # uuid 필드가 있어야 함
        assert "id" in body
        # id 값이 UUID 형식인지 확인 (하이픈 포함 36자)
        assert len(body["id"]) == 36
        assert "-" in body["id"]

        # 내부 정수 id가 노출되면 안 됨
        # (응답 JSON에 정수 타입 id가 없는지 확인)
        assert isinstance(body["id"], str)

        # 필수 필드 확인
        assert body["slug"] == "my-wiki"
        assert body["name"] == "내 위키"
        assert "created_at" in body
        assert "updated_at" in body

    def test_create_wiki_with_description(self, client):
        """설명 포함 생성 정상 동작"""
        payload = create_wiki_payload(
            slug="wiki-with-desc",
            name="설명 있는 위키",
            description="이 위키는 설명이 있습니다.",
        )
        resp = client.post("/api/v1/wikis", json=payload)

        assert resp.status_code == 201
        body = resp.json()
        assert body["description"] == "이 위키는 설명이 있습니다."

    def test_create_wiki_duplicate_slug(self, client):
        """중복 slug로 생성 시 409 반환"""
        payload = create_wiki_payload(slug="dup-wiki")
        # 첫 번째 생성
        resp1 = client.post("/api/v1/wikis", json=payload)
        assert resp1.status_code == 201

        # 동일 slug로 두 번째 생성 시도
        resp2 = client.post("/api/v1/wikis", json=payload)
        assert resp2.status_code == 409

        body = resp2.json()
        # 오류 코드 확인 (detail 내부에 code 필드)
        assert body["detail"]["code"] == "WIKI_SLUG_CONFLICT"

    def test_create_wiki_invalid_slug(self, client):
        """유효하지 않은 slug (대문자 포함) 시 422 반환"""
        payload = create_wiki_payload(slug="Invalid-Slug")
        resp = client.post("/api/v1/wikis", json=payload)
        assert resp.status_code == 422

    def test_create_wiki_slug_too_long(self, client):
        """slug 길이 초과 시 422 반환"""
        long_slug = "a" * 101
        payload = create_wiki_payload(slug=long_slug)
        resp = client.post("/api/v1/wikis", json=payload)
        assert resp.status_code == 422


class TestListWikis:
    """GET /api/v1/wikis — 위키 목록 조회"""

    def test_list_wikis_empty(self, client):
        """위키가 없는 경우 빈 목록 반환"""
        resp = client.get("/api/v1/wikis")
        assert resp.status_code == 200
        body = resp.json()
        assert body["items"] == []
        assert body["total"] == 0

    def test_list_wikis(self, client):
        """생성된 위키 목록 정상 반환"""
        # 위키 2개 생성
        client.post("/api/v1/wikis", json=create_wiki_payload(slug="wiki-a", name="위키 A"))
        client.post("/api/v1/wikis", json=create_wiki_payload(slug="wiki-b", name="위키 B"))

        resp = client.get("/api/v1/wikis")
        assert resp.status_code == 200
        body = resp.json()

        assert body["total"] == 2
        assert len(body["items"]) == 2
        assert body["skip"] == 0
        assert body["limit"] == 20

    def test_list_wikis_pagination(self, client):
        """페이지네이션 skip/limit 파라미터 동작 확인"""
        # 위키 3개 생성
        for i in range(3):
            client.post(
                "/api/v1/wikis",
                json=create_wiki_payload(slug=f"wiki-{i}", name=f"위키 {i}"),
            )

        # limit=1로 조회
        resp = client.get("/api/v1/wikis?limit=1")
        body = resp.json()
        assert body["total"] == 3
        assert len(body["items"]) == 1

        # skip=2로 조회
        resp2 = client.get("/api/v1/wikis?skip=2&limit=10")
        body2 = resp2.json()
        assert body2["total"] == 3
        assert len(body2["items"]) == 1


class TestGetWiki:
    """GET /api/v1/wikis/{slug} — 위키 단건 조회"""

    def test_get_wiki(self, client):
        """정상 조회 시 200 반환"""
        client.post("/api/v1/wikis", json=create_wiki_payload(slug="get-test"))
        resp = client.get("/api/v1/wikis/get-test")

        assert resp.status_code == 200
        body = resp.json()
        assert body["slug"] == "get-test"

    def test_get_wiki_not_found(self, client):
        """존재하지 않는 slug 조회 시 404 반환"""
        resp = client.get("/api/v1/wikis/nonexistent-wiki")
        assert resp.status_code == 404

        body = resp.json()
        assert body["detail"]["code"] == "WIKI_NOT_FOUND"


class TestUpdateWiki:
    """PATCH /api/v1/wikis/{slug} — 위키 수정"""

    def test_update_wiki(self, client):
        """name 변경 정상 반영 확인"""
        client.post("/api/v1/wikis", json=create_wiki_payload(slug="update-test", name="원래 이름"))

        resp = client.patch("/api/v1/wikis/update-test", json={"name": "바뀐 이름"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["name"] == "바뀐 이름"
        # slug는 변경 불가 (WikiUpdate에 없음), 그대로 유지
        assert body["slug"] == "update-test"

    def test_update_wiki_partial(self, client):
        """일부 필드만 수정해도 나머지는 유지됨"""
        client.post(
            "/api/v1/wikis",
            json=create_wiki_payload(
                slug="partial-update",
                name="원래",
                description="원래 설명",
                is_public=True,
            ),
        )

        # is_public만 변경
        resp = client.patch("/api/v1/wikis/partial-update", json={"is_public": False})
        assert resp.status_code == 200
        body = resp.json()
        assert body["is_public"] is False
        assert body["name"] == "원래"
        assert body["description"] == "원래 설명"

    def test_update_wiki_not_found(self, client):
        """존재하지 않는 위키 수정 시 404 반환"""
        resp = client.patch("/api/v1/wikis/ghost-wiki", json={"name": "새 이름"})
        assert resp.status_code == 404


class TestDeleteWiki:
    """DELETE /api/v1/wikis/{slug} — 위키 소프트 삭제"""

    def test_delete_wiki(self, client):
        """소프트 삭제 후 204 반환, 이후 조회 시 404 확인"""
        client.post("/api/v1/wikis", json=create_wiki_payload(slug="delete-test"))

        # 삭제 전 조회 성공
        assert client.get("/api/v1/wikis/delete-test").status_code == 200

        # 삭제
        resp = client.delete("/api/v1/wikis/delete-test")
        assert resp.status_code == 204

        # 삭제 후 조회 시 404
        assert client.get("/api/v1/wikis/delete-test").status_code == 404

    def test_delete_wiki_not_found(self, client):
        """존재하지 않는 위키 삭제 시 404 반환"""
        resp = client.delete("/api/v1/wikis/ghost-wiki")
        assert resp.status_code == 404

    def test_delete_wiki_excluded_from_list(self, client):
        """소프트 삭제된 위키는 목록에서 제외됨"""
        client.post("/api/v1/wikis", json=create_wiki_payload(slug="listed-wiki"))
        client.post("/api/v1/wikis", json=create_wiki_payload(slug="to-delete"))

        # 삭제 전 총 2개
        before = client.get("/api/v1/wikis").json()
        assert before["total"] == 2

        # 하나 삭제 후 총 1개
        client.delete("/api/v1/wikis/to-delete")
        after = client.get("/api/v1/wikis").json()
        assert after["total"] == 1
        assert after["items"][0]["slug"] == "listed-wiki"
