import os
import sys
import importlib
import pandas as pd
import builtins


SCRIPT_DIRS = [
    "/Users/chenyong/python_project/ta-learn/script",
]


def load_scripts(dirs=[]):
    does_not_exist = [directory for directory in dirs if not os.path.exists(directory)]
    if len(does_not_exist) > 0:
        print("The following script directories do not exist:")
        print(*does_not_exist, sep="\n")
        return

    results = []
    for dir in dirs:
        sys.path.append(dir)
        for file in os.listdir(dir):
            if not file.endswith(".py"):
                continue
            module_name = file[:-3:]
            # print(f"loading module: {dir} {module_name}")
            module = importlib.import_module(module_name)
            description = module.description if hasattr(module, "description") else ""
            results.append(
                {
                    "name": module_name,
                    "module": module,
                    "description": description
                }
            )
    return results


def print_scripts(scripts):
    df = pd.DataFrame(scripts)
    print(df.to_string())


def config():
    print("config")
    return {}


def main():
    scripts = load_scripts(SCRIPT_DIRS)
    args = sys.argv
    print(args)
    if len(args) == 1:
        print_scripts(scripts)
    else:
        script_target = args[1]
        scripts_filtered = list(filter(lambda x: script_target in x['name'], scripts))
        if len(scripts_filtered) == 0:
            print(f'>>>> can not find any script named: {script_target}!!!')
        elif len(scripts_filtered) == 1:
            globals()['xxxx'] = config
            print(dir(globals()))
            getattr(scripts_filtered[0]['module'], "run", scripts_filtered[0]['module'].main)()
        else:
            print_scripts(scripts_filtered)
        pass


if __name__ == '__main__':
    main()
