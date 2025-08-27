#!/usr/bin/env python3

# 실제 검증 시스템에서 사용할 예시
def validate_user_input(user_input: str, metadata_chunks):
    """사용자 입력 검증 및 정책 위반 안내"""
    
    violations = []
    
    # 예시: 포인트 관련 위반 검사
    if "포인트" in user_input and "적립" in user_input:
        # 블랙리스트에서 관련 메타데이터 찾기
        for chunk in metadata_chunks:
            if chunk.get("file_type") == "blacklist" and "포인트" in chunk.get("keywords", []):
                violations.append({
                    "violation_type": "포인트 적립 안내 위반",
                    "severity": chunk.get("severity", "medium"),
                    "description": "동의 없는 포인트 적립/소멸 메시지는 발송할 수 없습니다.",
                    "source_url": chunk.get("source_url"),
                    "page_title": chunk.get("page_title"),
                    "file_reference": chunk.get("source_file"),
                    "chunk_id": chunk.get("chunk_id")
                })
                break
    
    # 검증 결과 반환
    return {
        "is_valid": len(violations) == 0,
        "violations": violations,
        "recommendations": generate_recommendations(violations)
    }

def generate_recommendations(violations):
    """위반사항 기반 권장사항 생성"""
    if not violations:
        return ["입력하신 내용은 정책에 적합합니다."]
    
    recommendations = []
    for violation in violations:
        recommendations.append(
            f"📋 **{violation['violation_type']}**\n"
            f"   ⚠️  {violation['description']}\n"
            f"   📖 자세한 내용: [{violation['page_title']}]({violation['source_url']})\n"
            f"   📄 파일 참조: {violation['file_reference']} (청크 {violation['chunk_id']})"
        )
    
    return recommendations

# 테스트 예시
if __name__ == "__main__":
    # 메타데이터 예시 (실제로는 임베딩된 데이터에서 검색)
    sample_metadata = [
        {
            "file_type": "blacklist",
            "severity": "high",
            "keywords": ["포인트", "적립", "소멸"],
            "source_url": "https://kakaobusiness.gitbook.io/main/ad/bizmessage/notice-friend/audit/black-list",
            "page_title": "알림톡 블랙리스트",
            "source_file": "cleaned_black_list.md", 
            "chunk_id": 1
        }
    ]
    
    # 테스트 케이스들
    test_cases = [
        "포인트가 적립되었습니다",  # 위반
        "주문이 완료되었습니다",    # 정상
        "쿠폰이 발급되었습니다"     # 위반 가능성
    ]
    
    print("🔍 사용자 입력 검증 테스트")
    print("=" * 60)
    
    for user_input in test_cases:
        print(f"\n입력: '{user_input}'")
        result = validate_user_input(user_input, sample_metadata)
        
        if result["is_valid"]:
            print("✅ 정책 적합")
        else:
            print("❌ 정책 위반 감지")
            for rec in result["recommendations"]:
                print(f"   {rec}")