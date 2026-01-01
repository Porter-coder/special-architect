# 单元测试示例
class TestMessageHandler(unittest.TestCase):
    def test_format_message(self):
        handler = MessageHandler()
        result = handler.format_message("Hello World??")
        self.assertEqual(result, "Hello World??")

    def test_empty_message(self):
        handler = MessageHandler()
        with self.assertRaises(ValueError):
            handler.format_message("")