# -*- coding: utf-8 -*-
"""
@Create Time    : 2025/6/8 20:20
@Author  :  wangyiming
 
@Description:
"""
from typing import List

from leader_board_service import LeaderboardService, RankInfo


class DenseLeaderboardService(LeaderboardService):
    def get_player_rank(self, player_id: str) -> RankInfo:
        if player_id not in self.players:
            raise ValueError("Player not found")

        score, timestamp = self.players[player_id]
        # 计算密集排名
        rank = 1
        prev_score = None
        for i, (neg_score, _, _) in enumerate(self.sorted_players):
            current_score = -neg_score
            if prev_score is not None and current_score != prev_score:
                rank += 1
            if current_score == score:
                # 找到第一个等于当前分数的玩家
                return RankInfo(
                    player_id=player_id,
                    rank=rank,
                    score=score
                )
            prev_score = current_score
        return RankInfo(player_id=player_id, rank=rank, score=score)

    def get_top_n(self, n: int) -> List[RankInfo]:
        result = []
        rank = 1
        prev_score = None
        # count = 0

        for i, (neg_score, timestamp, player_id) in enumerate(self.sorted_players):
            current_score = -neg_score
            if prev_score is not None and current_score != prev_score:
                rank += 1
            if rank > n:
                # 如需返回前n个玩家 这里使用count >= n即可
                break
            result.append(RankInfo(
                player_id=player_id,
                rank=rank,
                score=current_score
            ))
            # count += 1
            prev_score = current_score

        return result

    def get_player_rank_range(self, player_id: str, range_size: int) -> List[RankInfo]:
        if player_id not in self.players:
            raise ValueError("Player not found")

        # 收集所有玩家及其密集排名
        all_players = []
        rank = 1
        prev_score = None
        for i, (neg_score, timestamp, pid) in enumerate(self.sorted_players):
            current_score = -neg_score
            if prev_score is not None and current_score != prev_score:
                rank += 1
            all_players.append((rank, pid, current_score, timestamp))
            prev_score = current_score

        # 找到目标玩家在列表中的位置
        target_index = next(i for i, (r, pid, *_) in enumerate(all_players)
                            if pid == player_id)

        # 获得遍历起始点与结束点
        start = max(0, target_index - range_size)
        end = min(len(all_players), target_index + range_size + 1)

        return [
            RankInfo(
                player_id=pid,
                rank=r,
                score=score
            )
            for r, pid, score, timestamp in all_players[start:end]
        ]


# 例子
if __name__ == "__main__":
    dense_leader_board_service = DenseLeaderboardService()

    # 更新分数
    dense_leader_board_service.update_score("A", 100, 1)
    dense_leader_board_service.update_score("B", 100, 2)
    dense_leader_board_service.update_score("C", 95, 3)
    dense_leader_board_service.update_score("D", 95, 4)
    dense_leader_board_service.update_score("E", 90, 5)

    # 查询排名
    print("A rank:", dense_leader_board_service.get_player_rank("A").rank)  # 应为1
    print("C rank:", dense_leader_board_service.get_player_rank("C").rank)  # 应为3

    # 获取前3名
    print("前3名:")
    for player in dense_leader_board_service.get_top_n(3):
        print(f"Rank {player.rank}: {player.player_id} ({player.score})")

    # 获取玩家C周边2名
    print("玩家C周边2位:")
    for player in dense_leader_board_service.get_player_rank_range("C", 2):
        print(f"Rank {player.rank}: {player.player_id} ({player.score})")