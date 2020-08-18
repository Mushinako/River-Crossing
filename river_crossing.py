#!/usr/bin/env python3
import math
import json
from dataclasses import dataclass
from itertools import combinations
from typing import Tuple, List, Generator, Dict

CONFIG_PATH = "config.json"
SOLUTION_PATH = "solution.json"


@dataclass
class Horse:
    id_: str
    speed: int
    spent: int = 0
    passed: bool = False


class Step:
    def __init__(self, parent, horses: Dict[str, Horse], choice: Tuple[str, ...], passed_after: bool) -> None:
        self.parent = parent
        self.horses = {h.id_: Horse(
            h.id_, h.speed, h.spent, h.passed) for h in horses.values()}
        self.choice = tuple((self.horses[hn] for hn in choice))
        self.passed = passed_after
        self.time = max((h.speed for h in self.choice))

    @property
    def is_viable(self) -> bool:
        return all((h.spent <= (TIME_MAX - self.time) for h in self.choice))

    @property
    def avail_horses(self) -> Generator[str, None, None]:
        return (h.id_ for h in self.horses.values() if h.passed == self.passed)

    @property
    def all_passed(self) -> bool:
        return all((h.passed for h in self.horses.values()))

    @property
    def tot_time(self) -> int:
        return self.parent.tot_time + self.time

    @property
    def horse_time(self) -> Tuple[int, ...]:
        return tuple(h.spent for h in sorted(self.horses.values(), key=lambda h: h.id_))

    @property
    def path(self) -> List[Tuple[str, ...]]:
        return self.parent.path + [tuple((h.id_ for h in self.choice))]

    def execute(self) -> List[Tuple[int, Tuple[int, ...], List[Tuple[str, ...]]]]:
        # print(f"Current: {self.path}")
        for h in self.choice:
            h.passed ^= True
            h.spent += self.time
        if self.all_passed:
            paths = [(self.tot_time, self.horse_time, self.path)]
            return paths
        avail_horses = tuple(self.avail_horses)
        if self.passed:
            step_pool = ((c, ) for c in avail_horses)
        else:
            step_pool = (c for r in range(2, HORSE_LIMIT + 1)
                         for c in combinations(avail_horses, r))
        pot_children = (Step(self, self.horses, choice, not self.passed)
                        for choice in step_pool)
        # Check each potential children
        paths: List[Tuple[int, Tuple[int, ...], List[Tuple[str, ...]]]] = []
        for s in pot_children:
            # Has to not exceed time limit
            if not s.is_viable:
                continue
            # Kinda recursion
            children_paths = s.execute()
            if len(children_paths) > 0:
                paths += children_paths
        return paths


class RootStep(Step):
    def __init__(self, horse_times: List[int]) -> None:
        self.parent = None
        if len(horse_times) <= 26:
            self.horses = {chr(65 + i): Horse(chr(65 + i), time)
                           for i, time in enumerate(horse_times)}
        else:
            self.horses = {str(i + 1): Horse(str(i + 1), time)
                           for i, time in enumerate(horse_times)}
        self.choice = tuple()
        self.passed = False
        self.time = 0

    @property
    def tot_time(self) -> int:
        return 0

    @property
    def path(self) -> List[Tuple[str, ...]]:
        return []

    def execute(self) -> List[Tuple[int, Tuple[int, ...], List[Tuple[str, ...]]]]:
        avail_horses = tuple(self.avail_horses)
        step_pool = (c for r in range(2, HORSE_LIMIT + 1)
                     for c in combinations(avail_horses, r))
        pot_children = (Step(self, self.horses, choice, not self.passed)
                        for choice in step_pool)
        # Check each potential children
        paths: List[Tuple[int, Tuple[int, ...], List[Tuple[str, ...]]]] = []
        for s in pot_children:
            # Has to not exceed time limit
            if not s.is_viable:
                continue
            # Kinda recursion
            children_paths = s.execute()
            if len(children_paths) > 0:
                paths += children_paths
        return paths


def main(horse_times: List[int]) -> None:
    root_step = RootStep(horse_times)
    paths = root_step.execute()
    solution = {
        "num_of_solutions": len(paths),
        "solutions": [{
            "total_time": time,
            "horses_time_spent": list(horses),
            "path": [list(step) for step in path]
        } for time, horses, path in sorted(paths)]
    }
    with open(SOLUTION_PATH, "w") as f:
        json.dump(solution, f)


if __name__ == "__main__":
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    TIME_MAX = config["horse_time_limit"]
    if TIME_MAX <= 0:
        TIME_MAX = math.inf
    HORSE_LIMIT = config["horse_num_limit"]
    if HORSE_LIMIT < 2:
        raise ValueError(
            f"At least 2 horses have to be able to go at the same time. Current limit {HORSE_LIMIT}")
    main(config["horse_times"])
