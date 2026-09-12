# result_saver.py
import os
import json
import csv
from datetime import datetime

class BatchResultSaver:
    def __init__(self, save_dir="backtest_results"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        self.results = []
        
    def add(self, result_dict):
        """添加单条回测结果"""
        if result_dict is not None:
            self.results.append(result_dict)
            
    def save_all(self, filename="batch_summary_15stocks"):
        """
        将收集到的所有结果同时保存为 JSON 和 CSV
        """
        if not self.results:
            print("⚠️ 没有可保存的结果")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # 保存JSON（适合程序读取）
        json_path = os.path.join(self.save_dir, f"{filename}_{timestamp}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
            
        # 保存CSV（适合Excel查看）
        csv_path = os.path.join(self.save_dir, f"{filename}_{timestamp}.csv")
        df = __import__('pandas').DataFrame(self.results)
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        print(f"\n💾 批量结果已保存:")
        print(f"   📄 JSON: {os.path.abspath(json_path)}")
        print(f"   📊 CSV:  {os.path.abspath(csv_path)}")
        print(f"   共 {len(self.results)} 只股票的有效净值")
        
        return  csv_path