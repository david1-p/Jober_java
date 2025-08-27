import re
import json
from pathlib import Path
from typing import Dict, List, Any

# Google AI 없이 작동하는 버전
try:
    import google.generativeai as genai
    from config import GEMINI_API_KEY
    USE_AI = True
except ImportError:
    USE_AI = False
    print("⚠️ Google AI 모듈을 찾을 수 없습니다. 패턴 기반으로만 작동합니다.")

class MetadataAutoGenerator:
    """MD 파일에 메타데이터를 자동으로 추출하고 삽입하는 클래스"""
    
    def __init__(self):
        if USE_AI:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None
        
        # 파일별 페이지 URL 매핑 (간단하게!)
        self.page_urls = {
            "cleaned_add_infotalk.md": "https://kakaobusiness.gitbook.io/main/ad/bizmessage/notice-friend",
            "cleaned_black_list.md": "https://kakaobusiness.gitbook.io/main/ad/bizmessage/notice-friend/audit/black-list", 
            "cleaned_white_list.md": "https://kakaobusiness.gitbook.io/main/ad/bizmessage/notice-friend/audit/white-list",
            "cleaned_content-guide.md": "https://kakaobusiness.gitbook.io/main/ad/bizmessage/notice-friend/infotalk/content-guide",
            "cleaned_message_yuisahang.md": "https://kakaobusiness.gitbook.io/main/ad/moment/start/messagead/operations",
            "cleaned_info_simsa.md": "https://kakaobusiness.gitbook.io/main/ad/bizmessage/notice-friend/audit",
            "cleaned_alrimtalk.md": "https://kakaobusiness.gitbook.io/main/ad/bizmessage/notice-friend",
            "cleaned_message.md": "https://kakaobusiness.gitbook.io/main/channel/run/message",
            "cleaned_run_message.md": "https://kakaobusiness.gitbook.io/main/channel/run/message",
            "cleaned_zipguide.md": "https://kakaobusiness.gitbook.io/main/"
        }

        # 파일별 기본 메타데이터 템플릿 (기존대로)
        self.file_templates = {
            "cleaned_add_infotalk.md": {
                "file_type": "service_guide",
                "target_audience": "developer",
                "service": "알림톡",
                "compliance_required": True
            },
            "cleaned_black_list.md": {
                "file_type": "blacklist",
                "severity": "high", 
                "compliance_level": "mandatory"
            },
            "cleaned_white_list.md": {
                "file_type": "whitelist",
                "allowed": True,
                "compliance_level": "recommended"
            },
            "cleaned_content-guide.md": {
                "file_type": "content_guide",
                "template_specs": True
            },
            "cleaned_message_yuisahang.md": {
                "file_type": "compliance_guide",
                "legal_reference": "정보통신망법"
            },
            "cleaned_info_simsa.md": {
                "file_type": "review_guide",
                "authority": "카카오"
            }
        }
    
    def detect_content_patterns(self, content: str) -> Dict[str, Any]:
        """패턴 매칭으로 메타데이터 자동 감지"""
        metadata = {}
        
        # 섹션 번호 감지
        section_match = re.search(r'## (\d+(?:\.\d+)*\.?\s*[^#\n]*)', content)
        if section_match:
            metadata["section"] = section_match.group(1).strip()
            
        # 하위 섹션 감지
        subsection_match = re.search(r'### (\d+(?:-\d+)+\.?\s*[^#\n]*)', content)
        if subsection_match:
            metadata["subsection"] = subsection_match.group(1).strip()
            
        # 페이지 정보 자동 감지 (섹션 기반)
        page_info = self._detect_page_info(content)
        if page_info:
            metadata["page_reference"] = page_info
            
        # 심각도 감지
        if any(word in content for word in ["영구적으로", "차단", "중지", "금지"]):
            metadata["severity"] = "critical"
        elif any(word in content for word in ["제한", "반려", "위반"]):
            metadata["severity"] = "high"
        elif any(word in content for word in ["권장", "주의", "확인"]):
            metadata["severity"] = "medium"
        else:
            metadata["severity"] = "low"
            
        # 콘텐츠 타입 감지
        if "| " in content and "---|" in content:
            metadata["content_type"] = "table"
        elif re.search(r'{% hint style="danger" %}', content):
            metadata["content_type"] = "warning"
        elif re.search(r'{% hint style="success" %}', content):
            metadata["content_type"] = "example"
        elif re.search(r'{% hint style="info" %}', content):
            metadata["content_type"] = "info"
        elif any(word in content for word in ["단계", "방법", "절차"]):
            metadata["content_type"] = "procedure"
        elif any(word in content for word in ["정의", "개념", "이란"]):
            metadata["content_type"] = "definition"
        else:
            metadata["content_type"] = "general"
            
        # 컴플라이언스 레벨 감지
        if any(word in content for word in ["필수", "반드시", "의무"]):
            metadata["compliance_level"] = "mandatory"
        elif any(word in content for word in ["권장", "바람직"]):
            metadata["compliance_level"] = "recommended"
        else:
            metadata["compliance_level"] = "optional"
            
        # 키워드 추출
        keywords = []
        keyword_patterns = [
            r'알림톡', r'친구톡', r'정보성', r'광고성', r'템플릿', 
            r'심사', r'승인', r'반려', r'발송', r'채널',
            r'정보통신망법', r'컴플라이언스', r'위반', r'차단'
        ]
        
        for pattern in keyword_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                keywords.append(pattern)
        
        metadata["keywords"] = keywords[:5]  # 최대 5개
        
        return metadata
    
    def _detect_page_info(self, content: str) -> str:
        """콘텐츠에서 페이지 정보 자동 감지"""
        # 회원가입 관련
        if any(keyword in content for keyword in ["회원가입", "가입", "회원"]):
            return "회원가입 가이드"
        # 주문/배송 관련  
        elif any(keyword in content for keyword in ["주문", "배송", "택배", "결제"]):
            return "주문/배송 가이드"
        # 예약 관련
        elif any(keyword in content for keyword in ["예약", "신청", "방문"]):
            return "예약/신청 가이드"
        # 쿠폰/포인트 관련
        elif any(keyword in content for keyword in ["쿠폰", "포인트", "마일리지", "적립"]):
            return "쿠폰/포인트 가이드"
        # 금융 관련
        elif any(keyword in content for keyword in ["은행", "대출", "이자", "증권", "카드"]):
            return "금융 서비스 가이드"
        # 보안 관련
        elif any(keyword in content for keyword in ["보안", "안전", "OTP", "비밀번호"]):
            return "보안/안전 가이드"
        # 심사 관련
        elif any(keyword in content for keyword in ["심사", "승인", "반려", "검토"]):
            return "심사 정책"
        # 블랙리스트 관련
        elif any(keyword in content for keyword in ["블랙리스트", "금지", "불가", "위반"]):
            return "블랙리스트 정책"
        # 화이트리스트 관련
        elif any(keyword in content for keyword in ["화이트리스트", "허용", "가능", "발송"]):
            return "화이트리스트 정책"
        # 템플릿 제작 관련
        elif any(keyword in content for keyword in ["템플릿", "제작", "가이드", "유형"]):
            return "템플릿 제작 가이드"
        else:
            return "일반 가이드"
    
    def extract_metadata_with_ai(self, content_chunk: str) -> Dict[str, Any]:
        """AI로 메타데이터 추출"""
        if not USE_AI or not self.model:
            # AI 없이 기본값 반환
            return {
                "main_topic": "알림톡 가이드",
                "purpose": "guide", 
                "business_impact": "medium",
                "tags": ["알림톡", "가이드"]
            }
        
        try:
            prompt = f"""
다음 텍스트를 분석해서 메타데이터를 JSON 형태로 추출해줘.
한국어로 된 알림톡 가이드 문서의 일부야.

텍스트:
{content_chunk[:1000]}...

다음 형태의 JSON으로 응답해줘:
{{
    "main_topic": "주요 주제 (한국어)",
    "purpose": "이 섹션의 목적 (setup/guide/warning/example 중 하나)",
    "business_impact": "비즈니스 영향도 (high/medium/low)",
    "tags": ["키워드1", "키워드2", "키워드3"]
}}
"""
            
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())
            return result
            
        except Exception as e:
            print(f"AI 메타데이터 추출 실패: {e}")
            return {
                "main_topic": "미분류",
                "purpose": "guide", 
                "business_impact": "medium",
                "tags": ["알림톡"]
            }
    
    def split_content_into_chunks(self, content: str) -> List[Dict[str, Any]]:
        """콘텐츠를 의미있는 청크로 분할"""
        chunks = []
        
        # 섹션별로 분할 (## 또는 ### 기준)
        sections = re.split(r'(^#{2,3}\s+.+$)', content, flags=re.MULTILINE)
        
        current_chunk = ""
        current_header = ""
        
        for i, section in enumerate(sections):
            if re.match(r'^#{2,3}\s+', section):  # 헤더인 경우
                if current_chunk.strip():  # 이전 청크가 있으면 저장
                    chunks.append({
                        "header": current_header,
                        "content": current_chunk.strip(),
                        "chunk_id": len(chunks) + 1
                    })
                
                current_header = section.strip()
                current_chunk = section + "\n"
            else:
                current_chunk += section
        
        # 마지막 청크 저장
        if current_chunk.strip():
            chunks.append({
                "header": current_header,
                "content": current_chunk.strip(),
                "chunk_id": len(chunks) + 1
            })
        
        return chunks
    
    def generate_metadata_for_chunk(self, chunk: Dict[str, Any], file_name: str) -> Dict[str, Any]:
        """청크별 메타데이터 생성"""
        # 기본 메타데이터
        base_metadata = self.file_templates.get(file_name, {})
        
        # 패턴 기반 메타데이터
        pattern_metadata = self.detect_content_patterns(chunk["content"])
        
        # AI 기반 메타데이터
        ai_metadata = self.extract_metadata_with_ai(chunk["content"])
        
        # 청크 고유 정보
        chunk_metadata = {
            "source_file": file_name,
            "chunk_id": chunk["chunk_id"],
            "header": chunk["header"],
            "content_length": len(chunk["content"])
        }
        
        # 모든 메타데이터 병합
        final_metadata = {
            **base_metadata,
            **pattern_metadata, 
            **ai_metadata,
            **chunk_metadata
        }
        
        return final_metadata
    
    def insert_metadata_into_content(self, chunks: List[Dict[str, Any]], file_name: str) -> str:
        """메타데이터를 콘텐츠에 삽입"""
        result_content = []
        
        # 첫 번째 청크에만 파일 전체 메타데이터 추가
        for i, chunk in enumerate(chunks):
            metadata = self.generate_metadata_for_chunk(chunk, file_name)
            
            # 첫 청크에만 source_url 추가
            if i == 0:
                metadata["source_url"] = self.page_urls.get(file_name, "")
            
            # 메타데이터를 YAML 프론트매터 형식으로 삽입
            metadata_block = "<!--\n"
            metadata_block += "METADATA:\n"
            for key, value in metadata.items():
                if isinstance(value, list):
                    metadata_block += f"  {key}: {json.dumps(value, ensure_ascii=False)}\n"
                else:
                    metadata_block += f"  {key}: {json.dumps(value, ensure_ascii=False)}\n"
            metadata_block += "-->\n\n"
            
            # 메타데이터 + 원본 콘텐츠
            result_content.append(metadata_block + chunk["content"])
        
        return "\n\n".join(result_content)
    
    def process_file(self, file_path: str) -> None:
        """파일 처리 메인 함수"""
        path = Path(file_path)
        
        if not path.exists():
            print(f"❌ 파일이 존재하지 않습니다: {file_path}")
            return
        
        print(f"🔄 처리 중: {path.name}")
        
        # 원본 파일 읽기
        with open(path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # 청크로 분할
        chunks = self.split_content_into_chunks(original_content)
        print(f"📝 {len(chunks)}개 청크로 분할")
        
        # 메타데이터 삽입
        enhanced_content = self.insert_metadata_into_content(chunks, path.name)
        
        # 백업 생성
        backup_path = path.parent / f"{path.stem}_backup{path.suffix}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"💾 백업 생성: {backup_path}")
        
        # 메타데이터가 추가된 파일 저장
        with open(path, 'w', encoding='utf-8') as f:
            f.write(enhanced_content)
        
        print(f"✅ 메타데이터 삽입 완료: {path}")

def main():
    """메인 실행 함수 - predata 폴더의 모든 MD 파일 처리"""
    generator = MetadataAutoGenerator()
    
    # predata 폴더의 모든 cleaned_*.md 파일 찾기
    predata_path = Path("predata")
    md_files = list(predata_path.glob("cleaned_*.md"))
    
    print(f"📂 {len(md_files)}개의 MD 파일을 찾았습니다.")
    
    for md_file in md_files:
        # 이미 처리된 파일인지 확인 (METADATA 주석이 있는지 체크)
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "<!--\nMETADATA:" in content:
                print(f"⏭️  이미 처리됨: {md_file.name}")
                continue
                
        except Exception as e:
            print(f"❌ 파일 읽기 오류 {md_file}: {e}")
            continue
            
        # 파일 처리
        generator.process_file(str(md_file))
    
    print(f"\n🎉 모든 파일 처리 완료!")

if __name__ == "__main__":
    main()