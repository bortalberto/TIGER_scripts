from multiprocessing import Pool
import numpy as np

def f(x):
    a={}
    a={"pippo":x}
    return a
pool = Pool(processes=4)

# print "[0, 1, 4,..., 81]"
print(pool.map(f, range(10)))

# print same numbers in arbitrary order
for i in pool.imap_unordered(f, range(10)):
    print(i)
#
# # evaluate "f(20)" asynchronously
# res = pool.apply_async(f, (20,))  # runs in *only* one process
# print(res.get(timeout=1))  # prints "400"
#
# # evaluate "os.getpid()" asynchronously
# res = pool.apply_async(os.getpid, ())  # runs in *only* one process
# print(res.get(timeout=1))  # prints the PID of that process
#
# # launching multiple evaluations asynchronously *may* use more processes
# multiple_results = [pool.apply_async(os.getpid, ()) for i in range(4)]
# print([res.get(timeout=1) for res in multiple_results])
#
# # make a single worker sleep for 10 secs
# res = pool.apply_async(time.sleep, (10,))
# try:
# except TimeoutError:
#     print("We lacked patience and got a multiprocessing.TimeoutError")
#
# print("For the moment, the pool remains available for more work")

# exiting the 'with'-block has stopped the pool
print("Now the pool is closed and no longer available")

