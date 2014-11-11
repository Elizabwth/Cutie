# http://stackoverflow.com/questions/3368969/find-string-between-two-substrings
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def find_between_r( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

def clock_from_seconds(seconds):
    seconds = int(seconds)
    m = seconds/60
    s = seconds%60
    if len(str(s)) == 1:
        s = "0"+str(s)
    return str(m)+":"+str(s)

def get_vid_code(url): 
    url = str(url)
    # remove some junk from the URL if it contains it
    url = url.replace('feature=player_embedded&', '') 
    idx = url.find("?v=")
    if idx >= 0:
        idx += 3
        vid_code = url[idx: idx+11]
    else:
        idx = url.find("youtu.be/")
        if idx >= 0:
            idx+=9
            vid_code = url[idx: idx+11]
        else:
            if idx <0:
                return "xxx"
    return vid_code