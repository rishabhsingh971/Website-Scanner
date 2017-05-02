import file_func
import time
import logging

logger = logging.getLogger()


class CrawlerFiles:
    def __init__(self, save_dir_path=None, start_url=None):
        self.paths = dict()
        self.log_file = 'log'
        self.config_file = 'config'
        self.crawled_file = 'crawled'
        self.found_files_file = 'files'
        self.found_strings_file = 'strings'
        self.invalid_file = 'invalid'
        self.waiting_file = 'waiting'
        self.info_file = 'info'
        if save_dir_path is not None:
            self.save_dir = save_dir_path
            self.log_dir = file_func.get_file_path(save_dir_path, 'logs')
            self.paths[self.log_file] = file_func.get_file_path(self.log_dir, 'wc_log.log')
            self.paths[self.info_file] = file_func.get_file_path(save_dir_path, 'info.txt')
            self.paths[self.config_file] = file_func.get_file_path(save_dir_path, 'config.cfg')
            self.paths[self.crawled_file] = file_func.get_file_path(save_dir_path, 'crawled_urls.txt')
            self.paths[self.found_files_file] = file_func.get_file_path(save_dir_path, 'found_files.txt')
            self.paths[self.found_strings_file] = file_func.get_file_path(save_dir_path, 'found_strings.txt')
            self.paths[self.invalid_file] = file_func.get_file_path(save_dir_path, 'invalid_urls.txt')
            self.paths[self.waiting_file] = file_func.get_file_path(save_dir_path, 'waiting_urls.txt')
            self.running_file = file_func.get_file_path(save_dir_path, 'running.cwl')
            if start_url is not None:
                self.create_files(start_url)

    def stopped(self):
        file_func.delete_file(self.running_file)

    def started(self):
        file_func.make_file(self.running_file)

    def is_running(self):
        rv = file_func.file_exists(self.running_file)
        logger.info('->' + str(rv))
        return rv

    def create_files(self, start_url):
        if not file_func.dir_exists(self.log_dir):
            file_func.make_dir(self.log_dir)
            logger.info('->Created log directory')
        for file in self.paths:
            file_path = self.paths[file]
            if not file_func.file_exists(file_path):
                if file is self.config_file or file is self.waiting_file:
                    file_func.make_file(file_path, start_url)
                    
                else:
                    file_func.make_file(file_path)
                logger.info('-> Created %s file' % file)

    def set_file_data(self, file_name, file_data):
        if file_name == self.config_file or file_name == self.info_file:
            file_func.json_dump_to_file(file_data, self.paths[file_name])
            logger.info('->Updated config file')
        else:
            file_func.set_to_file(file_data, self.paths[file_name])
            logger.info('->Updated %s file' % file_name)

    def get_file_data(self, file_name):
        if file_name == self.config_file or file_name == self.info_file:
            file_data = file_func.json_load_from_file(self.paths[file_name])
            logger.info('->Read %s file ' % file_name)
            return file_data
        else:
            file_data = file_func.file_to_set(self.paths[file_name])
            logger.info('->Read %s file' % file_name)
            return file_data

    def change_start_url(self, new_start_url):
        s_dir = self.save_dir
        s_dir_new = s_dir + time.strftime("%d%m%y%H%M%S")
        file_func.rename_dir(s_dir, s_dir_new)
        file_func.make_dir(s_dir)
        self.create_files(new_start_url)
        logger.info('->Saved previous data in %s' % s_dir_new)

    def open_save_dir(self):
        file_func.open_path(self.save_dir)
        logger.info('->Opened Save Directory %s' % self.save_dir)

    def get_files_data(self, *file_names):
        files_data = list()
        for file_name in file_names:
            if file_name == self.config_file or file_name == self.info_file:
                file_data = file_func.json_load_from_file(self.paths[file_name])
                logger.info('->Loaded %s file ' % file_name)
                files_data.append(file_data)
            else:
                file_data = file_func.file_to_set(self.paths[file_name])
                logger.info('->Loaded %s file' % file_name)
                files_data.append(file_data)
        return files_data

    def set_files_data(self, **files_data):
        for file_name in files_data.keys():
            if file_name == self.config_file or file_name == self.info_file:
                file_func.json_dump_to_file(files_data[file_name], self.paths[file_name])
                logger.info('->Updated %s file' % file_name)
            else:
                file_func.set_to_file(files_data, self.paths[file_name])
                logger.info('->Updated %s file' % file_name)
