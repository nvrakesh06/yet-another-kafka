import os
import pathlib

here = pathlib.Path(__file__).parent.resolve()


def topic_exists(topic: str) -> bool:

    if os.path.isdir(f"{here}\\topics\\{topic}"):  # dir_path+topic
        return True
    return False


def update_metadata(port: int) -> None:
    with open(f"{here}/metadata.txt", "w+") as f:
        f.write(str(port) + "\n")


def read_metadata() -> int:
    with open(f"{here}/metadata.txt", "r") as f:
        leader_port = f.readline().strip()

    return leader_port


#  https://gist.github.com/nkilm/596f21416b8ce914eee4b0551adcba06


class tcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    ENDC = "\033[0m"
    BPurple = "\033[1;35m"
    BIPurple = "\033[1;95m"  # Bold High Intensity

    # To highlight important information
    # usage:
    #    print(bcolor.highlight("My important message"))
    @staticmethod
    def highlight(message):
        message = str(message)
        return tcolors.BOLD + str(message) + tcolors.BOLD

    # Method that returns a message with the desired color
    # usage:
    #    print(bcolor.colored("My colored message", bcolor.OKBLUE))
    @staticmethod
    def colored(message, color):
        return color + str(message) + tcolors.ENDC

    # Method that returns a yellow warning
    # usage:
    #   print(tcolors.warning("What you are about to do is potentially dangerous. Continue?"))
    @staticmethod
    def warning(message):
        return tcolors.WARNING + str(message) + tcolors.ENDC

    # Method that returns a red fail
    # usage:
    #   print(tcolors.fail("What you did just failed massively. Bummer"))
    #   or:
    #   sys.exit(tcolors.fail("Not a valid date"))
    @staticmethod
    def fail(message):
        return tcolors.FAIL + str(message) + tcolors.ENDC

    # Method that returns a green ok
    # usage:
    #   print(tcolors.ok("What you did just ok-ed massively. Yay!"))
    @staticmethod
    def ok(message):
        return tcolors.OKGREEN + str(message) + tcolors.ENDC

    # Method that returns a blue ok
    # usage:
    #   print(tcolors.okblue("What you did just ok-ed into the blue. Wow!"))
    @staticmethod
    def okblue(message):
        return tcolors.OKBLUE + str(message) + tcolors.ENDC

    # Method that returns a header in some purple-ish color
    # usage:
    #   print(tcolors.header("This is great"))
    @staticmethod
    def header(message):
        return tcolors.HEADER + str(message) + tcolors.ENDC
