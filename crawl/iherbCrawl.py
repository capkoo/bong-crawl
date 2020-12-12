from selectorlib import Extractor
from urllib import parse
from urllib.parse import urlparse, parse_qsl
from util.excel import Excel
from util.image_downloader import ImageDownloader
import time
import requests
import json
import os
import datetime



class IherbCrawl:
    def __init__(self):
        self.TYPE = 'iherb'
        self.BASE_DIR = os.path.abspath('.');
        self.CONFIG_PATH = self.BASE_DIR + '/config/' + self.TYPE + '.json';
        self.SELECTOR_PATH = {
            "search": self.BASE_DIR + '/selector/' + self.TYPE + '/search.yml',
            "list": self.BASE_DIR + '/selector/' + self.TYPE + '/list.yml',
            "product": self.BASE_DIR + '/selector/' + self.TYPE + '/product.yml',
        };
        self.DATA_DIR_PATH = self.BASE_DIR + '/data/'+ self.TYPE +'/' + datetime.datetime.now().strftime('%Y%m%d')

        self.IherbConfig = json.load(open(self.CONFIG_PATH, 'r', encoding='UTF-8'));
        self.extractorSearch = Extractor.from_yaml_file(self.SELECTOR_PATH['search'])
        self.extractorList = Extractor.from_yaml_file(self.SELECTOR_PATH['list'])
        self.extractorProduct = Extractor.from_yaml_file(self.SELECTOR_PATH['product'])
        self.imageDownloader = ImageDownloader()
        forbiddenList = open("forbiddens.txt", 'r', encoding='UTF-8').readlines()
        forbiddenList = list(map(lambda s: s.strip(), forbiddenList))
        self.forbbiddenSet = set(forbiddenList)
        self.delay = 1


    def requestHtml(self, url):
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

        return r.text;


    def getProductList(self, keyword):
        searchUrl = (self.IherbConfig["searchUrl"]).replace('{keyword}', parse.quote(keyword))

        html = self.requestHtml(searchUrl);
        res = self.extractorSearch.extract(html)
        pagePaths = res.get('pagePaths', [])

        if type(pagePaths) is not list or len(pagePaths) <= 0:
            lastPageNo=2
        else:
            lastPath = pagePaths[-1]
            parsed = urlparse(lastPath)
            qs = dict(parse_qsl(parsed.query))
            lastPageNo = int(qs['p']) + 1

        for i in range(1, lastPageNo):
            print(str(i) + '페이지 조회')
            self.getProduct(keyword, i)
            # break


    def getProduct(self, keyword, pageNo):
        productListUrl = (self.IherbConfig["productListUrl"]).replace('{keyword}', keyword).replace('{pageNo}', str(pageNo))
        html = self.requestHtml(productListUrl)
        res = self.extractorList.extract(html)

        for productLink in res['productLinks']:
            self.getProductInfo(productLink)
            break


    def getProductInfo(self, link):
        self.productNumber += 1
        time.sleep(self.delay)
        html = self.requestHtml(link)
        res = self.extractorProduct.extract(html)
        print(res)
        self.writeRow(link, res)


    def writeRow(self, link, data):
        productUrl = link
        productId = self.productNumber
        productName = data.get('productName', '')
        brandName = data.get('brandName', '')
        price = data.get('price', '')
        weight = data.get('weight', '')
        dimension = data.get('dimensions', '')
        actualWeight = data.get('actualWeight', '')
        dimWeight = data.get('dimensions', '') + "," + data.get('actualWeight', '') if type(dimension) is str and type(actualWeight) is str else ''
        marketCode = data.get('productCode', '')
        upcCode = data.get('upc', '')
        images = data.get('images', [])
        images = images if type(images) is list else []
        images.reverse()
        imgUrl1 = images.pop() if len(images) > 0 else ''
        imgUrl2 = images.pop() if len(images) > 0 else ''
        imgUrl3 = images.pop() if len(images) > 0 else ''
        imgUrl4 = images.pop() if len(images) > 0 else ''
        imgUrl5 = images.pop() if len(images) > 0 else ''
        ingredients = data.get('ingredients', [])
        ingredients = ingredients if type(ingredients) is list else []

        ingredientList = []
        for ingredient in ingredients:
            ing = ingredient.get('i', '')
            if(type(ing) is str and len(ing) > 0):
                ingredientList.append(ing)

        ingredients = ', '.join(ingredientList)

        forbiddenIngredientList = []
        for ingredient in ingredientList:
            if self.is_forbbiden(ingredient):
                forbiddenIngredientList.append(ingredient)

        forbiddenIngredients = ', '.join(forbiddenIngredientList)

        self.excel.appendRow(
            [productUrl, productId, brandName, productName, price, weight, dimWeight, marketCode, upcCode, imgUrl1,
             imgUrl2, imgUrl3, imgUrl4, imgUrl5, forbiddenIngredients, ingredients])

        self.excel.save(self.keywordPath, self.keyword + '.xlsx')


    def is_forbbiden(self, ingredient):
        for forbbiedn in self.forbbiddenSet:
            if forbbiedn.lower() in ingredient.lower():
                return True

        return False


    # product_data = []
    def exRun(self):
        with open("keyword.txt", 'r', encoding='UTF-8') as keywordList:
            self.keywordList = list(map(lambda s: s.strip(), keywordList.readlines()))
            for keyword in self.keywordList:
                print(keyword)
                self.keyword = keyword
                self.productNumber = 0
                self.keywordPath = self.DATA_DIR_PATH + '/' + keyword
                self.imagePath = self.keywordPath + '/images'
                self.excel = Excel()
                self.excel.setSheetName(keyword)
                self.excel.appendRow(self.IherbConfig['excelColumn'])
                self.getProductList(keyword)
                self.excel.save(self.keywordPath, self.keyword + '.xlsx')