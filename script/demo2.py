

description = "demo2 description"

def main():
    print(dir(globals()))
    print(globals()['xxxx']())
    print("config", globals().get('xxxx'))
