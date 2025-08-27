#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

# PDF 처리 라이브러리들
from pdfminer.high_level import extract_text as pdfminer_extract
import fitz  # PyMuPDF for metadata extraction

def test_pdfminer(pdf_path):
    """pdfminer를 이용한 텍스트 추출"""
    try:
        start_time = datetime.now()
        text = pdfminer_extract(pdf_path)
        end_time = datetime.now()
        
        return {
            'success': True,
            'text': text,
            'length': len(text),
            'processing_time': (end_time - start_time).total_seconds(),
            'error': None
        }
    except Exception as e:
        return {
            'success': False,
            'text': '',
            'length': 0,
            'processing_time': 0,
            'error': str(e)
        }


def extract_pdf_metadata(pdf_path):
    """PDF 메타데이터 추출"""
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        doc.close()
        return metadata
    except Exception as e:
        return {'error': str(e)}

def analyze_text_quality(text, library_name):
    """텍스트 품질 분석"""
    analysis = {
        'library': library_name,
        'character_count': len(text),
        'line_count': text.count('\n'),
        'word_count': len(text.split()),
        'has_korean': bool(any(ord(char) >= 0xAC00 and ord(char) <= 0xD7A3 for char in text)),
        'korean_char_count': sum(1 for char in text if ord(char) >= 0xAC00 and ord(char) <= 0xD7A3),
        'special_chars': sum(1 for char in text if not char.isalnum() and not char.isspace()),
        'preview': text[:500] + '...' if len(text) > 500 else text
    }
    return analysis

def main():
    pdf_path = "/Users/david/Documents/study/Jober_java/data/불법스팸_방지를_위한_정보통신망법_안내서(24.3월).pdf"
    
    print("=== PDF 텍스트 추출 테스트 시작 ===")
    print(f"파일: {pdf_path}")
    print()
    
    # PDF 메타데이터 추출
    print("=== PDF 메타데이터 추출 ===")
    metadata = extract_pdf_metadata(pdf_path)
    if metadata and 'error' not in metadata:
        for key, value in metadata.items():
            print(f"{key}: {value}")
    else:
        error_msg = metadata.get('error', '알 수 없는 오류') if metadata else '메타데이터가 없습니다'
        print(f"메타데이터 추출 실패: {error_msg}")
    print()
    
    # 각 라이브러리별 테스트
    libraries = [
        ('pdfminer', test_pdfminer)
    ]
    
    results = {}
    
    for lib_name, test_func in libraries:
        print(f"[{lib_name}] 테스트 중...")
        result = test_func(pdf_path)
        results[lib_name] = result
        
        if result['success']:
            print(f"✓ 성공 - {result['length']:,}자, {result['processing_time']:.2f}초")
            # 품질 분석
            analysis = analyze_text_quality(result['text'], lib_name)
            print(f"  - 한글 문자: {analysis['korean_char_count']:,}개")
            print(f"  - 단어 수: {analysis['word_count']:,}개") 
            print(f"  - 줄 수: {analysis['line_count']:,}개")
        else:
            print(f"✗ 실패 - {result['error']}")
        print()
    
    # 결과 비교 분석
    print("=== 결과 비교 ===")
    successful_results = {k: v for k, v in results.items() if v['success']}
    
    if successful_results:
        # 처리 시간 비교
        print("처리 시간 비교:")
        sorted_by_time = sorted(successful_results.items(), key=lambda x: x[1]['processing_time'])
        for lib_name, result in sorted_by_time:
            print(f"  {lib_name}: {result['processing_time']:.2f}초")
        print()
        
        # 추출된 텍스트 길이 비교
        print("텍스트 길이 비교:")
        sorted_by_length = sorted(successful_results.items(), key=lambda x: x[1]['length'], reverse=True)
        for lib_name, result in sorted_by_length:
            print(f"  {lib_name}: {result['length']:,}자")
        print()
        
        # 첫 번째 페이지 미리보기 비교
        print("=== 텍스트 미리보기 비교 (첫 500자) ===")
        for lib_name, result in successful_results.items():
            print(f"\n[{lib_name}]:")
            print("-" * 50)
            preview = result['text'][:500].strip()
            print(preview)
            if len(result['text']) > 500:
                print("...")
            print("-" * 50)
    
    # 결과를 파일로 저장
    output_path = "/Users/david/Documents/study/Jober_java/predata/pdf_extraction_results.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("PDF 텍스트 추출 테스트 결과\n")
        f.write("=" * 50 + "\n\n")
        
        # 메타데이터 저장
        f.write("PDF 메타데이터\n")
        f.write("-" * 30 + "\n")
        if metadata and 'error' not in metadata:
            for key, value in metadata.items():
                f.write(f"{key}: {value}\n")
        else:
            error_msg = metadata.get('error', '알 수 없는 오류') if metadata else '메타데이터가 없습니다'
            f.write(f"메타데이터 추출 실패: {error_msg}\n")
        f.write("\n")
        
        for lib_name, result in results.items():
            f.write(f"[{lib_name}]\n")
            if result['success']:
                f.write(f"성공 - {result['length']:,}자, {result['processing_time']:.2f}초\n")
                f.write("추출된 텍스트:\n")
                f.write("-" * 30 + "\n")
                f.write(result['text'])
                f.write("\n" + "-" * 30 + "\n\n")
            else:
                f.write(f"실패 - {result['error']}\n\n")
    
    print(f"\n결과가 {output_path}에 저장되었습니다.")

if __name__ == "__main__":
    main()