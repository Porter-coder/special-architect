# core/application.py
class TimerApplication:
    """
    应用入口类，负责全局初始化和生命周期管理
    
    职责范围：
    1. 协调各层组件的初始化顺序
    2. 管理应用级别的事件循环
    3. 处理应用级异常和优雅退出
    4. 提供全局服务访问点
    """
    
    def __init__(self):
        self._instance = None
        self._is_running = False
        self._components = {}
        
    def initialize(self) -> bool:
        """按依赖顺序初始化所有组件"""
        # 第一阶段：初始化配置和日志
        self._components['config'] = ConfigManager.get_instance()
        self._components['logger'] = LoggerManager.get_instance()
        
        # 第二阶段：初始化数据层
        self._components['database'] = DatabaseManager.get_instance()
        self._components['repository'] = TimerRepository()
        
        # 第三阶段：初始化业务层
        self._components['engine'] = TimerEngine.get_instance()
        self._components['group_manager'] = GroupManager()
        self._components['statistics'] = StatisticsService()
        
        # 第四阶段：初始化表现层
        self._components['main_window'] = MainWindow()
        self._components['tray_icon'] = SystemTrayIcon()
        
        return True
    
    def run(self) -> None:
        """启动主事件循环"""
        self._is_running = True
        self._components['main_window'].show()
        self._components['engine'].start_all()
        self._main_loop()