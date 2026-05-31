import os
import tempfile
import re
from fpdf import FPDF

class XuanjiPDFReport(FPDF):
    def __init__(self, font_path="simhei.ttf"):
        super().__init__()
        self.font_path = font_path
        self.logo_url = "https://pystrategylab.com/proxy-assets/cdn-cgi/image/format=auto,w=768,fit=crop/1evUiS818YahKfZE/pythonlogo2-AfiMET3ydIQjjfId.png"
        self.official_site = "www.pystrategylab.com" # 建议替换为 PHSL 专有页面
        
        self.alias_nb_pages() # 开启总页数计算
        
        # 自动分页与底边距
        self.set_auto_page_break(auto=True, margin=15)
        
        if os.path.exists(self.font_path):
            self.add_font("SimHei", "", self.font_path)
            self.add_font("SimHei", "B", self.font_path)
            self.add_font("SimHei", "I", self.font_path)
            self.set_font("SimHei", size=10)
        else:
            self.set_font("Arial", size=10)
        self.add_page()
        
    def header(self):
        # 【关键修改】：仅在第一页显示 Logo 图片
        if self.page_no() == 1:
            logo_path = "logo.png" 
            if not os.path.exists(logo_path):
                logo_path = self.logo_url 

            try:
                self.image(logo_path, x=10, y=8, w=25)
            except:
                pass 
        
        # 顶部右侧文字：每一页都保留，保持实验室标识的一致性
        self.set_font("SimHei", 'B', 9)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, "PHSL | 璇玑战略定量审计中枢", 0, 0, 'R')
        
        # 统一留出 20mm 的页眉空间，防止正文标题上移
        self.ln(20)
        
    def add_intelligence_sources(self, sources):
        """新增：绘制情报溯源清单"""
        if not sources: return
        self.add_page()
        self.chapter_title("📡 附录 A：贝叶斯推断环境情报源 (Intelligence Anchors)")
        self.chapter_body("以下事实锚点由璇玑系统通过实时搜索全球情报网提取，直接构成了本次贝叶斯推断中逻辑密度 (ssc_d) 与环境波动率 (vol) 的计算基石。")
        
        self.set_font("SimHei", '', 9)
        for src in sources:
            polarity = src.get('polarity', '')
            # PDF 不支持某些 Emoji，替换为符号
            if "🔴" in polarity: polarity = "[负面/阻力]"
            elif "🟢" in polarity: polarity = "[正面/顺风]"
            
            source_name = src.get('source', '未知')
            fact = self.clean_pdf_text(src.get('fact', ''))
            impact = src.get('impact', '')
            
            # 格式：[负面] [彭博社] 核心事实... (作用于 vol 上升)
            text = f"{polarity} {source_name}: {fact} {impact}"
            self.multi_cell(0, 6, text, align='L')
            self.ln(1)
            
    def footer(self):
        """每一页底部的版权与链接"""
        # 设置在底部 15mm 处
        self.set_y(-15)
        self.set_font("SimHei", '', 8)
        self.set_text_color(120, 120, 120)
        
        # 左侧：官网链接 (带超链接功能)
        self.cell(0, 10, f"官方技术支持: {self.official_site}", 0, 0, 'L', link=f"http://{self.official_site}")
        
        # 右侧：页码
        self.cell(0, 10, f"第 {self.page_no()} 页 / {{nb}}", 0, 0, 'R')
        
    def clean_pdf_text(self, raw_text):
        """
        战报文本清洗器 (FPDF 专用安全版)
        抹除所有可能导致截断的 Markdown 符号和危险字符。
        """
        if not raw_text:
            return "无行动记录"
        
        text = str(raw_text)
        # 1. 物理抹除 Markdown 的加粗星号，保持排版纯净
        text = text.replace("**", "")
        # 2. 将英文尖括号转化为中文书名号，防止被底层解析器吞噬
        text = text.replace("<", "《").replace(">", "》")
        # 3. 将换行符转化为空格，让 fpdf2 的 table 自动换行接管排版
        text = text.replace("\n", " ")
        
        return text.strip()
    def clean_paragraph_text(self, raw_text):
        """
        长文本整形外科手术：
        专门处理大模型输出的分析段落，消灭幽灵空格，重塑段落呼吸感。
        """
        if not raw_text or raw_text == "暂无数据": 
            return "暂无数据"
            
        text = str(raw_text)
        
        # 1. 🛡️ 核心修复：只粉碎连续的空格和制表符，【绝对保留换行符 \n】
        text = re.sub(r'[ \t]{2,}', ' ', text)
        # ==========================================
        # 🌟 修复幽灵断行（解决右侧大片空白问题）
        # 抹除大模型强加在句子中间的单换行符，将断掉的句子重新熔合。
        text = re.sub(r'[ \t]*\n[ \t]*', '\n', text) # 先清理换行符前后的垃圾空格
        text = re.sub(r'(?<!\n)\n(?!\n)', '', text)  # 核心：抹除前后都不是 \n 的单换行符
        # 🎯 新增防线：拔除大模型联网搜索残留的引用角标 (如 [6, 21])
        text = re.sub(r'\s*\[\d+(?:,\s*\d+)*\]', '', text)
        # ==========================================
        # 🌟 修复：将 \u00A0 作为普通字符串拼接到两个正则组之间
        text = re.sub(r'([a-zA-Z])\s+([a-zA-Z])', r'\1' + '\u00A0' + r'\2', text)
        
        # ==========================================
        # 🌟 新增修复：智能列表排版引擎 (解决“数字孤儿”问题)
        # 匹配 "1." 或 "2、"，消除其周围的换行错位，强制将其推到新的一行起头
        # 匹配规则：前面不是数字，跟着任意空白，然后是数字+点/顿号，再跟着任意空白
        text = re.sub(r'(?<!\d)\s*([1-9]\d?[.、])\s+', r'\n\n\1 ', text)
        
        # ==========================================
        
       # 2. 视觉美化：使用正则一次性安全替换，彻底根除“双重替换嵌套”Bug
        text = re.sub(r'\[?\bPASS\b\]?(?:\s*-)?', '[√ PASS]', text)
        text = re.sub(r'\[?\bFAIL\b\]?(?:\s*-)?', '[X FAIL]', text)
        
        # 3. 智能段落重组：强制让每一个 【 标签都从新的一行开始，且上方留白
        text = text.replace("【", "\n\n【")
    
        # 4. 终极防线(V5 升级版)：专治大模型把英文参数名和中文句号黏在一起的“话痨”排版
        # 匹配规则：中文标点 + 可选空格 + 英文参数名(里面可能带括号和数字，甚至嵌套) + 冒号
        text = re.sub(r'([。，；？！：\uFF1A])\s*([a-zA-Z_]{3,}\s*(?:[\(\uFF08].*?[\)\uFF09])?\s*[:\uFF1A])', r'\1\n\n\2\n', text)
        
        # 补充防线：如果开头第一句就是参数名，强制把它也独立出来
        text = re.sub(r'^\s*([a-zA-Z_]{3,}\s*(?:[\(\uFF08].*?[\)\uFF09])?\s*[:\uFF1A])', r'\1\n', text)
        
        # 5. 极致美化：收尾清理，防止因为上面的替换产生过多空行（最多保留两个换行）
        text = re.sub(r'\n{3,}', '\n\n', text) 
        
        return text.strip()
    
    def chapter_title(self, title):
        self.ln(4)
        self.set_font("SimHei", 'B', 14)
        self.set_text_color(20, 50, 90) # 机构海军蓝
        self.cell(0, 8, title, 0, 1, 'L')
        # 增加下方极细分割线
        self.set_draw_color(200, 200, 200)
        self.line(self.get_x(), self.get_y(), self.get_x() + 170, self.get_y())
        self.ln(3)

    def chapter_body(self, text):
        if not text or text == "暂无数据": return
        safe_text = self.clean_paragraph_text(text)
        self.set_font("SimHei", '', 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, safe_text, align='L')
        self.ln(2)
        
    def add_strategic_formula(self):
        """用等宽字体在 PDF 中硬核排版战略效能公式"""
        self.ln(5)
        self.set_font("SimHei", 'B', 11)
        self.set_text_color(20, 50, 90)
        self.cell(0, 8, "📐 核心战略公理 (Strategic Effectiveness Axiom)", 0, 1, 'L')
        
        # 切换到等宽字体 (Courier)，这对于对齐分子和分母至关重要
        self.set_font("Courier", 'B', 12)
        self.set_text_color(40, 40, 40)
        
        # 利用空格精准对齐，画出物理公式的美感
        self.cell(0, 6, "         P * (ssc_d * L)", 0, 1, 'L')
        self.cell(0, 6, "   E  = -------------------------", 0, 1, 'L')
        self.cell(0, 6, "         [I * (1 + vol)] + P", 0, 1, 'L')
        
        self.ln(2)
        
        # 切回黑体，添加参数释义
        self.set_font("SimHei", '', 9)
        self.set_text_color(100, 100, 100)
        explanation = (
            "   E: 战略效能 | P: 资源压强 | ssc_d: 逻辑密度(P(E|H)) \n"
            "   L: 战略杠杆 | I: 惯性阻力 | vol: 环境波动摩擦"
        )
        self.multi_cell(0, 5, explanation, align='L')
        self.ln(5)
        
    def add_dense_table(self, headers, data_rows, col_widths=None):
        """核心模块：高信息密度表格绘制"""
        if not data_rows: return
        self.ln(2)
        self.set_font("SimHei", 'B', 9.5)
        
        try:
            # 尝试使用 fpdf2 的原生 table 上下文管理器 (支持自动换行与对齐)
            with self.table(col_widths=col_widths, text_align="LEFT", line_height=6) as table:
                # 渲染表头
                row = table.row()
                for header in headers:
                    self.set_fill_color(230, 240, 250) # 极淡的底色区分表头
                    self.set_text_color(20, 50, 90)
                    row.cell(header)
                
                # 渲染数据行
                self.set_font("SimHei", '', 9)
                self.set_text_color(40, 40, 40)
                for data in data_rows:
                    row = table.row()
                    for item in data:
                        row.cell(str(item))
        except AttributeError:
            # 兼容极老版本的 FPDF
            self.chapter_body("提示：当前 fpdf 库版本过低，建议 pip install fpdf2 获取最佳表格排版。")
            for r in data_rows:
                self.chapter_body(f" • {r[0]}: {r[1] if len(r)>1 else ''}")
        self.ln(4)

    def parse_and_add_isomorphism(self, text):
        """智能正则解析：将大模型的长文本图谱拆解为映射表格"""
        if not text or text == "暂无数据": 
            return
            
        # 寻找类似 【国电电力 <=> 风帆舰队】 的模式
        matches = re.findall(r'【(.*?)】', text)
        table_data = []
        
        for m in matches:
            if '<=>' in m:
                parts = m.split('<=>')
                table_data.append([parts[0].strip(), parts[1].strip()])
        
        if table_data:
            self.add_dense_table(["现代战略/物理节点", "历史/环境同构体"], table_data, col_widths=(45, 55))
            # 过滤掉括号里的内容，保留大模型的结论作为总述
            clean_text = re.sub(r'【.*?】', '', text).replace('、', '').strip()
            if clean_text:
                self.set_font("SimHei", 'B', 9.5)
                self.chapter_body(f"映射总论: {clean_text}")
        else:
            # 没抓取到特征，做单列表格包边
            self.add_dense_table(["同构映射图谱推演"], [[text]], col_widths=(100,))

    def add_plot(self, fig, title=""):
        if title:
            self.ln(4)
            self.set_font("SimHei", 'B', 12)
            self.set_text_color(20, 50, 90)
            self.cell(0, 7, title, 0, 1, 'L')
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            fig.tight_layout()
            # 提升 DPI，背景保持暗黑
            fig.savefig(tmpfile.name, format="png", bbox_inches="tight", dpi=300, facecolor='#0e1117')
            # 宽度缩减到 140，留出留白，增加高端感
            img_w = 140
            x_pos = (210 - img_w) / 2
            self.image(tmpfile.name, x=x_pos, w=img_w)
        os.remove(tmpfile.name)
        self.ln(2)
    def add_battle_log(self, universe_id, score, log_text):
        """核心模块：将单个平行宇宙的对抗战报转化为审计表格"""
        self.ln(4)
        self.set_font("SimHei", 'B', 11)
        self.set_text_color(20, 50, 90)
        
        # 🌟 终极动态标题修复：通过底层战报关键字，精准识别生死状态
        if "致死红线" in log_text or "坍塌" in log_text:
            # 如果战报里有致死红线或坍塌字眼，说明在这个宇宙中阵亡
            title = f"🌌 平行宇宙 {universe_id} 审计详情 (🚨 实测致死红线: {score:.1f}%)"
        else:
            # 否则说明活着扛过了压测
            title = f"🌌 平行宇宙 {universe_id} 审计详情 (🛡️ 完美扛过压测 | 剩余韧性: {score:.1f}%)"
            
        self.cell(0, 8, title, 0, 1, 'L')
        
        # 正则解析战报中的回合数据
        rounds = re.split(r'#### ⚔️ 第 \d+ 回合', log_text)
        table_data = []
        
        # 🌟 修复点：引入独立的有效回合计数器，不再依赖有缺陷的 enumerate 索引
        actual_round = 1 
        
        for r_content in rounds:
            if not r_content.strip(): continue
            
            # 🛡️ 升级版正则提取：使用 re.DOTALL 允许跨行抓取
            red = re.search(r'🔴 进攻方动作:\s*(.*?)(?=🔵|⚖️|💥|$)', r_content, re.DOTALL)
            blue = re.search(r'🔵 阻力方反扑:\s*(.*?)(?=⚖️|💥|$)', r_content, re.DOTALL)
            judge = re.search(r'⚖️ 裁判官仲裁:\s*(.*?)(?=💥|$)', r_content, re.DOTALL)
            damage = re.search(r'💥 物理损耗:\s*(.*?)(?=\n|$)', r_content)
            
            # 强制套上清洗器进行过滤
            safe_red = self.clean_pdf_text(red.group(1)) if red else "N/A"
            safe_blue = self.clean_pdf_text(blue.group(1)) if blue else "N/A"
            safe_judge = self.clean_pdf_text(judge.group(1)) if judge else ""
            safe_damage = damage.group(1).strip() if damage else ""
            
            # 组装安全的数据行
            row = [
                f"T+{actual_round}",  # 🌟 直接使用独立的计数器
                safe_red,
                safe_blue,
                f"{safe_judge} [{safe_damage}]"
            ]
            table_data.append(row)
            
            # 成功装填一行后，回合数才 +1
            actual_round += 1 

        if table_data:
            self.add_dense_table(
                ["时刻", "红方进攻动作", "蓝方环境反扑", "物理仲裁结论"], 
                table_data, 
                col_widths=(12, 30, 30, 28)
            )