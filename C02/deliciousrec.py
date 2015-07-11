# -*- coding=utf-8 -*-
from pydelicious import get_popular, get_userposts, get_urlposts
import time

'''
    The pydelicious didn't work, turns back with this info:
        [{'extended': '', 'description': u'something went wrong', 'tags': '', 'url': '', 'user': '', 'dt': ''}]
'''

def initializeUserDict(tag, count=5):
    suer_dict = {}
    a = get_popular(tag=tag)[0:count]
    print a
    for p1 in  a:
        # Find all user who posted it
        for p2 in get_urlposts(p1['href']):
            user = p2['user']
            user_dict[user] = {}
    return user_dict


def fillItems(user_dict):
    all_items = {}
    # Find links posted by all users
    for user in user_dict:
        for i in range(3):
            try:
                posts = get_userposts(user)
                break
            except:
                print "Failed uesr"+ user+ ", retrying"
                time.sleep(4)
        for post in posts:
            url = post['href']
            user_dict[user][url] = 1.0
            all_items[url] = 1
        
        for ratings in user_dict.values():
            for item in all_items:
                if item not in ratings:
                    ratings[item] = 0.0

if __name__=='__main__':
    delusers = initializeUserDict(tag='programming')
    delusers['ColinVon'] = {}
    fillItems(delusers)
    
