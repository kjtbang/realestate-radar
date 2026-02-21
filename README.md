# 🏠 부동산 레이더

Claude AI가 **5분마다** 자동으로 한국 부동산 최신 뉴스를 수집해 업데이트하는 사이트입니다.

## ⚙️ 자동화 구조

```
GitHub Actions (5분마다)
  → Claude AI 웹 검색
  → index.html 자동 생성
  → Git 커밋 & 푸시
  → Netlify 자동 배포
```

---

## 🚀 설치 방법 (단계별)

### 1단계 — GitHub 저장소 만들기

1. [github.com](https://github.com) 로그인
2. **New repository** 클릭
3. Repository name: `realestate-radar`
4. Public 선택 → **Create repository**

### 2단계 — 파일 업로드

이 폴더의 모든 파일을 GitHub에 업로드하세요:
```
realestate-radar/
├── .github/
│   └── workflows/
│       └── update-news.yml   ← GitHub Actions 설정
├── scripts/
│   └── generate_news.py      ← 뉴스 생성 스크립트
└── README.md
```

업로드 방법:
- GitHub 저장소 페이지에서 **uploading an existing file** 클릭
- 폴더째로 드래그앤드롭

### 3단계 — Anthropic API 키 등록

1. GitHub 저장소 → **Settings** 탭
2. 왼쪽 메뉴: **Secrets and variables → Actions**
3. **New repository secret** 클릭
4. Name: `ANTHROPIC_API_KEY`
5. Secret: `sk-ant-api03-...` (본인 API 키)
6. **Add secret** 클릭

> API 키 발급: [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)

### 4단계 — 첫 번째 실행 (index.html 생성)

1. GitHub 저장소 → **Actions** 탭
2. 왼쪽: **부동산 뉴스 자동 업데이트** 클릭
3. **Run workflow** 버튼 클릭
4. 1~2분 기다리면 `index.html` 자동 생성됨

### 5단계 — Netlify 연동 (자동 배포)

1. [netlify.com](https://netlify.com) 로그인
2. **Add new site → Import an existing project**
3. **GitHub** 선택
4. `realestate-radar` 저장소 선택
5. Build settings:
   - Build command: (비워두기)
   - Publish directory: `.`
6. **Deploy site** 클릭

이제 GitHub에 커밋될 때마다 Netlify가 자동으로 배포합니다!

---

## ✅ 완성 후 동작

- GitHub Actions가 **5분마다** 자동 실행
- Claude AI가 최신 부동산 뉴스 12개 검색
- `index.html` 새로 생성 후 Git 푸시
- Netlify가 변경 감지 → **자동 배포** (약 30초)
- 방문자는 항상 최신 뉴스를 볼 수 있음

---

## 💰 비용

| 항목 | 비용 |
|------|------|
| GitHub | 무료 |
| Netlify | 무료 |
| Anthropic API | 약 $0.01/회 × 288회/일 ≈ **$2.88/일** |

> API 비용을 줄이려면 `update-news.yml`에서 cron을 `0 * * * *` (매시간)으로 변경하세요.

---

## 🔧 업데이트 주기 변경

`.github/workflows/update-news.yml` 에서 cron 수정:

```yaml
# 5분마다
- cron: '*/5 * * * *'

# 30분마다
- cron: '*/30 * * * *'

# 매시간
- cron: '0 * * * *'

# 매일 오전 9시 (한국시간)
- cron: '0 0 * * *'
```
