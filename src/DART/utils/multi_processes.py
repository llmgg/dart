from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import Callable, List


def multi_process_run(
        func: Callable,
        args_list: List,
        num_workers: int = 16,
        keep_order: bool = True,
        pool_type='thread',
):
    if not callable(func):
        raise ValueError(f'func must be a callable object, but got {type(func)}')

    num_workers = min(num_workers, len(args_list))

    # execute in process pool
    if pool_type.lower() == 'thread':
        executor_used = ThreadPoolExecutor
    elif pool_type.lower() == 'process':
        executor_used = ProcessPoolExecutor
    else:
        raise ValueError(f'the input pool_type is not supported: {pool_type}')

    with executor_used(max_workers=num_workers) as executor:
        futures = [executor.submit(func, args) for args in args_list]
        if keep_order:
            for future in futures:
                try:
                    yield future.result()
                except Exception as e:
                    yield 'Executor Run Error: ' + str(e)
        else:
            for future in as_completed(futures):
                try:
                    yield future.result()
                except Exception as e:
                    yield 'Executor Run Error: ' + str(e)
