# -*- coding: utf-8 -*-
"""
@Create Time    : 2025/6/8 19:36
@Author  :  wangyiming
 
@Description: 乐堡互娱 - 后端社招笔试题目-游戏排行榜系统
"""
import bisect
from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class RankInfo:
    player_id: str
    rank: int
    score: int


class LeaderboardService:
    """基于内存的排行榜系统 按分数降序，时间戳升序排列"""
    def __init__(self):
        # 字典存储玩家数据
        self.players: Dict[str, Tuple[int, int]] = {}  # {player_id: (score, timestamp)}

        # 列表存储排序后的玩家数据
        self.sorted_players: List[Tuple[int, int, str]] = []  # (score, timestamp, player_id)

    def update_score(self, player_id: str, score: int, timestamp: int) -> None:
        """更新玩家分数"""
        # 历史数据处理
        if player_id in self.players:
            old_score, old_timestamp = self.players[player_id]
            if old_score == score and old_timestamp == timestamp:
                # 无变化
                return

            # 移除旧记录
            index = bisect.bisect_left(self.sorted_players, (-old_score, old_timestamp, player_id))
            if index < len(self.sorted_players) and self.sorted_players[index] == (
            -old_score, old_timestamp, player_id):
                self.sorted_players.pop(index)

        # 更新玩家数据
        self.players[player_id] = (score, timestamp)

        # 更新列表 (-score目的是降序排列)
        bisect.insort(self.sorted_players, (-score, timestamp, player_id))

    def get_player_rank(self, player_id: str) -> RankInfo:
        """获取玩家当前排名"""
        if player_id not in self.players:
            raise ValueError("Player not found")

        score, timestamp = self.players[player_id]
        # 查找玩家在排序列表中的位置
        index = bisect.bisect_left(self.sorted_players, (-score, timestamp, player_id))

        return RankInfo(
            player_id=player_id,
            rank=index + 1,  # 排名从1开始
            score=score
        )

    def get_top_n(self, n: int) -> List[RankInfo]:
        """获取排行榜前N名"""
        result = []
        for i, (neg_score, timestamp, player_id) in enumerate(self.sorted_players[:n]):
            result.append(RankInfo(
                player_id=player_id,
                rank=i + 1,
                score=-neg_score
            ))
        return result

    def get_player_rank_range(self, player_id: str, range_size: int) -> List[RankInfo]:
        """获取玩家周边排名"""
        if player_id not in self.players:
            raise ValueError("Player not found")

        rank_info = self.get_player_rank(player_id)
        rank = rank_info.rank
        # 获得遍历起始点与结束点
        start = max(0, rank - 1 - range_size)
        end = min(len(self.sorted_players), rank + range_size)

        result = []
        for i in range(start, end):
            neg_score, timestamp, pid = self.sorted_players[i]
            result.append(RankInfo(
                player_id=pid,
                rank=i + 1,
                score=-neg_score
            ))

        return result


# 例子
if __name__ == "__main__":
    leader_board_service = LeaderboardService()

    # 更新分数
    leader_board_service.update_score("A", 100, 1)
    leader_board_service.update_score("B", 100, 2)
    leader_board_service.update_score("C", 95, 3)
    leader_board_service.update_score("D", 95, 4)
    leader_board_service.update_score("E", 90, 5)

    # 查询排名
    print("A rank:", leader_board_service.get_player_rank("A").rank)  # 应为1
    print("C rank:", leader_board_service.get_player_rank("C").rank)  # 应为3

    # 获取前3名
    print("前3名:")
    for player in leader_board_service.get_top_n(3):
        print(f"Rank {player.rank}: {player.player_id} ({player.score})")

    # 获取玩家C周边2名
    print("玩家C周边2位:")
    for player in leader_board_service.get_player_rank_range("C", 2):
        print(f"Rank {player.rank}: {player.player_id} ({player.score})")