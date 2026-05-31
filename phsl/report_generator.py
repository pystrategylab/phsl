import matplotlib.pyplot as plt
import time
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei'] 
plt.rcParams['axes.unicode_minus'] = False

class StrategicReportGenerator:
    def __init__(self, visualizer):
        self.viz = visualizer

    def generate_all_domain_report(self, audit_data, strategy_name="Unnamed Strategy"):
        """
        生成全领域审计简报 (希望版/L-0 对冲校准)
        """
        physics = audit_data['physics_results']
        report = audit_data['audit_report']
        
        # 1. 打印指挥官简报标题
        print(f"\n{'='*70}")
        print(f"🏛️  璇玑通用战略原型机 - 全领域审计简报：{strategy_name}")
        print(f"📅 审计时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📂 核心公式: E = (P * (ssc_d * L)) / ((I * (1 + vol)) + P)")
        print(f"{'='*70}\n")

        # 2. 战略背景判词 (AI 叙事层)
        print(f"【首席审计官判词】: \n> {physics.get('leverage_desc', '无数据')}\n")
        
        # 3. 物理量纲审计 (对冲阻力层)
        i_val = report.get('inertia_coefficient', 0)
        vol_val = physics.get('volatility', 0)
        effective_r = i_val * (1 + vol_val)
        
        print(f"【物理量纲审计报告】:")
        print(f" 🚀 资源投入增益: {physics.get('ssc_density', 'N/A')} (ssc_density)")
        print(f" ⛓️ 环境惯性阻力 (I): {i_val}")
        print(f" 🌪️ 地缘波动摩擦 (vol): {vol_val}")
        print(f" 🛡️ 综合对冲阻力 (R): {effective_r:.2f} [I * (1+vol)]")
        print(f" 🚩 组织崩溃红线 (BP): {physics.get('applied_threshold', 'N/A')}%")
        
        # 4. 点火点 AP 横向对冲 (修正 L4 为 L-0)
        levers = physics.get('leverage_options', [])
        aps = physics.get('all_activation_aps', [])
        
        print(f"\n【点火点 AP 横向对冲 & 效能提前量】:")
        
        # 提取 L-0 基准 (假设 L-0 是列表的最后一项，且杠杆为 1.0)
        base_ap = aps[3] if len(aps) > 3 else None
        
        for i in range(len(levers)):
            L = levers[i]
            ap = aps[i]
            
            # 识别 L-0 基准
            if i == 3 or L == 1.0:
                label = f"L-0 基准锚点"
                status = f"P={ap:.2f}" if ap else "!!! 无法点火 (战略死区) !!!"
                print(f" 🔸 {label} (杠杆 {L:.2f}): {status}")
            else:
                label = f"预案 L{i+1}"
                if ap:
                    # 计算相对于 L-0 的提前量 (节省的压强 P)
                    if base_ap:
                        advance = base_ap - ap
                        advance_str = f" [较基准提速: {advance:.2f} P单位]"
                    else:
                        advance_str = " [基准失效，此杠杆为唯一生机]"
                    print(f" 🔹 {label} (杠杆 {L:.2f}): P={ap:.2f}{advance_str}")
                else:
                    print(f" 🔹 {label} (杠杆 {L:.2f}): !!! 效能不足，无法点火 !!!")

        # 5. 调用通用绘图模块进行可视化
        # 绘制逻辑稳健性图 (FRE)
        self.viz.plot_truth_curve(physics['mean'], physics['samples'])
        
        # 绘制点火与崩溃对冲图 (SIP + ERT)
        self.viz.plot_split_audit(physics, strategy_name)

        print(f"\n{'='*70}")
        print(f"🚨 审计完成。指挥官，L-0 的失效证明了您施加战略杠杆的必然性。")
        print(f"🎯 建议优先部署点火前移量最大的预案。")
        print(f"{'='*70}\n")