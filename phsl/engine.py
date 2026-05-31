import numpy as np

class XuanjiEngine:
    def __init__(self):
        # 统一采样分辨率，解决绘图对齐问题
        self.p_range = np.linspace(0, 25, 500)
        self.nodes = {} 
        self.audit_results = {}

    @staticmethod
    def refine_density_with_bayesian(prior, p_e_h, p_e_not_h, noise):
        """贝叶斯噪声对冲核心"""
        p_e_h_n = (p_e_h * (1 - noise)) + (0.5 * noise)
        p_e_not_h_n = (p_e_not_h * (1 - noise)) + (0.5 * noise)
        p_e = (p_e_h_n * prior) + (p_e_not_h_n * (1 - prior))
        return (p_e_h_n * prior) / p_e if p_e != 0 else prior

    def run_ert_stress_test(self, volatility, specific_threshold=38.2, noise_multiplier=1.0):
        """
        ERT 压测：接收 Oracle 动态估计的【专属红线】与【降噪透传率】
        noise_multiplier: 1.0 代表不降噪 (L-0),0.2 代表只承受 20% 伤害
        """
        if specific_threshold is None: 
            specific_threshold = 38.2
            
        # 🛡️ 物理装甲生效：环境破坏力直接乘以透传率 (noise_multiplier)
        # 如果是 L-0，乘数是 1.0，原样承受波动伤害
        stabilities = [100 - (p**2 * volatility * noise_multiplier) for p in self.p_range]
        
        # 寻找对应的独立崩溃交点 BP
        bp = next((p for p, s in zip(self.p_range, stabilities) if s <= specific_threshold), None)
        
        # 🚨 极其重要：这里必须返回 3 个值！因为前端画图需要用到这根动态红线
        return stabilities, bp, specific_threshold

    def calculate_activation_threshold(self, ssc_density, inertia_coefficient, leverage=1.0, ai_threshold=None, volatility=None):
        """
        SIP 压测：计算点火点
        ai_threshold: 由 AI 估计的起效门槛 (0.0 - 1.0)
    
        """
        effective_resistance = inertia_coefficient * (1 + volatility)
        # 计算效能分布
        efficiencies = [(p * (ssc_density * leverage)) / (effective_resistance + p) for p in self.p_range]
        
        # 寻找第一个超过 AI 设定门槛的压强点
        # 这里的 0.5 被替换成了动态的 ai_threshold
        ap = next((p for p, e in zip(self.p_range, efficiencies) if e >= ai_threshold), None)
        
        return efficiencies, ap
    
    def run_fre_validation(self, prior_base, vol, iterations=10000):
        """FRE 验证：蒙特卡洛真相模拟"""
        samples = np.random.normal(prior_base, vol, iterations)
        samples = np.clip(samples, 0, 1)
        return samples, np.mean(samples), np.std(samples)
    