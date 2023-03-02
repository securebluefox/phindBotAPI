from fake_useragent import UserAgent
import requests, json

userAgent = UserAgent().chrome
# Please get key form serper.dev
serperDevKey = ""
searchResFrom = "Google"

# Google Search API From serper.dev
def getSearchResultFromGoogle(question):
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": question,
        "num": 30
    })
    headers = {
        'X-API-KEY': serperDevKey,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    searchRes = response.json()
    search_data = {
        "_type":"SearchResponse",
        "queryContext":{
            "originalQuery":searchRes['searchParameters']['q'],
        },
        "webPages":{
            "webSearchUrl":f"https://www.google.com/search?q={searchRes['searchParameters']['q']}",
            "totalEstimatedMatches":len(searchRes["organic"]),
            "value":[]
        }
    }
    for resPageIdx in range(len(searchRes["organic"])):
        temp = {
            "id":f"https://api.bing.microsoft.com/api/v7/#WebPages.{resPageIdx}",
            "name":searchRes["organic"][resPageIdx]["title"],
            "url":searchRes["organic"][resPageIdx]["link"],
            # "isFamilyFriendly":true,
            "displayUrl":searchRes["organic"][resPageIdx]["link"],
            "snippet":searchRes["organic"][resPageIdx]["snippet"],
            # "dateLastCrawled":"2023-02-26T01:29:00.0000000Z",
            "deepLinks":[],
            "language":"zh_chs",
            "isNavigational":False
        }
        if "sitelinks" in searchRes["organic"][resPageIdx].keys():
            for deepLink in searchRes["organic"][resPageIdx]["sitelinks"]:
                temp["deepLinks"].append(
                    {
                        "name":deepLink["title"],
                        "url":deepLink["link"]
                    }
                )
        search_data["webPages"]["value"].append(temp)
    return search_data

def getSearchResultFromPhind(session,question):
    search_api = "https://phind.com/api/search"
    search_data = {
        "freshness":"",
        "q":question,
        "userRankList":{
            "developer.mozilla.org":1,
            "github.com":1,
            "stackoverflow.com":1,
            "www.reddit.com":1,
            "en.wikipedia.org":1,
            "www.amazon.com":-1,
            "www.quora.com":-2,
            "www.pinterest.com":-3,
            "rust-lang":2,
            ".rs":1
        }
    }
    search_api_res = session.post(search_api,json=search_data,headers={'User-Agent':userAgent})
    return search_api_res.json()["processedBingResults"]

if __name__ == '__main__':
    question = "如何使用Python解决01背包问题？"
    
    index_url = "https://phind.com/search"
    api_url = "https://phind.com/api/tldr"
    session = requests.session()
    session.get(index_url,headers={'User-Agent':userAgent})
    api_data = {
        "bingResults" : None,
        "question" : question
    }
    if searchResFrom == "Google":
        api_data["bingResults"] = getSearchResultFromGoogle(question)
    elif searchResFrom == "Phind":
        api_data["bingResults"] = getSearchResultFromPhind(session,question)
    else:
        print("请选定至少一个搜索引擎！")
        exit(-1)

    final_res = session.post(api_url,json=api_data,headers={'User-Agent':userAgent})
    answerText = ""
    answerList = final_res.text.split("data: ")
    for answer in answerList:
        if '{' not in answer or '}' not in answer:
            continue
        else:
            answer = json.loads(answer.strip('\n').strip('\r').strip('\n'))
            if "sentence" in answer.keys():
                answerText += answer["sentence"]
    print(answerText)
