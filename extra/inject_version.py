import os
import re
import subprocess
from typing import Tuple


def get_version():
    cp = subprocess.run(["git", "describe", "--tags", "--dirty", "--match=v*"], stdout=subprocess.PIPE, check=True,)
    version = str(cp.stdout, encoding="utf8").strip()
    return version


def parse(version) -> Tuple[Tuple[int], str]:
    """Parse version string like "v1.0.4-14-g241472-dirty" into ((0,14,0), "-g241472-dirty")
    """
    # similar regexp in gitlab .yml files
    # tested with https://regoio.herokuapp.com/

    # vMAJOR.MINOR.PATCH-PRERELEASE+BUILD as in https://semver.org/
    re_string = r"^v([0-9]+)\.([0-9]+)\.([0-9]+)(\-[0-9A-Za-z-]+)?(\+[0-9A-Za-z-]+)?$"
    match = re.match(re_string, version)
    groups = match.groups()
    version = tuple((int(s) for s in groups[0:3]))
    suffix = "" if len(groups) < 4 else groups[3]
    return version, suffix


def test():
    v = get_version()
    return parse(v)


def main():
    version = get_version()
    version_numbers, suffix = parse(version)
    version_strings = [str(i) for i in version_numbers]
    version_string = ".".join(version_strings)

    init_file = os.path.join("mixer", "__init__.py")
    new_init_file_str = ""
    done = False
    comment = " # Generated by inject_version.py"
    with open(init_file, "r") as fp:
        for line in fp.readlines():
            if not done:
                if line.startswith("__version__ = "):
                    new_init_file_str += f'__version__ = "v{version_string}"{comment}\n'
                elif line.startswith("display_version = "):
                    new_init_file_str += f'display_version = "v{version_string}{suffix}"{comment}\n'
                elif line.startswith('    "version": ('):
                    new_init_file_str += f'    "version": {str(tuple(version_numbers))},{comment}\n'
                    done = True
                else:
                    new_init_file_str += f"{line}"
            else:
                new_init_file_str += f"{line}"
    with open(init_file, "w") as fp:
        fp.write(new_init_file_str)


if __name__ == "__main__":
    main()
