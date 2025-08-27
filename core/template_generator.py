import re
from typing import Dict, List, Tuple
from .base_processor import BaseTemplateProcessor


class TemplateGenerator(BaseTemplateProcessor):
    """템플릿 생성 전용 클래스"""

    def __init__(self, api_key: str, gemini_model: str = "gemini-2.0-flash-exp"):
        super().__init__(api_key, gemini_model)

    def generate_template(
        self,
        user_input: str,
        entities: Dict,
        similar_templates: List[Tuple[str, float]],
        guidelines: List[str] = None,
    ) -> Tuple[str, str]:
        """템플릿 생성"""

        # 기본 템플릿 생성
        if guidelines:
            template = self._generate_guideline_based_template(
                user_input, entities, similar_templates, guidelines
            )
        else:
            template = self._generate_basic_template(
                user_input, entities, similar_templates
            )

        # 실제 값으로 채워진 미리보기 생성
        filled_template = self._fill_template_with_entities(template, entities)

        return template, filled_template

    def _generate_guideline_based_template(
        self,
        user_input: str,
        entities: Dict,
        similar_templates: List[Tuple[str, float]],
        guidelines: List[str],
    ) -> str:
        """가이드라인 기반 템플릿 생성"""

        template_examples = self._format_template_examples(similar_templates)
        guidelines_text = "\n".join(guidelines[:3]) if guidelines else ""

        prompt = self._create_template_generation_prompt(
            user_input,
            entities,
            template_examples,
            guidelines_text,
            use_guidelines=True,
        )

        try:
            response = self.generate_with_gemini(prompt)
            print(f"🔍 Gemini 원본 응답 길이: {len(response)}")
            print(f"🔍 Gemini 원본 응답 (처음 200자): {response[:200]}...")
            
            cleaned_response = response.replace("```", "").strip()
            print(f"🔍 정리된 응답 길이: {len(cleaned_response)}")
            
            return cleaned_response
        except Exception as e:
            print(f"가이드라인 기반 템플릿 생성 오류: {e}")
            return self._generate_fallback_template(user_input, entities)

    def _generate_basic_template(
        self,
        user_input: str,
        entities: Dict,
        similar_templates: List[Tuple[str, float]],
    ) -> str:
        """기본 템플릿 생성"""

        template_examples = self._format_template_examples(similar_templates)

        prompt = self._create_template_generation_prompt(
            user_input, entities, template_examples, "", use_guidelines=False
        )

        try:
            response = self.generate_with_gemini(prompt)
            print(f"🔍 기본 템플릿 - Gemini 원본 응답 길이: {len(response)}")
            print(f"🔍 기본 템플릿 - Gemini 원본 응답 (처음 200자): {response[:200]}...")
            
            cleaned_response = response.replace("```", "").strip()
            print(f"🔍 기본 템플릿 - 정리된 응답 길이: {len(cleaned_response)}")
            
            return cleaned_response
        except Exception as e:
            print(f"기본 템플릿 생성 오류: {e}")
            return self._generate_fallback_template(user_input, entities)

    def _create_template_generation_prompt(
        self,
        user_input: str,
        entities: Dict,
        template_examples: str,
        guidelines: str,
        use_guidelines: bool = False,
    ) -> str:
        """템플릿 생성 프롬프트 생성"""

        extracted_info = entities.get("extracted_info", {})
        intent = entities.get("message_intent", "일반안내")
        context = entities.get("context", user_input)
        message_type = entities.get("message_type", "정보성")
        urgency = entities.get("urgency_level", "보통")

        base_prompt = f"""
사용자 입력: "{user_input}"

추출된 정보:
- 날짜: {', '.join(extracted_info.get('dates', [])) if extracted_info.get('dates') else '없음'}
- 이름: {', '.join(extracted_info.get('names', [])) if extracted_info.get('names') else '없음'}
- 장소: {', '.join(extracted_info.get('locations', [])) if extracted_info.get('locations') else '없음'}
- 이벤트: {', '.join(extracted_info.get('events', [])) if extracted_info.get('events') else '없음'}
- 기타정보: {', '.join(extracted_info.get('others', [])) if extracted_info.get('others') else '없음'}

메시지 의도: {intent}
메시지 유형: {message_type}
긴급도: {urgency}
상황: {context}
"""

        if use_guidelines and guidelines:
            base_prompt += f"\n관련 알림톡 가이드라인:\n{guidelines}\n"

        if template_examples:
            base_prompt += f"\n참고 템플릿:\n{template_examples}\n"

        base_prompt += """
위 정보를 바탕으로 완성도 높은 알림톡 템플릿을 생성해주세요.

필수 준수사항:
1. 정보통신망법 준수 (정보성 메시지 기준)
2. 추출된 구체적 정보들을 #{{변수명}} 형태로 포함
3. 수신자에게 필요한 모든 정보 포함
4. 명확하고 정중한 안내 톤
5. 메시지 끝에 발송 사유 및 법적 근거 명시
6. 충분한 설명과 안내사항 포함 (최대 30자 이내)

템플릿 구조:
- 인사말 및 발신자 소개
- 주요 안내 내용 (상세히)
- 구체적인 정보 (일시, 장소, 방법 등)
- 추가 안내사항 또는 주의사항
- 문의처 또는 연락방법
- 발송 사유 및 법적 근거

실용적이고 완성도 높은 템플릿을 생성해주세요:
"""

        return base_prompt

    def _format_template_examples(
        self, similar_templates: List[Tuple[str, float]]
    ) -> str:
        """템플릿 예시 포맷팅"""
        if not similar_templates:
            return ""

        examples = []
        for i, (template, score) in enumerate(similar_templates[:2], 1):
            examples.append(f"{i}. {template}\n")

        return "\n".join(examples)

    def _fill_template_with_entities(self, template: str, entities: Dict) -> str:
        """템플릿에 추출된 엔티티 정보 자동 입력"""
        filled = template
        extracted_info = entities.get("extracted_info", {})

        # 날짜 정보 매핑
        if extracted_info.get("dates"):
            date_patterns = [
                (
                    r"#\{(일시|날짜|시간|적용일|방문일정|예약일정|행사일시)\}",
                    extracted_info["dates"][0],
                )
            ]
            for pattern, value in date_patterns:
                filled = re.sub(pattern, value, filled, flags=re.IGNORECASE)

        # 이름 정보 매핑
        if extracted_info.get("names"):
            name_patterns = [
                (
                    r"#\{(수신자명|수신자|고객명|보호자명|회원명)\}",
                    extracted_info["names"][0],
                )
            ]
            for pattern, value in name_patterns:
                filled = re.sub(pattern, value, filled, flags=re.IGNORECASE)

        # 장소 정보 매핑
        if extracted_info.get("locations"):
            location_patterns = [
                (
                    r"#\{(장소|매장명|주소|위치|행사장소)\}",
                    extracted_info["locations"][0],
                )
            ]
            for pattern, value in location_patterns:
                filled = re.sub(pattern, value, filled, flags=re.IGNORECASE)

        # 이벤트 정보 매핑
        if extracted_info.get("events"):
            event_patterns = [
                (
                    r"#\{(행사명|이벤트명|활동명|프로그램명)\}",
                    extracted_info["events"][0],
                )
            ]
            for pattern, value in event_patterns:
                filled = re.sub(pattern, value, filled, flags=re.IGNORECASE)

        return filled

    def _generate_fallback_template(self, user_input: str, entities: Dict) -> str:
        """오류 시 기본 템플릿 생성"""
        extracted_info = entities.get("extracted_info", {})
        intent = entities.get("message_intent", "일반안내")

        name_var = (
            extracted_info.get("names", ["#{수신자명}"])[0]
            if extracted_info.get("names")
            else "#{수신자명}"
        )
        date_var = (
            extracted_info.get("dates", ["#{일시}"])[0]
            if extracted_info.get("dates")
            else "#{일시}"
        )
        location_var = (
            extracted_info.get("locations", ["#{장소}"])[0]
            if extracted_info.get("locations")
            else "#{장소}"
        )
        event_var = (
            extracted_info.get("events", ["#{행사명}"])[0]
            if extracted_info.get("events")
            else "#{행사명}"
        )

        return f"""안녕하세요, {name_var}님.
{intent}에 대해 상세히 안내드립니다.

▶ 주요 내용: {event_var}
▶ 일시: {date_var}
▶ 장소: {location_var}

[상세 안내사항]
- 참석하실 분들께서는 미리 준비해주시기 바랍니다.
- 자세한 내용은 별도 공지사항을 확인해주세요.
- 변경사항이 있을 경우 개별 안내드리겠습니다.

[문의사항]
궁금한 사항이 있으시면 언제든 연락 부탁드립니다.
- 연락처: #{{연락처}}
- 운영시간: 평일 오전 9시~오후 6시

※ 본 메시지는 관련 서비스를 신청하신 분들께만 발송되는 정보성 안내 메시지입니다."""

    def optimize_template(self, template: str, entities: Dict) -> str:
        """템플릿 최적화"""
        # 길이 체크
        if len(template) < 200:
            return self._expand_template(template, entities)

        # 변수 체크
        variables = self.extract_variables(template)
        if len(variables) < 3:
            return self._add_more_variables(template, entities)

        return template

    def _expand_template(self, template: str, entities: Dict) -> str:
        """템플릿 확장"""
        # 추가 정보 섹션 삽입
        additional_info = """
[추가 안내사항]
- 정확한 정보 확인을 위해 사전 연락 부탁드립니다.
- 변경사항 발생 시 즉시 안내드리겠습니다.
- 기타 문의사항은 고객센터를 이용해주세요."""

        # 법적 고지 전에 추가 정보 삽입
        if "※" in template:
            parts = template.split("※")
            return parts[0] + additional_info + "\n\n※" + "※".join(parts[1:])
        else:
            return template + additional_info

    def _add_more_variables(self, template: str, entities: Dict) -> str:
        """더 많은 변수 추가"""
        # 기본 변수들 추가
        additional_vars = ["#{문의전화}", "#{운영시간}", "#{담당자명}"]

        contact_section = f"""
[문의 및 연락처]
- 담당자: {additional_vars[2]}
- 연락처: {additional_vars[0]} 
- 운영시간: {additional_vars[1]}"""

        if "※" in template:
            parts = template.split("※")
            return parts[0] + contact_section + "\n\n※" + "※".join(parts[1:])
        else:
            return template + contact_section
