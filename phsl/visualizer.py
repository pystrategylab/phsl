import matplotlib.pyplot as plt
import numpy as np

# 1. 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei'] 
plt.rcParams['axes.unicode_minus'] = False

class PHSLVisualizer:
    """
    璇玑战略可视化标准库 (全量样本增强版)
    """
    
    def __init__(self, theme='dark'):
        # 修复：去掉了 @staticmethod，改为标准的构造函数
        # 设置 2026 科技感审美风格
        self.colors = ['#FFD700', '#FFA500', '#FF4500']  # 黄金、橙色、深橙（对应L1-L3）
        self.stab_color = '#00FFCC'                     # 稳定性曲线颜色
        if theme == 'dark':
            plt.style.use('dark_background')
        else:
            plt.style.use('seaborn-v0_8')

    @staticmethod
    def plot_truth_curve(prior, samples):
        """
        绘制 FRE 真相分布图 (体现全量样本颗粒感)
        """
        mean = np.mean(samples)
        std = np.std(samples)
        
        fig, ax = plt.subplots(figsize=(20, 14), facecolor='#0e1117')
        ax.set_facecolor('#0e1117')

        # 绘制原始样本直方图
        ax.hist(samples, bins=60, density=True, alpha=0.25, color='#00ffcc', 
                label='Monte Carlo Raw Samples')

        # 绘制理论真相曲线 (高斯分布)
        x = np.linspace(0, 1, 200)
        epsilon = 1e-9
        y = (1/((std + epsilon) * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean)/(std + epsilon))**2)
        ax.plot(x, y, color='#00ffcc', lw=3, label='Fitted Truth Curve')
        
        # 标记关键战略基准线
        ax.axvline(prior, color='#ff4b4b', linestyle='--', lw=2, label=f'Prior Logic: {prior:.2f}')
        ax.axvline(mean, color='#f6ff00', linestyle='-', lw=2, label=f'Final Truth Mean: {mean:.2f}')
        ax.axvline(mean, color='#00ffcc', linestyle='-', lw=2, label=f'std: {std:.2f}')
        ax.set_title("Xuanji Strategic Audit: Truth Distribution (FRE)", color='white', fontsize=14, pad=15)
        ax.set_xlabel("Probability of Success (Win Rate)", color='white')
        ax.set_ylabel("Density / Confidence", color='white')
        ax.set_xlim(0, 1)
        ax.grid(color='#444', linestyle=':', alpha=0.4)
        ax.tick_params(colors='white')
        ax.legend(facecolor='#1e1e1e', edgecolor='#444', labelcolor='white')
        
        plt.tight_layout()
        return fig

    def plot_sip_audit(self, physics, title_prefix="Strategic Hope Audit"):
        """
        [子图 1 拆分] 效能对冲审计：基准线 vs 战略杠杆 (SIP Analysis)
        """
        p = physics['p_range']
        ai_thr = physics.get('ai_threshold', 0.5)
        lev_options = physics.get('leverage_options', [1.0, 1.0, 1.0, 1.0])
        all_effs = physics.get('all_efficiencies', [])
        all_aps = physics.get('all_activation_aps', [])
        desc = physics.get('leverage_desc', "基于旧逻辑校准的战略反馈")

    # 创建独立的画布
        fig, ax1 = plt.subplots(figsize=(15, 8))
    
    # 绘制点火阈值线
        ax1.axhline(y=ai_thr, color='red', linestyle='--', alpha=0.4, label=f'Ignition Threshold ({ai_thr})', zorder=1)
    
    # 1. 绘制 L0 基准线 (灰色虚线)
        if len(all_effs) > 3:
            base_eff = all_effs[3]
            base_ap = all_aps[3]
            ax1.plot(p, base_eff, color='#888888', linestyle='--', linewidth=2, label='Baseline (L=1.0)', alpha=0.6, zorder=2)
            if base_ap:
                ax1.scatter(base_ap, ai_thr, color='#888888', s=60, zorder=2)
                ax1.annotate(f"Base AP: {base_ap:.1f}", (base_ap, ai_thr), xytext=(5, -15), 
                         textcoords='offset points', fontsize=9, color='#888888')

    # 2. 循环绘制 L1-L3 战略杠杆曲线
        colors = ['#FFD700', '#FF8C00', '#FF4500'] 
        for i in range(min(3, len(all_effs))):
            effs = all_effs[i]
            ap = all_aps[i]
            if effs is None: continue
        
            label = f"战略杠杆 L{i+1}: {lev_options[i]:.2f}"
            ax1.plot(p, effs, color=colors[i], linewidth=3, label=label, alpha=0.9, zorder=3)
        
            if ap:
                ax1.scatter(ap, ai_thr, color=colors[i], s=120, edgecolors='white', zorder=5)
                advance_str = ""
                if len(all_aps) > 3 and all_aps[3]:
                    advance = all_aps[3] - ap
                    advance_str = f"\n(提前: {advance:.1f})"
            
                ax1.annotate(f"AP{i+1}: P={ap:.1f}{advance_str}", (ap, ai_thr), 
                         xytext=(0, 15), textcoords='offset points', 
                         ha='center', fontsize=10, color=colors[i], fontweight='bold')

        ax1.set_title(f"{title_prefix} - 效能对冲 (杠杆前移审计)", fontsize=16, pad=20)
        ax1.set_ylabel("战略效能 (Effectiveness)", fontsize=12)
        ax1.set_xlabel("资源投入压强 (P)", fontsize=12) # 独立画时建议加上 X 轴标签
        ax1.set_ylim(0, 1.1)
        ax1.grid(alpha=0.1)
        ax1.legend(loc='lower right', frameon=True, framealpha=0.9)

        plt.tight_layout()
        return fig
    def plot_resilience_audit(self, physics):
        """
        [子图 2 拆分 - 终极升级版] 结构韧性审计：多轨降噪与致死红线沉降
        """
        p = physics['p_range']
        all_stabs = physics.get('all_stabilities', [])
        all_bps = physics.get('all_bps', [])
        all_thrs = physics.get('all_dynamic_thrs', [])
        lev_options = physics.get('leverage_options', [1.0, 1.0, 1.0, 1.0])

        # 创建独立的画布
        fig, ax2 = plt.subplots(figsize=(15, 8))

        # 1. 绘制 L-0 基准现实 (灰色)
        if len(all_stabs) > 3 and all_stabs[3] is not None:
            stabs_0 = all_stabs[3]
            bp_0 = all_bps[3]
            thr_0 = all_thrs[3]
            
            # 绘制 L-0 裸奔稳定性曲线与基准红线
            ax2.plot(p, stabs_0, color='#888888', linestyle='--', linewidth=2, label='L-0 现实基准 (Status Quo)', alpha=0.6, zorder=2)
            ax2.axhline(y=thr_0, color='#888888', linestyle=':', linewidth=1.5, alpha=0.5, zorder=1)
            
            if bp_0:
                ax2.scatter(bp_0, thr_0, color='#888888', s=60, zorder=3)
                ax2.annotate(f"现状基准 BP: P={bp_0:.1f}", (bp_0, thr_0), 
                             xytext=(5, -15), textcoords='offset points', fontsize=9, color='#888888')
                # 填充基准崩溃区
                ax2.fill_between(p, 0, stabs_0, where=(np.array(stabs_0) < thr_0), color='#888888', alpha=0.1)

        # 2. 循环绘制 L1-L3 战略杠杆防线 (带降噪减伤与红线沉降)
        colors = ['#FFD700', '#FF8C00', '#FF4500'] 
        for i in range(min(3, len(all_stabs))):
            stabs = all_stabs[i]
            bp = all_bps[i]
            thr = all_thrs[i]
            l_val = lev_options[i]
            
            if stabs is None: continue

            label = f"物理装甲 L{i+1}: {l_val:.2f}"
            
            # 绘制被装甲托起的坚挺曲线
            ax2.plot(p, stabs, color=colors[i], linewidth=3, label=label, alpha=0.9, zorder=4)
            # 绘制专属的沉降红线
            ax2.axhline(y=thr, color=colors[i], linestyle='-.', linewidth=1.5, alpha=0.7, zorder=1)

            if bp:
                ax2.scatter(bp, thr, color=colors[i], s=120, edgecolors='white', zorder=5)
                # 注释中同时标明 P 值和下潜后的新红线
                ax2.annotate(f"BP{i+1}: P={bp:.1f}\n(红线沉至 {thr:.1f}%)", (bp, thr), 
                             xytext=(10, 10), textcoords='offset points', fontsize=10, color=colors[i], fontweight='bold')

        ax2.set_title("结构稳定性审计 (降噪屏蔽与致死红线沉降)", fontsize=16, pad=20)
        ax2.set_xlabel("资源投入压强 (P)", fontsize=12)
        ax2.set_ylabel("系统稳定性 / 专属崩溃阈值 (%)", fontsize=12)
        ax2.set_ylim(0, 110)
        ax2.grid(alpha=0.1)
        ax2.legend(loc='lower left', frameon=True, framealpha=0.9)

        plt.tight_layout()
        return fig
    # visualizer.py 增量更新

    def plot_five_affairs_radar(self, scores, sector_name="战略板块"):
        """
        绘制孙子兵法“五事”雷达图 (能级分布)
        scores: dict, e.g., {'道': 8, '天': 7, '地': 9, '将': 6, '法': 8}
        """
        labels = list(scores.keys())
        values = list(scores.values())
        
        # 确保雷达图闭合
        num_vars = len(labels)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True), facecolor='#0e1117')
        ax.set_facecolor('#0e1117')
        
        # 绘制背景网格
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        
        # 填充与连线
        ax.plot(angles, values, color=self.stab_color, linewidth=2, linestyle='solid')
        ax.fill(angles, values, color=self.stab_color, alpha=0.25)
        
        # 设置刻度与标签
        ax.set_thetagrids(np.degrees(angles[:-1]), labels, color='white', fontsize=12)
        ax.set_ylim(0, 10)
        ax.set_rgrids([2, 4, 6, 8, 10], color='#444', fontsize=8)
        
        ax.set_title(f"【{sector_name}】五事能级审计", color='white', fontsize=14, pad=20)
        
        plt.tight_layout()
        return fig