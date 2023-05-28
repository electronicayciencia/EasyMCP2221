import logging
from .App import App

if __name__ == "__main__":

    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(__name__)

    app = App()

    try:
        from ctypes import windll
        # For high DPI
        #windll.shcore.SetProcessDpiAwareness(1)
    finally:
        app.mainloop()
