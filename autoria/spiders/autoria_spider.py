# packages
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging 
import logging
import json
from datetime import datetime
import pytz 

from autoria.items import AutoriaItem

# spider class
class AutoriaScraper(scrapy.Spider):
    
    name = "autoria" 
    #configure scrapy logging
    # configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='logs/{}.log'.format(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%Y%m%d-%H%M%S")),
        format='%(levelname)s: %(message)s',
        level=logging.CRITICAL,
    )

    
    # truck brands to search 
    # brands =  {'Scania':'203','MAN': '177','DAF':'115','IVECO':'175','RENAULT':'62','VOLVO':'85','Mercedes':'48',}
    brands =  {'Scania':'203'}
    #filter for diesel engines
    diesel_filter = '&fuel.id[1]=2'
    
    #engine volume more than 10L 
    eng_volume_filter = '&engine.gte=10' 
    
    #Url for trucks
    core_url = 'https://auto.ria.com/uk/search/?indexName=auto&categories.main.id=6'
    
    # custom headers
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }
    

    # crawler's entry point
    def start_requests(self):

        # make HTTP request to brands URLs
        for v in self.brands.values():

            b_url = self.core_url + '&brand.id[0]='+ v

            #additional filters for brands with small trucks
            if v in ['175','62','48']:
                b_url += self.diesel_filter + self.eng_volume_filter
            
            yield scrapy.Request(
                url=b_url,  
                headers=self.headers,
                callback=self.parse_links,
                cb_kwargs=dict(base_url = b_url, cur_page = 0, total_pages = 1),
            )

    # parse product links
    def parse_links(self, response, base_url, cur_page, total_pages):
        # loop over product cards
        for card in response.css('div[class="item ticket-title"]'):
            # extract product URL
            product_url = card.css('a::attr(href)').get()
            # print(product_url)
            # make HTTP request to product link URL
            yield response.follow(
                url=product_url,
                headers=self.headers,
                callback=self.parse_product
            )
        
        if cur_page == 1:
            #Getting number of finded records and pagination pages
            x = response.css('script::text').re_first('resultsCountCommon = Number((.*));')
            total_pages = int(x[1:-1])//10+1
        
        # try to crawl next pages (infinite scroll)
        try:
            # increment current page counter
            
            cur_page += 1
            # generate next page URL
            next_page = base_url + '&page=' + str(cur_page)

            if cur_page <= total_pages:
                # print debug info
                # print('Crawling page %s' % self.current_page)

                # crawl next page
                yield response.follow(
                    url=next_page,
                    headers=self.headers,
                    callback=self.parse_links,
                    cb_kwargs=dict(base_url = base_url, cur_page = cur_page, total_pages = total_pages),
                )

        except Exception as e:
            print('\n\nERROR during crawling next page:', e)
        
        
    # parse product details
    def parse_product(self, response):


        # extract product details
        features = {
 
            'auto_id' : response.css('body::attr(data-auto-id)').get(), 

            'product_link': response.url,
            
            'product_name':'',

            # append brand
            'brand':'',

            # # append model
            'model':'',

            # append production year
            'production_date':'',

            #append type
            'mileage':'',
                        
            #append type
            'body_type':'',

            #append color
            'color':'',

            #append GearboxType
            'gearbox_type':'',

            #append Offer currency
            'price_currency':'',

            #append Offer Price
            'price':'',

            # append 'Description':
            'description':'',

        }

        try:
            
            # get currency exchange data
            exch_json =  json.loads(response.css('script::text').re_first(r'window.ria.exchangeRates = \s*(.*)')[:-2]) 
            for e in exch_json:
                if e['name'] == 'USD':
                    usd_exch_rate = e['ask']
                elif e['name'] == 'EUR':
                    eur_exch_rate = e['ask']  
                                
            
            # extract additional info
            json_data = json.loads([
                script.get()
                for script in
                response.css('script::text')
                if '@context' in script.get()
            ][0])


            #append name
            features['product_name'] = json_data.get('name','')

            # append brand
            features['brand'] = json_data.get("brand",{}).get("name",'')

            # # append model
            features['model'] = json_data.get("model",'')

            # append production year
            features['production_date'] = json_data.get("productionDate",'')

            #append type
            features['mileage'] = json_data.get("mileageFromOdometer",{}).get("value",'')
                        
            #append type
            features['body_type'] = json_data.get("bodyType",'')

            #append color
            features['color'] = json_data.get("color",'')

            #append GearboxType
            features['gearbox_type'] = json_data.get("vehicleTransmission",'')

            #append Offer currency
            features['price_currency'] = json_data.get("offers",{}).get("priceCurrency",'')

            #append Offer Price
            features['price'] = json_data.get("offers", {}).get("price",'')

            # # append 'Description':
            features['description'] = json_data.get("description",'')

            # append 'USD exchange rate':
            features['usd_exch_rate'] = usd_exch_rate or '0'

             # append 'EUR exchange rate':
            features['eur_exch_rate'] = eur_exch_rate or '0'

       
        except Exception as e:
            print('Additional date is not available!')

        yield features