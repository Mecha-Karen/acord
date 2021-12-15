# Basic CLI for acord
import argparse
import acord

parser = argparse.ArgumentParser()

parser.add_argument("--v", "-version", 
                    help="Display short version info", 
                    action='store_true', default=None)

default_usage = parser.format_usage()[7:]
parser.usage = default_usage.replace('__main__.py', 'python -m acord')

def about() -> str:
    return f"""\
Acord is an API wrapper for discord, \
built using aiohttp and pydantic.
Acord provides a simple interface between code and API, \
whilst still allowing you to write fast and scalable bots!

Acord was started by the Mecha Karen org and is licensed under the GPL-3.0 License.
Documentation: https://acord.rtfd.io
Github Repository: https://github.com/Mecha-Karen/ACord
File Location: {acord.__file__}
        
For any queries or questions don't hesitate to send us an email at \
admin@mechakaren.xyz."""

if __name__ == '__main__':
    args = vars(parser.parse_args())

    args = {k: v for k, v in args.items() if v is not None}

    if not args:
        print(about())
        exit()

    if args.get('v') or args.get('version'):
        print(acord.__version__)

    exit()
