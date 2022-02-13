from posixpath import relpath
import invoke
import os
import glob


TESTS_PATH = './tests'
MODULE_TESTS_PATH = f'{TESTS_PATH}/modules'


def relpath_to_module(relpath):
    return relpath.replace('./', '').replace('.py', '').replace('/', '.')


@invoke.task
def test(context):
    print(context)

@invoke.task
def run_tests(context, test=None):
    if test == None:
        # print(glob.glob(f'{MODULE_TESTS_PATH}/*/'))
        for directory in glob.glob(f'{MODULE_TESTS_PATH}/*/'):
            directory = directory.replace('\\', '/')
            print(f'***********************************\nRUNNING TESTS IN: {directory}\n')
            for test_file in glob.glob(f'{directory}*.py'):
                test_file = test_file.replace('\\', '/')
                print(f'RUNNING: {test_file}')
                test_module = relpath_to_module(test_file)
                context.run(f'python -m {test_module}')
    else:
        test = test.replace('.', '/')
        test_path = f'{MODULE_TESTS_PATH}/{test}'
        # print(test_path)
        if not(os.path.exists(test_path) or os.path.exists(f'{test_path}.py')):
            print(f'No directory or file named {test_path}')
            return
        if os.path.isdir(test_path):
            test_path = f'{test_path}/'
            print(f'***********************************\nRUNNING TESTS IN: {test_path}\n')
            for test_file in glob.glob(f'{test_path}*.py'):
                test_file = test_file.replace('\\', '/')
                print(f'RUNNING: {test_file}')
                test_module = relpath_to_module(test_file)
                context.run(f'python -m {test_module}')
        elif os.path.isfile(f'{test_path}.py'):
            test_module = test_path.replace('./', '').replace('/', '.')
            print(f'RUNNING: {test_path}.py')
            context.run(f'python -m {test_module}')
