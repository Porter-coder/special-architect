class GuessNumberGame:
    target_number: int      # 目标数字
    guess_count: int        # 猜测次数
    guess_history: List[int]  # 猜测历史
    min_range: int          # 范围最小值
    max_range: int          # 范围最大值
    best_record: Optional[int]  # 历史最佳记录