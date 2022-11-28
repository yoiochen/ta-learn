import os


def write(dir_name, filename, title_cols, rows):
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

    filename = filename[:-4:] if filename.endswith('.csv') else filename

    with open(os.path.join(dir_name, f"{filename}.csv"), "w") as f:
        f.write(",".join(title_cols))
        f.write("\n")
        for row in rows:
            f.write(",".join(list(map(lambda x: str(x) ,row))))
            f.write("\n")
    print(f">>>> save {dir_name} {filename} success")

# print("nihao.csv"[:-4:])