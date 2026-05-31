# phsl/protocol.py

class XuanjiProtocol:
    def __init__(self, history, target_strategy):
        """
        璇玑同构协议：历史与现实的同构守恒 # 贯穿审计全流程,以史为鉴，知今用古
        :param history: 历史案例镜像（如：诸葛亮北伐、空城计）
        :param target_strategy: 目标审计战略（如：出海决策、技术选型）
        """
        self.history = history
        self.target_strategy = target_strategy
        self.ctx = None

    def switch_context(self, mode="target"):
        """
        切换审计语境
        mode="target": 审计当前的现实战略
        mode="history": 审计作为对照组的历史原型
        """
        # 默认导向目标战略，体现“解决当下问题”的初衷
        self.ctx = self.target_strategy if mode == "target" else self.history