#!/usr/bin/env python3
"""템플릿 생성기 테스트 스크립트"""

from config import GEMINI_API_KEY
from core import EntityExtractor, TemplateGenerator
from utils import DataProcessor
from main import TemplateSystem

def test_template_generation():
    """템플릿 생성 테스트"""
    print("🚀 템플릿 생성기 테스트")
    print("=" * 50)
    
    try:
        system = TemplateSystem()
        print("✅ 시스템 초기화 완료\n")
        
        # 테스트 입력들
        test_inputs = [
            "12월 25일 크리스마스 이벤트 안내를 홍길동에게 보내고 싶어",
            "강남점 방문 예약 확인 메시지를 김철수님에게 보내려고 해",
            "가격 변경 안내를 기존 고객들에게 1월 1일부터 적용된다고 알려주고 싶어"
        ]
        
        for i, user_input in enumerate(test_inputs, 1):
            print(f"📝 테스트 {i}: {user_input}")
            print("-" * 30)
            
            try:
                result = system.generate_template(user_input)
                
                print("✨ 생성된 템플릿:")
                print(result["generated_template"][:200] + "..." if len(result["generated_template"]) > 200 else result["generated_template"])
                print()
                
                print(f"📝 변수: {', '.join(result['variables'][:5])}{'...' if len(result['variables']) > 5 else ''}")
                print()
                
            except Exception as e:
                print(f"❌ 오류: {e}")
            
            print("=" * 50)
            print()
    
    except Exception as e:
        print(f"❌ 시스템 초기화 실패: {e}")

if __name__ == "__main__":
    test_template_generation()