import gdata
import gdata.youtube 
import gdata.youtube.service
from utils import *

class User:
    def __init__(self, ip, user_name, group):
        self.ip = ip
        self.user_name = user_name
        self.group = group
        # possible groups: 
        ## regular (can't add videos)
        ## promoted (can add videos)
        ## curator (can add videos, promote and kick users, is user everyone will sync to)
        ### promoted admin if first user to connect or next successive

class QueueItem:
    def __init__(self, vid_id):
        self.vid_id   = vid_id
        yt_service = gdata.youtube.service.YouTubeService()
        entry = yt_service.GetYouTubeVideoEntry(video_id=self.vid_id)

        self.title            = entry.media.title.text
        self.duration         = entry.media.duration.seconds
        self.view_count       = entry.statistics.view_count
        self.rating_average   = entry.rating.average
        self.duration_display = clock_from_seconds(self.duration)
        
class Server:
    def __init__(self):
        self.users = []
        self.queue = []

    def broadcast_chat_message(self, message):
        pass

    def user_connect(self, ip, user_name, group):
        u = User(ip, user_name, group)
        self.users.append(u)

    def user_disconnect(self, user):
        self.users.remove(user)

    def add_video_to_queue(self, vid_id):
        qi = QueueItem(vid_id)
        self.queue.append(qi)

    def remove_video_from_queue(self, qi):
        self.queue.remove(qi)


if __name__ == '__main__':
    qi = QueueItem("ROecfEyl1XE")
    print "title            = "+qi.title+"\n", \
          "views            = "+qi.view_count+"\n", \
          "rating           = "+qi.rating_average+"\n", \
          "duration         = "+qi.duration+"\n", \
          "duration display = "+qi.duration_display