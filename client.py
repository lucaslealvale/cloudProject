import requests

url_get   = "http://loadbalancelucas1-321780380.us-east-1.elb.amazonaws.com/tasks/tarefas"
url_post  = "http://loadbalancelucas1-321780380.us-east-1.elb.amazonaws.com/tasks/post"

jsonPost = """{"title": "bbbbalvvvaaaaaaaaaaaaaaaaaaaaaaavvvvvoalo", "pub_date": "2020-11-20T18:14:49Z", "description": "bbbbccccccbbb"}"""

post = requests.post(url_post, data = jsonPost)
print(post.text)

get = requests.get(url_get)
print(get.text)

