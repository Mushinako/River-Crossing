# River Crossing

Solution to the puzzle where you have to get different horses to cross the river

## Usage

Put parameters in `config.json` and run `river_crossing.py`. The output will be in `solution.json`

### `config.json`

| Parameter          | Explanation                                                        | Acceptable values                |
| :----------------: | :----------------------------------------------------------------: | :------------------------------: |
| `horse_time_limit` | The limit on amount of time each horse can go                      | An integer. Use `0` for no limit |
| `horse_num_limit`  | The number of horses that can go at once, including the one riding | An integer that's at least 2     |
| `horse_times"`     | Amount of time it takes for each horse to cross the river          | An array of integers             |

### `solution.json`

```json
{
    "num_of_solutions": [int] "Total number of solutions found",
    "solutions": [{
        "total_time": [int] "Total amount of time taken for this solution",
        "horses_time_spent": [List[int]] "List of time each horse spent crossing the river",
        "path": [List[List[str]]] "List of steps, showing the horses moved each step"
    }, ...]
}
```

## Notes

This solver tries to avoid inefficient solutions, including:

* Bringing only the horse you're riding to the other side
* Bring back multiple horses when coming back
