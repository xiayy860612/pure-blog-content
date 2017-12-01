import os
import time
import re


class FileBuilder:

    def __init__(self, pure_content_root, hugo_content_root, md_temp_src):
        self.__pure_content_root = pure_content_root
        self.__hugo_content_root = hugo_content_root
        self.__md_temp_src = md_temp_src

    def __get_pure_md_content(self, ab_md_src):
        with open(ab_md_src, 'r') as pure_md:
            return pure_md.read()

    def build(self, relative_file, weight):
        ab_hugo_file = os.path.join(self.__hugo_content_root, relative_file)

        # if os.path.exists(ab_hugo_file):
            # return

        ab_md_src = os.path.join(self.__pure_content_root, relative_file)
        info = os.stat(ab_md_src)

        param_pattern_str = r'\${(?P<key>\w+)}'
        pattern = re.compile(param_pattern_str)
        key_processor = {
            "title": lambda: os.path.basename(ab_md_src).rsplit('.', 1)[0].capitalize(),
            "date": lambda: time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(info.st_ctime)),
            "weight": lambda: "%s" % weight,
            "content": lambda: self.__get_pure_md_content(ab_md_src)
        }

        with open(self.__md_temp_src, 'r') as md_temp:
            with open(ab_hugo_file, 'w+') as target_hugo_md:
                for line in md_temp.readlines():
                    m = pattern.search(line)
                    if m is not None:
                        key = m.group('key')
                        rep_str = key_processor[key]()
                        line = pattern.sub(rep_str, line)

                    target_hugo_md.write(line)
                target_hugo_md.flush()
                
        return