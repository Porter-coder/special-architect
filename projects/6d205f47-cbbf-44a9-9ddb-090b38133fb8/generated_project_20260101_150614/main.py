# main.py
class HelloWorldProgram:
    def __init__(self):
        self.config = self._load_config()
        self.output_handler = OutputHandler()
        self.logger = Logger()

    def _load_config(self):
        # 配置加载逻辑
        return {"message": "Hello, World!"}

    def run(self):
        try:
            message = self.config.get("message")
            self.output_handler.print_message(message)
            self.logger.info("程序执行成功")
        except Exception as e:
            self.logger.error(f"执行错误: {e}")
            raise

if __name__ == "__main__":
    program = HelloWorldProgram()
    program.run()