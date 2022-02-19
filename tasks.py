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


@invoke.task(help={'test': '<testdir>.<testname> (e.g. mymodule.mytest to run tests/modules/mymodule/mytest.py,\n'\
                           'use mymodule to run all tests in tests/modules/mymodule)'})
def run_tests(context, test=None):
    if test == None:
        for directory in glob.glob(f'{MODULE_TESTS_PATH}/*/'):
            directory = directory.replace('\\', '/')
            user_message = f'RUNNING TESTS IN: {directory}'
            message_width =  len(user_message)
            user_message = f'\n{"*"*message_width}\n{user_message}\n{"*"*message_width}'
            print(user_message)
            for test_file in glob.glob(f'{directory}*.py'):
                test_file = test_file.replace('\\', '/')
                run_message = f'\n\nRUNNING: {test_file}'
                run_message += '\n' + '-'*len(run_message)
                print(run_message)
                test_module = relpath_to_module(test_file)
                context.run(f'python -m {test_module}')
    else:
        test = test.replace('.', '/')
        test_path = f'{MODULE_TESTS_PATH}/{test}'
        if not(os.path.exists(test_path) or os.path.exists(f'{test_path}.py')):
            print(f'No directory or file named {test_path}')
            return
        if os.path.isdir(test_path):
            test_path = f'{test_path}/'
            user_message = f'RUNNING TESTS IN: {test_path}'
            message_width =  len(user_message)
            user_message = f'\n{"*"*message_width}\n{user_message}\n{"*"*message_width}'
            print(user_message)
            for test_file in glob.glob(f'{test_path}*.py'):
                test_file = test_file.replace('\\', '/')
                run_message = f'\n\nRUNNING: {test_file}'
                run_message += '\n' + '-'*len(run_message)
                print(run_message)
                test_module = relpath_to_module(test_file)
                context.run(f'python -m {test_module}')
        elif os.path.isfile(f'{test_path}.py'):
            test_module = test_path.replace('./', '').replace('/', '.')
            run_message = f'\n\nRUNNING: {test_module}'
            run_message += '\n' + '-'*len(run_message)
            print(run_message)
            context.run(f'python -m {test_module}')
