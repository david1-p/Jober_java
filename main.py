import json
import re
from pathlib import Path
from typing import Dict

from config import GEMINI_API_KEY
from core import EntityExtractor, TemplateGenerator
from utils import DataProcessor


class TemplateSystem:

    def __init__(self):
        self.entity_extractor = EntityExtractor(GEMINI_API_KEY)
        self.template_generator = TemplateGenerator(GEMINI_API_KEY)
        self.data_processor = DataProcessor()

        self.templates = self._load_sample_templates()
        self.guidelines = self._load_guidelines()

        self._build_indexes()

    def _load_sample_templates(self) -> list:
        """샘플 템플릿 로드"""
        return [
            "[가격 변경 안내]\n\n안녕하세요, #{수신자명}님.\n#{서비스명} 서비스 가격 변경을 안내드립니다.\n\n▶ 변경 적용일: #{적용일}\n▶ 기존 가격: #{기존가격}원\n▶ 변경 가격: #{변경가격}원\n\n[변경 사유 및 개선사항]\n#{변경사유}에 따라 서비스 품질 개선을 위해 가격을 조정합니다.\n주요 개선사항: #{개선사항}\n\n[기존 이용자 안내]\n- 현재 이용 중인 서비스: #{유예기간}까지 기존 가격 적용\n- 자동 연장 서비스: 변경된 가격으로 갱신\n- 서비스 해지 희망: #{해지마감일}까지 신청 가능\n\n[문의 및 지원]\n- 고객센터: #{고객센터번호}\n- 상담시간: 평일 09:00-18:00\n- 온라인 문의: #{문의링크}\n\n※ 본 메시지는 정보통신망법에 따라 서비스 약관 변경 안내를 위해 발송된 정보성 메시지입니다.",
            "[#{매장명} 방문 예약 확인]\n\n#{고객명}님, 안녕하세요.\n#{매장명} 방문 예약이 완료되었습니다.\n\n▶ 예약 정보\n- 예약번호: #{예약번호}\n- 방문일시: #{방문일시}\n- 예상 소요시간: #{소요시간}\n- 담당 직원: #{담당자명}\n\n▶ 매장 정보\n- 위치: #{매장주소}\n- 연락처: #{매장전화번호}\n- 주차: #{주차안내}\n\n[방문 전 준비사항]\n- 신분증 지참 필수 (본인 확인)\n- 예약 10분 전 도착 권장\n- 마스크 착용 협조\n- 예약 확인 문자 제시\n\n[교통 및 위치 안내]\n- 대중교통: #{교통편안내}\n- 자가용: #{길찾기정보}\n- 주변 랜드마크: #{랜드마크}\n\n[예약 변경 및 취소]\n방문 예정일 1일 전까지 변경/취소 가능\n- 전화: #{매장전화번호}\n- 온라인: #{변경링크}\n- 문자 회신으로도 변경 가능\n\n※ 본 메시지는 매장 방문 예약 신청고객에게 발송되는 예약 확인 메시지입니다.",
            "[#{행사명} 참가 안내]\n\n#{수신자명}님, 안녕하세요.\n#{주최기관}에서 개최하는 #{행사명} 참가를 안내드립니다.\n\n▶ 행사 개요\n- 행사명: #{행사명}\n- 일시: #{행사일시}\n- 장소: #{행사장소}\n- 대상: #{참가대상}\n- 참가비: #{참가비}\n\n▶ 프로그램 일정\n#{프로그램일정상세}\n\n▶ 참가 신청\n- 신청 방법: #{신청방법}\n- 신청 마감: #{신청마감일}\n- 신청 문의: #{신청문의전화}\n- 온라인 신청: #{신청링크}\n\n[준비물 및 복장]\n- 필수 준비물: #{필수준비물}\n- 권장 복장: #{복장안내}\n- 개인 준비물: #{개인준비물}\n\n[행사장 안내]\n- 상세 주소: #{상세주소}\n- 교통편: #{교통편}\n- 주차 시설: #{주차정보}\n- 편의 시설: #{편의시설}\n\n[주의사항 및 안내]\n- 코로나19 방역수칙 준수\n- 행사 당일 발열체크 실시\n- 우천 시 일정: #{우천시대안}\n- 기타 문의: #{기타문의처}\n\n※ 본 메시지는 #{행사명} 관심 등록자에게 발송되는 행사 안내 메시지입니다.",
        ]

    def _load_guidelines(self) -> list:
        """predata 폴더의 모든 파일 로드 및 임베딩"""
        all_chunks = []
        predata_dir = Path("predata")
        
        if not predata_dir.exists():
            print("❌ predata 폴더가 존재하지 않습니다.")
            return []
        
        try:
            # predata 폴더의 모든 파일 목록
            predata_files = [
                "cleaned_add_infotalk.md",
                "cleaned_alrimtalk.md", 
                "cleaned_black_list.md",
                "cleaned_content-guide.md",
                "cleaned_info_simsa.md",
                "cleaned_message.md",
                "cleaned_message_yuisahang.md",
                "cleaned_run_message.md",
                "cleaned_white_list.md",
                "cleaned_zipguide.md",
                "pdf_extraction_results.txt"
            ]
            
            print(f"📁 predata 폴더에서 {len(predata_files)}개 파일 로딩 중...")
            
            for filename in predata_files:
                file_path = predata_dir / filename
                if file_path.exists():
                    try:
                        # 파일 내용 로드
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 청킹
                        chunks = self.entity_extractor.chunk_text(content, 800, 100)
                        all_chunks.extend(chunks)
                        print(f"✅ {filename}: {len(chunks)}개 청크 생성")
                        
                    except Exception as e:
                        print(f"⚠️ {filename} 로드 실패: {e}")
                else:
                    print(f"⚠️ {filename} 파일이 존재하지 않습니다.")
            
            print(f"🔄 총 {len(all_chunks)}개 청크를 predata에서 로드 완료")
            return all_chunks
            
        except Exception as e:
            print(f"가이드라인 로드 오류: {e}")
            return []

    def _build_indexes(self):
        """인덱스 구축"""
        # 템플릿 인덱스
        if self.templates:
            clean_templates = []
            for template in self.templates:
                clean_template = re.sub(r"#\{[^}]+\}", "[VARIABLE]", template)
                clean_templates.append(clean_template)

            template_embeddings = self.template_generator.encode_texts(clean_templates)
            self.template_generator.template_index = (
                self.template_generator.build_faiss_index(template_embeddings)
            )
            self.template_generator.templates = self.templates

        # 가이드라인 인덱스
        if self.guidelines:
            guideline_embeddings = self.entity_extractor.encode_texts(self.guidelines)
            self.entity_extractor.guideline_index = (
                self.entity_extractor.build_faiss_index(guideline_embeddings)
            )
            self.entity_extractor.guidelines = self.guidelines

    def generate_template(self, user_input: str) -> dict:
        """템플릿 생성"""

        # 1. 엔티티 추출
        entities = self.entity_extractor.extract_entities(user_input)

        # 2. 유사 템플릿 검색
        similar_templates = self.template_generator.search_similar(
            user_input,
            self.template_generator.template_index,
            self.template_generator.templates,
            top_k=3,
        )

        # 3. 관련 가이드라인 검색
        relevant_guidelines = self.entity_extractor.search_similar(
            user_input + " " + entities.get("message_intent", ""),
            self.entity_extractor.guideline_index,
            self.entity_extractor.guidelines,
            top_k=3,
        )
        guidelines = [guideline for guideline, _ in relevant_guidelines]

        # 4. 템플릿 생성
        template, filled_template = self.template_generator.generate_template(
            user_input, entities, similar_templates, guidelines
        )

        # 5. 템플릿 최적화
        optimized_template = self.template_generator.optimize_template(
            template, entities
        )

        # 6. 변수 추출
        variables = self.template_generator.extract_variables(optimized_template)

        return {
            "user_input": user_input,
            "generated_template": optimized_template,
            "filled_template": self.template_generator._fill_template_with_entities(
                optimized_template, entities
            ),
            "variables": variables,
            "entities": entities,
        }


