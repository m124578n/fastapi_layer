
# note
在python3.12版本中，aioredis的TimeoutError有bug，需要修改把TimeoutError中繼承的asyncio刪除即可

- 8/8更新

    把aioredis換成redis-py



# dependency
- python 3.12
- fastapi
- bcrypt
- ~~aioredis~~
- redis-py
- motor
- jwt
- mongodb
- redis
- docker
- docker-compose