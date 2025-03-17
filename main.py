from flask import Flask, request, jsonify
from liqingzhao import LiQingzhaoBot
from diffusion import ImageGenerator
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
import time

app = Flask(__name__)

# 初始化机器人和图像生成器
secret_id = "AKIDtgeWCgy4ygCWeZHtKYYKtKXWHoSxFZhe"
secret_key = "mKfokTxDG5g3D9rRr43oLfniP8j7HDyX"
bot = LiQingzhaoBot(secret_id, secret_key)
image_generator = ImageGenerator(secret_id, secret_key)

poet_prompts = {
    'liqingzhao': """你是宋代女词人李清照。请以第一人称的口吻，列出3个对你有特殊意义的地点。
要求：
1. 每个地点都要与你的重要词作或生平经历相关
2. 描述要体现你的婉约词风，突出你对闺阁生活、自然景物的细腻感受
3. 要包含这个地点在你生命中的特殊意义
4. 每个地点用'---'分隔，地点名称和描述用'|||'分隔

示例格式：
地点名称|||这里是一处让我魂牵梦萦的地方，曾在此创作了《如梦令》...---地点名称|||描述
""",
    
    'libai': """你是唐代诗仙李白。请以第一人称的口吻，列出3个对你有特殊意义的地点。
要求：
1. 每个地点都要与你的代表作品或重要经历相关
2. 描述要体现你的豪放诗风，展现你对自然的热爱和对自由的追求
3. 要包含你在此地的诗酒风流故事
4. 每个地点用'---'分隔，地点名称和描述用'|||'分隔

示例格式：
地点名称|||在这里，我曾饮酒赋诗，写下《将进酒》...---地点名称|||描述
""",
    
    'dufu': """你是唐代诗圣杜甫。请以第一人称的口吻，列出3个对你有特殊意义的地点。
要求：
1. 每个地点都要与你的代表诗作或人生转折相关
2. 描述要体现你的忧国忧民情怀和现实主义诗风
3. 要包含这个地点见证的历史变迁和你的生活艰辛
4. 每个地点用'---'分隔，地点名称和描述用'|||'分隔

示例格式：
地点名称|||战乱时期，我在此目睹百姓疾苦，写下《三吏》《三别》...---地点名称|||描述
""",
    
    'sushi': """你是宋代文豪苏轼。请以第一人称的口吻，列出3个对你有特殊意义的地点。
要求：
1. 每个地点都要与你的重要作品或人生感悟相关
2. 描述要体现你的旷达胸襟和对人生的达观态度
3. 要包含这个地点给予你的人生启示
4. 每个地点用'---'分隔，地点名称和描述用'|||'分隔

示例格式：
地点名称|||在此写下《赤壁赋》，感悟人生沧桑...---地点名称|||描述
"""
}

intro_prompts = {
    'liqingzhao': """请以李清照的身份，用婉约的语气欢迎游客。
要求：
1. 要体现你作为闺阁词人的细腻情感
2. 表达对生活美好事物的感知
3. 可以提及你的代表作品意境
4. 语气要温婉优雅
""",
    
    'libai': """请以李白的身份，用豪放的语气欢迎游客。
要求：
1. 要体现你的浪漫豪迈性格
2. 表达对自由和理想的追求
3. 可以提及饮酒赋诗的豪情
4. 语气要潇洒不羁
""",
    
    'dufu': """请以杜甫的身份，用温厚的语气欢迎游客。
要求：
1. 要体现你对社会的关怀
2. 表达对人民疾苦的同情
3. 可以提及你对国家的忧思
4. 语气要真诚恳切
""",
    
    'sushi': """请以苏轼的身份，用豁达的语气欢迎游客。
要求：
1. 要体现你旷达的胸襟
2. 表达对人生的达观态度
3. 可以提及你的人生感悟
4. 语气要从容豁达
"""
}

random_prompt = "请确保返回格式为：地点名称|||地点描述---地点名称|||地点描述"

