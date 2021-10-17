import requests
import pandas as pd
#from datetime import datetime as dt
import telegram_send
import time


def get_reddit_token():
    auth = requests.auth.HTTPBasicAuth('4eJzmKNKIY1TeBuSYB7pGw', '_7ZMeTvgh89ec2N4gepMNCd47db49A')

    data = {'grant_type': 'password',
            'username': 'EagleSkies',
            'password': '6n92vc998Z4843V'}

    headers = {'User-Agent': 'legodeals_scraper/0.1.0'}
    res = requests.post('https://www.reddit.com/api/v1/access_token',
                        auth=auth, data=data, headers=headers)

    token = res.json()['access_token']

    return token


def get_posts(token, previous_sent_post='0'):
    if previous_sent_post == '0':
        params = {'limit': 1000}
    else:
        params = {'before': previous_sent_post}

    token = token
    headers = {'User-Agent': 'legodeals_scraper/0.1.0'}

    headers = {**headers, **{'Authorization': f"bearer {token}"}}

    # params = {'limit':1000}

    results = requests.get("https://oauth.reddit.com/r/hardwareswap/new/",
                       headers=headers,
                       params=params)

    return results


def match_criteria(row, criteria_list, payment_methods):
    title = row['title'].lower()
    match = 0

    h_loc = title.find('[h]')
    w_loc = title.find('[w]')

    h_str = title[h_loc:w_loc].lower()
    w_str = title[w_loc:].lower()

    for payment_method in payment_methods:
        if payment_method in w_str:
            for item in criteria_list:
                if item in h_str:
                    match = 1
                    break

    return match


def return_relevant_posts(criteria, payment_methods, posts):
    df = pd.DataFrame()

    for post in posts.json()['data']['children']:
        df = df.append({
            'subreddit': post['data']['subreddit'],
            'title': post['data']['title'],
            'selftext': post['data']['selftext'],
            'url': post['data']['url'],
            'name': post['data']['name']
        }, ignore_index=True)

    df['match'] = df.apply(lambda row: match_criteria(row, criteria, payment_methods), axis=1)

    df_match = df.loc[df['match'] == 1]
    df_match = df_match.reset_index()

    return df_match


def send_latest_posts(posts):
    if not posts.empty:
        for i in range(len(relevant_posts.index)):
            telegram_send.send(messages=[relevant_posts.iloc[i]['url']])

            time.sleep(1.0)


search_items = ['i5', 'rtx 3060', 'rtx 3080']
payment_methods = ['paypal']
last_post_name = '0'
i = 0

while i <= 144:

    i = i + 1

    relevant_posts = return_relevant_posts(search_items, payment_methods,
                                           get_posts(get_reddit_token(), last_post_name))

    if not relevant_posts.empty:
        last_post_name = relevant_posts.iloc[0]['name']

        send_latest_posts(relevant_posts)

    print(i)

    time.sleep(600.0)