def main():
    """메인 실행 함수 - 간단한 템플릿 생성"""
    print("🚀 알림톡 템플릿 생성기")
    print("=" * 50)

    try:
        system = TemplateSystem()
        print("✅ 시스템 준비 완료\n")
    except Exception as e:
        print(f"❌ 시스템 초기화 실패: {e}")
        return

    while True:
        print("💬 알림톡 내용을 설명해주세요:")

        user_input = input("\n➤ ").strip()

        if user_input.lower() in ["quit", "exit", "종료"]:
            print("👋 시스템을 종료합니다.")
            break

        if user_input:
            try:
                print(f"\n💬 사용자 입력: '{user_input}'")
                print("\n🔄 템플릿 생성 중...")
                result = system.generate_template(user_input)

                print("\n✨ 생성된 템플릿:")
                print("=" * 50)
                print(result["generated_template"])
                print("=" * 50)

                print(f"\n📝 추출된 변수 ({len(result['variables'])}개):")
                print(f"   {', '.join(result['variables'])}")

                print(f"\n📊 추출된 정보:")
                entities = result["entities"]
                extracted = entities.get("extracted_info", {})
                if extracted.get("dates"):
                    print(f"   📅 날짜: {', '.join(extracted['dates'])}")
                if extracted.get("names"):
                    print(f"   👤 이름: {', '.join(extracted['names'])}")
                if extracted.get("locations"):
                    print(f"   📍 장소: {', '.join(extracted['locations'])}")
                if extracted.get("events"):
                    print(f"   🎉 이벤트: {', '.join(extracted['events'])}")

                print("\n" + "=" * 50 + "\n")

            except Exception as e:
                print(f"❌ 오류: {e}\n")
        else:
            print("❌ 입력이 비어있습니다.\n")


if __name__ == "__main__":
    main()
