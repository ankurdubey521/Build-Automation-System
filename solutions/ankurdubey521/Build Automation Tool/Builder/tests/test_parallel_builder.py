import unittest
from Builder.lib.parallel_builder import ParallelBuilder
import subprocess
from multiprocessing import Process
from time import sleep
import pprint
import os

MAX_THREAD_COUNT = 12


class TestParallelBuilder(unittest.TestCase):
    # The tests should work for any path inside the project
    def setUp(self):
        while os.path.basename(os.getcwd()) != 'Build Automation Tool':
            os.chdir('..')
        os.chdir('Builder/tests')

    def test_basic_shell_command(self):
        command = "echo 'Hello World!'"
        exit_code = ParallelBuilder._run_shell(command, cwd='/').wait()
        self.assertEqual(0, exit_code)

    def test_nonzero_exit_code_for_shell_command(self):
        command = "exit 1"
        exit_code = ParallelBuilder._run_shell(command, cwd='/').wait()
        self.assertEqual(1, exit_code)

    def test_dependency_graph_creation(self):
        path = os.getcwd() + '/test_builder_files/test_dependency_graph_creation'
        parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
        parallel_builder._explore_and_build_dependency_graph('Z', path)
        dependency_graph = {}
        for node_tuple in parallel_builder._dependency_graph:
            dependency_graph[node_tuple[0]] = []
            for item in parallel_builder._dependency_graph[node_tuple]:
                dependency_graph[node_tuple[0]].append(item[0])
        pprint.pprint(dependency_graph, indent=4)
        correct_dependency_graph = {'X': ['Z'], 'XX': ['X'], 'XY': ['X'], 'Y': ['Z'], 'YX': ['Y'], 'YY': ['Y']}
        self.assertEqual(correct_dependency_graph, dependency_graph)

    def test_topological_sort_creation(self):
        path = os.getcwd() + '/test_builder_files/test_dependency_graph_creation'
        parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
        parallel_builder.execute_build_rule_and_dependencies('Z', path)
        toposort = [item[0] for item in parallel_builder._dependency_topological_sort]
        print(toposort)
        self.assertEqual(['XX', 'XY', 'YX', 'YY', 'X', 'Y', 'Z'], toposort)

    def test_basic_circular_dependency_throws_exception(self):
        path = os.getcwd() + '/test_builder_files/test_basic_circular_dependency_throws_exception'
        parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
        self.assertRaises(
            parallel_builder.CircularDependencyException, parallel_builder.execute_build_rule_and_dependencies, 'A',
            path)

    def test_basic_circular_dependency2_throws_exception(self):
        path = os.getcwd() + '/test_builder_files/test_basic_circular_dependency2_throws_exception'
        parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
        self.assertRaises(
            parallel_builder.CircularDependencyException, parallel_builder.execute_build_rule_and_dependencies, 'A',
            path)

    def test_compilation_basic(self):
        path = os.getcwd() + '/test_builder_files/test_compilation_basic'
        # RUN
        parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
        parallel_builder.execute_build_rule_and_dependencies('run', path)
        exec_path = '"' + path + '/test.out' + '"'
        result = subprocess.run(exec_path, shell=True, capture_output=True, text=True)
        self.assertEqual('1 2 3 4 5 \n1 2 3 4 5 \n1 2 3 4 5 \n', result.stdout)
        # CLEANUP
        parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
        parallel_builder.execute_build_rule_and_dependencies('clean', path)
        self.assertFalse(os.path.isfile(path + "/test.out"))

    def test_commands_referenced_from_root(self):
        path = os.getcwd() + '/test_builder_files/test_commands_referenced_from_root'
        # RUN
        parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
        parallel_builder.execute_build_rule_and_dependencies('run', path)
        output_file_path = path + '/output'
        result = ''
        with open(output_file_path) as file_handle:
            result = file_handle.readable()
        self.assertEqual(True, result)
        # CLEANUP
        parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
        parallel_builder.execute_build_rule_and_dependencies('clean', path)
        self.assertFalse(os.path.isfile(path + "/output"))

    def test_parallel_sleep_commands(self):
        path = os.getcwd() + '/test_builder_files/test_parallel_sleep_commands'
        parallel_builder = ParallelBuilder(path, MAX_THREAD_COUNT)
        process = Process(target=parallel_builder.execute_build_rule_and_dependencies,
                          args=('Z', path))
        sleep(16)
        self.assertEqual(False, process.is_alive())


if __name__ == '__main__':
    unittest.main()
