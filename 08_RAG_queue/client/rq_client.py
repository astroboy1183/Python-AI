import redis
from rq import Queue
from rq.job import Job

r = redis.Redis(host="localhost", port=6379)

q = Queue(connection=r)



