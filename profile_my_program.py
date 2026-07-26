#!/usr/bin/env python3
"""
profile_my_program.py
=====================
A simple tool to measure the performance and resource usage of YOUR Python program.

It reports:
  - Wall-clock time  (real time you actually waited)
  - CPU time         (time the processor spent working)
  - Peak memory use  (the most RAM your program held at once)
  - Slowest functions (a ranked breakdown of where time went)

It uses only Python's standard library, so there is nothing to install.
(If the 'psutil' package happens to be installed, memory numbers get a bit
more accurate, but it is completely optional.)

--------------------------------------------------------------------
HOW TO USE IT (in the VS Code terminal, or any terminal)
--------------------------------------------------------------------
1. Put this file in the same folder as the program you want to test.
2. Open a terminal (in VS Code: Terminal -> New Terminal).
3. Run:

       python profile_my_program.py your_program.py

   Replace "your_program.py" with the name of your own script.

   If your program needs command-line arguments, just add them after:

       python profile_my_program.py your_program.py arg1 arg2

--------------------------------------------------------------------
"""

import sys
import os
import time
import cProfile
import pstats
import tracemalloc
import runpy
import io


def human_bytes(n):
    """Turn a number of bytes into something readable, e.g. 12.4 MB."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024.0:
            return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} PB"


def try_get_psutil_memory():
    """Return current process RSS memory via psutil, or None if unavailable."""
    try:
        import psutil
        return psutil.Process(os.getpid()).memory_info().rss
    except Exception:
        return None


def main():
    # ---- Check the user gave us a script to run ---------------------------
    if len(sys.argv) < 2:
        print(__doc__)
        print("ERROR: You didn't tell me which program to test.\n")
        print("Example:  python profile_my_program.py your_program.py")
        sys.exit(1)

    target = sys.argv[1]

    if not os.path.isfile(target):
        print(f"ERROR: I can't find a file named '{target}'.")
        print("Make sure the name is spelled correctly and it's in this folder.")
        sys.exit(1)

    # Hand any extra arguments to the target program, as if it were run directly.
    # sys.argv[0] should be the target's name so the program sees itself normally.
    forwarded_args = sys.argv[2:]
    sys.argv = [target] + forwarded_args

    print("=" * 60)
    print(f"  Profiling: {target}")
    if forwarded_args:
        print(f"  Arguments: {' '.join(forwarded_args)}")
    print("=" * 60)
    print("  ...running your program now...\n")

    # ---- Start the measuring instruments ----------------------------------
    tracemalloc.start()          # tracks Python memory allocations
    profiler = cProfile.Profile()  # records per-function timing

    wall_start = time.perf_counter()  # real elapsed time
    cpu_start = time.process_time()   # processor time used

    error = None
    try:
        # Run the user's script in a clean namespace, as if it were "__main__".
        profiler.enable()
        runpy.run_path(target, run_name="__main__")
        profiler.disable()
    except SystemExit:
        # A normal sys.exit() inside their program is fine; don't treat as error.
        profiler.disable()
    except Exception as e:
        profiler.disable()
        error = e

    wall_end = time.perf_counter()
    cpu_end = time.process_time()

    # Grab memory stats before stopping the tracer.
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    psutil_mem = try_get_psutil_memory()

    # ---- Report the results -----------------------------------------------
    print("\n" + "=" * 60)
    print("  RESULTS")
    print("=" * 60)

    if error is not None:
        print("  Your program stopped with an error:")
        print(f"    {type(error).__name__}: {error}")
        print("  (The measurements below cover the part that ran.)\n")

    print(f"  Wall-clock time : {wall_end - wall_start:.4f} seconds  (real time)")
    print(f"  CPU time        : {cpu_end - cpu_start:.4f} seconds  (processor time)")
    print(f"  Peak memory     : {human_bytes(peak_mem)}  (max Python allocated)")
    if psutil_mem is not None:
        print(f"  Process memory  : {human_bytes(psutil_mem)}  (total, via psutil)")
    print()

    # ---- Slowest functions -------------------------------------------------
    print("-" * 60)
    print("  TOP 12 SLOWEST FUNCTIONS (by total time spent inside them)")
    print("-" * 60)
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumulative")  # rank by cumulative time
    stats.print_stats(12)
    print(stream.getvalue())

    print("=" * 60)
    print("  Reading the table:")
    print("   - ncalls  = how many times the function was called")
    print("   - tottime = time spent in the function itself only")
    print("   - cumtime = time in the function AND everything it called")
    print("  Look at the largest cumtime rows to find your bottlenecks.")
    print("=" * 60)


if __name__ == "__main__":
    main()
