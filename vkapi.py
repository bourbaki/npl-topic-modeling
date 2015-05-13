import requests as req

# NPL VK Freeze data
FREEZE_HOST = "api.vk.com"
FREEZE_API = "method"

ITEMS_KEY="items"

# Main methods
def api(method, params, vk_host=FREEZE_HOST, api_path=FREEZE_API):
    # construct args for api call
    path = "%s/%s" % (api_path, method)
    # construct url for api call
    url = construct_url(host=vk_host, path=path)
    print(url, params)
    res = req.get(url, params=params)
    data = res.json()['response']
    return data

def construct_url(host, path, protocol="https"):
    return "{protocol}://{host}/{path}".format(protocol=protocol, host=host, path=path)

def get_all(method, args, limit=1000, items_key=ITEMS_KEY):
    # make initial request
    data = api(method, dict(offset=0, count=limit, **args))
    n_items, items = data['count'], data[items_key]
    if limit and n_items > limit:
        r_n = n_items // limit # number of requests
        r_ofs = list((i + 1) * limit for i in range(r_n)) # offsets
        r_params = list(dict(offset=of, count=limit, **args) for of in r_ofs) # parameters for requests
        items.extend(item for p in r_params for item in api(method, p)[items_key]) # add remainder
    assert len(items) == api(method, dict(offset=0, count=0, **args))['count']
    return items

# wrappers for basic methods
def get_members(group_id):
    return get_all("groups.getMembers", {"group_id": group_id, "scope": "super"})

def get_friends(user_id):
    return get_all("friends.get", {"user_id": user_id, "v": "5.29", "lang": "en"}, limit=None)

def get_followers(user_id):
    return get_all("users.getFollowers", {"user_id": user_id, "v": "5.29", "lang": "en"})

def get_wall_posts(group_name):
    return get_all("wall.get", {"domain": group_name, "v": "5.32"}, limit=100)
