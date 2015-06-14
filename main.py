__author__ = 'yardeneitan'

from instagram import client
import foursquare
from Levenshtein import distance


IG_CONFIG = {
    'client_id': '',
    'client_secret': '',
}

class InstagramUser:
    def __init__(self, name, username, picture, followers, id):
        self.name = name
        self.username = username
        self.picture = picture
        self.followers = followers
        self.id = id

def foursquare_connect():
    # Construct the client object
    client = foursquare.Foursquare(client_id='', client_secret='')
    return client


def instagram_connect():
    api = client.InstagramAPI(client_id=IG_CONFIG['client_id'], client_secret=IG_CONFIG['client_secret'])
    return api

def write_to_file(instagram_user, i, file):
    file.write('----------------------------\n')
    file.write('User #' + str(i) + '\n')
    file.write('name: ' + instagram_user.name + '\n')
    file.write('id: ' + instagram_user.id + '\n')
    file.write('username: ' + instagram_user.username + '\n')
    file.write('profile picture: ' + instagram_user.picture + '\n')
    file.write('followers: ' + str(instagram_user.followers) + '\n\n')

fs_api = foursquare_connect()
ig_api = instagram_connect()

places = [line.rstrip('\n') for line in open('cool_places')]
f = open('influencers','w')
i = 1
user_output = []


for place in places:
    place = place.encode('utf-8')
    print(place)
    response = fs_api.venues.search(params={'query': place, 'near': 'San Francisco, CA'})
    if not response['venues'] or len(response['venues']) == 0:
        print('venue not found')
        continue

    best_dist = 1000
    best_index = 0
    for index,fs_venue in enumerate(response['venues']):
        if index == 5:
            break
        dist = distance(place, fs_venue['name'].encode('utf-8'))
        if dist < best_dist:
            best_dist = dist
            best_index = index

    fs_venue_id = response['venues'][best_index]['id']
    ig_venue = ig_api.location_search(foursquare_v2_id=fs_venue_id)
    if not ig_venue or len(ig_venue) == 0:
        print('couldnt find the venue on instagram')
        continue
    ig_venue_id = ig_venue[0].id
    recent_media_for_venue = ig_api.location_recent_media(location_id=ig_venue_id, count=100)
    if len(recent_media_for_venue) == 0:
        print('couldnt find media for venue')
        continue

    for media in recent_media_for_venue[0]:
        user = media.user
        if not user:
            print('this media has no proper user')
            continue

        full_user = ig_api.user(user_id=user.id)
        if full_user.counts['followed_by'] > 1000:
            print(i)
            ig_user = InstagramUser(name=user.full_name.encode('utf-8'),
                                    username=user.username.encode('utf-8'),
                                    id=user.id,
                                    picture=user.profile_picture,
                                    followers=full_user.counts['followed_by'])
            write_to_file(ig_user, i, f)
            user_output.append(ig_user)
            i+=1

f.close()
i = 1
user_output.sort(key=lambda x: x.followers, reverse=True)
user_output = list(set(user_output))
f = open('influencers_ordered','w')
for user in user_output:
    write_to_file(user, i, f)
    i+=1