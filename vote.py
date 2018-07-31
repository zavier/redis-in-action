import time
import redis

ONE_WEEK_IN_SECONDS = 7 * 24 * 60 * 60
# 一票得分
VOTE_SCORE = 432
# 每页展示文章数
ARTICLES_PER_PAGE = 25

# 对文章进行投票
def article_vote(conn, user, article):
    cutoff = time.time() - ONE_WEEK_IN_SECONDS
    if conn.zscore('time:', article) < cutoff:
        return
    article_id = article.partition(':')[-1]
    if conn.sadd('voted:' + article_id, user):
        conn.zincrby('score:', article, VOTE_SCORE)
        conn.hincrby(article, 'votes', 1)


# 发布文章
def post_article(conn, user, title, link):
    article_id = str(conn.incr('article:'))

    voted = 'voted:' + article_id
    conn.sadd(voted, user)
    conn.expire(voted, ONE_WEEK_IN_SECONDS)

    now = time.time()
    article = 'article:' + article_id
    conn.hmset(article, {
        'title': title,
        'link': link,
        'poster': user,
        'time': now,
        'votes': 1,
    })
    conn.zadd('score:', article, now + VOTE_SCORE)
    conn.zadd('time:', article, now)
    return article_id

# 获取文章
def get_articles(conn, page, order='score:'):
    start = (page - 1) * ARTICLES_PER_PAGE
    end = start + ARTICLES_PER_PAGE - 1

    ids = conn.zrevrange(order, start, end)
    articles = []
    for id in ids:
        article_data = conn.hgetall(id)
        article_data['id'] = id
        articles.append(article_data)
    return articles

# 对文章进行分组，将文章添加到分组、从分组中删除
def add_remove_groups(conn, article_id, to_add=[], to_remote=[]):
    article = 'article:' + article_id
    for group in to_add:
        conn.sadd('group:' + group, article)
    for group in to_remote:
        conn.srem('group:' + group, article)



# 对分组进行排序
def get_group_articles(conn, group, page, order='score:'):
    key = order + group
    if not conn.exists(key):
        conn.zinterstore(key,
            ['group:' + group, order],
            aggregate='max')
        conn.expire(key, 60)
    return get_articles(conn, page, key)


if __name__ == '__main__':
    conn = redis.Redis()
    # post_article(conn, 'zhang', 'redis-in-action-1', 'http://github.com/zavier-1')
    # article_vote(conn, 'zheng', 'article:2')
    #res = get_articles(conn, 1)
    # print(res)
    # add_remove_groups(conn, '2', ['redis'])
    res = get_group_articles(conn, 'redis', 1)
    print(res)