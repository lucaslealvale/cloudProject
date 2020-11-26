import requests
import time

url_get  = 'http://loadbalancelucas1-115339538.us-east-1.elb.amazonaws.com/tasks/tarefas'
url_post = 'http://loadbalancelucas1-115339538.us-east-1.elb.amazonaws.com/tasks/post'

def post(url, json):
    post = requests.post(url, data = json)
    return post
def get(url):
    get = requests.get(url_get)
    return get


while(1):
    print(" ")
    print("Post --> 1 ")
    print("Get  --> 2  ")
    print("Sair --> 3  ")
    print(" ")

    x = input("O que deseja fazer: ")
    if x == "1":
        print("""o post deve ser algo no formato: {"title": "task example", "pub_date": "2020-11-20T18:14:49Z", "description": "task example number 1"}""")
        
        postUser = input("Insira o Post: ")
        b = post(url_post,postUser)

    elif x == "2":
        a = get(url_get)
        print(a.text)
        time.sleep(2)
    
    elif x == "3":
        print(" ")
        print("Client encerrado")
        break
    
    else:
        print(" ")
        print("entrada invalida")
