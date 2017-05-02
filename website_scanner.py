from tkinter import messagebox, ttk
from scrolled_links import ScrolledLink
from urllib.error import URLError
from logging import handlers
from crawler import Crawler
from queue import Queue
from timer import Timer
import tkinter as tk
import threading
import logging
import time

logger = logging.getLogger()


# noinspection PyBroadException
class WebsiteScanner:
    thread_name_prefix = 'Crawler_'

    def __init__(self, num_threads, total_time):
        self.win = tk.Toplevel()
        self.num_threads = num_threads
        self.total_time = total_time
        self.thread_set = set()
        self.thread_task_queue = Queue()
        text_font = ("Cambria", 11)
        lbl_font = ("Verdana bold", 10)
        lbf_font = ("Verdana", 12)
        pw = tk.PanedWindow(self.win)
        pw1 = tk.PanedWindow(pw, orient="vertical")
        pw2 = tk.PanedWindow(pw, orient="vertical")
        lbf1 = tk.LabelFrame(pw1, text="Main", font=lbf_font)
        lbf2 = tk.LabelFrame(pw1, text="Invalid URLs", font=lbf_font)
        lbf3 = tk.LabelFrame(pw2, text="Searched URLs", font=lbf_font)
        lbf4 = tk.LabelFrame(pw2, text="Searched Files", font=lbf_font)
        self.main_text = ScrolledLink(lbf1, font=text_font, bg="black", fg="white")
        self.invalids = ScrolledLink(lbf2, font=text_font, bg="black", fg="white")
        self.strings = ScrolledLink(lbf3, font=text_font, bg="black", fg="white")
        self.files = ScrolledLink(lbf4, font=text_font, bg="black", fg="white")
        self.status = tk.StringVar()
        self.labelText = tk.StringVar()
        status_lbl = tk.Label(self.win, bd=1, relief="sunken", textvariable=self.status, font=lbl_font, anchor="w",
                              justify="left")
        self.stop_request = False
        self.all_thread_stopped = False
        self.stopped = False

        self.win.title("Crawler")
        # to start maximized
        self.win.winfo_toplevel().wm_state("zoomed")

        self.main_text.pack(fill="both", expand=True)
        self.invalids.pack(fill="both", expand=True)
        self.strings.pack(fill="both", expand=True)
        self.files.pack(fill="both", expand=True)
        pw1.add(lbf1, stretch="always")
        pw1.add(lbf2, stretch="always")
        pw2.add(lbf3, stretch="always")
        pw2.add(lbf4, stretch="always")
        pw.add(pw1, stretch="always")
        pw.add(pw2, stretch="always")
        status_lbl.pack(fill="x", expand=True)
        pw.pack(fill="both", expand=True)

    # noinspection PyBroadException
    class GuiHandler(logging.Handler):
        def __init__(self, links, invalids, strings, files, status):
            logging.Handler.__init__(self)
            self.links = links
            self.invalids = invalids
            self.strings = strings
            self.files = files
            self.status = status
            self.setFormatter(logging.Formatter("%(asctime)s,%(msecs)03d : %(message)s", datefmt='%H:%M:%S'))

        def emit(self, record):
            try:
                line = record.message
                if line.startswith(WebsiteScanner.thread_name_prefix):
                    self.links.insert_lwl(1.0, line + " \n")
                elif line.startswith(Crawler.bad_url_prefix):
                    self.invalids.insert_lwl(1.0, "=> " + line[len(Crawler.bad_url_prefix):] + " \n")
                elif line.startswith(Crawler.found_flname_prefix):
                    self.files.insert_lwl(1.0, "=> " + line[len(Crawler.found_flname_prefix):] + " \n")
                elif line.startswith(Crawler.found_string_prefix):
                    self.strings.insert_lwl(1.0, "=> " + line[len(Crawler.found_string_prefix):] + " \n")
                else:
                    self.links.insert_lwl(1.0, line + " \n")
            except:
                # logger.exception("Error in emitter")
                pass

    def init_logger(self, log_file_name):
        # create file handler
        fh = handlers.RotatingFileHandler(log_file_name, mode="a", maxBytes=102400, backupCount=5)
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter("%(asctime)s : %(levelname)-7s : %(message)s"))
        logger.addHandler(fh)
        # text
        gh = WebsiteScanner.GuiHandler(self.main_text, self.invalids, self.strings, self.files, self.status)
        gh.setLevel(logging.DEBUG)
        logger.addHandler(gh)

    def start_crawl(self, *args):
        try:
            logger.info("Crawler initiating")
            Crawler(*args)
            start_cus_len = len(Crawler.crawled_url_set)
            start_wus_len = len(Crawler.waiting_url_set)
            start_bus_len = len(Crawler.bad_url_set)
            start_ffs_len = len(Crawler.found_flname_set)
            start_fss_len = len(Crawler.found_string_set)
            stat = "All Time  : Crawled URLs-%6d | Waiting URLs-%6d | " % (start_cus_len, start_wus_len)
            stat += "Bad URLs-%6d | Found Files-%6d | Found String-%6d" % (start_bus_len, start_ffs_len, start_fss_len)
            self.status.set(stat)
            self.load_data()
            logger.debug("Crawlers starting...")
            self.create_threads()
            self.win.protocol("WM_DELETE_WINDOW", self.stop_crawl)
            threading.Thread(target=self.assign_task, daemon=True).start()
            total_timer = Timer(seconds=self.total_time)
            sess_timer = Timer()
            while not self.stopped:
                delay = time.perf_counter()
                total_timer += 1
                sess_timer += 1
                stm = "Curr Session Timer - " + str(sess_timer) + " | "
                ttm = "All Sessions Timer - " + str(total_timer) + " | "
                curr_cus_len = len(Crawler.crawled_url_set)
                curr_wus_len = len(Crawler.waiting_url_set)
                curr_bus_len = len(Crawler.bad_url_set)
                curr_ffs_len = len(Crawler.found_flname_set)
                curr_fss_len = len(Crawler.found_string_set)
                curr_stat = "Crawled URLs - %-8d | Waiting URLs - %-8d | Bad URLs - %-8d | " % (
                    curr_cus_len - start_cus_len, curr_wus_len, curr_bus_len - start_bus_len)
                curr_stat += "Found Files - %-8d | Found String - %-8d | " % (
                    curr_ffs_len - start_ffs_len, curr_fss_len - start_fss_len)
                total_stat = "Crawled URLs - %-8d | Waiting URLs - %-8d | Bad URLs - %-8d | " % (
                    curr_cus_len, curr_wus_len, curr_bus_len)
                total_stat += "Found Files - %-8d | Found String - %-8d | " % (curr_ffs_len, curr_fss_len)
                curr_speed = "Crawl speed - %.2f/s" % ((curr_cus_len - start_cus_len) / sess_timer.tot_sec)
                total_speed = "Crawl speed - %.2f/s" % (curr_cus_len / total_timer.tot_sec)
                self.status.set(stm + curr_stat + curr_speed + "\n" + ttm + total_stat + total_speed)
                time.sleep(1-(time.perf_counter()-delay))
            Crawler.update_files()
            self.total_time = total_timer.tot_sec
        except URLError:  # thrown by RERP
            logger.error("Cannot Connect to Internet")
            messagebox.showerror("Error", "Cannot Connect to Internet", parent=self.win)
        except Exception as e:
            logger.exception("Error in handler")
            messagebox.showerror("Error", e, parent=self.win)
        finally:
            # Removing FileHandler and GuiHandler
            logger.info("Crawlers Stopped")
            logger.handlers.pop()
            logger.handlers.pop()
            self.win.destroy()
            return self.total_time

    def load_data(self):
        logger.info("->Loading invalid urls file")
        for iu in Crawler.bad_url_set:
            self.invalids.insert_lwl(1.0, "=> " + iu + " \n")
        logger.info("->Loading found string file")
        for fs in Crawler.found_string_set:
            self.strings.insert_lwl(1.0, "=> " + fs + " \n")
        logger.info("->Loading found files file")
        for ff in Crawler.found_flname_set:
            self.files.insert_lwl(1.0, "=> " + ff + " \n")

    def wait_for_threads(self):
        for thread in self.thread_set:
            thread.join(30)
        self.all_thread_stopped = True

    def stop_crawl(self):
        if messagebox.askquestion("Alert", "Are You Sure?", parent=self.win) == "yes":
            # noinspection PyBroadException
            try:
                self.stop_request = True
                Crawler.stop_request = True
                tl = tk.Toplevel(self.win)
                tl.title("Stopping Crawler")
                tl.wm_protocol('WM_DELETE_WINDOW', lambda: None)
                tk.Label(tl, text="Waiting for all Crawlers to exit. Please Wait...").pack()
                pb = ttk.Progressbar(tl, mode="indeterminate", length=200)
                pb.pack(fill="x", expand=True)
                pb.start(10)
                tl.grab_set()
                tl.transient(self.win)
                tl.update_idletasks()
                w = tl.winfo_screenwidth()
                h = tl.winfo_screenheight()
                size = tuple(int(_) for _ in tl.geometry().split("+")[0].split("x"))
                x = w / 2 - size[0] / 2
                y = h / 2 - size[1] / 2
                tl.geometry("%dx%d+%d+%d" % (size[0], size[1], x, y))
                threading.Thread(target=self.wait_for_threads).start()
                while not self.all_thread_stopped:
                    time.sleep(0.01)
                    tl.update()
                tl.destroy()
            except Exception:
                logger.exception("Exception while stopping")
            finally:
                self.stopped = True

    # Create threads for multitasking
    def create_threads(self):
        for i in range(self.num_threads):
            thread = threading.Thread(target=self.do_task, name=self.thread_name_prefix + str(i + 1), daemon=True)
            self.thread_set.add(thread)
            thread.start()
        logger.info("Crawlers started")

    # Do the assigned task
    def do_task(self):
        name = threading.current_thread().getName()
        logger.debug(name + " started")
        while not self.stop_request:
            url = self.thread_task_queue.get()
            Crawler.crawl_page(name, url)
            self.thread_task_queue.task_done()
        logger.debug(name + " exited")

    # Add urls/task in thread task queue
    def assign_task(self):
        if not self.stop_request:
            waiting_set = Crawler.waiting_url_set.copy()
            if len(waiting_set) > 0:
                for link in waiting_set:
                    self.thread_task_queue.put(link)
                self.thread_task_queue.join()
                self.assign_task()
            else:
                logger.info("Crawling Complete!")
                messagebox.showinfo("Info", "Crawl Complete!!", parent=self.win)
                self.win.destroy()
