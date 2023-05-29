import logging
import argparse
from App import App

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                        prog='EasyMCP2221-GUI',
                        description='A graphical user interface for MCP2221 and MCP2221A devices based on EasyMCP2221 library.')

    parser.add_argument('--debug', dest='debug', action='store_const',
                        const=True, default=False,
                        help='Set loglevel to debug. (default: warning)')

    parser.add_argument('--highdpi', dest='highdpi', action='store_const',
                    const=True, default=False,
                    help='Solve blurry fonts on High DPI systems.')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    logger = logging.getLogger(__name__)

    app = App()

    if args.highdpi:
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

    app.mainloop()
