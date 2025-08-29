# 🚀 알림톡 템플릿 생성기 v2.0 (리팩토링)

> AI 기반 알림톡 템플릿 자동 생성 시스템

## 📁 프로젝트 구조
```
Jober_java/
├── main.py                    # 🎯 메인 실행 파일 (통합 인터페이스)
├── config.py                  # ⚙️ 설정 파일 
├── requirements.txt           # 📦 의존성 (pip용)
├── pyproject.toml            # 📦 의존성 (poetry용)
├── core/                     # 🧠 핵심 AI 모듈
│   ├── __init__.py           
│   ├── base_processor.py     # 공통 기능 (임베딩, FAISS, Gemini)
│   ├── entity_extractor.py   # 엔티티 추출 전용
│   └── template_generator.py # 템플릿 생성 전용
├── utils/                    # 🛠️ 유틸리티 모듈
│   ├── __init__.py          
│   └── data_processor.py     # 통합 데이터 처리
└── data/                     # 📊 데이터 파일
    ├── alrimtalk.md          # 원본 가이드라인
    ├── cleaned_alrimtalk.md  # 정리된 가이드라인
    ├── message.md            # 원본 메시지 샘플
    └── cleaned_message.md    # 정리된 메시지 샘플
```

## 🚀 설치 및 실행

### Option 1: pip 사용
```bash
pip install -r requirements.txt
```

### Option 2: poetry 사용 (권장)
```bash
poetry install
poetry shell
```

### 환경설정
1. `.env` 파일 생성
```bash
GOOGLE_API_KEY=your_google_api_key_here
```

### 실행
```bash
python main.py
```

## 🎯 주요 기능

### 1. 📝 템플릿 생성
- **엔티티 자동 추출**: 날짜, 이름, 장소, 이벤트 등 자동 인식
- **FAISS 유사도 검색**: 기존 템플릿과 유사도 매칭  
- **AI 템플릿 생성**: Gemini AI로 맞춤형 템플릿 생성
- **가이드라인 반영**: 알림톡 규정 준수 템플릿 생성

### 2. 🔧 데이터 처리 도구
- **마크다운 정리**: HTML 이미지 태그 자동 제거
- **파일 통합 처리**: 여러 파일 일괄 처리
- **자동 백업**: `cleaned_` 접두사로 정리된 파일 저장

### 3. 📊 시스템 모니터링
- **실시간 상태 확인**: 로드된 데이터 현황
- **파일 무결성 체크**: 데이터 파일 존재 여부 확인
- **성능 정보**: AI 모델 및 검색 엔진 상태

## 🔧 리팩토링 개선사항

### ✅ **중복 제거 (70% → 0%)**
- **제거된 파일**: `htmlloader.py`, `txtloader.py`, `deleteImg.py`, `markdownV0.ipynb`
- **통합 모듈**: `utils/data_processor.py`로 모든 데이터 처리 기능 통합

### ✅ **모듈화 구조**
- **core/**: AI 핵심 기능 분리
- **utils/**: 유틸리티 기능 분리
- **명확한 책임 분리**: 각 모듈이 단일 책임 수행

### ✅ **사용성 개선**
- **통합 인터페이스**: 메뉴 기반 직관적 조작
- **오류 처리 강화**: 파일 없음, API 오류 등 예외상황 대응
- **자동 복구**: 누락된 파일 자동 생성

## 📖 사용 예시

### 템플릿 생성
```
입력: "2025.8.26 david 어머님, 어린이집에서 바자회가 열립니다"

출력:
[바자회 개최 안내]

david님, 안녕하세요.
어린이집에서 바자회 개최를 안내드립니다.

▶ 행사 정보
- 행사명: 바자회  
- 개최일시: 2025.8.26
- 장소: 어린이집

▶ 프로그램 안내
- 운영시간: #{운영시간}
- 주요 프로그램: #{프로그램내용}

[참가 안내사항]  
- 준비물: #{준비물}
- 주차: #{주차안내}

※ 본 메시지는 어린이집 행사 참가자에게 발송되는 안내 메시지입니다.
```

## 🛠️ 기술 스택
- **AI**: Google Gemini, SentenceTransformers
- **검색**: FAISS (벡터 유사도 검색)
- **문서처리**: LangChain
- **의존성관리**: Poetry + pip

## 📋 TODO
- [ ] BLACK/WHITE LIST 시스템 추가
- [ ] 다국어 지원
- [ ] 웹 인터페이스 개발
- [ ] 배치 처리 기능
