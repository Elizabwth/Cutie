def clock_from_seconds(seconds):
    seconds = int(seconds)
    m = seconds/60
    s = seconds%60
    if len(str(s)) == 1:
        s = "0"+str(s)
    return str(m)+":"+str(s)

def get_video_id(url): 
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

# http://stackoverflow.com/questions/1823058/how-to-print-number-with-commas-as-thousands-separators
def intWithCommas(x):
    if type(x) not in [type(0), type(0L)]:
        raise TypeError("Parameter must be an integer.")
    if x < 0:
        return '-' + intWithCommas(-x)
    result = ''
    while x >= 1000:
        x, r = divmod(x, 1000)
        result = ",%03d%s" % (r, result)
    return "%d%s" % (x, result)