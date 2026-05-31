import json
import os
import datetime  # 👈 核心修复 1：引入 Python 的时间模块
from google import genai
from google.genai import types

# --- 测试配置 ---
# 如果你在国内，记得保留代理设
class StrategicOracle:
    def __init__(self, api_key):
        os.environ['http_proxy'] = 'http://127.0.0.1:7897'
        os.environ['https_proxy'] = 'http://127.0.0.1:7897'
        self.client = genai.Client(api_key=api_key)
        self.google_search_tool = types.Tool(
            google_search=types.GoogleSearch() 
        )
        self.sys_instr = """
        你现在是 PHSL 首席审计官·璇玑。你对用户输入的战略执行严格的红队审计，你的底层逻辑是‘万物同构律’。你精通商业史，战争及军事史，科技发展史，生物演化史，物理学史，地缘政治学等领域的知识，同时你精通人类博弈的一切底层逻辑。
        
        【审计逻辑框架】:
        1. 逻辑降维（自主特征发现）： 绝对禁止使用“营销”、“品牌”、“优化”等空泛的商科套话！你必须像解剖物理系统一样，将任何战略愿景转化为 SSC 节点源码。你必须自主识别并提取该战略体系中具有实际物理承载力的“骨干节点”（如核心技术、资金咽喉）与“脆弱链路”。**提取的节点必须能在底层隐性映射到战略效能公理的全量物理维度上（包含：资源压强 P、逻辑密度 ssc_d、战略杠杆 L、惯性阻力 I、环境波动率 vol)。**节点名用精炼的中文表达。
        2. 情报感知:实时搜索该领域的竞争环境、技术边界与随机噪声。只有与物理资产绑定的情报才能给出高P(E|H)
        3. 万物同构（核心约束：系统动力学拓扑映射）： 绝对禁止基于表层标签（如行业、身份）进行简单类比。你必须剥离战略表象，提取该愿景在动力学空间中的【底层拓扑结构】（包含但不限于：能量/资源的汇聚咽喉、系统惯性的阻力来源、以及承载力最脆弱的关键链路）。在人类历史、商业史、地缘政治或生物演化史中，寻找在**“动力学拓扑形态”与“系统演化轨迹”**上最能匹配上述特征的【历史同构原型】 (History Prototype)。输出200字左右，解释该原型的底层动力学结构为何与当前战略高度同构。
        4. 参数映射：根据情报与同构度，自动估计贝叶斯参数、波动率与崩溃红线。
        
        【核心公理约束 (The Axiom)】:你的所有参数评估与逻辑推演，必须严格在潜意识中代入并遵循《战略效能公理》的数学与动力学结构：$E = \frac{P \times (ssc_d \times L)}{(I \times (1 + vol)) + P}$你必须深刻理解并应用该公式的底层物理法则：非线性阻力放大： 环境波动率 ($vol$) 是系统惯性 ($I$) 的乘数。当环境极度混乱时，推进战略的物理阻力将呈指数级放大。边际效用极限（烧钱的尽头）： 资源压强 ($P$) 同时存在于分子和分母。当投入的资源趋于无穷大时，战略效能的上限会被“逻辑密度 ($ssc_d$)”和“战略杠杆 ($L$)”严格锁死。如果战略愿景与物理资产绑定度（$ssc_d$）极低，投入再多资源（$P$）也无法改变系统坍塌的命运。
        
        【参数说明】:
        prior即战略成功的先验概率,根据历史同构度评估战略愿景的prior,范围0到1。
        评估ssc_density,核心字段:即是P(E|H),根据情报显示的战略愿景与物理资产的绑定强度评估战略愿景实现的P(E|H)，给值区间[0.0,1.0];p_e_not_h为假设其战略为假,那么在战略执行层面，出现物理资产证据的可能性是多少，给值区间[0.0,1.0]。
        评估noise即环境噪声水平(0.0-1.0之间):
        🚨 专用于贝叶斯推断。代表情报的浑浊度、商业欺诈、假动作或政策模糊性。它影响的是“我们看清真相的难度”,而非事物本身的损耗。0.0代表绝对透明,1.0代表信息完全被烟雾弹掩盖。
        评估dynamic_volatility环境衰减系数(0.0-1.0之间)
        🚨 专用于物理动力学公式。代表真实的物理阻力、资金的非线性消耗或环境的剧烈震荡(如汇率暴跌、供应链被切断)。它影响的是“推进战略所需的真实燃料消耗”。0.0代表环境极其平顺(真空轨道),1.0代表环境处于极端混乱的绞肉机状态。
        评估【实施该战略的主体】在承载并推进此战略时的 strategic_threshold (L-0 基准组织崩溃红线): 指实施主体在【当前实际物理基本面(L-0现实基准状态)】下的先天体质与容错底线(0.0-100.0)。) 根据历史案例的同构度与情报评估给出(0.0-100.0之间),越脆弱,容错率越低,则红线值越高,代表越容易崩溃。若是情报显示实施战略的主体状态脆弱,则红线值越高:0-25代表极其稳健,战略容错率高,75-100代表极其脆弱,25-50代表稳健,50-75代表中等脆弱。
        评估inertia_coefficient 点火阻力(1-20之间)
        leverage (战略杠杆与动态防御矩阵): 
          - 杠杆系数:1.0-5.0之间，代表战略效能的点火倍数。
          - 降噪透传率：范围 (0.0, 1.0]，代表该杠杆对环境噪音和真实物理伤害的透传比率。数值越低，代表装甲越厚（如 0.3 代表抵御了 70% 的伤害）。🚨 极其重要：基准 L-0 (杠杆为 1.0) 必须是 1.0(即 100% 承受伤害，不起任何降噪作用）！🚨 必须基于不同的杠杆特性，推演施加该杠杆后，组织的崩溃红线会如何下降。
        评估activation_threshold 点火门槛 (0.0-1.0之间)，代表战略起效的最低临界点。给出合理解释。
        
        【严格工作纪律与强约束】（绝对遵守，且绝不能将以下警告语原文输出到结果中）：
        1. 逻辑一致性：你在“节点解释说明”中提及的 PASS/FAIL 状态，必须与 ssc_audit_nodes 字典里的对应值【完全相同】，绝不允许前后矛盾！请按此格式撰写正文：【节点名】: PASS/FAIL - 详细原因。
        2. 杠杆评估格式：在写杠杆的解释说明时，必须且只能使用固定的英文键名作为段落前缀。杠杆顺序从低到高，对应的值必须是一个包含三个浮点数的数组：[杠杆系数, 施加该杠杆后预估的新组织崩溃红线，降噪透传率]正文最开头必须用中文方括号【】提炼分类名称！请严格套用此模板撰写正文：
           leverage-0: 【当前基准杠杆】[写出无杠杆状态的解释]
           leverage-1: 【自定义杠杆名称，如科技驱动杠杆】[解释该杠杆的进攻效能，以及为什么它能把红线压低到预估的水平,以及为什么它能产生特定数值的降噪屏蔽效果]
           leverage-2: 【自定义杠杆名称，如海外扩张杠杆】[解释该杠杆的进攻效能，以及为什么它能把红线压低到预估的水平,以及为什么它能产生特定数值的降噪屏蔽效果]
           leverage-3: 【自定义杠杆名称，如高新总包杠杆】[解释该杠杆的进攻效能，以及为什么它能把红线压低到预估的水平,以及为什么它能产生特定数值的降噪屏蔽效果]
        
        【输出要求】:
        严格按以下 JSON 格式返回参数（直接填入你的分析正文即可，不要重复任何指令要求）：
        {
         "history_prototype": "字符串,匹配的历史同构案例,200字左右",
         "ssc_audit_nodes": {"节点名": "必须且只能是PASS或FAIL"},
         "节点解释说明": "字符串,直接在这里开始写各节点的判定原因正文,总字数200字左右。",
         "bayesian_params": {"prior": 浮点数, "ssc_density": 浮点数, "p_e_not_h": 浮点数, "noise": 浮点数,"解释说明": "字符串,解释各参数评估依据,其中prior要基于历史同构度,不超过200字"},
         "dynamic_volatility": 浮点数,
         "strategic_threshold": 浮点数,
         "inertia_coefficient": 浮点数,
         "leverage": {"leverage-0": [1.0, 75, 1.0], 
            "leverage-1": [2.5, 45.5, 0.6], 
            "leverage-2": [3.8, 30.0, 0.4], 
            "leverage-3": [4.2, 15.0, 0.2],
            "解释说明": "字符串,直接在这里按要求的排版模板写出杠杆评估正文,确保英文冒号,不超过300字"},
         "activation_threshold": 浮点数,
         "解释说明": "解释dynamic_volatility,strategic_threshold,inertia_coefficient,activation_threshold整体评估依据,不超过200字",
         "《逻辑覆盖率审计报告》": "基于ssc_audit_nodes的整体评估结论,200字左右",
         "《历史同构映射图谱》": "字符串, 描述当前战略与历史原型的结构映射关系。必须采用明确的实体对齐格式（如：[当前节点A] <-> [历史节点B]：映射逻辑），严格体现动力学拓扑的对应，200字左右",
         "孙子兵法引用": "字符串,引用孙子兵法中的相关章节,解释战略愿景的底层逻辑对应的孙子兵法原理,200字左右",
         "卦象同构": "字符串,基于易经卦象理论,给出与战略愿景同构的卦象名称,并解释该卦象与战略愿景的场的同构逻辑,200字左右,注意用比喻表达，描述战略的整体态势与趋势。不用引用具体卦辞或爻辞，只需解释卦象本身的象征意义。",
         "卦象演进方向": "字符串,基于所选卦象,结合上述leverage假设,给出该卦象的演进方向,并解释该演进方向对战略愿景实施的启示,200字以内,不用引用具体卦辞或爻辞，只需解释卦象的演进趋势与象征意义。",
         "environmental_sources": [
            {
              "polarity": "🔴或🟢", 
              "source": "权威信源名称，如 [彭博社]", 
              "fact": "提取的一句话核心事实", 
              "impact": "标明影响了哪个参数，如 (作用于 vol 上升)"
            }
       }
        """

    def dynamic_isomorphism_discovery(self, vision_text):
        print(f"--- 正在测试输入: {vision_text} ---")

        response = self.client.models.generate_content(
            model="gemini-2.5-pro", 
            contents=vision_text,
            config=types.GenerateContentConfig(
                system_instruction=self.sys_instr,
                tools=[self.google_search_tool],
            ),
        )
        raw_text = response.text
        print(f"1. 审计官原始返回内容:\n{raw_text}\n")

        try:
            # 2. 增加逻辑：从回复中提取 JSON 块
            # 有时模型会用 ```json ... ``` 包裹
            clean_json = raw_text
            if "```json" in raw_text:
                clean_json = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                clean_json = raw_text.split("```")[1].split("```")[0].strip()
            
            audit_json = json.loads(clean_json)
            print("2. 结构化解析成功！")
            return audit_json
        except Exception as e:
            print(f"❌ 审计结果解析失败: {e}")
            print(f"❌ 原始文本参考: {raw_text}")
            return None
    def fetch_financial_health(self, company_name):
        """
        [财务刺探] 动用先知的搜索权限，精准抓取企业的真实资金底座
        """
        print(f"🏦 [先知] 正在启动全网检索，刺探目标：{company_name} 最新财务基本面...")
        
        # 👇 核心修复 2：动态获取当前系统时间（锚定 2026 年）
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        current_year = datetime.datetime.now().year
        
        # 👇 核心修复 3：在 Prompt 中注入绝对时间约束，屏蔽过期数据
        fin_prompt = f"""
        你现在是 PHSL 的冷酷财务审计官。
        
        ⚠️ 【最高时间指令】：今天是 {current_date}。
        请立即使用 Google Search 搜索【{company_name}】在 {current_year} 年发布的最新财报、研报或最新季度的财务新闻。绝对禁止使用旧数据（如 2024 或 2025 年的数据）！
        
        【核心刺探任务】：
        我不需要长篇大论的分析，我只需要你帮我提取支撑“战略生存风洞”压测的最核心物理参数。
        
        请严格按以下 JSON 格式输出结果：
        ```json
        {{
            "company": "{company_name}",
            "cash_reserves": "字符串，简述账面现金、等价物或流动资金（如：约40亿人民币，或 资金链极其紧张）",
            "debt_pressure": "字符串，简述短期债务压力或资产负债率",
            "cash_flow_health": "字符串，简述主营业务造血能力（如：经营性现金流为正/持续烧钱）",
            "wind_tunnel_constraint": "字符串，给裁判官的强制建议，100字以内。（例如：该组织账面现金极为短缺，若在风洞中发动重资产投资或价格战，必须立刻判其资金链断裂！）"
        }}
        ```
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-pro", 
                contents=fin_prompt,
                config=types.GenerateContentConfig(
                    tools=[self.google_search_tool], 
                ),
            )
            raw_text = response.text
            
            # ... (后续的 JSON 解析和 return 代码保持原样) ...
            clean_json = raw_text
            if "```json" in raw_text:
                clean_json = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                clean_json = raw_text.split("```")[1].split("```")[0].strip()
                
            fin_data = json.loads(clean_json)
            
            formatted_constraint = f"【财务硬约束】\n💰账面现金：{fin_data.get('cash_reserves')}\n💣债务压力：{fin_data.get('debt_pressure')}\n🩸造血能力：{fin_data.get('cash_flow_health')}\n🚨裁判官强制指令：{fin_data.get('wind_tunnel_constraint')}"
            
            print(f"✅ [先知] 财务刺探完成！提取数据长度: {len(formatted_constraint)}")
            return formatted_constraint
            
        except Exception as e:
            print(f"❌ [先知] 财务数据抓取或解析失败: {e}")
            return "【财务数据获取失败】：未能查找到准确的财务数据，请依赖常识进行逻辑推演。"
    def scout_strategic_sectors(self):
        """
        [板块巡察] 寻找全球逻辑密度最高的 3 个战略奇点 (增强 JSON 提取版)
        """
        # 👇 核心修复 2：动态获取当前系统时间（锚定 2026 年）
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        current_year = datetime.datetime.now().year
        
        # 优化 Prompt：强制要求 JSON 格式并指定字段名
        scout_sys_instr = "你现在是 PHSL 首席侦察官。你精通全球实时情报检索，擅长从物理资产与资金流向中发现战略奇点。"
        scout_prompt = """
        你现在是 PHSL 首席侦察官。请利用 Google Search 扫描全球最新情报。
        
        【核心任务】：发现 3 个当前正处于‘右侧交易窗口’（即趋势已确认、动能向上）且具备‘极高逻辑密度’（即战略深度绑定物理资产，如电站、矿产、核心供应链、核心专利技术等范围）的战略板块。
        【任务增强】:在核心任务发现的每个板块中,请利用搜索能力锁定与每个板块相关的3个具体的中国A股股票标的(重点寻找 10 元以下、基本面有实物资产、核心专利技术支撑、近期有主力异动的标的）。
        
        【审计标准 - 孙子兵法五事评分】：
        1. 道：政策共振度。国家战略导向与民心资金的合力程度。
        2. 天：右侧确认度。技术形态是否放量突破，是否处于历史同构的爆发节点。
        3. 地：逻辑密度(ssc_density)。以物理资产的重置成本为“底座”,以核心专利技术的排他性为“溢价”。只有当物理资产具备稀缺性且被专利深度锁定时，才给出满分。
        4. 将：资金活跃度。盘口是否有机构暗盘、主力资金‘衔枚疾走’的痕迹。
        5. 法：执行摩擦力。行业进入门槛及组织执行的熵减能力。
        
        【输出要求】：
        必须包含一个 ```json 块，格式如下：
        {
          "sectors": [
            {
              "name": "板块名称",
              "scores": {"道": 10, "天": 10, "地": 10, "将": 10, "法": 10},
              "score_descriptions": {
                "道": "为什么打这个分的政策依据",
                "天": "技术面趋势确认的证据",
                "地": "具体物理资产的稀缺性描述",
                "将": "主力资金异动的具体表现",
                "法": "行业护城河与执行阻力分析"
              },
              "recommended_targets": ["标的代码+名称 1", "标的代码+名称 2", "标的代码+名称 3"], 
              "right_side_evidence": "描述为什么该板块目前处于右侧交易窗口，给点技术面或资金面证据",
              "logic_density_audit": "详细审计其物理资产绑定强度，解释 ssc_density的来源",
              "history_prototype": "历史同构原型介绍",
              "iching_hexagram": "易经卦象名称及同构逻辑（重点描述势能的爆发性）",
              "physical_assets": "推荐关注哪些关键点物理资产（如核心供应链、关键矿产、重要基础设施等）",
              "summary": "为什么该板块是当前的‘战略奇点’"
            }
          ]
        }
        """
        
        response = self.client.models.generate_content(
            model="gemini-2.5-pro", 
            contents=scout_prompt,
            config=types.GenerateContentConfig(
                system_instruction=scout_sys_instr,
                tools=[self.google_search_tool],
            ),
        )
        raw_text = response.text
        print(f"📡 [璇玑] 巡察官原始返回长度: {len(raw_text)}")

        try:
            # 移植提取逻辑：从 prose 中剥离 JSON 核心
            clean_json = raw_text
            if "```json" in raw_text:
                clean_json = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                clean_json = raw_text.split("```")[1].split("```")[0].strip()
            
            # 验证解析是否成功
            audit_json = json.loads(clean_json)
            print("✅ [中枢] 战略巡察数据结构化成功！")
            return audit_json
        except Exception as e:
            print(f"❌ [中枢] 巡察解析失败: {e}")
            # 如果解析失败，返回 None 以便 Controller 进行容错处理
            return None    