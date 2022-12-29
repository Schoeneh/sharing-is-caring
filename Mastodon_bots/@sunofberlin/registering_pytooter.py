# https://github.com/halcy/Mastodon.py

from mastodon import Mastodon

# Register your app! This only needs to be done once (per server, or when
# distributing rather than hosting an application, most likely per device and server).
# Uncomment the code and substitute in your information:
'''
Mastodon.create_app(
    'pytooterapp',
    api_base_url = 'https://mastodon.social',
    to_file = 'pytooter_clientcred.secret'
)
'''

# Then, log in. This can be done every time your application starts (e.g. when writing a
# simple bot), or you can use the persisted information:
mastodon = Mastodon(client_id = 'pytooter_clientcred.secret',)
mastodon.log_in(
    'my_login_email@example.com',
    'incrediblygoodpassword',
    to_file = 'pytooter_usercred.secret'
)