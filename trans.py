import time
import redis
import threading

conn = redis.Redis()

def notrans():
    print(conn.incr('notrans:'))
    time.sleep(.1)
    conn.incr('notrans:', -1)


def trans():
    pipeline = conn.pipeline()
    pipeline.incr('trans:')
    time.sleep(.1)

    pipeline.incr('trans:', -1)
    print(pipeline.execute()[0])

if __name__ == '__main__':
    for i in range(3):
        threading.Thread(target=trans).start()
    time.sleep(.5)
