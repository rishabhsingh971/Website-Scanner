import logging
import time
from contextlib import closing
from urllib import parse

import requests
from bs4 import BeautifulSoup
from robotexclusionrulesparser import RobotExclusionRulesParser

import url_func
from crawler_files import CrawlerFiles
from file_func import dir_exists, make_dir, file_size, get_file_path

logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("chardet").setLevel(logging.ERROR)
logger = logging.getLogger()


class Crawler:
    start_page_url = ''
    rerp = RobotExclusionRulesParser()
    cFiles = CrawlerFiles()
    tld = ''
    waiting_url_set = set()
    crawled_url_set = set()
    bad_url_set = set()
    find_string_set = set()
    find_flname_set = set()
    found_flname_set = set()
    found_string_set = set()
    stop_request = False
    download_chunk_size = 0
    conn_timeout = 0
    delay = 0
    user_agent = ''
    bad_url_prefix = '->Bad Url '
    found_string_prefix = '->Found '
    found_flname_prefix = '->Saved '

    def __init__(self, save_dir, start_url, find_flname_set, find_string_set, chunk_size, conn_timeout, default_delay,
                 user_agent):
        logger.info('->Starting RERP')
        Crawler.rerp.fetch(start_url + '/robots.txt')
        Crawler.user_agent = user_agent
        delay = Crawler.rerp.get_crawl_delay(Crawler.user_agent)
        Crawler.conn_timeout = conn_timeout
        if delay is None:
            Crawler.delay = default_delay
        else:
            Crawler.delay = delay
        Crawler.cFiles = CrawlerFiles(save_dir, start_url)
        logger.info('->Getting Previous Session files (if any) ')
        Crawler.crawled_url_set = Crawler.cFiles.get_file_data(Crawler.cFiles.crawled_file)
        Crawler.found_flname_set = Crawler.cFiles.get_file_data(Crawler.cFiles.found_files_file)
        Crawler.found_string_set = Crawler.cFiles.get_file_data(Crawler.cFiles.found_strings_file)
        Crawler.bad_url_set = Crawler.cFiles.get_file_data(Crawler.cFiles.invalid_file)
        Crawler.waiting_url_set = Crawler.cFiles.get_file_data(Crawler.cFiles.waiting_file)
        info = Crawler.cFiles.get_file_data(Crawler.cFiles.info_file)

        Crawler.start_page_url = start_url

        Crawler.tld = url_func.return_tld(start_url)

        Crawler.find_string_set = find_string_set
        Crawler.find_flname_set = find_flname_set
        Crawler.download_chunk_size = chunk_size
        logger.info('Crawler Initiated')
        logger.info('->Loading Website Info')
        logger.debug('* ' * 20 + 'Website Info' + '* ' * 20)
        if info is None:
            info = url_func.get_domain_info(Crawler.tld)
            Crawler.cFiles.set_file_data(Crawler.cFiles.info_file, info)
        for key in info:
            val = info[key]
            if val:
                logger.debug("%-20s : %s" % (str(key).upper(), str(val)))
        logger.debug('* ' * 40)

    @staticmethod
    def crawl_page(t_name, page_url):
        # noinspection PyBroadException
        try:
            logger.debug("%s - %s" % (t_name, page_url))
            if not Crawler.rerp.is_allowed(Crawler.user_agent, page_url):
                logger.debug('->%s not allowed to crawl %s' % (t_name, page_url))
                return
            Crawler.add_urls(page_url)
            if not Crawler.stop_request:
                Crawler.waiting_url_set.remove(page_url)
                Crawler.crawled_url_set.add(page_url)
                time.sleep(Crawler.delay)
        except requests.HTTPError as h:
            string = "HTTP Error %d - %s" % (h.response.status_code, page_url)
            logger.debug(Crawler.bad_url_prefix + string)
            Crawler.bad_url_set.add(string)
            Crawler.waiting_url_set.remove(page_url)
            Crawler.crawled_url_set.add(page_url)
        except requests.ReadTimeout:
            string = "Timeout %0.1f secs - %s " % (Crawler.conn_timeout, page_url)
            logger.debug(Crawler.bad_url_prefix + string)
            Crawler.bad_url_set.add(string)
            Crawler.waiting_url_set.remove(page_url)
            Crawler.crawled_url_set.add(page_url)
        except requests.TooManyRedirects as t:
            string = "%s - %s" % (t, page_url)
            logger.debug(Crawler.bad_url_prefix + string)
            Crawler.bad_url_set.add(string)
            Crawler.waiting_url_set.remove(page_url)
            Crawler.crawled_url_set.add(page_url)
        except (requests.ConnectionError, requests.ConnectTimeout):
            if url_func.check_connection() != url_func.CONNECTION_OK:
                Crawler.wait(t_name)
        except Exception:
            logger.exception('Exception in %s ' % page_url)
            Crawler.waiting_url_set.remove(page_url)
            Crawler.crawled_url_set.add(page_url)

    @staticmethod
    def add_urls(page_url):
        not_html = False
        with closing(requests.get(page_url, stream=True, timeout=Crawler.conn_timeout)) as page:  # html code of page
            type_of_page = page.headers['Content-Type']  # get content type from header of html page
            page.raise_for_status()
            if 'html' in type_of_page:  # web page
                soup = BeautifulSoup(page.content, "html.parser")  # parse the content of page
                text = soup.text
                for string in Crawler.find_string_set:
                    if Crawler.stop_request:  # if stop is requested by user
                        return
                    str_url = string + ' ' + page_url
                    if text is not None and string in text:
                        Crawler.found_string_set.add(str_url)
                        logger.debug('%s %s %s' % (Crawler.found_string_prefix, string, page_url))
                for a_tag_content in soup.find_all('a'):
                    if Crawler.stop_request:  # if stop is requested by user
                        return
                    url = parse.urljoin(Crawler.start_page_url, a_tag_content.get('href'))
                    if '#' in url:
                        url = url.split('#')[0]
                    if ' ' in url:
                        url = url.replace(' ', '%20')
                    if url_func.return_tld(url) == Crawler.tld:
                        if url not in Crawler.crawled_url_set:
                            Crawler.waiting_url_set.add(url)
            else:
                not_html = True
        if not_html:
            f_name = page_url.split('/')[-1]
            download_file = False
            for string in Crawler.find_flname_set:
                if Crawler.stop_request:
                    break
                if string in f_name:
                    download_file = True
                    break
            if download_file:
                type_split = type_of_page.split('/')
                f_dir = Crawler.cFiles.save_dir + '/' + type_split[0]
                if not dir_exists(f_dir):
                    make_dir(f_dir)
                Crawler.found_flname_set.add(page_url)
                Crawler.file_download(page_url, f_dir, f_name)
                if not Crawler.stop_request:
                    logger.debug('%s %s' % (Crawler.found_flname_prefix, page_url))

    # wait
    @staticmethod
    def wait(t_name):
        logger.info('->%s waiting for connection...' % t_name)
        while True:
            if Crawler.stop_request:
                break
            if url_func.check_connection() == url_func.CONNECTION_OK:
                break
            time.sleep(2)

    @staticmethod
    def update_files():
        logger.info('Updating Files')
        Crawler.cFiles.set_file_data(Crawler.cFiles.crawled_file, Crawler.crawled_url_set)
        Crawler.cFiles.set_file_data(Crawler.cFiles.found_files_file, Crawler.found_flname_set)
        Crawler.cFiles.set_file_data(Crawler.cFiles.found_strings_file, Crawler.found_string_set)
        Crawler.cFiles.set_file_data(Crawler.cFiles.invalid_file, Crawler.bad_url_set)
        Crawler.cFiles.set_file_data(Crawler.cFiles.waiting_file, Crawler.waiting_url_set)

    @staticmethod
    def file_download(file_url, f_dir, f_name):
        f_path = get_file_path(f_dir, f_name)
        # logger.info('Saving  ', f_name)
        dl = file_size(f_path)
        resume_header = {'Range': 'bytes=%d-' % dl}
        with closing(requests.get(file_url, stream=True, headers=resume_header, timeout=Crawler.conn_timeout)) as file:
            tl_str = file.headers.get('content-length')
            # if there is no content length specified in header website doesnt support resuming
            mode = 'ab' if tl_str else 'wb'
            with open(f_path, mode) as handle:
                for chunk in file.iter_content(chunk_size=Crawler.download_chunk_size):
                    if Crawler.stop_request:  # if stop is requested by user
                        return
                    if chunk:
                        handle.write(chunk)