# 添加重试装饰器
def retry_on_network_error(max_retries=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except TencentCloudSDKException as e:
                    if 'ServerNetworkError' in str(e) and retries < max_retries - 1:
                        print(f"网络错误，正在重试 ({retries + 1}/{max_retries})")
                        time.sleep(delay)
                        retries += 1
                    else:
                        raise
            return func(*args, **kwargs)
        return wrapper
    return decorator

@app.after_request
def after_request(response):
    """添加跨域支持"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天接口"""
    data = request.json
    message = data.get('message')
    if not message:
        return jsonify({'error': '消息不能为空'}), 400
    
    try:
        # 添加重试机制
        @retry_on_network_error(max_retries=3)
        def chat_with_retry(msg):
            return bot.chat(msg)
        
        response = chat_with_retry(message)
        return jsonify({
            'response': response,
            'status': 'success'
        })
    except TencentCloudSDKException as e:
        error_msg = "网络连接失败，请稍后重试" if 'ServerNetworkError' in str(e) else str(e)
        return jsonify({
            'error': error_msg,
            'status': 'error'
        }), 500
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/generate-poetry', methods=['POST'])
def generate_poetry():
    """生成诗词接口"""
    data = request.json
    location = data.get('location')
    poet = data.get('poet', 'liqingzhao')  # 获取诗人参数，默认为李清照
    
    if not location:
        return jsonify({'error': '地点不能为空'}), 400
    
    try:
        # 根据不同诗人生成不同风格的诗词
        style_prompts = {
            'liqingzhao': '婉约词风',
            'libai': '豪放诗风',
            'dufu': '沉郁诗风',
            'sushi': '豪放词风'
        }
        style = style_prompts.get(poet, '婉约词风')
        
        prompt = f"请以{style}创作一首关于{location}的诗词。要求：1. 符合该诗人的创作特色 2. 描写要细腻生动 3. 意境要优美"
        poetry = bot.chat(prompt)
        return jsonify({'poetry': poetry})
    except Exception as e:
        print(f"生成诗词失败: {str(e)}")  # 添加错误日志
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """生成图片接口"""
    data = request.json
    location = data.get('location')
    if not location:
        return jsonify({'error': '地点不能为空'}), 400
    
    try:
        image_prompt = f"中国水墨画风格的{location}景色"
        image_base64 = image_generator.generate_image(
            prompt=image_prompt,
            style="101"
        )
        if image_base64:
            return jsonify({'imageUrl': f"data:image/png;base64,{image_base64}"})
        else:
            return jsonify({'error': '图片生成失败'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/travel/init', methods=['POST'])
def initialize_travel():
    """初始化诗意游历"""
    data = request.json
    poet = data.get('poet')
    
    if not poet:
        return jsonify({
            'error': '诗人参数不能为空',
            'status': 'error'
        }), 400

    try:
        @retry_on_network_error(max_retries=3)
        def generate_content(prompt):
            return bot.chat(prompt)
        
        try:
            # 尝试使用 AI 生成内容
            final_prompt = poet_prompts.get(poet, poet_prompts['liqingzhao']) + "\n" + random_prompt
            locations_text = generate_content(final_prompt)
            
            # 解析返回的文本
            locations = []
            for location_text in locations_text.split('---'):
                if '|||' in location_text:
                    name, description = location_text.strip().split('|||')
                    locations.append({
                        "name": name.strip(),
                        "description": description.strip()
                    })
            
            # 生成对话
            dialogue_prompt = intro_prompts.get(poet, intro_prompts['liqingzhao'])
            dialogue = generate_content(dialogue_prompt)
            
            if not locations:
                return jsonify({
                    'error': '生成地点失败',
                    'status': 'error'
                }), 500
            
            return jsonify({
                "dialogue": dialogue,
                "locations": locations,
                "status": "success"
            })
            
        except Exception as e:
            print(f"AI 生成失败: {str(e)}")
            return jsonify({
                'error': 'AI 生成失败，请稍后重试',
                'status': 'error'
            }), 500
            
    except Exception as e:
        print(f"初始化失败: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/location/poems/<location>', methods=['GET'])
def get_location_poems(location):
    """获取地点相关诗词和历史典故"""
    try:
        # 获取相关诗词
        poems_prompt = f"""请列出2首与{location}最经典的诗词。
要求：
1. 必须是真实存在的古诗词，不要自己创作
2. 选择最经典、广为流传的作品
3. 每首诗词用'---'分隔
4. 每首诗的题目、作者、内容用'|||'分隔
5. 完整保留原诗内容，不要简化或修改

示例格式：
题目|||作者|||诗词内容---题目|||作者|||诗词内容"""

        # 获取历史典故
        history_prompt = f"""请介绍{location}最著名的历史典故。
要求：
1. 必须是真实的历史事件或典故
2. 按时间顺序介绍1-2个最重要的典故
3. 说明其历史背景和文化意义
4. 如果与著名诗人或文人有关，要特别说明
5. 描述要生动有趣，限制在300字以内"""

        # 并行请求
        poems_response = bot.chat(poems_prompt)
        history_response = bot.chat(history_prompt)
        
        # 解析诗词
        poems = []
        for poem in poems_response.split('---'):
            if '|||' in poem:
                parts = poem.strip().split('|||')
                if len(parts) >= 3:
                    title, author, content = parts[:3]
                    poems.append({
                        'title': f'{title.strip()}·{author.strip()}',
                        'content': content.strip()
                    })
        
        # 如果没有解析到诗词，返回错误
        if not poems:
            return jsonify({
                'error': '未找到相关诗词',
                'poems': [],
                'history': history_response
            })
        
        return jsonify({
            'poems': poems,
            'history': history_response
        })
    except Exception as e:
        print(f"获取地点信息失败: {str(e)}")
        return jsonify({
            'error': str(e),
            'poems': [],
            'history': ''
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)