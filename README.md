# ChatEndpoint
一个闲着没事干随便搓的小玩意，就两个作用：
    1.当一个破产版酒馆用
    2.为[XUnity Auto Translator](https://github.com/bbepis/XUnity.AutoTranslator)提供官方和第三方api站的翻译接口

这破产版酒馆唯一的作用就是测测角色卡的水平

XUnity Auto Translator是为unity提供的一个翻译插件，这个插件作者似乎没有提供比较懒狗的api站接口，于是随便拿python搓了一个
    简单的使用教程：
    1.安装python3.x
    2.安装一堆库：pip install openai markdown tkhtmlview aiohttp fastapi uvicorn
    3.运行ChatEndpoint.py并配置好你的key和url，点击启动翻译接口
    4.根据[XUnity Auto Translator](https://github.com/bbepis/XUnity.AutoTranslator)的教程将XUnity Auto Translator注入到unity的游戏中
    5.在游戏目录中找到并修改AutoTranslator\Config.ini：
    Endpoint=CustomTranslate

    [Custom]
    Url=http://localhost:5000/translate
    
    6.然后就完了

这玩意经过测试支持并发翻译，但是在XUnity Auto Translator似乎没什么太大区别，希望有大佬来修一下

看到同样用[XUnity Auto Translator](https://github.com/bbepis/XUnity.AutoTranslator)提供unity翻译的，4o且只有4o卖30一个月，去api站买30r的4o能用半年，况且现在还有很多比4o更好更便宜的模型

