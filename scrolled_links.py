from tkinter.scrolledtext import ScrolledText
import url_func
from file_func import open_path


# noinspection PyBroadException
class ScrolledLink(ScrolledText):
    def __init__(self, master, **kw):
        ScrolledText.__init__(self, master, **kw)
        self.bind("<Key>", lambda x: "break")
        self.tag_config("url", foreground="blue", underline=1)

        self.tag_bind("url", "<Enter>", self._enter)
        self.tag_bind("url", "<Leave>", self._leave)
        self.tag_bind("url", "<Button-1>", self._open_url)
        self.tag_bind("url", "<Button-3>", self._copy)

    def _get_url_near_cursor(self, event):
        index = self.index("@%s,%s" % (event.x, event.y))
        line_num, col_num = index.split(".")
        line = self.get(line_num + ".0", line_num + ".end")
        i = 0
        for word in line.split(" "):
            i += len(word)
            if int(col_num) <= i and url_func.check_url_syntax(word):
                return word
        return ""

    def _copy(self, event):
        url = self._get_url_near_cursor(event)
        self.clipboard_clear()
        self.clipboard_append(url)

    def _enter(self, event):
        self.config(cursor="hand2")

    def _leave(self, event):
        self.config(cursor="")

    def _open_url(self, event):
        url = self._get_url_near_cursor(event)
        open_path(url)

    # insert line with links
    def insert_lwl(self, index, chars):
        try:
            line_num, col_num = str(index).split(".")
            first_word = True
            i = int(col_num)
            for word in chars.split(' '):
                col_num = str(i)
                if first_word:
                    first_word = False
                else:
                    ScrolledText.insert(self, line_num + "." + col_num, " ")
                    i += 1
                    col_num = str(i)
                if url_func.check_url_syntax(word):
                    ScrolledText.insert(self, line_num + "." + col_num, word, "url")
                else:
                    ScrolledText.insert(self, line_num + "." + col_num, word)
                i += len(word)
        except:
            # logger.exception("Error in insertion")
            pass
