from makepanda_vars import *
import makepanda_default as mp

import threading
import enum
import queue
import time

# Filesystem necessary locks
FsLock = threading.Lock()

_MakeDirs = mp.MakeDirs
def MakeDirs(path):
    with FsLock:
        _MakeDirs(path)

mp.MakeDirs = MakeDirs


class TaskType(enum.IntEnum):
    Compile = 1
    Library = 2
    Interrogate = 3
    Module = 4
    
    
class TaskStatus(enum.IntEnum):
    Awaiting = 1
    Completed = 2
    Failed = 3
    
    
class Task:
    def __init__(self, type, args=None, kwargs=None):
        self.type = type
        self.args = args 
        self.kwargs = kwargs
        
        self.status = TaskStatus.Awaiting
        self.value = None
        
        
InterrogateTasks = {}
TaskQueue = queue.Queue()
TaskCount = 0


def Compile(path, *args, **kwargs):
    tsk = Task(TaskType.Compile, (path, *args), kwargs)
    TaskQueue.put(tsk)
    return tsk
    

def Library(name, files):
    tsk = Task(TaskType.Library, (name, files), {})
    TaskQueue.put(tsk)
    return tsk
    

def Interrogate(name, *args, **kwargs):
    tsk = Task(TaskType.Interrogate, (name, *args), kwargs)
    TaskQueue.put(tsk)
    InterrogateTasks[name] = tsk
    return tsk
    
    
def Module(name, module, library, files, opts=None):
    tsk = Task(TaskType.Module, (name, module, library, files, opts), {})
    TaskQueue.put(tsk)
    return tsk
    
    
def HandleQueue():
    print("Started thread")
    while True:
        try:
            task = TaskQueue.get(False)
        except queue.Empty:
            break
        
        if task.type == TaskType.Compile:
            try:
                task.value = mp.Compile(*task.args, **task.kwargs)
            except Exception as e:
                print(e)
                task.status = TaskStatus.Failed
            else:
                task.status = TaskStatus.Completed
                ShowProgress()
            
            
        elif task.type == TaskType.Library:
            name, files = task.args
            for file in files:
                if file.status == TaskStatus.Failed:
                    print("Ignoring library task as a child task failed")
                    break
                    
            else:
                for file in files:
                    if file.status == TaskStatus.Awaiting:
                        TaskQueue.put(task)
                        time.sleep(0.2)
                        break
                        
                else:
                    # every task is available
                    files = [file.value for file in files]
                    try:
                        task.value = mp.Library(name, files)
                    except Exception as e:
                        print(e)
                        task.status = TaskStatus.Failed
                    else:
                        task.status = TaskStatus.Completed
                        ShowProgress()
                
        
        elif task.type == TaskType.Interrogate:
            try:
                task.value = mp.Interrogate(*task.args, **task.kwargs)
            except Exception as e:
                print(e)
                task.status = TaskStatus.Failed
            else:
                task.status = TaskStatus.Completed
                ShowProgress()
            
        
        elif task.type == TaskType.Module:
            files = task.args[3]
            for file in files:
                itask = InterrogateTasks[file]
                if itask.status == TaskStatus.Failed:
                    print("Ignoring module task as a child task failed")
                    break
                    
            else:
                for file in files:
                    itask = InterrogateTasks[file]
                    if itask.status == TaskStatus.Awaiting:
                        TaskQueue.put(task)
                        time.sleep(0.2)
                        break
                        
                else:
                    # every task is available
                    try:
                        task.value = mp.Module(*task.args, **task.kwargs)
                    except Exception as e:
                        print(e)
                        task.status = TaskStatus.Failed
                    else:
                        task.status = TaskStatus.Completed
                        ShowProgress()
            
        
        
def ShowProgress():
    remaining = TaskCount - TaskQueue.qsize()
    progress = round((remaining / TaskCount) * 20)
    
    with FsLock:
        print()
        print("Progress: [" + ("=" * progress) + (" " * (20 - progress)) + "]")
        print("  " + str(remaining) + "/" + str(TaskCount))
        print()
    
    
def StartThreads():
    global TaskCount
    TaskCount = TaskQueue.qsize()
    
    print("Starting threads!")
    for n in range(12):
        th = threading.Thread(target=HandleQueue)
        th.start()
        