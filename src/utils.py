def clock_from_seconds(seconds):
    seconds = int(seconds)
    m = seconds/60
    s = seconds%60
    if len(str(s)) == 1:
        s = "0"+str(s)
    return str(m)+":"+str(s)

def get_vid_id(url): 
    url = str(url)
    url = url.replace('feature=player_embedded&', '') 
    idx = url.find("?v=")
    if idx >= 0:
        idx += 3
        vid_id = url[idx: idx+11]
    else:
        idx = url.find("youtu.be/")
        if idx >= 0:
            idx+=9
            vid_id = url[idx: idx+11]
        else:
            if idx <0:
                return "xxx"
    return vid_id