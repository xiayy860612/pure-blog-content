import os
import time
import re

class DirBuilder:
    """
    """
    def __init__(self, pure_content_root, hugo_root, dir_index_src):
        self.__pure_content_root = pure_content_root
        self.__hugo_content_root = os.path.join(hugo_root, "content")
        self.__dir_index_src = dir_index_src

    def build(self, relative_dir, weight):
        ab_dir = os.path.join(self.__hugo_content_root, relative_dir)
        ab_dir_index = os.path.join(ab_dir, '_index.md')

        if not os.path.exists(ab_dir):
            os.makedirs(ab_dir)
        
        if os.path.exists(ab_dir_index):
            return

        info = os.stat(ab_dir)
        param_pattern_str = r'\${(?P<key>\w+)}'
        pattern = re.compile(param_pattern_str)
        key_processor = {
            "title": lambda: os.path.basename(ab_dir).capitalize(),
            "date": lambda: time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(info.st_ctime)),
            "weight": lambda: "%s" % weight
        }
        with open(self.__dir_index_src, 'r') as index_file:
            with open(ab_dir_index, 'w+') as target_index_file:
                for line in index_file.readlines():
                    m = pattern.search(line)
                    if m is not None:
                        key = m.group('key')
                        rep_str = key_processor[key]()
                        line = pattern.sub(rep_str, line)

                    target_index_file.write(line)
                target_index_file.flush()

        return
    