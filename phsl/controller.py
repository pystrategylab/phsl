from .engine import XuanjiEngine
from .oracle import StrategicOracle

class XuanjiController:
    def __init__(self, oracle, engine):
        self.oracle = oracle
        self.engine = engine    
    def run_strategic_scout(self):
        """
        [新增] 执行板块战略巡察逻辑
        功能：调用先知模块的主动侦察功能，获取全球战略板块的五事能级 JSON。
        """
        # 调用 Oracle 模块中新增的 scout_strategic_sectors 方法
        scout_json = self.oracle.scout_strategic_sectors()
        
        if not scout_json:
            print("🚨 [中枢] 巡察指令未获得有效数据包，全球雷达扫描中断。")
            return None
        
        # 返回结构化数据供 App.py 进行雷达图渲染
        return scout_json
    
    def execute_full_audit(self, vision_text):
        audit_json = self.oracle.dynamic_isomorphism_discovery(vision_text)
        if not audit_json:
            print("🚨 [中枢] 收到空数据包，物理压测无法点火。请检查网络或 API 配置。")
            return None
            
        # ==========================================
        # 1. 提取基础参数与 3 维杠杆矩阵
        # ==========================================
        vol = audit_json.get('dynamic_volatility', 0.22)
        thr = audit_json.get('strategic_threshold', 38.2)
        ine = audit_json.get('inertia_coefficient', 10.0)
        b = audit_json.get('bayesian_params', {})
        lev_bundle = audit_json.get('leverage', {})
        leverage_desc = lev_bundle.get('解释说明', "无")
        ai_thr = audit_json.get('activation_threshold', 0.5) 
        
        # 提取 [点火杠杆, 专属红线, 降噪透传率]
        levers_data = [
            lev_bundle.get('leverage-1', [1.0, thr, 1.0]),
            lev_bundle.get('leverage-2', [1.0, thr, 1.0]),
            lev_bundle.get('leverage-3', [1.0, thr, 1.0]),
            lev_bundle.get('leverage-0', [1.0, thr, 1.0])
        ]
        levers = [data[0] for data in levers_data]

        # ==========================================
        # 2. 物理压测 1：ERT 结构韧性压测 (盾)
        # ==========================================
        ert_results = [
            self.engine.run_ert_stress_test(vol, specific_threshold=data[1], noise_multiplier=data[2])
            for data in levers_data
        ]
        # 🌟 关键解包：将数据拆解给前端绘图用
        all_stabs = [r[0] for r in ert_results]
        all_bps = [r[1] for r in ert_results]
        all_dynamic_thrs = [r[2] for r in ert_results]
        
        # ==========================================
        # 3. 贝叶斯对冲与 物理压测 2：SIP 点火效能 (矛)
        # ==========================================
        refined_density = self.engine.refine_density_with_bayesian(
            b.get('prior', 0.5), b.get('ssc_density', 0.5), 
            b.get('p_e_not_h', 0.2), b.get('noise', 0.1)
        )
        
        sip_results = [
            self.engine.calculate_activation_threshold(refined_density, ine, data[0], ai_thr, vol)
            for data in levers_data
        ]
        all_effs = [r[0] for r in sip_results]
        all_aps = [r[1] for r in sip_results]
        
        # ==========================================
        # 4. FRE 蒙特卡洛真理验证
        # ==========================================
      
        samples, mean, std = self.engine.run_fre_validation(refined_density, vol)
        # ==========================================
        # 5. 封包传出
        # ==========================================
        res = {
            'p_range': self.engine.p_range, 
            
            # 🌟 新增：防守数据矩阵 (前端画多条下沉红线全靠它)
            'all_stabilities': all_stabs,       
            'all_bps': all_bps,                 
            'all_dynamic_thrs': all_dynamic_thrs, 
            
            # 🌟 新增：进攻数据矩阵
            'all_efficiencies': all_effs, 
            'all_activation_aps': all_aps,
            
            # 兜底旧字段 (防止其他老代码报错)
            'stabilities': all_stabs[0], 
            'efficiencies': all_effs[0], 
            'break_point': all_bps[0], 
            'activation_p': all_aps[0], 
            'applied_threshold': thr,
            'samples': samples, 
            'mean': mean, 
            'std': std, 
            'volatility': vol, 
            'leverage': levers[0], 
            'leverage_desc': leverage_desc, 
            'leverage_options': levers, 
            'ai_threshold': ai_thr
        }
        return {"audit_report": audit_json, "physics_results": res}