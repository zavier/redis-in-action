import redis
import time

QUIT = False
LIMIT = 10

def add_to_cart(conn, session, item, count):
    if count <= 0:
        conn.hrem('cart:' + session, item)
    else:
        conn.hset('cart:' + session, item, count)

def clean_full_sessions(conn):
    while not QUIT:
        size = conn.zcard('recent:')
        if size <= LIMIT:
            time.sleep(1)
            continue
        end_index = min(size - LIMIT, 1)
        sessions = conn.zrange('recent:', 0, end_index - 1)

        sessions_keys = []
        for sess in sessions:
            sessions_keys.append('viewed:' + sess)
            sessions_keys.append('cart:' + sess)
        
        conn.delete(*sessions_keys)
        conn.hdel('login:', *sessions)
        conn.zrem('recent:', *sessions)