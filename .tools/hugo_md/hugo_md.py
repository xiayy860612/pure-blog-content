#!/usr/bin/python
import os
import io
import re

import hugo_config
from content_walker import *
from dir_build import *
from file_build import *

if __name__ == "__main__":
    """
    """
    # default input dir
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(cur_dir, 'template')

    relative_pure_content_dir = hugo_config.pure_md_content 
    if relative_pure_content_dir == '':
        relative_pure_content_dir = "../../content"
    ab_pure_content_dir = os.path.join(cur_dir, relative_pure_content_dir)

    relative_hugo_content_dir = hugo_config.hugo_blog_root
    if relative_hugo_content_dir == '':
        relative_hugo_content_dir = "../../hugo_blog"
    ab_hugo_content_dir = os.path.join(cur_dir, relative_hugo_content_dir, "content")

    dir_index_path = os.path.join(template_dir, '_index.md')
    dir_builder = DirBuilder(ab_pure_content_dir, ab_hugo_content_dir, dir_index_path)

    md_temp_path = os.path.join(template_dir, 'single.md')
    md_file_builder = FileBuilder(ab_pure_content_dir, ab_hugo_content_dir, md_temp_path)
    
    walker = ContentWalker(ab_pure_content_dir)
    for info in walker.run():
        # print info.content_type, info.content_path
        if info.content_type == ContentInfo.Content_Type_Dir:
            dir_builder.build(info.content_path, info.weight)
        elif info.content_type == ContentInfo.Content_Type_File:
            md_file_builder.build(info.content_path, info.weight)
        else:
            continue
                
    print "Done!!!"