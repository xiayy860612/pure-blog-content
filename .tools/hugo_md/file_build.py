import os
import time
import re
import shutil


class FileBuilder:

    def __init__(self, host_root_postfix, pure_content_root, hugo_root, md_temp_src):
        self.__host_root_postfix = host_root_postfix
        self.__pure_content_root = pure_content_root
        self.__hugo_content_root = os.path.join(hugo_root, "content")
        self.__hugo_static_root = os.path.join(hugo_root, 'static')
        self.__md_temp_src = md_temp_src

        title_pattern_str = r'^#\s+(?P<title>.+)$';
        self.__title_pattern = re.compile(title_pattern_str)

        img_pattern_str = r'![[](?P<img_title>.+)[]][(](?P<img_path>.+)[)]'
        self.__img_pattern = re.compile(img_pattern_str)

        special_keys_pattern_str = r''

    def __is_local_img(self, img_path):
        if re.match('^http[s]*://.+', img_path, re.IGNORECASE):
            return False
        return True

    def __process_img(self, relative_file, line):
        m = self.__img_pattern.search(line)
        if m is None:
            return line

        img_path = m.group('img_path')
        if not self.__is_local_img(img_path):
            return line

        ab_md_src = os.path.join(self.__pure_content_root, relative_file)
        ab_md_dir = os.path.dirname(ab_md_src)
        ab_local_img_path = os.path.join(ab_md_dir, img_path)

        if not os.path.exists(ab_local_img_path): 
            print "img[%s] not exists." % ab_local_img_path
            return line

        rel_file_no_ext = relative_file.rsplit('.', 1)[0]
        rel_hugo_img_path = os.path.join('content', rel_file_no_ext, img_path)
        ab_hugo_img_path = os.path.join(
            self.__hugo_static_root, 
            rel_hugo_img_path
        )
        ab_hugo_img_dir = os.path.dirname(ab_hugo_img_path)
        if not os.path.exists(ab_hugo_img_dir):
            os.makedirs(ab_hugo_img_dir)
        
        shutil.copyfile(ab_local_img_path, ab_hugo_img_path)
        hugo_img_link = os.path.join(self.__host_root_postfix, rel_hugo_img_path)
        hugo_img_line = "![%s](/%s)" % (m.group('img_title'), hugo_img_link)
        line = self.__img_pattern.sub(hugo_img_line, line)
        return line
        
    def __get_title_from_line(self, line):
        m = self.__title_pattern.match(line)
        if m is not None:
            return m.group('title')
        return None

    def __get_hugo_md_title(self, relative_file):
        ab_md_src = os.path.join(self.__pure_content_root, relative_file)
        
        with open(ab_md_src, 'r') as pure_md:
            line = pure_md.readline()
            title = self.__get_title_from_line(line)
            if title:
                return title
        
        return os.path.basename(relative_file).rsplit('.', 1)[0].capitalize()

    def __get_hugo_md_content(self, relative_file):
        ab_md_src = os.path.join(self.__pure_content_root, relative_file)
        hugo_md_content = ''
        with open(ab_md_src, 'r') as pure_md:
            is_first_line_processed = False
            for line in pure_md.readlines():
                if not is_first_line_processed:
                    is_first_line_processed = True
                    title = self.__get_title_from_line(line)
                    if title:
                        continue

                line = self.__process_img(relative_file, line)
                hugo_md_content += line
                
        return hugo_md_content

    def build(self, relative_file, weight):
        ab_hugo_file = os.path.join(self.__hugo_content_root, relative_file)

        # if os.path.exists(ab_hugo_file):
            # return

        ab_md_src = os.path.join(self.__pure_content_root, relative_file)
        info = os.stat(ab_md_src)

        param_pattern_str = r'\${(?P<key>\w+)}'
        pattern = re.compile(param_pattern_str)
        key_processor = {
            "title": lambda: self.__get_hugo_md_title(relative_file),
            "date": lambda: time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(info.st_ctime)),
            "weight": lambda: "%s" % weight,
            "content": lambda: self.__get_hugo_md_content(relative_file)
        }

        with open(self.__md_temp_src, 'rb') as md_temp:
            with open(ab_hugo_file, 'wb+') as target_hugo_md:
                for line in md_temp.readlines():
                    m = pattern.search(line)
                    if m is not None:
                        key = m.group('key')
                        rep_str = key_processor[key]()
                        if key != 'content':
                            line = pattern.sub(rep_str, line)
                        else:
                            line = rep_str

                    target_hugo_md.write(line)
                target_hugo_md.flush()
                
        return