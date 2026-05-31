import json
import time
import asyncio
import random
import numpy as np
from google import genai
from google.genai import types

class StrategicArena:
    def __init__(self, api_key, max_rounds=2):
        """
        璇玑多智能体对抗沙盘 (异步并发 + 战报封存版)
        """
        self.client = genai.Client(api_key=api_key)
        # 👇 核心修复 3：初始化时强制抹掉可能存在的小数点
        self.max_rounds = int(max_rounds)
    # 👇 新增：防熔断的安全调用包装器
    # 在参数里加上 model_name，默认使用 flash
    def _safe_api_call(self, prompt, is_json=False, max_retries=3, model_name="gemini-2.5-flash"):
        """带有指数退避、强制冷却和多发引擎切换的安全调用"""
        for attempt in range(max_retries):
            try:
                # 即使是 Flash，也保留极其微小（0.5秒）的错峰，保证绝对稳定
                time.sleep(random.uniform(0.1, 0.5)) 
                
                if is_json:
                    config = types.GenerateContentConfig(response_mime_type="application/json")
                    response = self.client.models.generate_content(
                        model=model_name, # 👈 使用传入的模型
                        contents=prompt,
                        config=config
                    )
                else:
                    response = self.client.models.generate_content(
                        model=model_name, # 👈 使用传入的模型
                        contents=prompt
                    )
                return response.text
                
            except Exception as e:
                print(f"⚠️ API 遭到拦截/断联 (尝试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    sleep_time = 2 ** (attempt + 1)
                    print(f"⏳ 正在冷却引擎，等待 {sleep_time} 秒后重试...")
                    time.sleep(sleep_time)
                else:
                    raise Exception(f"🚨 彻底熔断!API 连续 {max_retries} 次调用失败。")
    def red_agent_turn(self, strategy, round_num, current_stability, context, leverage_desc="无特殊杠杆", use_financial_report=False, financial_data="",current_cash=None):
        # 🌟 动态切换：财报约束 与 存量盘点指令
        fin_constraint = ""
        # 默认模式（纯逻辑推演）的存量指令
        stock_prompt = "1. 🛡️ 【物理存量】：我方的老本（资金、资源、品牌资产）还剩多少？⚠️ 警告：你必须根据【上一回合历史记忆】评估你的资源消耗！"
        
        # 🏦 Python 强制财务账本介入
        if use_financial_report and current_cash is not None:
            fin_constraint = f"""
        💰 【系统强制财务账本（绝对真理）】：
        系统查账显示，你当前可用现金精确余额为：【{current_cash:.2f} 亿元】。
        ⚠️ 警告：这是物理铁律！如果你的动作耗资超过这个数字，你将直接破产！
            """
            stock_prompt = f"1. 🛡️ 【物理存量】：系统提示我方账上仅剩 {current_cash:.2f} 亿元。我必须基于这个数字量力而行。"
            
        # 💰 财报约束动态注入
        fin_constraint = ""
        if use_financial_report and financial_data:
            fin_constraint = f"""
        💰 【真实财务铁律】：
        以下是你的真实财务底牌，你【必须】根据账面现金流和资产负债情况量力而行：
        {financial_data}
        ⚠️ 警告：绝不允许战略幻觉！如果你的动作超出了财报支撑极限，你将被系统直接抹杀。
            """
            # 财报模式（硬核资金盘点）专属存量指令
            stock_prompt = "1. 🛡️ 【物理存量】：我方账面资金还剩多少？⚠️ 警告：你必须根据【上一回合历史记忆】中你自己的花费，对初始财报数据进行扣减！绝不允许拿着同一笔钱花两次！"
            
        prompt = f"""
        你现在是以下战略的【绝对主导者与执行方】（第一人称视角）：
        核心战略设定：【{strategy}】
        🛡️ 核心底牌与物理装甲：【{leverage_desc}】
        
        📊 【系统遥测仪表盘】：
        - 当前交锋回合：第 {round_num} 回合
        - 当前组织稳定性（总体生命值）：{current_stability:.1f}% 
        {fin_constraint} 
        【当前环境态势】
        {context}
        
        ⚠️ 请严格按照以下两步逻辑进行思考和输出（总字数控制在 150 字以内）：
        
        【第一步：三维体征自检】(存量、增量与调动通道)
        蓝方正在对你进行攻击，你必须根据蓝方的攻击，极其冷酷地盘点你真实的资源现状。必须明确评估以下三个维度：
        {stock_prompt}
        2. 🩸 【造血增量】：我方的未来血液（如：新订单、流水）是否已断裂？
        3. ⛓️ 【调动通道（节点）】：最关键的！蓝方是否切断了我的传输节点？我的存量资产是随时可用的，还是被冻结的“远水”？
        
        【第二步：基于三维自检的战术动作】(知行合一)
        - 若【通道被切断（有存量无法调动）】：你【绝对不能】直接使用被冻结的存量发起反击！你必须优先消耗其他资源去“打通节点”、“建立地下通道”或“寻找极其昂贵的替代物流”。
        - 若【双双重创】：无权反攻，只能极其凄惨地断尾求生。
        (你的动作必须符合严丝合缝的物理与后勤常识！)
        ```json
        {{
            "self_check": "第一步：三维体征自检的简要描述",
            "action": "第二步：战术动作的简要描述",
            "cost_incurred": (本次动作预计消耗的现金。纯数字浮点数，以'亿'为单位。如果不花钱填 0.0)
        }}
        ```
        """
        raw_text = self._safe_api_call(prompt, is_json=False, model_name="gemini-3-flash-preview")

        # 👇 核心修复：引入 JSON 清洗并强制返回 (动作, 花费) 双变量
        try:
            clean_text = raw_text.strip()
            if clean_text.startswith("```json"): clean_text = clean_text[7:]
            elif clean_text.startswith("```"): clean_text = clean_text[3:]
            if clean_text.endswith("```"): clean_text = clean_text[:-3]
                
            red_data = json.loads(clean_text.strip())
            
            # 将自检结果与战术动作合并，让战报和记忆链更加丰满
            self_check = red_data.get('self_check', '')
            action_desc = red_data.get('action', '强制保守防御，维持生命线。')
            cost = float(red_data.get('cost_incurred', 0.0))
            
            final_action = f"【三维自检】{self_check}\n> 【战术动作】{action_desc}" if self_check else action_desc
            
            return final_action, cost
            
        except Exception as e:
            print(f"⚠️ 红方生存风洞 JSON 解析失败: {e}")
            return "强制保守防御，维持生命线。", 0.0
       
    # 🌟 修复：新增 round_num 和 max_rounds 参数，引入战争迷雾
    def blue_agent_turn(self, strategy, red_action, historical_prototype="无特定原型", round_num=1, max_rounds=2):
        
        # 🌪️ 动态烈度与随机性引擎
        if round_num == 1:
            attack_mode = "【盲盒摩擦（高度随机性）】：你现在处于战争迷雾中，不知道红方的致命弱点。请基于历史同构原型，制造一场【随机的、无差异的宏观波动或常规竞争摩擦】（例如：全行业原材料普涨、汇率波动、新规草案出台）。⚠️ 绝对不要进行极其精准的定向狙击！"
        elif round_num < max_rounds:
            attack_mode = "【战术试探（针对性增强）】：红方在上一轮的行动中不可避免地暴露了资源调动轨迹。请分析其刚刚的动作，寻找其防线的薄弱环节，发动一次中等烈度的【针对性商业阻击或围堵】。"
        else:
            attack_mode = "【终极绞杀（致命降维）】：扯下伪装！结合历史同构的深层规律，直接锁定红方在之前回合中暴露出的最致命断裂点（资金链、核心节点或技术底座），发动一次极其凶狠的【极端黑天鹅或结构性摧毁打击】！"

        prompt = f"""
        你是客观环境与竞争对手的无情集合体（蓝方）。
        面对红方战略：【{strategy}】
        红方刚刚应对的动作：【{red_action}】
        先知锁定的历史同构规律：【{historical_prototype}】
        
        🌪️ 【当前环境生成法则】：{attack_mode}
        
        ⚠️ 请严格按照以下两步逻辑进行思考和输出（总字数严格控制在 150 字以内）：
        【第一步：局势演化】用一句话客观描述当前市场/环境发生了什么变化。
        【第二步：物理施压】描述这次变化/攻击将如何具体消耗红方的资源、增加阻力或切断通道。
        """
   
        return self._safe_api_call(prompt, is_json=False, model_name="gemini-3-flash-preview")
    

    # 🌟 增加财报参数
    def referee_judge(self, strategy, red_action, blue_reaction, current_stability, round_num, leverage_desc="", is_end_state=False, use_financial_report=False, financial_data="", current_cash=None):
        
       # 👇 核心升级：如果 Python 传来了精准的账本余额，优先使用该余额进行铁血审判！
        if use_financial_report and current_cash is not None:
            fin_constraint = f"💰【真实财报审计模式（强制查账）】：\n系统后台查明，红方当前可用现金精确余额仅剩：【{current_cash:.2f} 亿元】。\n⚠️ 裁判官强制指令：如果红方的动作描述显得财大气粗，而这笔残存现金根本无法支撑，立刻以资金链断裂为由判死(is_bankrupt=true)！"
        # 兼容逻辑：如果没有精确余额，但有原始财报文本
        elif use_financial_report and financial_data:
            fin_constraint = f"💰【真实财报审计模式】：必须严格对照财报数据审查：\n{financial_data}\n⚠️ 若红方反击耗资巨大而财报无法支撑，立刻以资金链断裂为由判死！"
        # 兼容逻辑：未开启财报模式
        else:
            fin_constraint = "🌪️【纯逻辑审计模式】：无财报约束。红方不受账面资金限制，但【绝对受限于】当前的稳定性（后勤调度能力）。"

        # 🪐 动态生成因果律法则
        if is_end_state:
            causality_law = """
        0. ⏳【因果律审查（已获得上帝视角豁免）】：
           本次测试为大后期模拟。裁判官必须强制假设：红方已经度过了漫长而痛苦的培育期，当前描述的战略杠杆/装甲已处于【100% 完美激活的完全体状态】，调用边际成本为 0。
           ⚠️ 【绝对禁止】执行任何时序倒置惩罚！请直接测试该装甲在理想完全体状态下的极限降噪能力。
            """
        else:
            causality_law = """
        0. ⏳【因果律与时序审查（严格执行）】：
           你必须死死盯住当前的回合数（第 {round_num} 冲程）与装甲类型！
           - 如果装甲是“品牌信任、规模效应、未来双边网络”，且当前在极早期（如前 3 冲程），这属于【把未来的结果当成当下的护盾】（时序倒置）。此时装甲未建成，防御彻底失效，透穿率必须接近 1.0！
           - 只有“母公司存量平移、绝对专利独占”等【现成杠杆】，才能在第 1 冲程提供高降噪。
            """

        prompt = f"""
        你是璇玑(PHSL)系统的无情物理仲裁官。你处于一个【绝对双盲实验】中。

        【当前战局快照】
        - 核心战略逻辑：{strategy}
        - 🛡️ 红方物理装甲（杠杆）：{leverage_desc} 
        - 交锋前红方稳定性：{current_stability:.1f}%
        - ⏳ 当前时间序列：第 {round_num} 冲程
        {fin_constraint}

        【本回合交锋记录】
        🔴 红方动作：{red_action}
        🔵 蓝方反扑：{blue_reaction}

        ⚖️ 【判决核心法则】：
        {causality_law}

        1. 🛡️【降噪透穿率测算（核心物理参数）】：
           在严格执行上述因果律的前提下，评估装甲能否抵御蓝方攻击。输出【降噪透穿率(noise_multiplier)】，取值 [0.0, 1.0]。1.0 代表装甲失效/完全裸奔，0.0 代表完美降噪。

        2. 🩸【预估原始伤害】：
           根据蓝方攻击的烈度和红方的失误，直接给出一个【原始伤害 5-25%】。

        3. 💀【物理猝死判定 (is_bankrupt)】：
           - 【基座坍塌】：若蓝方摧毁核心资产且装甲失效，无视血量，满血判死！
           - 【动作变形】：红方动作明显超过当前剩余稳定性支撑极限，判死！
           - 【通道窒息】：造血与存量调动皆被锁死，判死！

        请【严格以 JSON 格式】输出你的判决：
        ```json
        {{
            "noise_multiplier": (浮点数,0.0到1.0之间),
            "raw_damage_percentage": (浮点数),
            "referee_logic": "(120字以内。冷酷说明：是否发生时序倒置？现成杠杆是否起效？为何给出该透穿率和伤害？)",
            "is_bankrupt": (布尔值)
        }}
        ```
        """
        raw_text = self._safe_api_call(prompt, is_json=False, model_name="gemini-3-flash-preview")
        
        # ==========================================
        # 🛡️ 新增：装甲级 JSON 解析与清洗中心
        # ==========================================
        try:
            # 1. 防止交白卷
            if not raw_text or not raw_text.strip():
                raise ValueError("裁判官模型返回了空字符串 (可能触发了安全拦截)")
            
            clean_text = raw_text.strip()
            
            # 2. 物理切除大模型喜欢乱加的 Markdown 标记 (```json 和 ```)
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            elif clean_text.startswith("```"):
                clean_text = clean_text[3:]
                
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
                
            clean_text = clean_text.strip()
            
            # 3. 安全解析
            return json.loads(clean_text)
            
        except Exception as e:
            # 4. 终极防线：如果解析彻底失败，绝对不让系统崩溃！
            # 强制返回一个默认的“轻伤”判定，让沙盘推演能够继续活下去
            print(f"⚠️ JSON 解析防线触发！原始文本: {raw_text} | 错误: {e}")
            return {
                "noise_multiplier": 1.0,
                "raw_damage_percentage": 5.0,
                "referee_logic": "裁判官系统发生认知偏离或安全拦截，按系统强制协议判定为轻度磨损。",
                "is_bankrupt": False
            }
    async def consensus_referee_judge(self, strategy, red_action, blue_reaction, stability, round_num, leverage_desc, is_end_state=False, use_financial_report=False, financial_data="", current_cash=None, committee_size=3):
        """
        ⚖️ 生存风洞合议中枢 (最高法院机制)
        """
        # 👇 核心修复 2：确保启动的法官人数是绝对整数
        committee_size = int(committee_size)
        
        # 1. 瞬间并发启动 N 个独立的裁判官
        tasks = [
            asyncio.to_thread(
                self.referee_judge, strategy, red_action, blue_reaction, 
                stability, round_num, leverage_desc, is_end_state, 
                use_financial_report, financial_data, current_cash
            ) for _ in range(committee_size)
        ]
        
        # 收集所有裁判的独立判决
        judgements = await asyncio.gather(*tasks)
        
        # 2. 提取各项参数列表
        damages = [j.get('raw_damage_percentage', 5.0) for j in judgements]
        noises = [j.get('noise_multiplier', 1.0) for j in judgements]
        bankruptcies = [j.get('is_bankrupt', False) for j in judgements]
        
        # 3. 核心统计学裁决
        final_damage = np.median(damages)
        final_noise = np.median(noises)
        
        # 生死变量：多数表决制
        death_votes = sum(bankruptcies)
        final_bankrupt = death_votes > (committee_size / 2)
        
        # 4. 提取主审法官的判词
        median_idx = np.argmin(np.abs(np.array(damages) - final_damage))
        chief_logic = judgements[median_idx].get('referee_logic', '合议庭未给出明确结论')
        
        if final_bankrupt:
            chief_logic = f"【最高法院以 {death_votes}/{committee_size} 票通过死刑裁决】" + chief_logic

        return {
            "noise_multiplier": float(final_noise),
            "raw_damage_percentage": float(final_damage),
            "referee_logic": chief_logic,
            "is_bankrupt": final_bankrupt
        }
    # ==========================================
    # 🚀 独立的 SIP 点火效能测试模块 
    # ==========================================

    def red_ignition_turn(self, strategy, round_num, current_e, threshold, context, leverage_desc="", use_financial_report=False, financial_data="", current_cash=None):
        """【1. 点火驾驶员】红方点火决策模块：专注于资源转化效率 (已兼容财报模式与 JSON 剥离)"""
        progress = (current_e / threshold) * 100 if threshold > 0 else 0
        
        # 🌟 财务约束动态注入 (兼容最新记账架构)
        fin_constraint = ""
        budget_prompt = "⚠️ 预算约束:本回合你只有【1 个标准单位的资源(P=1)】可供调配。"
        
        if use_financial_report and current_cash is not None:
            fin_constraint = f"""
        💰 【系统强制财务账本】：
        系统查账显示，你当前可用现金精确余额为：【{current_cash:.2f} 亿元】。
        ⚠️ 警告：这是你的绝对物理底线！如果资金枯竭，点火引擎将直接报废！
            """
            budget_prompt = f"⚠️ 预算约束: 你必须动用真实的现金来驱动这 1 个标准单位资源(P=1)。请结合账面剩余的 {current_cash:.2f} 亿元量力而行。"

        prompt = f"""
        你现在是以下战略的【首席执行官】（第一人称视角）：
        核心战略：【{strategy}】
        🛡️ 当前动能引擎（杠杆）：【{leverage_desc}】
        
        📊 【点火遥测仪表盘】：
        - 序列状态：第 {round_num} 冲程
        - 当前效能 E:{current_e:.2f} / 起效门槛：{threshold:.2f}
        - 推进进度：{progress:.1f}%
        {fin_constraint}
        
        ⚖️ 【决策任务】：
        面对当前的摩擦阻力 {context}，你将如何精确使用这 1 个单位的资源？
        你的目标是尽快跨越点火门槛。你应该选择：
        1. 物理穿透（直接砸向核心瓶颈）；
        2. 逻辑修补（消除认知噪音）；
        3. 还是通道加速（提升转化效率）？
        
        {budget_prompt}
        
        ⚠️ 请必须以严格的 JSON 格式输出（目标是最大化转化效率 ΔE）：
        ```json
        {{
            "action": "你的动作描述(100字以内，具体说明采取上述哪种策略来突破瓶颈)",
            "cost_incurred": (本次动作预计消耗的真实现金，纯数字浮点数，以'亿'为单位。若未开启财报填 0.0)
        }}
        ```
        """
        raw_text = self._safe_api_call(prompt, is_json=False, model_name="gemini-3-flash-preview")
        # 👇 补全的逻辑：意图与数值强制剥离，并返回 2 个值！
        try:
            clean_text = raw_text.strip()
            if clean_text.startswith("```json"): clean_text = clean_text[7:]
            elif clean_text.startswith("```"): clean_text = clean_text[3:]
            if clean_text.endswith("```"): clean_text = clean_text[:-3]
                
            red_data = json.loads(clean_text.strip())
            
            action_desc = red_data.get('action', '强制推进既定战略，尝试突破瓶颈。')
            cost = float(red_data.get('cost_incurred', 0.0))
            
            # 核心修复点：这里必须返回两个变量，以满足外层解包的期望！
            return action_desc, cost
            
        except Exception as e:
            print(f"⚠️ 红方点火 JSON 解析失败: {e}")
            # 容错处理：解析失败也必须安全返回两个变量
            return "强制推进既定战略，尝试突破瓶颈。", 0.0
        
        
    def ignition_referee_judge(self, strategy, red_action, blue_reaction, round_num, leverage_desc="", use_financial_report=False, financial_data="", current_cash=None):
        """【2. 点火测功机】点火专用仲裁官 (完美兼容版)"""
        
        # 🌟 智能离合：根据是否开启财报，动态切换法官的审查视角
        if use_financial_report and current_cash is not None:
            fin_constraint = f"💰【真实财报审计模式】：\n系统查明，红方现金仅剩：【{current_cash:.2f} 亿元】。\n⚠️ 强制指令：若红方动作显得财大气粗而残存现金无法支撑，请判定其陷入「死区」，转化效率趋近于 0！"
            eval_rules = "- 🚀 [极度有效]: 杠杆完美克制阻力且资金充裕。ΔE [0.15, 0.25]\n- 🛑 [完美拦截/死区]: 战略死区或严重透支资金导致动作报废。ΔE [0.00, 0.01]"
        elif use_financial_report and financial_data:
            fin_constraint = f"💰【真实财报审计模式】：严格对照财报审查：\n{financial_data}\n⚠️ 强制指令：若耗资巨大而财报无法支撑，转化效率必须大幅降级！"
            eval_rules = "- 🚀 [极度有效]: 杠杆完美克制阻力且资金充裕。ΔE [0.15, 0.25]\n- 🛑 [完美拦截/死区]: 战略死区或严重透支资金导致动作报废。ΔE [0.00, 0.01]"
        else:
            # 👇 完美兼容：未开启财报时，进入纯物理逻辑测算模式
            fin_constraint = "🌪️【纯逻辑测功模式】：当前未开启财报约束。请纯粹基于物理杠杆、动作与环境阻力的克制关系来判定转化效率，无需考虑资金消耗。"
            eval_rules = "- 🚀 [极度有效]: 杠杆完美穿透阻力。ΔE [0.15, 0.25]\n- 🛑 [完美拦截/死区]: 杠杆完全失效，资源打水漂。ΔE [0.00, 0.01]"

        prompt = f"""
        你是物理测功机。任务：评估红方 1 单位资源(P=1) 的绝对转化效率。
        
        【战局快照】
        - 核心战略：{strategy}
        - 第 {round_num} 冲程
        {fin_constraint}
        
        [红方动作]: {red_action}
        [环境阻力]: {blue_reaction}
        [物理装甲(杠杆)]: {leverage_desc}

       【物理标尺守则】（绝对遵守）：
        请根据装甲的降噪能力和阻力的强度，客观判定这 1 个 P 换来了多少【绝对战略效能增量 ΔE】。
        {eval_rules}
        - 🚶 [常规推进]: 有一定阻力但仍能前进。ΔE 取值 [0.08, 0.14]
        - 🐌 [深陷泥潭]: 阻力极大或动作变形。ΔE 取值 [0.02, 0.07]
        
        必须输出 JSON:
        ```json
        {{
            "effectiveness_increment": (浮点数),
            "referee_logic": "(冷酷说明：为什么落在该刻度区间？如果有财务约束，必须说明资金是否支持了该动作)"
        }}
        ```
        """
        raw_text = self._safe_api_call(prompt, is_json=False, model_name="gemini-3-flash-preview")
        try:
            if not raw_text or not raw_text.strip():
                raise ValueError("点火仲裁官返回了空字符串 (可能触发了安全拦截)")
            
            clean_text = raw_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            elif clean_text.startswith("```"):
                clean_text = clean_text[3:]
                
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
                
            clean_text = clean_text.strip()
            return json.loads(clean_text)
        except Exception as e:
            print(f"⚠️ 点火仲裁官防线触发！原始文本: {raw_text} | 错误: {e}")
            return {
                "effectiveness_increment": 0.0,
                "referee_logic": "仲裁官系统发生认知偏离或安全拦截，按系统强制协议判定为最低转化效率。"
            }

    # 【核心改造 1】：升级为异步方法
# 增加 noise_multiplier 参数，默认 1.0 (不降噪)
    #🌟 修复：在参数中加入财报和终态开关
    async def run_single_simulation(self, strategy_vision, historical_prototype="无", leverage_val=1.0, leverage_desc="L-0 裸奔基准", noise_multiplier=1.0, log_output=False, is_end_state=False, use_financial_report=False, financial_data="", committee_size=3):
        """ERT 极限生存主循环 (带 Python 财务硬接管)"""
        await asyncio.sleep(random.uniform(0.5, 1.5))
        stability = 100.0
        context = "战略刚刚启动，各方势力处于观望状态。"
        battle_log = ""
        
        # 🏦 Python 抓取初始账本：瞬间提取准确资金
        current_cash = None
        if use_financial_report and financial_data:
            extractor_prompt = f"请从以下财务数据中提取【可用现金/资金】。只输出代表‘亿’的纯数字浮点数（如55.63）。无明确数字输出 100.0。\n{financial_data}"
            try:
                cash_str = await asyncio.to_thread(self._safe_api_call, extractor_prompt, False, 1, "gemini-3-flash-preview")
                import re
                nums = re.findall(r"[-+]?(?:\d*\.*\d+)", cash_str)
                current_cash = float(nums[0]) if nums else 100.0
            except:
                current_cash = 100.0
        
        for round_num in range(1, self.max_rounds + 1):
            await asyncio.sleep(1)
            # 🔴 红方动作与财务成本提取：强制剥离花费数字
            red_action, cost = await asyncio.to_thread(
                self.red_agent_turn, strategy_vision, round_num, stability, context, leverage_desc, use_financial_report, financial_data, current_cash
            )
            
            # 🧮 Python 物理记账：引擎强行扣款，杜绝大模型算术幻觉
            cash_log = ""
            if current_cash is not None:
                old_cash = current_cash
                current_cash -= cost
                cash_log = f" 💸 [系统硬核查账: 账面 {old_cash:.2f}亿 - 本轮耗资 {cost:.2f}亿 = 剩余 {current_cash:.2f}亿]"
            
            await asyncio.sleep(1)
            # 🔵 蓝方环境反扑
            blue_reaction = await asyncio.to_thread(self.blue_agent_turn, strategy_vision, red_action, historical_prototype, round_num, self.max_rounds)
            
            await asyncio.sleep(1)
            # ⚖️ 召唤最高法院：把 Python 强制算完的 current_cash 传给法官查账！
            judgement = await self.consensus_referee_judge( 
                strategy_vision, red_action, blue_reaction, stability, round_num, leverage_desc, is_end_state=is_end_state, 
                use_financial_report=use_financial_report, 
                financial_data=financial_data, 
                current_cash=current_cash,         # 👈 明确告诉系统，钱就是钱
                committee_size=committee_size      # 👈 明确告诉系统，人就是人
            )
            
            raw_damage = judgement.get('raw_damage_percentage', 5.0)
            is_collapsed = judgement.get('is_bankrupt', False)
            actual_damage = raw_damage * noise_multiplier 
            stability -= actual_damage
            
            # 🌟 构建动态记忆链：传给下回合的红方，锁死历史行为
            context = f"【上回合记忆】：你执行了「{red_action}」。随后蓝方反扑「{blue_reaction}」。"
            
            battle_log += f"#### ⚔️ 第 {round_num} 回合\n> **🔴 进攻方:** {red_action}{cash_log}\n>\n> **🔵 阻力方:** {blue_reaction}\n>\n"
            judgement_text = judgement.get('referee_logic', '无判定理由')
            
            # ⚡ 终极底线熔断：就算裁判官没判死，账本变负数 Python 直接拔管
            if is_collapsed or stability <= 0 or (current_cash is not None and current_cash < 0):
                if current_cash is not None and current_cash < 0:
                    judgement_text = "【系统强制熔断】红方资金链透支，引发严重违约，物理防御彻底坍塌！"
                battle_log += f"> **⚖️ 裁判官:** {judgement_text} **💥 损耗: -{actual_damage:.1f}% | 🚨 触发致死红线: {stability:.1f}%**\n\n---\n"
                battle_log += f"🚨 **战略在第 {round_num} 回合发生不可逆坍塌！**\n"
                return max(0, stability), battle_log 
            else:
                battle_log += f"> **⚖️ 裁判官:** {judgement_text} **💥 损耗: -{actual_damage:.1f}% | 🛡️ 剩余稳定性: {stability:.1f}%**\n\n---\n"
                
        battle_log += "✅ **战略韧性极佳，成功扛过所有压测回合！**\n"
        return max(0, stability), battle_log
    async def run_single_ignition(self, strategy_vision, ai_threshold, historical_prototype="无", leverage_desc="L-0 裸奔基准", committee_size=3, use_financial_report=False, financial_data=""):
        """【3. 点火主引擎】单次点火推演主循环 (已兼容财报约束与硬核记账)"""
        await asyncio.sleep(random.uniform(1.0, 3.0))
        current_e = 0.0
        total_p_spent = 0.0
        context = "点火序列启动，各方势力处于观望状态。"
        battle_log = ""
        
        # 🏦 ==========================================
        # 新增：Python 抓取初始账本（点火前先看看账上有多少钱）
        # ==========================================
        current_cash = None
        if use_financial_report and financial_data:
            extractor_prompt = f"请从以下财务数据中提取【可用现金/资金】。只输出代表‘亿’的纯数字浮点数（如55.63）。无明确数字输出 100.0。\n{financial_data}"
            try:
                cash_str = await asyncio.to_thread(self._safe_api_call, extractor_prompt, False, 1, "gemini-3-flash-preview")
                import re
                nums = re.findall(r"[-+]?(?:\d*\.*\d+)", cash_str)
                current_cash = float(nums[0]) if nums else 100.0
            except:
                current_cash = 100.0
        # ==========================================
        
        for round_num in range(1, self.max_rounds + 1):
            await asyncio.sleep(1)
            total_p_spent += 1.0  # 核心物理约束：每回合强制燃烧 1 个 P
            
            # 🔴 核心替换：接收两个返回值 (红方动作 和 耗资金额)，并喂入财报数据
            red_action, cost = await asyncio.to_thread(
                self.red_ignition_turn, 
                strategy_vision, 
                round_num, 
                current_e, 
                ai_threshold,
                context, 
                leverage_desc,
                use_financial_report, 
                financial_data, 
                current_cash
            )
            
            # 🧮 新增：Python 物理记账，强制扣款
            cash_log = ""
            if current_cash is not None:
                old_cash = current_cash
                current_cash -= cost
                cash_log = f" 💸 [系统硬核查账: 账面 {old_cash:.2f}亿 - 点火耗资 {cost:.2f}亿 = 剩余 {current_cash:.2f}亿]"
            
            await asyncio.sleep(1)
            # 🔵 蓝方依然复用现有的阻击模块
            blue_reaction = await asyncio.to_thread(
                self.blue_agent_turn, 
                strategy_vision, 
                red_action, 
                historical_prototype, 
                round_num, 
                self.max_rounds
            )
            
            await asyncio.sleep(1)
            # ⚖️ 核心替换：召唤点火合议庭，并把 Python 算好的 current_cash 传给他们！
            judgement = await self.consensus_ignition_referee_judge( 
                strategy_vision, 
                red_action, 
                blue_reaction, 
                round_num,
                leverage_desc,
                committee_size=committee_size,
                use_financial_report=use_financial_report,   
                financial_data=financial_data,         
                current_cash=current_cash           
            )
            
            # 提取数据与更新状态
            e_inc = judgement.get('effectiveness_increment', 0.05)
            current_e += e_inc
            
            # 🌟 新增：动态记忆链，让红方记住上一拳的动作和环境的阻力
            context = f"【上回合记忆】：你执行了「{red_action}」。随后蓝方阻力「{blue_reaction}」。"
            judgement_text = judgement.get('referee_logic', '无判定理由')
            
            # 记录战报（加上了 cash_log 的展示）
            battle_log += f"#### 🔥 点火序列 第 {round_num} 冲程 (累计消耗 P={total_p_spent})\n"
            battle_log += f"> **🔴 资源注入(P=1):** {red_action}{cash_log}\n>\n"
            battle_log += f"> **🔵 环境摩擦:** {blue_reaction}\n>\n"
            
            # ⚡ 新增：炸机熔断检测！如果在点火过程把钱烧光了，直接物理报废！
            if current_cash is not None and current_cash < 0:
                judgement_text = "【系统强制熔断】红方点火资金透支，引发严重违约，引擎物理报废！"
                battle_log += f"> **⚖️ 裁判官仲裁:** {judgement_text} **📈 效能跃升: +0.00 | 📊 当前效能 E: {current_e:.2f} / 门槛: {ai_threshold}**\n\n---\n"
                battle_log += f"🚨 **点火失败！资金链断裂导致引擎炸机。**\n"
                return None, battle_log
            
            battle_log += f"> **⚖️ 裁判官仲裁:** {judgement_text} **📈 效能跃升: +{e_inc:.2f} | 📊 当前效能 E: {current_e:.2f} / 门槛: {ai_threshold}**\n\n---\n"
            
            # 🎯 判定：如果达到了门槛，直接点火成功，停止烧钱！
            if current_e >= ai_threshold:
                battle_log += f"✅ **点火成功！** 战略引擎已跨越起效门槛。总共消耗资源压强 P = {total_p_spent}。\n"
                return total_p_spent, battle_log
                
        # 耗尽了 P 预算（最大回合数）依然没达到门槛
        battle_log += f"🚨 **点火失败 (死区)！** 耗尽最大预算仍未达到起效门槛。\n"
        return None, battle_log
    async def consensus_ignition_referee_judge(self, strategy, red_action, blue_reaction, round_num, leverage_desc="", committee_size=3, use_financial_report=False, financial_data="", current_cash=None):
        """
        ⚖️ 点火测功机合议中枢 (最高法院机制 - SIP专用版，已打通财报传参通道)
        """
        # 1. 瞬间并发启动 N 个独立的点火裁判官
        tasks = [
            asyncio.to_thread(
                # 👇 核心修改：把财务参数接力传递给每一个底层的点火法官
                self.ignition_referee_judge, strategy, red_action, blue_reaction, round_num, leverage_desc, use_financial_report, financial_data, current_cash
            ) for _ in range(committee_size)
        ]
        
        # 收集所有裁判的独立判决
        judgements = await asyncio.gather(*tasks)
        
        # 2. 提取效能增量 (ΔE)
        increments = [j.get('effectiveness_increment', 0.05) for j in judgements]
        
        # 3. 核心统计学裁决：强制取中位数，彻底过滤大模型的幻觉极端值
        final_increment = np.median(increments)
        
        # 4. 提取主审法官的判词 (挑一个最接近中位数的判词作为代表)
        median_idx = np.argmin(np.abs(np.array(increments) - final_increment))
        chief_logic = judgements[median_idx].get('referee_logic', '合议庭未给出明确结论')
        
        # 盖上合议庭印章
        chief_logic = f"【合议庭 {committee_size} 席联合测算】" + chief_logic

        return {
            "effectiveness_increment": float(final_increment),
            "referee_logic": chief_logic
        }
class XuanjiValidator:
    def __init__(self, api_key):
        self.arena = StrategicArena(api_key)
        
    # 🌟 修复 1：在函数定义中，补齐前端传来的三个装甲参数！
    async def run_monte_carlo_validation(self, strategy_vision, oracle_bp, historical_prototype="无", iterations=2, leverage_val=1.0, leverage_desc="L-0 裸奔基准", noise_multiplier=1.0, is_end_state=False, use_financial_report=False, financial_data="", committee_size=3):
        # 👇 核心修复 1：强制将前端传来的浮点数转为安全整数！
        iterations = int(iterations)
        committee_size = int(committee_size)
        
        print(f"\n{'='*70}")
        print(f"🔬 璇玑系统双盲验证启动 | 目标战略：{strategy_vision[:20]}...")
        print(f"⏳ 正在瞬间并发 {iterations} 次独立 ABM 沙盘推演...")
        
        tasks = []
        for i in range(iterations):
            # 🌟 修复 2：将这三个参数接力传递给底层的单次推演引擎！
            tasks.append(self.arena.run_single_simulation(
                strategy_vision=strategy_vision, 
                historical_prototype=historical_prototype, 
                leverage_val=leverage_val,          # 接力向下传
                leverage_desc=leverage_desc,        # 接力向下传
                noise_multiplier=noise_multiplier,  # 接力向下传
                log_output=False,
                # 🌟 修复：将前端截获的参数无缝喂入深层引擎！
                is_end_state=is_end_state,
                use_financial_report=use_financial_report,
                financial_data=financial_data,
                committee_size=committee_size
            ))
            
        results = await asyncio.gather(*tasks)
        
        # 结果拆解：results 里是类似于 [(分1, 战报1), (分2, 战报2)] 的结构
        emergent_bps = [res[0] for res in results]
        battle_logs = [res[1] for res in results]
        # ==========================================
        # 👁️ 新增模块：全知智者 (Omniscient Sage) 的 Map-Reduce 归约
        # ==========================================
        print("\n👁️ 唤醒全知智者，进行跨宇宙降维打击分析...")
        
        # 1. 提取战报摘要 (Map阶段：只取每个宇宙最后几行生死判词，防止上下文爆炸)
        sage_context = []
        for i, (bp, log) in enumerate(zip(emergent_bps, battle_logs)):
            status = "🛡️存活" if "✅" in log else "💀阵亡"
            log_snippet = "\n".join(log.split('\n')[-6:]) # 截取死因追踪
            sage_context.append(f"【宇宙 {i+1}】状态: {status} | 最终稳定性(BP): {bp:.1f}%\n核心记录: {log_snippet}")
        sage_context_str = "\n".join(sage_context)

        # 2. 全局贝叶斯审判 (Reduce阶段)
        sage_prompt = f"""
        你是璇玑系统的【全知智者(Omniscient Sage)】，负责俯瞰所有平行宇宙的沙盘压测结果，并定下最终的“真实涌现红线(Emergent BP)”。

        【测试战略】：{strategy_vision}
        【先知预估红线】：{oracle_bp}% (注意：红线数值越高，代表系统越容易死亡)

        【各平行宇宙战报快照】：
        {sage_context_str}

        ⚠️ 你的神圣任务：
        请综合评估所有宇宙的方差与死因。如果你发现有宇宙阵亡，有宇宙幸存，你【绝对不能】使用简单的数学平均值！
        木桶效应决定了战略的极限：只要有一个宇宙暴露了致命的结构性断裂点，你就必须【向上修正】(即给出更高的BP数值) 战略的绝对安全底线。

        请严格以 JSON 格式输出：
        ```json
        {{
            "sage_adjusted_bp": (浮点数，你经过全局判断后得出的最终真实崩溃红线。若全员防线未被击穿，请返回 0.0),
            "sage_insight": "(150字以内。冷酷且高维地解释：为什么你定下了这个红线？不同宇宙的差异暴露了该战略底层怎样的脆弱本质？)"
        }}
        ```
        """

        sage_raw = self.arena._safe_api_call(sage_prompt, is_json=False, model_name="gemini-2.5-pro") 
        # ==========================================
        # 🛠️ 核心修复：增加智者判词的 JSON 清洗与解析
        # ==========================================
        sage_adjusted_bp = None
        sage_insight = ""
        try:
            if sage_raw:
                clean_text = sage_raw.strip()
                if clean_text.startswith("```json"):
                    clean_text = clean_text[7:]
                elif clean_text.startswith("```"):
                    clean_text = clean_text[3:]
                if clean_text.endswith("```"):
                    clean_text = clean_text[:-3]
                    
                sage_json = json.loads(clean_text.strip())
                sage_adjusted_bp = sage_json.get("sage_adjusted_bp")
                sage_insight = sage_json.get("sage_insight", "")
        except Exception as e:
            print(f"⚠️ 全知智者 JSON 解析失败: {e} | 原始返回: {sage_raw}")

        # 统计学计算
        avg_emergent_bp = np.mean(emergent_bps)
        std_dev = np.std(emergent_bps)
        delta = abs(oracle_bp - avg_emergent_bp)
        
        print(f"\n📊 【双盲验证结算报告】")
        print(f"🔹 平均崩溃红线: {avg_emergent_bp:.2f}% | 波动: {std_dev:.2f} | 误差(Δ): {delta:.2f}%")
        
        # ==========================================
        # 🛠️ 核心修复：把智者的数据装进快递箱，发给前端！
        # ==========================================
        return {
            "emergent_bps": emergent_bps,
            "avg_emergent_bp": avg_emergent_bp,
            "std_dev": std_dev,
            "delta": delta,
            "battle_logs": battle_logs,
            # 前端 app.py 需要这两个键才能激活智者面板！
            "sage_adjusted_bp": sage_adjusted_bp if sage_adjusted_bp is not None else avg_emergent_bp,
            "sage_insight": sage_insight
        }
    async def run_ignition_comparison(self, strategy_vision, ai_threshold, leverage_val, leverage_desc, iterations=2, is_end_state=False, committee_size=3):
        """
        SIP 点火风洞双盲对比：测试组 vs L-0 基准组
        """
        # ==========================================
        # 👑 核心注入：终态压测授权 (沙盒指令)
        # ==========================================
        actual_leverage_desc = leverage_desc
        if is_end_state:
            magic_prompt = "\n\n【终态压测授权（最高优先级）】：本次测试为大后期模拟。请裁判官强制假设：红方已经度过了漫长而痛苦的培育期，当前描述的战略杠杆已处于【100% 完美激活的完全体状态】，调用边际成本为 0，且绝对不存在时序倒置问题！请直接测试在此完全体状态下，红方跨越点火门槛所需的资源压强。"
            actual_leverage_desc += magic_prompt
            print("🚀 [系统提示] 已强行注入终态压测指令，时间线已快进！")

        # 1. 运行【当前测试装甲】的宇宙 (使用拼接后的 actual_leverage_desc)
        # 发送给测试组
        tasks_test = [self.arena.run_single_ignition(
            strategy_vision, ai_threshold, leverage_desc=actual_leverage_desc, committee_size=committee_size # 👈 传参
        ) for _ in range(iterations)]
        
        # 2. 运行【L-0 裸奔基准】的宇宙 (强制重置杠杆描述，且不带终态授权)
        base_desc = "L-0 裸奔基准：无任何战略杠杆掩护，直面所有环境物理阻力。"
        # 发送给裸奔组
        tasks_base = [self.arena.run_single_ignition(
            strategy_vision, ai_threshold, leverage_desc=base_desc, committee_size=committee_size # 👈 传参
        ) for _ in range(iterations)]
        
        # 并发执行所有宇宙
        results_test = await asyncio.gather(*tasks_test)
        results_base = await asyncio.gather(*tasks_base)
        
        # 提取成功的 P 值 (过滤掉耗尽回合仍未点火的 None 值)
        valid_p_test = [res[0] for res in results_test if res[0] is not None]
        valid_p_base = [res[0] for res in results_base if res[0] is not None]
        
        # 计算两组的平均点火压强
        avg_p_test = np.mean(valid_p_test) if valid_p_test else None
        avg_p_base = np.mean(valid_p_base) if valid_p_base else None
        
        # 计算点火提前量 ΔP
        delta_p = None
        if avg_p_test is not None and avg_p_base is not None:
            delta_p = avg_p_base - avg_p_test
            
        return {
            "avg_p_test": avg_p_test,
            "avg_p_base": avg_p_base,
            "delta_p": delta_p,
            "logs_test": [res[1] for res in results_test] 
        }