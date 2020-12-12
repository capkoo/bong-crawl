import requests
import os


class ImageDownloader:
    def download(self, imageUrl, savePath, fileName):
        print(imageUrl)
        print(fileName)
        try:
            response = self.request(imageUrl)
            os.makedirs(savePath, exist_ok=True)
            file = open(savePath + '/' + fileName, 'wb')
            file.write(response.content)
            file.close()
        except Exception as exception:
            print(exception)
            return False

        return True

    def request(self, url):
        headers = {
            'authority': 'www.iherb.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'cookie': 'iher-pref1=storeid=0&sccode=US&lan=en-US&scurcode=USD&wp=1&lchg=1&ifv=1; ih-preference=store=0&country=US&language=en-US&currency=USD;'
        }

        r = requests.get(url, headers=headers)
        # Simple check to check if page was blocked (Usually 503)
        if r.status_code > 500:
            if "To discuss automated access to Amazon data please contact" in r.text:
                print("Page %s was blocked by Amazon. Please try using better proxies\n" % url)
            else:
                print("Page %s must have been blocked by Amazon as the status code was %d" % (url, r.status_code))
            return None

        return r;