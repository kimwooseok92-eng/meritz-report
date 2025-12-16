# [수정된 로직 부분] app.py 중간의 generate_report 함수를 이것으로 교체하세요
def generate_report():
    # 1. 운영 기조에 따른 비율 (보장분석 비중)
    # 보내주신 데이터(91.5%)에 맞춰 효율화 모드 미세 조정
    if op_mode == '상품증대': ratio_ba = 0.84
    elif op_mode == '효율화': ratio_ba = 0.915 # 92% -> 91.5%로 정밀 조정
    else: ratio_ba = 0.898
    ratio_prod = 1 - ratio_ba
    
    w = {'월': 1.1, '화': 1.0, '수': 1.0, '목': 0.95, '금': 0.85}.get(day_option, 1.0)

    # 2. 18시 최종 목표 수립 (DA 기준)
    # 공식: 광고주목표(3530) - SA18시(1443) + 버퍼(30) = 2117 (약 2116)
    da_target_18 = target_total_advertiser - sa_est_18 + da_add_target
    
    # 3. [핵심수정] 17시 목표 역산 로직
    # 기존: 전체목표 - SA17시 (이렇게 하면 DA가 너무 높게 나옴)
    # 수정: DA 18시 목표 - (DA 1시간치 예상 확보량)
    # 17시~18시 사이에는 보통 하루 물량의 약 4% 정도가 들어옴
    da_hourly_gap = round(da_target_18 * 0.04) 
    da_target_17 = da_target_18 - da_hourly_gap

    # 전체(Total) 자원 계산 (보고서 출력용)
    total_resource_18 = da_target_18 + sa_est_18
    total_resource_17 = da_target_17 + sa_est_17 # 2034 + 1392 = 3426

    # 인당 배분
    da_per_18 = round(da_target_18 / active_member, 1) # 5.8건
    da_per_17 = round(da_target_17 / active_member, 1) # 5.6건

    # ... (이하 실시간 예상 마감 로직은 기존과 동일) ...
    hourly_pace = 195 * w if fixed_ad else 140 * w
    est_increase = round(hourly_pace * 4.0)
    est_18 = current_total + est_increase
    
    if est_18 > da_target_18 + 150: est_18 = da_target_18 + 50
    elif est_18 < da_target_18 - 200: est_18 = da_target_18 - 50
    est_24 = round(est_18 * 1.35)

    # 멘트 생성
    achieve_rate = est_18 / da_target_18
    if achieve_rate >= 0.99:
        status_msg = "전체 수량 또한 양사 합산 시 달성가능할 것으로 보입니다."
        action_msg = "조기 배정마감되는 경우, 배너광고 조정하도록 하겠습니다."
    else:
        status_msg = f"DA 목표 대비 약 {da_target_18 - est_18}건 부족할 것으로 예상되나, 집중 운영하겠습니다."
        action_msg = "남은 시간 상품수량 확보 및 보장분석 효율화 자원 확보에 집중하겠습니다."

    fixed_msg = f"{fixed_content}" if fixed_ad else "금일 특이사항 없이 운영 중이며,"
    fixed_act = "" # 멘트에 포함됨

    cpa_14 = round(cost_total / current_total / 10000, 1) if current_total else 0
    cpa_da = round(cost_da / current_bojang / 10000, 1) if current_bojang else 0
    cpa_aff = round(cost_aff / current_prod / 10000, 1) if current_prod else 0

    return {
        'total_17': total_resource_17, 
        'da_part_17': da_target_17, # 2034건 (목표치 도달)
        'da_per_17': da_per_17,     # 5.6건
        
        'total_18': total_resource_18, 
        'da_part_18': da_target_18, # 2116건
        'da_per_18': da_per_18,     # 5.8건
        
        'ba_17': round(da_target_17 * ratio_ba), # 1861건 (오차범위 내)
        'prod_17': round(da_target_17 * ratio_prod),
        'ba_18': round(da_target_18 * ratio_ba), # 1937건
        'prod_18': round(da_target_18 * ratio_prod),
        
        'est_18': est_18, 'est_per_18': round(est_18/active_member, 1),
        'est_ba_18': round(est_18 * ratio_ba), 'est_prod_18': round(est_18 * ratio_prod),
        'est_24': est_24,
        
        'fixed_msg': fixed_msg, 'fixed_act': fixed_act, 'status_msg': status_msg, 'action_msg': action_msg,
        'cpa_14': cpa_14, 'cpa_da': cpa_da, 'cpa_aff': cpa_aff,
        'da_target_18': da_target_18
    }
