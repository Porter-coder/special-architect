# -*- coding: utf-8 -*-
"""
Hello World 程序单元测试
"""

import sys
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

# 导入被测试模块
from main import HelloWorldDisplay, ApplicationBootstrap

class TestHelloWorldDisplay(unittest.TestCase):
    """测试 HelloWorldDisplay 类"""

    def test_default_message(self):
        """测试默认消息"""
        display = HelloWorldDisplay()
        self.assertEqual(display.message, "Hello World!")

    def test_custom_message(self):
        """测试自定义消息"""
        display = HelloWorldDisplay(message="Custom Message")
        self.assertEqual(display.message, "Custom Message")

    def test_output_to_stdout(self):
        """测试输出到标准输出"""
        display = HelloWorldDisplay()

        # 捕获标准输出
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            display.show()
            output = mock_stdout.getvalue()
            self.assertEqual(output, "Hello World!\n")

    def test_output_to_custom_stream(self):
        """测试输出到自定义流"""
        custom_stream = StringIO()
        display = HelloWorldDisplay(output_stream=custom_stream)
        display.show()

        self.assertEqual(custom_stream.getvalue(), "Hello World!\n")

class TestConfigurationManager(unittest.TestCase):
    """测试配置管理器类"""

    def test_default_config(self):
        """测试默认配置"""
        from config_manager import ConfigurationManager

        config = ConfigurationManager()
        self.assertEqual(config.message, "Hello World!")
        self.assertEqual(config.encoding, "utf-8")

    @patch.dict('os.environ', {'HELLO_WORLD_MESSAGE': 'Env Message'})
    def test_env_config_override(self):
        """测试环境变量覆盖"""
        from config_manager import ConfigurationManager

        # 重新创建配置管理器以加载环境变量
        config = ConfigurationManager()
        self.assertEqual(config.message, "Env Message")

class TestMessagePipeline(unittest.TestCase):
    """测试消息处理管道"""

    def test_empty_pipeline(self):
        """测试空管道"""
        from message_handler import MessagePipeline

        pipeline = MessagePipeline()
        result = pipeline.process("Hello")
        self.assertEqual(result, "Hello")

    def test_single_handler(self):
        """测试单个处理器"""
        from message_handler import (
            MessagePipeline, 
            TrimHandler, 
            UpperCaseHandler
        )

        pipeline = MessagePipeline()
        pipeline.add_handler(UpperCaseHandler())

        result = pipeline.process("hello")
        self.assertEqual(result, "HELLO")

    def test_multiple_handlers(self):
        """测试多个处理器"""
        from message_handler import (
            MessagePipeline, 
            TrimHandler, 
            UpperCaseHandler
        )

        pipeline = MessagePipeline()
        pipeline.add_handler(TrimHandler())
        pipeline.add_handler(UpperCaseHandler())

        result = pipeline.process("  hello world  ")
        self.assertEqual(result, "HELLO WORLD")

class TestApplicationBootstrap(unittest.TestCase):
    """测试应用启动器类"""

    def test_init_with_custom_message(self):
        """测试自定义消息初始化"""
        bootstrap = ApplicationBootstrap("Custom Message")
        self.assertEqual(bootstrap.display_message, "Custom Message")

    def test_init_with_default_message(self):
        """测试默认消息初始化"""
        bootstrap = ApplicationBootstrap()
        self.assertEqual(bootstrap.display_message, "Hello World!")

if __name__ == '__main__':
    unittest.main()