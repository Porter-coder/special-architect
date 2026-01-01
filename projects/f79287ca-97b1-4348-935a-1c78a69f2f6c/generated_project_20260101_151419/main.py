import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json

# 测试夹具定义
@pytest.fixture
def sample_config():
    """示例配置"""
    return {
        "greeting": "Hello, World!",
        "name": "Test",
        "count": 1,
        "locale": "en",
        "format": "plain"
    }

@pytest.fixture
def mock_locale_manager():
    """模拟语言管理器"""
    manager = Mock()
    manager.get_message.return_value = "Hello, World!"
    return manager

class TestGreetingGenerator:
    """问候语生成器单元测试"""

    def test_default_greeting(self, mock_locale_manager):
        """测试默认问候语生成"""
        from src.core.greeter import GreetingGenerator, GreetingConfig

        generator = GreetingGenerator(mock_locale_manager)
        config = GreetingConfig()

        result = generator.generate(config)

        assert result == "Hello, World!"
        mock_locale_manager.get_message.assert_called_once()

    def test_custom_name_replacement(self, mock_locale_manager):
        """测试自定义名称替换"""
        from src.core.greeter import GreetingGenerator, GreetingConfig

        generator = GreetingGenerator(mock_locale_manager)
        config = GreetingConfig(
            template="Hello, {name}!",
            name="Alice"
        )

        result = generator.generate(config)

        assert result == "Hello, Alice!"

    def test_multiple_placeholders(self, mock_locale_manager):
        """测试多个占位符替换"""
        from src.core.greeter import GreetingGenerator, GreetingConfig

        generator = GreetingGenerator(mock_locale_manager)
        config = GreetingConfig(
            template="Hello, {name}! Current time: {time}",
            name="Bob"
        )

        result = generator.generate(config)

        assert "Hello, Bob!" in result
        assert "Current time:" in result

    def test_unknown_placeholder_preserved(self, mock_locale_manager):
        """测试未知占位符保持不变"""
        from src.core.greeter import GreetingGenerator, GreetingConfig

        generator = GreetingGenerator(mock_locale_manager)
        config = GreetingConfig(
            template="Hello, {name}! {unknown}",
            name="Charlie"
        )

        result = generator.generate(config)

        assert "{unknown}" in result

    @pytest.mark.parametrize("count,expected", [
        (1, 1),
        (5, 5),
        (100, 100),
    ])
    def test_repeat_count(self, count, expected, mock_locale_manager):
        """参数化测试:重复次数"""
        from src.core.greeter import GreetingGenerator, GreetingConfig

        generator = GreetingGenerator(mock_locale_manager)
        # 测试生成逻辑中count的处理
        # 具体断言根据实现而定

class TestConfigValidation:
    """配置验证单元测试"""

    def test_valid_config(self):
        """测试有效配置"""
        from src.config.settings import AppConfig

        config = AppConfig(count=5)
        assert config.validate() is True

    def test_invalid_count_below_minimum(self):
        """测试无效配置:次数低于最小值"""
        from src.config.settings import AppConfig
        from src.config.exceptions import ValidationError

        config = AppConfig(count=0)

        with pytest.raises(ValidationError):
            config.validate()

    def test_invalid_count_above_maximum(self):
        """测试无效配置:次数超过最大值"""
        from src.config.settings import AppConfig
        from src.config.exceptions import ValidationError

        config = AppConfig(count=101)

        with pytest.raises(ValidationError):
            config.validate()

    def test_invalid_format(self):
        """测试无效配置:未知格式"""
        from src.config.settings import AppConfig
        from src.config.exceptions import ValidationError

        config = AppConfig(format="invalid")

        with pytest.raises(ValidationError):
            config.validate()

class TestOutputFormatting:
    """输出格式化单元测试"""

    def test_plain_format(self):
        """测试纯文本格式"""
        from src.core.output import PlainFormatter, FormattedOutput
        from datetime import datetime

        formatter = PlainFormatter()
        output = FormattedOutput(
            message="Hello",
            timestamp=datetime(2024, 1, 15, 10, 30, 0)
        )

        result = formatter.format(output)

        assert "Hello" in result
        assert "2024-01-15" in result

    def test_json_format(self):
        """测试JSON格式"""
        from src.core.output import JsonFormatter, FormattedOutput
        from datetime import datetime

        formatter = JsonFormatter()
        output = FormattedOutput(
            message="Hello",
            timestamp=datetime(2024, 1, 15, 10, 30, 0)
        )

        result = formatter.format(output)

        # 验证JSON可以解析
        parsed = json.loads(result)
        assert parsed["message"] == "Hello"
        assert "timestamp" in parsed

    def test_json_unicode_handling(self):
        """测试JSON的Unicode处理"""
        from src.core.output import JsonFormatter, FormattedOutput

        formatter = JsonFormatter()
        output = FormattedOutput(message="你好,世界！")

        result = formatter.format(output)
        parsed = json.loads(result)

        assert parsed["message"] == "你好,世界！"

class TestCLIInterface:
    """命令行接口单元测试"""

    def test_help_option(self, runner):
        """测试帮助选项"""
        from src.cli.main import cli

        result = runner.invoke(cli, ['--help'])

        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "Hello World" in result.output

    def test_version_option(self, runner):
        """测试版本选项"""
        from src.cli.main import cli

        result = runner.invoke(cli, ['--version'])

        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_default_execution(self, runner):
        """测试默认执行"""
        from src.cli.main import cli

        result = runner.invoke(cli)

        assert result.exit_code == 0
        assert "Hello, World!" in result.output

    def test_custom_name(self, runner):
        """测试自定义名称"""
        from src.cli.main import cli

        result = runner.invoke(cli, ['--name', 'Alice'])

        assert result.exit_code == 0
        assert "Alice" in result.output

    def test_invalid_count(self, runner):
        """测试无效次数参数"""
        from src.cli.main import cli

        result = runner.invoke(cli, ['--count', '0'])

        assert result.exit_code != 0
        assert "Error" in result.output

    @pytest.fixture
    def runner(self):
        """测试运行器夹具"""
        from click.testing import CliRunner
        return CliRunner()