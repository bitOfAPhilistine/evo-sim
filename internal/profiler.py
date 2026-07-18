import internal.globals as globals

import time

def profiler(func):
    def inner(*args, **kwargs):
        if globals.profiling and (len(globals.profilerFuncStack) == 0 or globals.profilerFuncStack[-1] != func):
            mainTimes: dict[function, ProfilerStats] = globals.profilerTimes
            frameTimes: dict[function, ProfilerStats] = globals.profiledFrameTimes

            try:
                for parent in globals.profilerFuncStack:
                    mainTimes = mainTimes[parent].children
            except Exception as e:
                print(globals.profilerFuncStack)
                print(globals.profilerTimes)
                print(globals.profiledFrameTimes)
                raise e

            if func not in mainTimes:
                mainTimes[func] = ProfilerStats()
            
            if func not in frameTimes:
                frameTimes[func] = ProfilerStats()
            
            globals.profilerFuncStack.append(func)

            startTime = time.time()
            result = func(*args, **kwargs)
            timeTaken = time.time() - startTime
            
            mainTimes[func].callCount += 1
            mainTimes[func].totalTime += timeTaken
            mainTimes[func].avgTime = mainTimes[func].totalTime / mainTimes[func].callCount
            if timeTaken > mainTimes[func].maxTime:
                mainTimes[func].maxTime = timeTaken
            
            frameTimes[func].callCount += 1
            frameTimes[func].totalTime += timeTaken

            globals.profilerFuncStack.pop()

            return result
        
        return func(*args, **kwargs)

    return inner

class ProfilerStats:
    def __init__(self):
        self.callCount: int = 0
        self.totalTime: float = 0.0
        self.avgTime: float = 0.0
        self.maxTime: float = 0.0
        self.children: dict[function] = {}