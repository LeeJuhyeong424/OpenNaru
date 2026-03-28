# 배포 가이드

## 배포 전 필수 체크리스트

- [ ] `.env` 에서 `APP_SECRET_KEY` 를 강력한 랜덤 값으로 변경
- [ ] `APP_ENV=production` 설정
- [ ] `APP_DEBUG=false` 설정 (Swagger UI 비활성화)
- [ ] `DATABASE_URL` 을 프로덕션 DB로 변경
- [ ] `CORS_ORIGINS` 를 실제 도메인으로 제한
- [ ] HTTPS (TLS) 설정 완료
- [ ] DB 백업 정책 수립

## 방식 A — Docker Compose (단일 서버 / VPS)

### 최소 서버 사양

| 항목 | 최소 | 권장 |
|------|------|------|
| CPU | 2 vCPU | 4 vCPU |
| RAM | 4 GB | 8 GB |
| 디스크 | 20 GB SSD | 50 GB SSD |
| OS | Ubuntu 22.04 LTS | Ubuntu 24.04 LTS |

### 배포 절차

```bash
# 1. 서버에 저장소 클론
git clone https://github.com/LeeJuhyeong424/OpenNaru.git
cd OpenNaru

# 2. 환경변수 설정
cp .env.example .env
# .env 편집 — 프로덕션 값으로 변경

# 3. 실행
docker compose -f docker-compose.yml up -d

# 4. DB 마이그레이션
docker compose exec backend alembic upgrade head
```

### 무중단 업데이트

```bash
git pull origin main
docker compose pull
docker compose up -d --no-deps backend frontend
docker compose exec backend alembic upgrade head
```

### 롤백

```bash
# 이전 이미지로 롤백
docker compose up -d --no-deps backend=ghcr.io/leejuhyeong424/opennaru-backend:<이전 태그>
# DB 롤백 (필요시)
docker compose exec backend alembic downgrade -1
```

## 방식 B — Kubernetes (대규모 / 클라우드)

Kubernetes 배포는 `infra/k8s/` 디렉토리의 매니페스트를 참조하세요.

### 구성 요소

| 리소스 | 설명 |
|--------|------|
| `Deployment` | backend, frontend |
| `Service` | ClusterIP (내부), LoadBalancer (외부) |
| `Ingress` | HTTPS 종단, 경로 라우팅 |
| `HorizontalPodAutoscaler` | CPU 기반 자동 스케일링 |
| `PersistentVolumeClaim` | 업로드 파일 스토리지 |
| `Secret` | 환경변수 (base64 인코딩) |
| `ConfigMap` | 비민감 설정값 |

## DB 백업 전략

```bash
# PostgreSQL 덤프 (매일 cron)
docker compose exec db pg_dump -U opennaru opennaru | gzip > backup_$(date +%Y%m%d).sql.gz

# S3 업로드 예시
aws s3 cp backup_$(date +%Y%m%d).sql.gz s3://your-bucket/opennaru-backups/
```

- 최근 7일치 백업 로컬 보관
- 월별 백업은 오브젝트 스토리지(S3 등)에 90일 보관

## 모니터링

| 도구 | 용도 |
|------|------|
| Prometheus + Grafana | 메트릭 수집 및 대시보드 |
| Sentry | 에러 트래킹 |
| Uptime Robot | 외부 가용성 모니터링 |

FastAPI는 `/metrics` 엔드포인트(Prometheus 포맷)를 제공합니다 (별도 설정 필요).

## 배포 후 확인 절차

```bash
# 헬스 체크
curl https://your-domain.com/health

# 응답 예시
{"status": "ok", "env": "production"}

# 로그 확인
docker compose logs backend --tail=50
docker compose logs frontend --tail=50
```
