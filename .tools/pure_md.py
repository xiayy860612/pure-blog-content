#!/usr/bin/python
import os
import sys
import io
import re
import Queue
import multiprocessing
import time


# List all md formatter header of engine
pattern_dict = {
    "hugo": "^[+]{3,}.*title.*=.*\"(?P<title>.*)\".*[+]{3,}",
}

def walk_dir(dir_queue, dir_done_evt, md_queue, ignore_flag):
    """
    check everything in pop dir,
    if dir, put into dir_queue; 
    if md file, put into md_queue;
    or ignore

    Everything start with "." will be ignored
    """
    while True:
        if dir_queue.empty():
            dir_done_evt.set()
            break

        src_dir = dir_queue.get()
        if ignore_flag and src_dir.startswith("."):
            continue

        for sub_item in os.listdir(src_dir):
            _process_sub_item(src_dir, sub_item, dir_queue, md_queue, ignore_flag)


def _process_sub_item(src_dir, sub_item, dir_queue, md_queue, ignore_flag):
    """
    Process sub_item in src_dir, 
    if start with "." will be ignored 
    """
    if ignore_flag and sub_item.startswith("."):
        return

    # get full path of sub item
    sub_item = os.path.join(src_dir, sub_item)
    # print "Sub Item: %s" % sub_item
    if os.path.isdir(sub_item):
        dir_queue.put(sub_item)
    elif sub_item.endswith(".md"):
        md_queue.put(sub_item)

    return


def process_md(regex_pattern_dict, md_queue, dir_done_evt):
    """
    Process available md file from md_queue to make it pure md
    """
    regex_list = []

    for key, pattern in regex_pattern_dict.iteritems():
        regex = re.compile(pattern, re.M | re.DOTALL)
        regex_list.append(regex)

    while True:
        if md_queue.empty():
            if dir_done_evt.is_set():
                # everything is done
                break
            time.sleep(0.5)
            continue

        md_file = md_queue.get()
        with open(md_file, "r+") as f:
            orig_ctx = f.read()
            dest_ctx = None
            for regex in regex_list:
                match_ctx = regex.match(orig_ctx)
                if not match_ctx:
                    continue

                title = "# %s" % match_ctx.group('title')
                dest_ctx = regex.sub(title, orig_ctx)

            if not dest_ctx:
                continue
            
            # Overwrite file
            f.seek(0)
            f.write(dest_ctx)
            f.truncate()


if __name__ == "__main__":
    """
    cmd: pure_md.py [-p abs_path] [-i]
    """
    # default input dir
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.join(cur_dir, os.path.pardir)
    input_dir = os.path.join(root_dir, "content")
    ignore_flag = True

    argv_len = len(sys.argv)
    if argv_len > 1:
        for index in xrange(argv_len):
            if index == 0:
                continue

            arg = sys.argv[index]
            if '-p' in arg:
                input_dir = sys.argv[index+1]
            elif '-i' in arg:
                ignore_flag = False

    if not os.path.isdir(input_dir):
        raise Exception("Error Input Dir: %s" % input_dir)

    data_manager = multiprocessing.Manager()
    
    dir_queue = data_manager.Queue()
    dir_done_evt = data_manager.Event()
    md_queue = data_manager.Queue()
    
    worker_pool = multiprocessing.Pool(7)

    for i in xrange(3):
        worker_pool.apply_async(process_md, (pattern_dict, md_queue, dir_done_evt))

    dir_queue.put(input_dir)
    # sync test
    # walk_dir(dir_queue, dir_done_evt, md_queue, ignore_flag)
    # process_md(pattern_dict, md_queue, dir_done_evt)
    worker_pool.apply_async(walk_dir, (dir_queue, dir_done_evt, md_queue, ignore_flag))

    worker_pool.close()
    worker_pool.join()
    print "Done!!!"