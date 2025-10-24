#!/usr/bin/env python3
"""
Config Utils 사용 예제

Redis에서 설정을 dictionary와 SimpleNamespace 형태로 가져오는 다양한 방법들을 보여줍니다.
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
    get_anthropic_config,
    get_vast_config,
    get_vllm_config
)
from types import SimpleNamespace
import json


def print_section(title):
    """섹션 제목 출력"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def namespace_to_dict(obj):
    """SimpleNamespace를 dict로 변환 (JSON 출력용)"""
    if isinstance(obj, SimpleNamespace):
        return {key: namespace_to_dict(value) for key, value in vars(obj).items()}
    elif isinstance(obj, list):
        return [namespace_to_dict(item) for item in obj]
    else:
        return obj


def main():
    print("=" * 70)
    print("  Config Utils 사용 예제 (SimpleNamespace 지원)")
    print("=" * 70)

    # 1. 전체 설정 - SimpleNamespace로 가져오기
    print_section("1. 전체 설정 - SimpleNamespace (속성 접근)")
    all_configs = get_config_dict(flatten=False, as_namespace=True)
    print("\n📂 app 카테고리 (속성 접근):")
    print(f"  • environment: {all_configs.app.environment}")
    print(f"  • port: {all_configs.app.port}")
    print(f"  • debug_mode: {all_configs.app.debug_mode}")
    
    if hasattr(all_configs, 'openai'):
        print("\n📂 openai 카테고리 (속성 접근):")
        print(f"  • model_default: {all_configs.openai.model_default}")
        print(f"  • api_key: {all_configs.openai.api_key[:20]}..." if hasattr(all_configs.openai, 'api_key') else "  • api_key: (없음)")

    # 2. 전체 설정 - dict로 가져오기
    print_section("2. 전체 설정 - Dict (키 접근)")
    all_dict = get_config_dict(flatten=False, as_namespace=False)
    print("\n📂 app 카테고리 (JSON):")
    print(json.dumps(all_dict.get("app", {}), indent=2, ensure_ascii=False))

    # 3. 전체 설정 평탄화 구조
    print_section("3. 전체 설정 - 평탄화 구조")
    all_flat = get_config_dict(flatten=True)
    print("\n일부 설정 값들:")
    for key in sorted(all_flat.keys())[:10]:
        print(f"  • {key}: {all_flat[key]}")

    # 4. 특정 카테고리 - SimpleNamespace (기본값)
    print_section("4. 특정 카테고리 설정 - SimpleNamespace")
    
    app_config = get_category_config("app")
    print("\n📱 app 설정 (속성 접근):")
    print(f"  • app.environment: {app_config.environment}")
    print(f"  • app.port: {app_config.port}")
    print(f"  • app.debug_mode: {app_config.debug_mode}")
    
    openai_config = get_category_config("openai")
    print("\n🤖 openai 설정 (속성 접근):")
    if hasattr(openai_config, 'model_default'):
        print(f"  • openai.model_default: {openai_config.model_default}")
    if hasattr(openai_config, 'temperature_default'):
        print(f"  • openai.temperature_default: {openai_config.temperature_default}")

    # 5. 특정 카테고리 - dict로 받기
    print_section("5. 특정 카테고리 설정 - Dict")
    app_dict = get_category_config("app", as_namespace=False)
    print("\n📁 app 설정 (JSON):")
    print(json.dumps(app_dict, indent=2, ensure_ascii=False))

    # 6. 평탄화된 카테고리 설정
    print_section("6. 평탄화된 카테고리 설정")
    app_flat = get_flat_config(category="app")
    print("\n📊 app 설정 (평탄화):")
    for key, value in sorted(app_flat.items()):
        print(f"  • {key}: {value} ({type(value).__name__})")

    # 7. 특정 값만 가져오기
    print_section("7. 특정 설정 값 가져오기")
    environment = get_config_value("app.environment")
    port = get_config_value("app.port")
    debug_mode = get_config_value("app.debug_mode")
    api_key = get_config_value("openai.api_key", default="(비어있음)")

    print(f"\n환경: {environment}")
    print(f"포트: {port}")
    print(f"디버그 모드: {debug_mode}")
    print(f"OpenAI API Key: {api_key[:20]}..." if len(str(api_key)) > 20 else f"OpenAI API Key: {api_key}")

    # 8. 여러 설정 한 번에 가져오기
    print_section("8. 여러 설정 한 번에 가져오기")
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

    # 9. 모든 카테고리 목록
    print_section("9. 모든 카테고리 목록")
    categories = get_all_categories()
    print(f"\n총 {len(categories)}개 카테고리:")
    for i, cat in enumerate(categories, 1):
        print(f"  {i:2d}. {cat}")

    # 10. 편의 함수 사용 (SimpleNamespace)
    print_section("10. 편의 함수 사용 (SimpleNamespace)")

    print("\n📱 get_app_config():")
    app = get_app_config()
    print(f"  • app.environment: {app.environment}")
    print(f"  • app.port: {app.port}")
    print(f"  • app.debug_mode: {app.debug_mode}")

    print("\n🤖 get_openai_config():")
    openai = get_openai_config()
    if hasattr(openai, 'model_default'):
        print(f"  • openai.model_default: {openai.model_default}")
    if hasattr(openai, 'temperature_default'):
        print(f"  • openai.temperature_default: {openai.temperature_default}")

    print("\n🧠 get_anthropic_config():")
    anthropic = get_anthropic_config()
    if hasattr(anthropic, 'model_default'):
        print(f"  • anthropic.model_default: {anthropic.model_default}")

    # 11. VAST 설정 - 자동 언래핑 테스트
    print_section("11. 🚀 get_vast_config() - 자동 언래핑")
    vast = get_vast_config()
    
    print("\n✅ VAST 설정 (속성으로 직접 접근!):")
    
    # vllm 설정
    if hasattr(vast, 'vllm'):
        print("\n  📦 VLLM 설정:")
        if hasattr(vast.vllm, 'gpu_memory_utilization'):
            print(f"    • gpu_memory_utilization: {vast.vllm.gpu_memory_utilization}")
        if hasattr(vast.vllm, 'port'):
            print(f"    • port: {vast.vllm.port}")
        if hasattr(vast.vllm, 'serve_model_name'):
            print(f"    • serve_model_name: {vast.vllm.serve_model_name}")
        if hasattr(vast.vllm, 'dtype'):
            print(f"    • dtype: {vast.vllm.dtype}")
    
    # image 설정
    if hasattr(vast, 'image'):
        print("\n  🖼️ Image 설정:")
        if hasattr(vast.image, 'name'):
            print(f"    • name: {vast.image.name}")
        if hasattr(vast.image, 'tag'):
            print(f"    • tag: {vast.image.tag}")
    
    # proxy 설정
    if hasattr(vast, 'proxy'):
        print("\n  🌐 Proxy 설정:")
        if hasattr(vast.proxy, 'base_url'):
            print(f"    • base_url: {vast.proxy.base_url}")
        if hasattr(vast.proxy, 'mode'):
            print(f"    • mode: {vast.proxy.mode}")
    
    # network 설정
    if hasattr(vast, 'network'):
        print("\n  🔌 Network 설정:")
        if hasattr(vast.network, 'default_ports'):
            print(f"    • default_ports: {vast.network.default_ports}")

    print("\n  🎉 'vast' 래퍼 키가 자동으로 제거되어 바로 접근 가능!")

    # 12. VLLM 설정
    print_section("12. get_vllm_config()")
    vllm = get_vllm_config()
    print("\n⚙️ VLLM 설정:")
    vllm_dict = namespace_to_dict(vllm)
    print(json.dumps(vllm_dict, indent=2, ensure_ascii=False))

    # 13. 실제 사용 예제
    print_section("13. 💡 실제 코드 사용 예제")
    print("""
# ============================================
# SimpleNamespace로 속성 접근 (추천!)
# ============================================

from service.config_utils import (
    get_app_config, 
    get_openai_config, 
    get_vast_config
)

# 방법 1: 편의 함수 사용 (SimpleNamespace)
app = get_app_config()
print(app.environment)      # "development"
print(app.port)             # 8010
print(app.debug_mode)       # True

# 방법 2: OpenAI 설정
openai = get_openai_config()
print(openai.api_key)
print(openai.model_default)

# 방법 3: VAST 설정 (자동 언래핑!)
vast = get_vast_config()
print(vast.vllm.gpu_memory_utilization)  # 0.5
print(vast.vllm.port)                     # 12434
print(vast.image.name)                    # "cocorof/vllm-openai-xgen"

# ============================================
# Dict로 키 접근
# ============================================

from service.config_utils import get_category_config

# as_namespace=False로 dict 받기
app_dict = get_category_config("app", as_namespace=False)
print(app_dict["app"]["environment"])

# ============================================
# 특정 값만 가져오기
# ============================================

from service.config_utils import get_config_value

env = get_config_value("app.environment")
port = get_config_value("app.port", default=8000)
api_key = get_config_value("openai.api_key")

# ============================================
# 여러 값 한 번에
# ============================================

from service.config_utils import get_multiple_configs

configs = get_multiple_configs([
    "app.environment",
    "openai.api_key",
    "vast.vllm.port"
])
print(configs["app.environment"])
    """)

    print("\n" + "=" * 70)
    print("  ✅ 완료!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()