import sys 

def __getattr__(name):
    raise ImportError(f"cannot import name '{name}' from '{__name__}' please use `import {__name__}.{name}`")

def __dir__():
    return []

if __name__ == '__main__':
    sys.exit()
