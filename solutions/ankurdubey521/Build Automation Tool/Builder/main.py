from Builder.lib.buildconfig import BuildConfig
from Builder.lib.file_watcher import FileWatcher
from Builder.lib.parallel_builder import ParallelBuilder
import argparse
import sys
import os


if __name__ == '__main__':
    # Parse Args
    parser = argparse.ArgumentParser()
    parser.add_argument('build_rule', type=str)
    parser.add_argument('--watch', action="store_true")
    parser.add_argument('--root-dir', type=str)
    parser.add_argument('--max-threads', type=int)
    args = parser.parse_args(sys.argv[1:])

    # Parse Command
    command = args.build_rule
    root_dir = ""
    if args.root_dir is not None:
        root_dir = args.root_dir
    else:
        root_dir = os.getcwd()

    builder = ParallelBuilder(root_dir, args.max_threads)
    relative_path = ''
    if '/' in command:
        # Handle relative paths
        relative_path, command = command.rsplit('/', 1)
    path = root_dir + "/" + relative_path

    try:
        if not args.watch:
            builder.execute_build_rule_and_dependencies(command, path)
        else:
            # Watch files and run build rule on changes
            file_list = BuildConfig(path).get_command(command).get_files()
            # Convert file paths to absolute
            file_list = [(path + file) for file in file_list]
            FileWatcher.watch_and_execute(file_list, builder.execute_build_rule_and_dependencies, command, path)

    except Exception as e:
        print(e)

