"""
可视化模块 - 负责生成各种图表
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import pandas as pd
import numpy as np
from typing import Optional, Dict, List
from datetime import datetime
import seaborn as sns
from core.config import SystemConfig

class SalesVisualizer:
    """销售数据可视化器类"""

    def __init__(self, config: SystemConfig.visualization.__class__ = None):
        self.config = config or SystemConfig.visualization
        self._setup_plotting_style()

    def _setup_plotting_style(self):
        """设置绘图样式"""
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams['figure.figsize'] = self.config.figure_size
        plt.rcParams['font.size'] = self.config.label_fontsize
        plt.rcParams['axes.titlesize'] = self.config.title_fontsize

    def create_monthly_revenue_bar_chart(self, monthly_data: pd.DataFrame, 
                                        title: str = None) -> plt.Figure:
        """创建月度收入条形图"""
        if monthly_data.empty:
            raise ValueError("月度数据为空,无法创建图表")

        fig, ax = plt.subplots(figsize=self.config.figure_size, dpi=self.config.dpi)

        # 准备数据
        months = monthly_data['year_month'].astype(str)
        revenues = monthly_data['total_revenue'] / 10000  # 转换为万元

        # 创建渐变色条形图
        colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(months)))

        bars = ax.bar(months, revenues, color=colors, edgecolor='navy', linewidth=0.5)

        # 添加数据标签
        for bar, revenue in zip(bars, revenues):
            height = bar.get_height()
            ax.annotate(f'{revenue:.1f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),  # 3 points vertical offset
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=9)

        # 设置标题和标签
        title = title or "月度销售收入统计"
        ax.set_title(title, fontsize=self.config.title_fontsize + 2, fontweight='bold')
        ax.set_xlabel('月份', fontsize=self.config.label_fontsize)
        ax.set_ylabel('收入(万元)', fontsize=self.config.label_fontsize)

        # 设置x轴标签旋转
        plt.xticks(rotation=self.config.rotation_angle, ha='right')

        # 添加网格线
        ax.yaxis.grid(True, linestyle='--', alpha=self.config.grid_alpha)
        ax.set_axisbelow(True)

        # 调整布局
        plt.tight_layout()

        return fig

    def create_combined_dashboard(self, monthly_data: pd.DataFrame, 
                                 channel_data: pd.DataFrame) -> plt.Figure:
        """创建综合仪表板"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=self.config.dpi)

        # 1. 月度收入条形图
        ax1 = axes[0, 0]
        months = monthly_data['year_month'].astype(str)
        revenues = monthly_data['total_revenue'] / 10000

        colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(months)))
        bars = ax1.bar(months, revenues, color=colors, edgecolor='navy', linewidth=0.5)
        ax1.set_title('月度收入趋势', fontsize=12, fontweight='bold')
        ax1.set_xlabel('月份')
        ax1.set_ylabel('收入(万元)')
        ax1.tick_params(axis='x', rotation=45)

        # 2. 渠道分布饼图
        ax2 = axes[0, 1]
        if not channel_data.empty:
            colors_pie = plt.cm.Set3(np.linspace(0, 1, len(channel_data)))
            wedges, texts, autotexts = ax2.pie(
                channel_data['total_amount'], 
                labels=channel_data['sales_channel'],
                autopct='%1.1f%%',
                colors=colors_pie,
                explode=[0.05] * len(channel_data)
            )
            ax2.set_title('渠道收入分布', fontsize=12, fontweight='bold')

        # 3. 增长率折线图
        ax3 = axes[1, 0]
        if 'growth_rate' in monthly_data.columns:
            growth_rates = monthly_data['growth_rate'].fillna(0)
            ax3.plot(months, growth_rates, marker='o', color='green', linewidth=2)
            ax3.axhline(y=0, color='red', linestyle='--', alpha=0.7)
            ax3.fill_between(months, growth_rates, 0, alpha=0.3, color='green')
            ax3.set_title('月环比增长率', fontsize=12, fontweight='bold')
            ax3.set_xlabel('月份')
            ax3.set_ylabel('增长率(%)')
            ax3.tick_params(axis='x', rotation=45)

        # 4. 季度对比柱状图
        ax4 = axes[1, 1]
        quarterly_data = monthly_data.copy()
        quarterly_data['quarter'] = pd.to_datetime(quarterly_data['year_month'].astype(str)).dt.quarter
        quarterly_revenue = quarterly_data.groupby('quarter')['total_revenue'].sum() / 10000

        quarter_colors = plt.cm.Paired(np.linspace(0, 1, 4))
        ax4.bar(['Q1', 'Q2', 'Q3', 'Q4'], quarterly_revenue, color=quarter_colors, edgecolor='black')
        ax4.set_title('季度收入对比', fontsize=12, fontweight='bold')
        ax4.set_xlabel('季度')
        ax4.set_ylabel('收入(万元)')

        # 添加数值标签
        for i, (q, rev) in enumerate(zip(['Q1', 'Q2', 'Q3', 'Q4'], quarterly_revenue)):
            ax4.text(i, rev + 5, f'{rev:.1f}', ha='center', fontsize=10)

        plt.suptitle('销售数据分析仪表板', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()

        return fig

    def save_chart(self, fig: plt.Figure, filename: str = None) -> str:
        """保存图表到文件"""
        if filename is None:
            filename = self.config.output_path

        fig.savefig(filename, dpi=self.config.dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')

        return filename