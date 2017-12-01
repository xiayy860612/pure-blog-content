import os
import Queue

class ContentInfo:
    """
    """

    # content type
    Content_Type_Dir = 0
    Content_Type_File = 1

    def __init__(self, content_type, content_path, weight):
        self.content_type = content_type
        self.content_path = content_path
        self.weight = weight

class DirQueueItem:
        
    def __init__(self, rel_path, depth):
        self.rel_path = rel_path
        self.depth = depth

class ContentWalker:
    """
    """
    def __init__(self, content_root):
        self.__content_root = content_root
        self.__dir_queue = Queue.Queue()


    def run(self):
        # add 1 level dir into dir queue
        parent_queue_item = DirQueueItem("", 0)
        for sub_item in os.listdir(self.__content_root):
            ci = self.__process_sub_item(parent_queue_item, sub_item)
            if ci is None:
                continue

            yield ci 
        
        while not self.__dir_queue.empty():
            parent_queue_item = self.__dir_queue.get()
            ab_parent_dir = os.path.join(self.__content_root, parent_queue_item.rel_path)
            for sub_item in os.listdir(ab_parent_dir):
                ci = self.__process_sub_item(parent_queue_item, sub_item)
                if ci is None:
                    continue

                yield ci

    def __process_sub_item(self, parent_queue_item, sub_item):
        if sub_item.startswith("."):
            return None

        relative_path = os.path.join(parent_queue_item.rel_path, sub_item)
        ab_path = os.path.join(self.__content_root, relative_path)
        if os.path.isdir(ab_path):
            dir_queue_item = DirQueueItem(relative_path, parent_queue_item.depth + 1)
            self.__dir_queue.put(dir_queue_item)
            return ContentInfo(ContentInfo.Content_Type_Dir, relative_path, parent_queue_item.depth + 1)
        elif sub_item.endswith(".md"):
            return ContentInfo(ContentInfo.Content_Type_File, relative_path, parent_queue_item.depth + 1)
        else:
            return None
