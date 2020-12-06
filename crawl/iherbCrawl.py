from selectorlib import Extractor
from urllib import parse
from urllib.parse import urlparse, parse_qsl
from util.excel import Excel
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

        self.IherbConfig = json.load(open(self.CONFIG_PATH, 'r', encoding='UTF-8'));
        self.extractorSearch = Extractor.from_yaml_file(self.SELECTOR_PATH['search'])
        self.extractorList = Extractor.from_yaml_file(self.SELECTOR_PATH['list'])
        self.extractorProduct = Extractor.from_yaml_file(self.SELECTOR_PATH['product'])
        forbiddenList = open("forbiddens.txt", 'r', encoding='UTF-8').readlines()
        forbiddenList = list(map(lambda s: s.strip(), forbiddenList))
        self.forbbiddenSet = set(forbiddenList)


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

        # print(res['productLinks'])

        for productLink in res['productLinks']:
            self.getProductInfo(productLink)
            # break


    def getProductInfo(self, link):
        time.sleep(0.5)
        html = self.requestHtml(link)
        res = self.extractorProduct.extract(html)
        print(res)
        self.writeRow(link, res)


    def writeRow(self, link, data):
        productUrl = link
        productId = data.get('productId', '')
        productName = data.get('productName', '')
        brandName = data.get('brandName', '')
        price = data.get('price', '')
        weight = data.get('weight', '')
        dimension = data.get('dimensions', '')
        actualWeight = data.get('actualWeight', '')
        dimWeight = data.get('dimensions', '') + "," + data.get('actualWeight', '') if type(dimension) is str and type(actualWeight) is str else ''
        marketCode = data.get('marketCode', '')
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

        ingredients = ','.join(ingredientList)
        # check forbidden
        forbiddenIngredientSet = self.forbbiddenSet & set(ingredientList)
        forbiddenIngredients = ','.join(forbiddenIngredientSet)

        self.excel.appendRow(
            [productUrl, productId, brandName, productName, price, weight, dimWeight, marketCode, upcCode, imgUrl1,
             imgUrl2, imgUrl3, imgUrl4, imgUrl5, forbiddenIngredients, ingredients])


    # product_data = []
    def exRun(self):
        with open("keyword.txt", 'r', encoding='UTF-8') as keywordList:
            now = datetime.datetime.now().strftime('%Y%m%d')
            excelDirPath = self.BASE_DIR + '/excel/iherb/' + now
            self.keywordList = list(map(lambda s: s.strip(), keywordList.readlines()))
            for keyword in self.keywordList:
                print(keyword)
                self.excel = Excel()
                self.excel.setSheetName(keyword)
                self.excel.appendRow(self.IherbConfig['excelColumn'])
                self.getProductList(keyword)
                self.excel.save(excelDirPath, keyword + '.xlsx')