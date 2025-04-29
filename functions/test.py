groups = ['a','b', 'c']

import base64  

# # idx = next((idx for idx, value in enumerate(groups) if value == 'c'), None)
# # print(idx)


# import random

# print(random.sample(groups, 4))


# keys = [{'id': {'S': group_id}} for group_id in group_ids]


# def fetch_random_group(group_ids):
#     """
#     Fetch a random group from the list of group IDs.
#     """
#     if not group_ids:
#         return None

#     random_group_id = random.choice(group_ids)['S']
#     return fetch_group_by_id(random_group_id)


if __name__ == "__main__":
    print(base64.b64encode('r5n1u8dodck65qnftsc26bb4u:ol6qjprdhfmd5hnvrn48vcl07uak4l4l4d33cfm878ljqcssc08'.encode()).decode())


