# Build Automation Tool

Usage:
```
python3 main.py <build_rule>
Optional Arguments:
--root-dir <path>:    Directory to be considered as root
--max-threads <int>:  Maximum build rules/dependencies to process in parallel
--watch:              If specified, poll for file referenced by build_rule and execute the rule on any change
```
Sample build.json:
```
[
  {
    "name": "clean",
    "deps": ["algorithms/clean"],
    "files": ["test.cpp"],
    "command": "rm -f test.o && rm -f test.out"
  },
  {
    "name": "test",
    "files": ["test.cpp"],
    "command": "g++ -std=c++11 -c test.cpp"
  },
  {
    "name": "run",
    "deps": ["test", "algorithms/sort_bubble", "algorithms/sort_merge", "algorithms/sort_quick"],
    "command": "g++ algorithms/sort_bubble.o algorithms/sort_merge.o"
  }
]
```
Dependencies located in root-dir/<some_path> can also be referenced as //<some_path>
