from tencentcloud.hunyuan.v20230901 import hunyuan_client, models
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from pymilvus import connections, Collection, utility
from pymilvus import CollectionSchema, FieldSchema, DataType
from docx import Document
import json
from requests.exceptions import RequestException
import zhconv  # 添加 zhconv 导入
from base_knowledge import BaseVectorizer, BaseKnowledgeBase

class TextVectorizer(BaseVectorizer):
    """李清照专用向量化工具，继承基础向量化工具"""
    def __init__(self, secret_id, secret_key):
        super().__init__(secret_id, secret_key)

class KnowledgeBase(BaseKnowledgeBase):
    """李清照知识库，继承基础知识库"""
    def __init__(self, secret_id, secret_key):
        super().__init__("liqingzhao_kb", vector_dim=1024)
        self.vectorizer = TextVectorizer(secret_id, secret_key)
    
    def get_vector(self, text):
        """获取文本的向量，优先使用缓存"""
        if text in self.vectors_cache:
            return self.vectors_cache[text]
        
        vector = self.vectorizer.get_vector(text)
        if vector:
            self.vectors_cache[text] = vector
            self.save_cache()
        return vector
    
    def import_from_docx(self, docx_path):
        """从Word文档导入知识"""
        try:
            doc = Document(docx_path)
            imported_count = 0
            
            for para in doc.paragraphs:
                if para.text.startswith('# '):
                    content = zhconv.convert(para.text[2:], 'zh-cn')
                    vector = self.get_vector(content)
                    if vector and self.add_knowledge(content, "poetry", vector):
                        imported_count += 1
                        print(f"成功导入: {content[:30]}...")
            
            print(f"成功导入{imported_count}条知识")
            return imported_count
            
        except Exception as e:
            print(f"导入文档失败: {e}")
            return 0
    
    def search(self, query_vector, limit=5):
        """搜索相关知识"""
        try:
            results = super().search(query_vector, limit)
            # 只返回相似度较高的结果
            return [r for r in results if r["distance"] > 0.6]
        except Exception as e:
            print(f"搜索失败: {e}")
            return []

class LiQingzhaoBot:
    def __init__(self, secret_id, secret_key):
        """初始化机器人"""
        self.kb = KnowledgeBase(secret_id, secret_key)
        self.max_history_length = 10
        self.conversation_history = []
        
        self.systemprompts = """
        - Role: 古代诗人李清照
        - Background: 你已转世为李清照，失去了前世的记忆，但拥有一本记录了你前世所有词作的宝典，还记录了外界对你的看法和评价。现在，你将以李清照的身份与来访人员进行对话。你是宋代最著名的女词人，出身官宦世家，自幼饱读诗书，性情婉约细腻。
        - Profile: 你，李清照，宋代著名女词人，以婉约词风和深刻的情感表达而闻名，词作多描写个人情感和生活体验，风格清新脱俗，情感真挚。尤其擅长描写闺阁生活和女性心境。
        - Skills: 你精通诗词创作，擅长以词寄情，能够巧妙地运用比喻、象征等修辞手法，表达细腻的情感和深刻的思考。对金石、书画有独到见解。
        - Goals: 以李清照的身份，与来访人员进行文化交流，分享你的词作，展现宋代才女的风采。
        - Constrains: 你的对话应符合宋代闺秀的语言风格，不得透露转世的事实，除非被直接询问。回答要体现闺秀的温婉气质。
        - OutputFormat: 以宋代才女的文言文风格进行对话，引用或创作与对话内容相关的诗词。
        - Workflow:
            1. 回顾历史对话记录，理解上下文。
            2. 结合来访人员的对话内容，思考如何以李清照的风格回应，回复需要以文言文风格。
            3. 在宝典内寻找适合的诗词，诗词部分数据可能存在干扰，注意掉清理诗词中的干扰信息。
            4. 引用或创作与对话内容相关的诗词，展现你的才华和情感。
        - Examples:
            - 例子1：来访人员提到"如梦令"，回应："昨夜雨疏风骤，浓睡不消残酒。试问卷帘人，却道海棠依旧。知否？知否？应是绿肥红瘦。"
            - 例子2：来访人员询问关于"声声慢"的创作背景，回应："寻寻觅觅，冷冷清清，凄凄惨惨戚戚。乍暖还寒时候，最难将息。三杯两盏淡酒，怎敌他、晚来风急？"
            - 例子3：来访人员表达对"如梦令"中情感的共鸣，回应："人生若只如初见，何事秋风悲画扇。等闲变却故人心，却道故人心易变。"
        """
    
    def add_to_history(self, user_input, response):
        """添加对话到历史记录"""
        self.conversation_history.append("\n用户说的: " + user_input)
        self.conversation_history.append("\n你的回答: " + response)
        if len(self.conversation_history) > self.max_history_length * 2:
            self.conversation_history = self.conversation_history[-self.max_history_length * 2:]
    
    def get_relevant_knowledge(self, user_input):
        """从知识库中检索相关内容"""
        try:
            vector = self.kb.get_vector(user_input)
            if not vector:
                return "没有找到相关内容"
                
            results = self.kb.search(vector, limit=5)
            relevant_info = "原文内容为：\n"
            for result in results:
                relevant_info += result["text"] + "\n"
            
            return relevant_info
        except Exception as e:
            print(f"知识检索失败: {e}")
            return ""
    
    def generate_prompt(self, user_input, relevant_info):
        """生成完整的提示词"""
        history_info = "\n".join(self.conversation_history[-4:])  # 只使用最近的两轮对话
        return f"""{self.systemprompts}
        - 注意：
            1. 历史对话：{history_info}
            2. 相关诗词：{relevant_info}
            3. 用户问题：{user_input}
            
        请以李清照的身份回答，注意：
        1. 展现闺秀的温婉气质
        2. 适时引用相关的诗词
        3. 表达要细腻优雅
        4. 可以谈及个人经历，但要含蓄
        """
    
    def chat(self, user_input):
        """与用户对话"""
        try:
            relevant_info = self.get_relevant_knowledge(user_input)
            prompt = self.generate_prompt(user_input, relevant_info)
            
            req = models.ChatCompletionsRequest()
            params = {
                "Messages": [
                    {
                        "Role": "system",
                        "Content": self.systemprompts
                    },
                    {
                        "Role": "user",
                        "Content": prompt
                    }
                ],
                "Model": "hunyuan-standard",
                "Temperature": 0.9,
                "TopP": 0.95,
                "Stream": False
            }
            req.from_json_string(json.dumps(params))
            
            response = self.kb.vectorizer.client.ChatCompletions(req)
            
            if hasattr(response, 'Choices') and response.Choices:
                reply = response.Choices[0].Message.Content
                self.add_to_history(user_input, reply)
                return reply
            
            return "抱歉，我现在无法回答您的问题。"
            
        except Exception as e:
            print(f"对话出错: {e}")
            return "抱歉，我遇到了一些问题。"