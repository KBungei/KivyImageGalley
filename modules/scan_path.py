import os
from PIL import Image


def check_path_is_image(path):
    try:
        with Image.open(path) as _:
            pass
        return True

    except Exception:
        return False


def is_ignore(name):
    ignore_list = [
        'main.py',
    ]

    if name in ignore_list:
        return True

    return False


def scan_path_for_files(path: str, results: list = []) -> list | None:

    if os.path.isdir(path):

        for entry in os.scandir(path):
            if is_ignore(entry.name):
                continue

            if entry.is_dir():
                print(f"Scanning {entry.name} ...")
                scan_path_for_files(entry.path, results)

            elif entry.is_file():
                results.append(entry.path)

        return results

    elif os.path.isfile(path):
        results.append(path)
        return results

    else:
        return []


def scan_path_for_images(path: str, results: list = []) -> list:

    if os.path.isdir(path):

        for entry in os.scandir(path):
            if is_ignore(entry.name):
                continue

            if entry.is_dir():
                print(f"Scanning {entry.name} ...")
                scan_path_for_files(entry.path, results)

            elif entry.is_file():
                if check_path_is_image(entry.path):
                    results.append(entry.path)

                else:
                    continue

        return results

    elif os.path.isfile(path):
        results.append(path)
        return results

    else:
        return []
