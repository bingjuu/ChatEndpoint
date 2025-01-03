from openai import AsyncOpenAI
import tkinter as tk
from tkinter import ttk
import threading
import markdown
from tkhtmlview import HTMLLabel
import time
from tkinter import scrolledtext
import asyncio
import aiohttp
import queue
from fastapi.responses import PlainTextResponse
import uvicorn
from fastapi import FastAPI, Query

class ChatGPTApp:
    def __init__(self, root):
        # 初始化 OpenAI 客户端，使用默认值
        self.api_key_var = tk.StringVar(root, value="")
        self.base_url_var = tk.StringVar(root, value="")
        self.client = self.create_openai_client()
        
        self.root = root
        self.root.title("ChatEndpoint")
        self.root.geometry("1100x1000")
        
        # 设置默认字体
        default_font = ("Microsoft YaHei", 10)
        
        # 创建主框架
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # API 设置部分
        api_frame = ttk.Frame(main_frame)
        api_frame.pack(fill=tk.X, pady=5)
        
        # api_key 输入框
        api_key_label = ttk.Label(api_frame, text="API Key:", font=default_font)
        api_key_label.pack(side=tk.LEFT, padx=5)
        self.api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, width=40, font=default_font)
        self.api_key_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # base_url 输入框
        base_url_label = ttk.Label(api_frame, text="Base URL:", font=default_font)
        base_url_label.pack(side=tk.LEFT, padx=5)
        self.base_url_entry = ttk.Entry(api_frame, textvariable=self.base_url_var, width=40, font=default_font)
        self.base_url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
         # 更新 API 设置按钮
        update_api_button = ttk.Button(api_frame, text="更新 API 设置", command=self.update_api_settings)
        update_api_button.pack(side=tk.LEFT, padx=5)
        
        # 模型选择部分
        model_frame = ttk.Frame(main_frame)
        model_frame.pack(fill=tk.X, pady=5)
        
        model_label = ttk.Label(model_frame, text="选择模型:", font=default_font)
        model_label.pack(side=tk.LEFT, padx=5)
        
        self.model_var = tk.StringVar(root)
        self.model_var.set("gemini-2.0-flash-exp")
        
        self.model_dropdown = ttk.Combobox(model_frame, textvariable=self.model_var, 
                                         values=["gemini-2.0-flash-exp", "claude-3-5-sonnet-20241022", "gpt-4o-all"],
                                         font=default_font)
        self.model_dropdown.pack(side=tk.LEFT, padx=5)
        
        # 翻译接口按钮
        translate_button = ttk.Button(model_frame, text="翻译接口", command=self.open_translation_window)
        translate_button.pack(side=tk.LEFT, padx=5)
        
        # 参数设置部分
        params_frame = ttk.Frame(main_frame)
        params_frame.pack(fill=tk.X, pady=5)
        
        # temperature
        temp_label = ttk.Label(params_frame, text="随机性 (Temperature):", font=default_font)
        temp_label.pack(side=tk.LEFT, padx=5)
        self.temp_var = tk.DoubleVar(root, value=0.7)
        self.temp_entry = ttk.Entry(params_frame, textvariable=self.temp_var, width=5, font=default_font)
        self.temp_entry.pack(side=tk.LEFT, padx=5)
        
        # max_tokens
        max_tokens_label = ttk.Label(params_frame, text="单次回复限制 (Max Tokens):", font=default_font)
        max_tokens_label.pack(side=tk.LEFT, padx=5)
        self.max_tokens_var = tk.IntVar(root, value=1000)
        self.max_tokens_entry = ttk.Entry(params_frame, textvariable=self.max_tokens_var, width=5, font=default_font)
        self.max_tokens_entry.pack(side=tk.LEFT, padx=5)
        
        # presence_penalty
        presence_label = ttk.Label(params_frame, text="话题新鲜度 (Presence Penalty):", font=default_font)
        presence_label.pack(side=tk.LEFT, padx=5)
        self.presence_var = tk.DoubleVar(root, value=0.0)
        self.presence_entry = ttk.Entry(params_frame, textvariable=self.presence_var, width=5, font=default_font)
        self.presence_entry.pack(side=tk.LEFT, padx=5)
        
        # frequency_penalty
        frequency_label = ttk.Label(params_frame, text="频率惩罚度 (Frequency Penalty):", font=default_font)
        frequency_label.pack(side=tk.LEFT, padx=5)
        self.frequency_var = tk.DoubleVar(root, value=0.0)
        self.frequency_entry = ttk.Entry(params_frame, textvariable=self.frequency_var, width=5, font=default_font)
        self.frequency_entry.pack(side=tk.LEFT, padx=5)
        
        # history_count
        history_label = ttk.Label(params_frame, text="历史消息数:", font=default_font)
        history_label.pack(side=tk.LEFT, padx=5)
        self.history_var = tk.IntVar(root, value=5)  # 默认保留最近5条消息
        self.history_entry = ttk.Entry(params_frame, textvariable=self.history_var, width=5, font=default_font)
        self.history_entry.pack(side=tk.LEFT, padx=5)
        
        # Prompt输入区域
        prompt_frame = ttk.Frame(main_frame)
        prompt_frame.pack(fill=tk.X, pady=5)
        
        # 角色名输入框
        role_name_label = ttk.Label(prompt_frame, text="角色名:", font=default_font)
        role_name_label.pack(anchor=tk.W)
        self.role_name_entry = ttk.Entry(prompt_frame, font=default_font)
        self.role_name_entry.pack(fill=tk.X)
        
        # 命令区输入框
        command_label = ttk.Label(prompt_frame, text="命令区:", font=default_font)
        command_label.pack(anchor=tk.W)
        self.command_field = tk.Text(prompt_frame, wrap=tk.WORD, height=3, font=default_font)
        self.command_field.pack(fill=tk.X)
        
        # 记忆区输入框
        memory_label = ttk.Label(prompt_frame, text="记忆区:", font=default_font)
        memory_label.pack(anchor=tk.W)
        self.memory_field = tk.Text(prompt_frame, wrap=tk.WORD, height=3, font=default_font)
        self.memory_field.pack(fill=tk.X)
        
        # 回顾区输入框
        review_label = ttk.Label(prompt_frame, text="回顾区:", font=default_font)
        review_label.pack(anchor=tk.W)
        self.review_field = tk.Text(prompt_frame, wrap=tk.WORD, height=3, font=default_font)
        self.review_field.pack(fill=tk.X)
        
        # 交互区输入框
        interaction_label = ttk.Label(prompt_frame, text="交互区:", font=default_font)
        interaction_label.pack(anchor=tk.W)
        self.interaction_field = tk.Text(prompt_frame, wrap=tk.WORD, height=3, font=default_font)
        self.interaction_field.pack(fill=tk.X)
        
        
        # 创建聊天显示区域（带滚动条）
        chat_frame = ttk.Frame(main_frame)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(chat_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建HTML显示区域
        self.html_label = HTMLLabel(chat_frame, html="", height=20)
        self.html_label.pack(fill=tk.BOTH, expand=True)
        
        # 配置滚动条
        scrollbar.config(command=self.html_label.yview)
        self.html_label.configure(yscrollcommand=scrollbar.set)
        
        # 创建输入区域
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        self.input_field = ttk.Entry(input_frame, font=default_font)
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.send_button = ttk.Button(input_frame, text="发送", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)
        
        # 绑定回车键
        self.input_field.bind('<Return>', lambda event: self.send_message())
        
        # 初始化对话历史
        self.conversation_history = []
        self.messages_html = []
        
        # 初始化显示
        self.update_chat_display()
        
        # 初始化 UI 更新队列
        self.ui_queue = queue.Queue()
        self.root.after(100, self.process_ui_queue)  # 每 100 毫秒处理一次 UI 队列
        
        # 创建并启动 asyncio 事件循环线程
        self.loop = asyncio.new_event_loop()
        self.async_thread = threading.Thread(target=self.start_async_loop, args=(self.loop,), daemon=True)
        self.async_thread.start()

    def start_async_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()
    
    def create_openai_client(self):
        return AsyncOpenAI(
            api_key=self.api_key_var.get(),
            base_url=self.base_url_var.get()
        )
    
    def update_api_settings(self):
        self.client = self.create_openai_client()
        print("API设置已更新")
    
    def update_chat_display(self):
        html_content = """
        <html>
        <body style="font-family: 'Microsoft YaHei', sans-serif; background-color: #f0f0f0;">
        <div style="padding: 10px;">
        {}
        </div>
        </body>
        </html>
        """.format("\n".join(self.messages_html))
        
        self.html_label.set_html(html_content)

    def send_message(self):
        user_message = self.input_field.get()
        if user_message.strip() == "":
            return
        
        # 获取各个prompt区域的内容
        role_name = self.role_name_entry.get().strip()
        command_text = self.command_field.get("1.0", tk.END).strip()
        memory_text = self.memory_field.get("1.0", tk.END).strip()
        review_text = self.review_field.get("1.0", tk.END).strip()
        interaction_text = self.interaction_field.get("1.0", tk.END).strip()
        
        # 构建完整的prompt，不包含角色名
        prompt_text = self.construct_prompt(command_text, memory_text, review_text, interaction_text)
        
        if prompt_text:
            self.conversation_history.append({"role": "system", "content": prompt_text})
            
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # 添加用户消息到HTML显示
        user_bubble = f"""<div style="background-color: #DCF8C6; padding: 10px; margin: 5px; border-radius: 10px; font-size: 14px; word-wrap: break-word;">
            <strong>You:</strong><br>{user_message}
            </div>"""
        self.messages_html.append(user_bubble)
        self.update_chat_display()
        
        self.input_field.delete(0, tk.END)
        
        # 使用 asyncio.run_coroutine_threadsafe
        asyncio.run_coroutine_threadsafe(self.get_bot_response(user_message, role_name), self.loop)

    def construct_prompt(self, command_text, memory_text, review_text, interaction_text):
        prompt = f"""
        命令区:
        {command_text if command_text else "无"}
        
        记忆区:
        {memory_text if memory_text else "无"}
        
        回顾区:
        {review_text if review_text else "无"}
        
        交互区:
        {interaction_text if interaction_text else "无"}
        
        请注意，以下是对各个区域的解释：
        - 命令区：AI 必须遵守的命令，任何时候都不能忘记和违抗的命令。
        - 记忆区：存放角色设定、世界观等，用于保持角色的一致性。
        - 回顾区：存放 AI 之前的历史内容，用于上下文理解。
        - 交互区：用户扮演的角色的行为、对话和心理。
        """
        return prompt
    
    def process_ui_queue(self):
        """处理 UI 更新队列"""
        try:
            while True:
                update_type, data = self.ui_queue.get_nowait()
                if update_type == "chat_message":
                    self.messages_html.append(data)
                    self.update_chat_display()
                    self.html_label.yview_moveto(1.0)
                elif update_type == "update_chat":
                    self.messages_html.pop()
                    self.messages_html.append(data)
                    self.update_chat_display()
                    self.html_label.yview_moveto(1.0)
                self.ui_queue.task_done()
        except queue.Empty:
            pass
        self.root.after(100, self.process_ui_queue)
    
    async def get_bot_response(self, user_message, role_name):
        try:
            # 获取历史消息数
            history_count = self.history_var.get()
            
            # 截取历史消息
            if len(self.conversation_history) > history_count:
                messages_to_send = self.conversation_history[-history_count:]
            else:
                messages_to_send = self.conversation_history
            
            stream = await self.client.chat.completions.create(
                model=self.model_var.get(),
                messages=messages_to_send,
                temperature=self.temp_var.get(),
                max_tokens=self.max_tokens_var.get(),
                presence_penalty=self.presence_var.get(),
                frequency_penalty=self.frequency_var.get(),
                stream=True
            )
            
            bot_response = ""
            # 创建初始的空消息
            html_content = markdown.markdown(bot_response)
            
            # 根据角色名设置显示名称
            display_name = role_name if role_name else "AI"
            
            temp_message = f"""<div style="background-color: #E8E8E8; padding: 10px; margin: 5px; border-radius: 10px; font-size: 14px; word-wrap: break-word;">
                <strong>{display_name}:</strong><br>{html_content}
                </div>"""
            
            # 添加初始消息到 UI 队列
            self.ui_queue.put(("chat_message", temp_message))
            
            # 用于批量更新的缓冲区
            buffer = ""
            last_update_time = time.time()
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    new_content = chunk.choices[0].delta.content
                    bot_response += new_content
                    buffer += new_content
                    
                    # 每10ms更新一次显示，或缓冲区达到一定大小
                    current_time = time.time()
                    if current_time - last_update_time > 0.01 or len(buffer) > 5:
                        html_content = markdown.markdown(bot_response)
                        
                        # 根据角色名设置显示名称
                        display_name = role_name if role_name else "AI"
                        
                        temp_message = f"""<div style="background-color: #E8E8E8; padding: 10px; margin: 5px; border-radius: 10px; font-size: 14px; word-wrap: break-word;">
                            <strong>{display_name}:</strong><br>{html_content}
                            </div>"""
                        
                        # 添加更新消息到 UI 队列
                        self.ui_queue.put(("update_chat", temp_message))
                        buffer = ""
                        last_update_time = current_time
            
            # 确保最后一次更新显示完整消息
            if buffer:  # 处理剩余的缓冲区内容
                html_content = markdown.markdown(bot_response)
                
                # 根据角色名设置显示名称
                display_name = role_name if role_name else "AI"
                
                temp_message = f"""<div style="background-color: #E8E8E8; padding: 10px; margin: 5px; border-radius: 10px; font-size: 14px; word-wrap: break-word;">
                    <strong>{display_name}:</strong><br>{html_content}
                    </div>"""
                # 添加最后一次更新消息到 UI 队列
                self.ui_queue.put(("update_chat", temp_message))
            
            self.conversation_history.append({"role": "assistant", "content": bot_response})
            
        except Exception as e:
            error_message = f"Error: {str(e)}"
            error_bubble = f"""<div style="background-color: #FFD2D2; padding: 10px; margin: 5px; border-radius: 10px; font-size: 14px; word-wrap: break-word;">
                <strong>Error:</strong><br>{error_message}
                </div>"""
            # 添加错误消息到 UI 队列
            self.ui_queue.put(("chat_message", error_bubble))


    def open_translation_window(self):
        translation_window = tk.Toplevel(self.root)
        translation_window.title("翻译接口设置")
        translation_window.geometry("1100x600")
        
        # 设置默认字体
        default_font = ("Microsoft YaHei", 10)
        
        # 创建主框架
        main_frame = ttk.Frame(translation_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # API 设置部分
        api_frame = ttk.Frame(main_frame)
        api_frame.pack(fill=tk.X, pady=5)
        
        # api_key 输入框
        api_key_label = ttk.Label(api_frame, text="API Key:", font=default_font)
        api_key_label.pack(side=tk.LEFT, padx=5)
        self.trans_api_key_var = tk.StringVar(translation_window, value=self.api_key_var.get())
        api_key_entry = ttk.Entry(api_frame, textvariable=self.trans_api_key_var, width=40, font=default_font)
        api_key_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # base_url 输入框
        base_url_label = ttk.Label(api_frame, text="Base URL:", font=default_font)
        base_url_label.pack(side=tk.LEFT, padx=5)
        self.trans_base_url_var = tk.StringVar(translation_window, value=self.base_url_var.get())
        base_url_entry = ttk.Entry(api_frame, textvariable=self.trans_base_url_var, width=40, font=default_font)
        base_url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
         # 更新 API 设置按钮
        update_api_button = ttk.Button(api_frame, text="更新 API 设置", command=self.update_trans_api_settings)
        update_api_button.pack(side=tk.LEFT, padx=5)
        
        # 模型选择部分
        model_frame = ttk.Frame(main_frame)
        model_frame.pack(fill=tk.X, pady=5)
        
        model_label = ttk.Label(model_frame, text="选择模型:", font=default_font)
        model_label.pack(side=tk.LEFT, padx=5)
        
        self.trans_model_var = tk.StringVar(translation_window, value=self.model_var.get())
        
        model_dropdown = ttk.Combobox(model_frame, textvariable=self.trans_model_var, 
                                         values=["gemini-2.0-flash-exp", "claude-3-5-sonnet-20241022", "gpt-4o-all"],
                                         font=default_font)
        model_dropdown.pack(side=tk.LEFT, padx=5)
        
        # 参数设置部分
        params_frame = ttk.Frame(main_frame)
        params_frame.pack(fill=tk.X, pady=5)
        
        # temperature
        temp_label = ttk.Label(params_frame, text="随机性 (Temperature):", font=default_font)
        temp_label.pack(side=tk.LEFT, padx=5)
        self.trans_temp_var = tk.DoubleVar(translation_window, value=self.temp_var.get())
        temp_entry = ttk.Entry(params_frame, textvariable=self.trans_temp_var, width=5, font=default_font)
        temp_entry.pack(side=tk.LEFT, padx=5)
        
        # max_tokens
        max_tokens_label = ttk.Label(params_frame, text="单次回复限制 (Max Tokens):", font=default_font)
        max_tokens_label.pack(side=tk.LEFT, padx=5)
        self.trans_max_tokens_var = tk.IntVar(translation_window, value=self.max_tokens_var.get())
        max_tokens_entry = ttk.Entry(params_frame, textvariable=self.trans_max_tokens_var, width=5, font=default_font)
        max_tokens_entry.pack(side=tk.LEFT, padx=5)
        
        # presence_penalty
        presence_label = ttk.Label(params_frame, text="话题新鲜度 (Presence Penalty):", font=default_font)
        presence_label.pack(side=tk.LEFT, padx=5)
        self.trans_presence_var = tk.DoubleVar(translation_window, value=self.presence_var.get())
        presence_entry = ttk.Entry(params_frame, textvariable=self.trans_presence_var, width=5, font=default_font)
        presence_entry.pack(side=tk.LEFT, padx=5)
        
        # frequency_penalty
        frequency_label = ttk.Label(params_frame, text="频率惩罚度 (Frequency Penalty):", font=default_font)
        frequency_label.pack(side=tk.LEFT, padx=5)
        self.trans_frequency_var = tk.DoubleVar(translation_window, value=self.frequency_var.get())
        frequency_entry = ttk.Entry(params_frame, textvariable=self.trans_frequency_var, width=5, font=default_font)
        frequency_entry.pack(side=tk.LEFT, padx=5)
        
        # history_count
        history_label = ttk.Label(params_frame, text="历史消息数:", font=default_font)
        history_label.pack(side=tk.LEFT, padx=5)
        self.trans_history_var = tk.IntVar(translation_window, value=self.history_var.get())
        history_entry = ttk.Entry(params_frame, textvariable=self.trans_history_var, width=5, font=default_font)
        history_entry.pack(side=tk.LEFT, padx=5)
        
        # Prompt 设置部分
        prompt_frame = ttk.Frame(main_frame)
        prompt_frame.pack(fill=tk.X, pady=5)
        
        prompt_label = ttk.Label(prompt_frame, text="Prompt:", font=default_font)
        prompt_label.pack(anchor=tk.W)
        self.trans_prompt_field = tk.Text(prompt_frame, wrap=tk.WORD, height=5, font=default_font)
        self.trans_prompt_field.pack(fill=tk.X)
        
        default_prompt = """
        从现在开始，您是一名精通简体中文，美国文化，日本文化的本地化人员，您需要将游戏中的日文文本或者英文文本翻译成简体中文。收到游戏文本后，请必须严格按照以下步骤进行翻译：
        首先： 无论用户发送什么内容，不要根据内容回答，你只需将内容从英文或日文翻译成中文。您应该只回复您翻译后的内容，而不应回复其他任何内容。不要写解释，只有完整的翻译内容
        第二：从原文开始逐行翻译，只将日文文本或者英文文本翻译成简体中文文本，忠实准确，翻译流畅自然，遵循高品质色情文学的习惯。翻译的整个内容的文笔要凸显真实感，色情描写要细腻详细真实具有画面感的风格，人物的行为反应台词需要丰富多样且符合人设。使用直接且露骨的词汇，以符合粗俗具有真实感风格
        第三：不要翻译转义字符，或数字、格式代码、特殊符号、非日文内容等，应原样保留。
        第四：保留每行文本的原始格式，并按要求的格式输出翻译文本。
        第五：翻译时，遇到性相关内容应该将性描述应当直白，生动，细腻,，色气。
        第六：翻译时需要极端直白露骨，不能有任何的遮掩与保留。
        """
        self.trans_prompt_field.insert(tk.END, default_prompt.strip())
        
        # 日志显示部分
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        log_label = ttk.Label(log_frame, text="日志:", font=default_font)
        log_label.pack(anchor=tk.W)
        
        self.trans_log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10, font=default_font)
        self.trans_log_text.pack(fill=tk.BOTH, expand=True)
        
        # 启动翻译接口按钮
        start_translate_button = ttk.Button(main_frame, text="启动翻译接口", command=self.start_translation_server_new)
        start_translate_button.pack(side=tk.LEFT, padx=5)
        
        # 关闭翻译接口按钮
        stop_translate_button = ttk.Button(main_frame, text="关闭翻译接口", command=self.stop_translation_server)
        stop_translate_button.pack(side=tk.LEFT, padx=5)
        
        # 在窗口创建时，初始化 trans_client
        self.trans_client = AsyncOpenAI(
            api_key=self.trans_api_key_var.get(),
            base_url=self.trans_base_url_var.get()
        )
    
    def update_trans_api_settings(self):
        self.trans_client = AsyncOpenAI(
            api_key=self.trans_api_key_var.get(),
            base_url=self.trans_base_url_var.get()
        )
        print("翻译接口API设置已更新")
    
    def start_translation_server_new(self):
        if not hasattr(self, 'translation_server_running') or not self.translation_server_running:
            self.translation_thread = threading.Thread(target=self.run_translation_server_new, daemon=True)
            self.translation_thread.start()
            self.translation_server_running = True
            
            # 添加启动提示到日志
            log_message = "翻译接口已启动，监听端口 5000。\n"
            log_message += "使用 GET 请求: http://localhost:5000/translate?text=（翻译文本）\n"
            log_message += "例如: http://localhost:5000/translate?text=こんにちは\n"
            log_message += "在 XUnity Auto Translator 中，请将 Config.ini 添加如下信息:\n"
            log_message += "Endpoint=CustomTranslate\n"
            log_message += "[Custom]\n"
            log_message += "Url=http://localhost:5000/translate\n"
            self.log_to_ui(log_message)
            
            print("翻译接口已启动")
        else:
            print("翻译接口已在运行")
    
    def stop_translation_server(self):
        if hasattr(self, 'translation_server') and self.translation_server:
            # 使用 werkzeug.server.shutdown 来停止 Flask 应用
            self.translation_server.shutdown()
            self.translation_server = None
            self.translation_server_running = False
            
            # 添加关闭提示到日志
            log_message = "翻译接口已关闭。\n"
            self.log_to_ui(log_message)
            
            print("翻译接口已关闭")
        else:
            print("翻译接口未运行")
            
    def log_to_ui(self, message):
        """将日志消息添加到 UI，使用 tkinter 的 after 方法"""
        self.root.after(0, lambda: self.trans_log_text.insert(tk.END, message))
        self.root.after(0, lambda: self.trans_log_text.see(tk.END))

    def run_translation_server_new(self):
        
        app = FastAPI()
        
        async def fetch_translation(session, text, prompt):
            messages = [{"role": "system", "content": prompt},
                       {"role": "user", "content": text}]
            
            try:
                response = await self.trans_client.chat.completions.create(
                    model=self.trans_model_var.get(),
                    messages=messages,
                    temperature=self.trans_temp_var.get(),
                    max_tokens=self.trans_max_tokens_var.get(),
                    presence_penalty=self.trans_presence_var.get(),
                    frequency_penalty=self.trans_frequency_var.get()
                )
                translation_result = response.choices[0].message.content.strip()

                
                # Log the request and response
                log_message = f"请求: text={text}\n回复: {translation_result}\n"
                self.log_to_ui(log_message)
                
                return translation_result, 200
            except Exception as e:
                error_message = f"Request failed: {e}"
                log_message = f"请求: text={text}\n错误: {error_message}\n"
                self.log_to_ui(log_message)
                return {"error": error_message}, 500
        
        @app.get("/translate",response_class=PlainTextResponse)
        async def translate(text: str = Query(...)):
            if not text:
                return {"error": "Missing text parameter"}
            
            prompt = self.trans_prompt_field.get("1.0", tk.END).strip()
            
            async with aiohttp.ClientSession() as session:
                translation, status_code = await fetch_translation(session, text, prompt)
                return translation
        
        config = uvicorn.Config(app, host="0.0.0.0", port=5000, log_level="info")
        self.translation_server = uvicorn.Server(config)
        self.translation_server.run()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatGPTApp(root)
    root.mainloop()
