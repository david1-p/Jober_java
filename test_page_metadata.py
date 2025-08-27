#!/usr/bin/env python3

from metadata_auto_generator import MetadataAutoGenerator

# 테스트용 간단한 스크립트
def test_page_detection():
    generator = MetadataAutoGenerator()
    
    # 테스트 케이스들
    test_cases = [
        ("회원가입을 완료했습니다", "회원가입 가이드"),
        ("주문이 완료되었습니다. 배송 정보를 확인하세요", "주문/배송 가이드"), 
        ("포인트가 적립되었습니다", "쿠폰/포인트 가이드"),
        ("템플릿 심사가 완료되었습니다", "심사 정책"),
        ("블랙리스트에 해당하는 메시지입니다", "블랙리스트 정책")
    ]
    
    print("🔍 페이지 정보 감지 테스트")
    print("=" * 50)
    
    for content, expected in test_cases:
        detected = generator._detect_page_info(content)
        status = "✅" if detected == expected else "❌"
        print(f"{status} '{content[:30]}...' -> {detected}")
    
    # 메타데이터 생성 테스트
    print("\n📝 전체 메타데이터 생성 테스트")
    print("=" * 50)
    
    sample_content = """
    ## 회원가입 가이드
    
    회원가입을 완료하신 고객님께 발송되는 메시지입니다.
    포인트 적립과 관련된 혜택을 확인하세요.
    """
    
    metadata = generator.detect_content_patterns(sample_content)
    print("생성된 메타데이터:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    test_page_detection()