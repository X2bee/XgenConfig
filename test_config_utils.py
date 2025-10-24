#!/usr/bin/env python3
"""
Config Utils 사용 예제

Redis에서 설정을 dictionary 형태로 가져오는 다양한 방법들을 보여줍니다.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from service.config_utils import (
    get_config_dict,
    get_category_config,
    get_flat_config,
    get_config_value,
    get_multiple_configs,
    get_all_categories,
    update_config,
    get_app_config,
    get_openai_config,
    get_vast_config
)
import json


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main():
    print("=" * 70)
    print("  Config Utils 사용 예제")
    print("=" * 70)

    # 1. 전체 설정 중첩 구조로 가져오기
    print_section("1. 전체 설정 - 중첩 구조")
    all_nested = get_config_dict(flatten=False)
    print("\n📂 app 카테고리:")
    print(json.dumps(all_nested.get("app", {}), indent=2, ensure_ascii=False))
    print("\n📂 openai 카테고리:")
    print(json.dumps(all_nested.get("openai", {}), indent=2, ensure_ascii=False))

    # 2. 전체 설정 평탄화 구조로 가져오기
    print_section("2. 전체 설정 - 평탄화 구조")
    all_flat = get_config_dict(flatten=True)
    print("\n일부 설정 값들:")
    for key in sorted(all_flat.keys())[:10]:
        print(f"  • {key}: {all_flat[key]}")

    # 3. 특정 카테고리만 가져오기
    print_section("3. 특정 카테고리 설정 가져오기")

    app_config = get_category_config("app")
    print("\n📁 app 설정:")
    print(json.dumps(app_config, indent=2, ensure_ascii=False))

    openai_config = get_category_config("openai")
    print("\n📁 openai 설정:")
    print(json.dumps(openai_config, indent=2, ensure_ascii=False))

    # 4. 평탄화된 카테고리 설정
    print_section("4. 평탄화된 카테고리 설정")
    app_flat = get_flat_config(category="app")
    print("\n📊 app 설정 (평탄화):")
    for key, value in app_flat.items():
        print(f"  • {key}: {value} ({type(value).__name__})")

    # 5. 특정 값만 가져오기
    print_section("5. 특정 설정 값 가져오기")
    environment = get_config_value("app.environment")
    port = get_config_value("app.port")
    debug_mode = get_config_value("app.debug_mode")
    api_key = get_config_value("openai.api_key", default="(비어있음)")

    print(f"\n환경: {environment}")
    print(f"포트: {port}")
    print(f"디버그 모드: {debug_mode}")
    print(f"OpenAI API Key: {api_key}")

    # 6. 여러 설정 한 번에 가져오기
    print_section("6. 여러 설정 한 번에 가져오기")
    configs = get_multiple_configs([
        "app.environment",
        "app.port",
        "openai.model_default",
        "vast.vllm.port",
        "vllm.api_base_url"
    ])
    print("\n선택한 설정들:")
    for key, value in configs.items():
        print(f"  • {key}: {value}")

    # 7. 모든 카테고리 목록
    print_section("7. 모든 카테고리 목록")
    categories = get_all_categories()
    print(f"\n총 {len(categories)}개 카테고리:")
    for i, cat in enumerate(categories, 1):
        print(f"  {i:2d}. {cat}")

    # 8. 편의 함수 사용
    print_section("8. 편의 함수 사용")

    app = get_app_config()
    print("\n📱 get_app_config():")
    print(json.dumps(app, indent=2, ensure_ascii=False))

    vast = get_vast_config()
    print("\n🚀 get_vast_config() - vllm 설정만:")
    print(json.dumps(vast.get("vast", {}).get("vllm", {}), indent=2, ensure_ascii=False))

    # 9. 실제 사용 예제
    print_section("9. 실제 사용 예제")

    print("\n# Python 코드에서 사용하기:")
    print("""
        # 방법 1: 전체 설정 가져오기
        from service.config_utils import get_config_dict
        configs = get_config_dict()
        print(configs["app"]["environment"])

        # 방법 2: 특정 카테고리
        from service.config_utils import get_openai_config
        openai = get_openai_config()
        api_key = openai["openai"]["api_key"]

        # 방법 3: 특정 값만
        from service.config_utils import get_config_value
        env = get_config_value("app.environment")
        port = get_config_value("app.port", default=8000)

        # 방법 4: 여러 값 한 번에
        from service.config_utils import get_multiple_configs
        configs = get_multiple_configs([
            "app.environment",
            "openai.api_key",
            "vast.vllm.port"
        ])
            """)

    print("\n" + "=" * 70)
    print("  완료!")
    print("=" * 70)


if __name__ == "__main__":
    main()
