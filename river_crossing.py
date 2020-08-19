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
    """Data of each horse at each instant

    Properties:
        id_    (str) : ID of horse
        speed  (int) : Amount of time the horse takes to cross the river
        spent  (int) : Amount of time the horse has accured crossing the river
        passed (bool): Whether the horse is on the other side of the river
    """
    id_: str
    speed: int
    spent: int = 0
    passed: bool = False


@dataclass
class Solution:
    """Data of each solution

    Properties:
        total_time  (int)            : Total time for this solution
        horses_time (tuple[int, ...]): Total time each horse accured
        path  (list[tuple[str, ...]]): Steps for this solution
    """
    total_time: int
    horses_time: Tuple[int, ...]
    path: List[Tuple[str, ...]]


class Step:
    """Tree node for each step

    Arguments:
        parent (Step)             : Parent node
        horses (dict[str, Horse]) : Conditions of each horse at the moment
        choice (tuple[Horse, ...]): The ids of the horses chosen to move in this step
        passed_after (bool)       : Whether the human is on the other side of the water after this step

    Properties:
        parent (Step)             : Same as args.parent
        horses (dict[str, Horse]) : Same as args.horses; copied
        choice (tuple[Horse, ...]): Horses corresponding to args.choice
        passed (bool)             : Same as args.passed_after
        time   (int)              : Amount of time for this step
        is_viable.getter    (bool)          : Whether this step is legal
        avail_horses.getter (Generator[str]): Generator of available horses to be used for next step
        all_passed.getter   (bool)          : Whether all horses are on the other side (end of solution)
        tot_time.getter     (int)           : Total time spent on the steps up to (incl.) this one
        horse_time.getter  (tuple[int, ...]): Amount of time each horse accured up to (incl.) this step
        path.getter  (List[Tuple[str, ...]]): Path taken so far
    """

    def __init__(self, parent, horses: Dict[str, Horse], choice: Tuple[str, ...], passed_after: bool) -> None:
        self.parent = parent
        self.horses = {h.id_: Horse(
            h.id_, h.speed, h.spent, h.passed) for h in horses.values()}
        self.choice: Tuple[Horse, ...] = tuple(
            (self.horses[hn] for hn in choice))
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

    def execute(self) -> List[Solution]:
        """Generate child nodes and run testing on each path

        Returns:
            (list[Solution]): List of solutions that pass through this node
        """
        # print(f"Current: {self.path}")
        for h in self.choice:
            h.passed ^= True
            h.spent += self.time
        if self.all_passed:
            paths = [Solution(self.tot_time, self.horse_time, self.path)]
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
        paths: List[Solution] = []
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
    """Topmost tree node

    Arguments:
        horse_times (list[int]): List of times each horse takes to cross the river

    Properties:
        parent (None)            : No parent
        horses (dict[str, Horse]): All horses present
        choice (tuple)           : None
        passed (bool)            : No crossing water yet
        time   (int)             : Placeholder step. No time taken
        is_viable.getter    (bool)          : Inherited. No use
        avail_horses.getter (Generator[str]): Inherited. No use. Available horses are all horses
        all_passed.getter   (bool)          : Inherited. No use. No horse on the other side
        tot_time.getter     (int)           : Inherited. No time spent yet
        horse_time.getter  (tuple[int, ...]): Inherited. No use. No actions yet
        path.getter  (List[Tuple[str, ...]]): Inherited. No path taken yet
    """

    def __init__(self, horse_times: List[int]) -> None:
        self.parent = None
        # Use letters to represent the IDs if there're at most 26 horses;
        #   otherwise, use numbers
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

    def execute(self) -> List[Solution]:
        """Generate child nodes and run testing on each path

        Returns:
            (list[Solution]): List of all solutions
        """
        avail_horses = tuple(self.avail_horses)
        step_pool = (c for r in range(2, HORSE_LIMIT + 1)
                     for c in combinations(avail_horses, r))
        pot_children = (Step(self, self.horses, choice, not self.passed)
                        for choice in step_pool)
        # Check each potential children
        paths: List[Solution] = []
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
            "total_time": sol.total_time,
            "horses_time": list(sol.horses_time),
            "path": [list(step) for step in sol.path]
        } for sol in sorted(paths, key=lambda s: s.total_time)]
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
