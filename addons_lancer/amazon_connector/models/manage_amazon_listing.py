# -*- coding: utf-8 -*-
import time
import os
import logging
logger = logging.getLogger('amazonerp_osv')

from odoo.addons.amazon_connector.amazon_api import amazonerp_osv as amazon_api_obj
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError

class  UploadAmazonProducts(models.Model):
    _name = "upload.amazon.products"
    
    def sched_upload_inventory(self):
        product_obj = self.env['product.product']
        
        product_ids = product_obj.search()
        for product in product_ids:
                for amazon_prod in product.amazon_prodlisting_ids:
                    #Form Parent XML
                    xml_data=""
                    message_count = 1
                    
                    if not product.asin:
                        logger.info('  NO ASIN FOR SKU: %s',product.default_code)
                        continue
                    
                    if not product.default_code:
                        raise UserError(_('Please enter Product SKU for Image Feed "%s"'% (product.name)))
    
                    if product.qty_available !=0:
                        inventory = int(product.qty_available + product.outgoing_qty)
                        
                    else:
                        raise UserError(_('Inventory is less than 0'))
                    
                    lead_time = int(product.sale_delay)
                    if inventory < 1:
                        inventory = 0
                    if lead_time <= 0:
                        lead_time = 1
                        
                    merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(amazon_prod.shop_id.amazon_instance_id.aws_merchant_id)
                    message_type = '<MessageType>Inventory</MessageType>'
                    
                    if product.fulfillment_by != 'AFN':
                        update_xml_data = '''<SKU>%s</SKU>
                                            <Quantity>%s</Quantity><FulfillmentLatency>%s</FulfillmentLatency>'''%(amazon_prod.default_code, inventory, lead_time)
                        
                        xml_data += '''<Message>
                                    <MessageID>%s</MessageID><OperationType>Update</OperationType>
                                    <Inventory>%s</Inventory></Message>
                                '''% (message_count,update_xml_data)
                       
                        #Uploading Product Inventory Feed
                        message_count+=1
                        list_str = """
                                <?xml version="1.0" encoding="utf-8"?>
                                <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
                                <Header>
                                <DocumentVersion>1.01</DocumentVersion>
                                """+merchant_string+"""
                                </Header>
                                """+message_type + xml_data+"""
                                """
                        list_str +="""</AmazonEnvelope>"""
                        
                        product_submission_id = amazon_api_obj.call(amazon_prod.shop_id,'POST_INVENTORY_AVAILABILITY_DATA', list_str)
                        logger.info(' INVENTORY SUBMISSION ID: %s', product_submission_id)

                        if product_submission_id.get('FeedSubmissionId',False):
                            time.sleep(20)
                            submission_results = amazon_api_obj.call(amazon_prod.shop_id, 'GetFeedSubmissionResult',product_submission_id.get('FeedSubmissionId',False))
                            logger.info(' INVENTORY FEED SUBMISSION ID: %s', submission_results)
        return True 
             
    def upload_amazon_products(self, product_ids):
        sale_shop_obj = self.env['sale.shop']
        category_obj = self.env['product.category']
        
        #get shop information
        amazon_shop_ids = sale_shop_obj.search([])
        if amazon_shop_ids and amazon_shop_ids[0].amazon_instance_id:
            instance = amazon_shop_ids[0].amazon_instance_id
        else:
            raise UserError(_('Please select Amazon Instance and try again.'))
        
        res_company_ids = amazon_shop_ids[0].partner_id.name
        if res_company_ids:
            currency = res_company_ids[0].currency_id.name
            
        #set merchent xml
        merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(amazon_shop_ids[0].amazon_instance_id)
        
        release_date = datetime.datetime.now()
        release_date = release_date.strftime("%Y-%m-%dT%H:%M:%S")
        date_string = """<LaunchDate>%s</LaunchDate>
                             <ReleaseDate>%s</ReleaseDate>"""%(release_date,release_date)
        
        message_information = ''
        desc = ''
        message_id = 1
        for main_product in product_ids:
            for product in main_product.prod_listing_ids:
                item_type = product.product_id.product_type_name
                product_sku = product.product_id.default_code

                if product.is_new_listing:
                    if product.product_id.ean13:
                        standard_product_string = """
                        <StandardProductID>
                        <Type>EAN</Type>
                        <Value>%s</Value>
                        </StandardProductID>
                        """%(product.product_id.ean13)
                    else:
                        if not product.product_id.upc:
                            raise UserError(_('UPC Required!!'))

                        standard_product_string = """
                        <StandardProductID>
                        <Type>UPC</Type>
                        <Value>%s</Value>
                        </StandardProductID>
                        """%(product.product_id.upc)
                else:
                    if not product.product_id.asin:
                        raise UserError(_('ASIN Required!!'))

                    standard_product_string = """
                    <StandardProductID>
                    <Type>ASIN</Type>
                    <Value>%s</Value>
                    </StandardProductID>
                    """%(product.product_id.asin)
                
                platinum_keywords = ''
                if product.product_id.platinum_keywords:
                    platinum_keyword_list = product.product_id.platinum_keywords.split('|')
                    for keyword in platinum_keyword_list:
                        platinum_keywords += '<PlatinumKeywords><%s></PlatinumKeywords>'%(keyword)
                if platinum_keywords == '':
                    platinum_keywords = '<PlatinumKeywords>No Keywords</PlatinumKeywords>' 

                if product.product_id.amazon_categ_id:
                    categ_ids = category_obj.search([('id','=',product.product_id.amazon_categ_id.id)]) 
                    if categ_ids:
                        search_term = categ_ids[0].name       
                    else:
                        search_term = product.product_id.name
                       
                if product.product_id.feature:
                    bullet_points ="""<BulletPoint><![CDATA[%s]]></BulletPoint>""" %product.product_id.feature
                else:
                    bullet_points = '<BulletPoint>No Bullet points</BulletPoint>'                        
                     
                style_keywords = ''
                if product.product_id.style_keywords:
                    style_keyword_list = product.product_id.style_keywords.split('|')
                    for keyword_style in style_keyword_list:
                            style_keywords += '<StyleKeywords>%s</StyleKeywords>'%(keyword_style)
                if style_keywords == '':
                    style_keywords = '<StyleKeywords>No Keywords</StyleKeywords>'
                if not product.product_id.package_quantity:
                    raise UserError(_('Please Enter Package Qunatity Of Product'))
                else:
                    package_quantity=product.product_id.package_quantity
                if not product.product_id.item_dimension_weight:
                    raise UserError(_('Please Enter No Of Items'))
                else:
                    item_quantity=product.product_id.item_dimension_weight
                
                message_information += """<Message><MessageID>%s</MessageID>
                                            <OperationType>Update</OperationType>
                                            <Product>
                                            <SKU>%s</SKU>%s
                                            <ProductTaxCode>A_GEN_NOTAX</ProductTaxCode>
                                            %s
                                            <ItemPackageQuantity>%d</ItemPackageQuantity>
                                            <NumberOfItems>%d</NumberOfItems>
                                            <DescriptionData>
                                            <Title>%s</Title>"""%(message_id,product_sku,standard_product_string,date_string,
                                                                  package_quantity,item_quantity,main_product.name)
                                            
                
                if not product.product_id.brand:
                    raise UserError(_('Plz Enter Brand!!'))
                message_information += """<Brand>
                %s
                </Brand>"""%(product.product_id.brand)
                message_information += desc
                message_information += bullet_points
                message_information +="""<MSRP currency="%s">%s</MSRP>"""%(currency,product.product_id.list_price)
                message_information +="""<Manufacturer>%s</Manufacturer>"""%(product.product_id.manufacturer)
                message_information += search_term
                #message_information += platinum_keywords
               
                
                if not product.product_id.manufacturer:
                    raise UserError(_('Plz Enter manufacturer!!'))

                xml_product_type =''
                if main_product.product_data == 'CE':
                    xml_product_type = self.ce_xml(main_product)
                elif main_product.product_data == 'Computers':
                    xml_product_type += self.com_xml(main_product)
                elif main_product.product_data == 'AutoAccessory':
                    xml_product_type += self.Auto_xml(main_product)
                elif main_product.product_data == 'ToysBaby':
                    xml_product_type += self.ToysBaby_xml(main_product)
                elif main_product.product_data == 'Beauty':
                    xml_product_type += self.Beauty_xml(main_product)
                elif main_product.product_data == 'CameraPhoto':
                    xml_product_type += self.CameraPhoto_xml(main_product)
                elif main_product.product_data == 'Wireless':
                    xml_product_type += self.WirelessAccessories_xml(main_product)
                elif main_product.product_data == 'ClothingAccessories':
                    xml_product_type +=self.ClothingAccessories_xml(main_product)
                    #xml_product_type += products.product_data
                elif main_product.product_data == 'GiftCard':
                    xml_product_type += self.GiftCard_xml(main_product)
                elif main_product.product_data == 'FoodAndBeverages':
                    xml_product_type += self.FoodAndBeverages_xml(main_product)
                elif main_product.product_data == 'Health':
                    xml_product_type += self.Health_xml(main_product)
                elif main_product.product_data == 'Home':
                    xml_product_type += self.Home_xml(main_product)
                elif main_product.product_data == 'Jewelry':
                    xml_product_type += self.Jewelry_xml(main_product)
                elif main_product.product_data == 'Miscellaneous':
                    xml_product_type += self.Miscellaneous_xml(main_product)
                elif main_product.product_data == 'MusicalInstruments':
                    xml_product_type += self.MusicalInstruments_xml(main_product)
                elif main_product.product_data == 'Music':
                    xml_product_type += self.music_xml(main_product)
                elif main_product.product_data == 'Office':
                    xml_product_type += self.office_xml(main_product)
                elif main_product.product_data == 'PetSupplies':
                    xml_product_type += self.PetSupplies_xml(main_product)
                elif main_product.product_data == 'Shoes':
                    xml_product_type += self.Shoes_xml(main_product)
                elif main_product.product_data == 'SWVG':
                    xml_product_type += self.SoftwareVideoGames_xml(main_product)
                elif main_product.product_data == 'Sports':
                    xml_product_type += self.Sport_xml(main_product)
                elif main_product.product_data == 'SportsMemorabilia':
                    xml_product_type += self.sportsmemorabilia_xml(main_product)
                elif main_product.product_data == 'TiresAndWheels':
                    xml_product_type += self.tiresandwheels_xml(main_product)
                elif main_product.product_data == 'Tools':
                    xml_product_type += self.Tools_xml(main_product)
                elif main_product.product_data == 'Toys':
                    xml_product_type += self.toys_xml(main_product)
                elif main_product.product_data == 'Video':
                    xml_product_type += self.Video_xml(main_product)
                elif main_product.product_data == 'Lighting':
                    xml_product_type += self.Lighting_xml(main_product)

                message_information +=""" <ItemType>%s</ItemType>
                                            </DescriptionData>
                                            <ProductData>
                                           <%s>
                                           <ProductType>
                                            %s
                                           </ProductType>
                                          </%s></ProductData>"""%(item_type, main_product.product_data, xml_product_type, main_product.product_data)
                message_information += """</Product>
                                            </Message>"""
                message_id = message_id + 1
                product_str = """<MessageType>Product</MessageType>
                                <PurgeAndReplace>false</PurgeAndReplace>"""
            product_data = sale_shop_obj.xml_format(product_str, merchant_string, message_information)
            if product_data:
                product_submission_id = amazon_api_obj.call(instance, 'POST_PRODUCT_DATA',product_data)
                if product_submission_id.get('FeedSubmissionId',False):
                    time.sleep(500)
                    submission_results = amazon_api_obj.call(instance, 'GetFeedSubmissionResult',product_submission_id.get('FeedSubmissionId',False))
                    self.write({'feed_result':submission_results})
                    updated = product_ids.write({'updated_data':True})
                    self.env.cr.commit()
                            
        return True   

    def Lighting_xml(self, self_data):
        if not self_data.product_type_light:
            raise UserError(_('Plz select Product Type!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_light,self_data.product_type_light)
        return xml_ce

    def Tools_xml(self, self_data):
        if not self_data.product_type_tools:
            raise UserError(_('Plz select Product Type!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_tools,self_data.product_type_tools)
        return xml_ce

    def Video_xml(self, self_data):
        if not self_data.product_type_Video:
            raise UserError(_('Plz select Product Type!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_Video,self_data.product_type_Video)
        return xml_ce

    def MusicalInstruments_xml(self, self_data):
        if not self_data.product_type_musicalinstruments:
            raise UserError(_('Plz select Product Type!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_musicalinstruments,self_data.product_type_musicalinstruments)
        return xml_ce

    def PetSupplies_xml(self, self_data):
        if not self_data.product_type_petsupplies:
            raise UserError(_('Plz select Product Type!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_petsupplies,self_data.product_type_petsupplies)
        return xml_ce

    def Home_xml(self, self_data):
        if not self_data.product_type_home:
            raise UserError(_('Plz select Product Type!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_home,self_data.product_type_home)
        return xml_ce

    def music_xml(self, self_data):
        if not self_data.product_type_music:
            raise UserError(_('Plz select Product Type!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_music,self_data.product_type_music)
        return xml_ce

    def Miscellaneous_xml(self,cr,uid,ids,self_data):
        if not self_data.product_type_miscellaneous:
            raise UserError(_('Plz select Product Type!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_miscellaneous,self_data.product_type_miscellaneous)
        return xml_ce

    def ce_xml(self, self_data):
        if not self_data.product_type_ce:
            raise UserError(_('Plz select CE Product Type!!'))
        xml_ce = '''<%s>
                        <PowerSource>AC</PowerSource>
                   </%s>'''%(self_data.product_type_ce,self_data.product_type_ce)
        return xml_ce


    def Jewelry_xml(self, self_data):
        if not self_data.product_type_jewelry:
            raise UserError(_('Plz select Product Type!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_jewelry,self_data.product_type_jewelry)
        return xml_ce

    def GiftCard_xml(self, self_data):
        if not self_data.product_type_giftcard:
            raise UserError(_('Plz select Product Type!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_giftcard,self_data.product_type_giftcard)
        return xml_ce

    def Health_xml(self, self_data):
        if not self_data.product_type_health:
            raise UserError(_('Plz select Product Type!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_health,self_data.product_type_health)
        return xml_ce

    def Shoes_xml(self, self_data):
        if not self_data.product_type_shoes:
            raise UserError(_('Plz select Product Type!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_shoes,self_data.product_type_shoes)
        return xml_ce

    def Auto_xml(self, self_data):
        if not self_data.product_type_auto_accessory:
            raise UserError(_('Plz select AutoAccessory Product Type!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_auto_accessory,self_data.product_type_auto_accessory)
        return xml_ce

    def ToysBaby_xml(self, self_data):
        if not self_data.product_type_toys_baby:
            raise UserError(_('Plz select Product Type!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_toys_baby,self_data.product_type_toys_baby)
        return xml_ce

    def Beauty_xml(self, self_data):
        if not self_data.product_type_beauty:
            raise UserError(_('Plz select Product Type!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_beauty,self_data.product_type_beauty)
        return xml_ce

    def CameraPhoto_xml(self, self_data):
        if not self_data.product_type_cameraphoto:
            raise UserError(_('Plz select Product Type!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_cameraphoto,self_data.product_type_cameraphoto)
        return xml_ce

    def WirelessAccessories_xml(self, self_data):
        if not self_data.product_type_wirelessaccessories:
            raise UserError(_('Plz select Product Type!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_wirelessaccessories,self_data.product_type_wirelessaccessories)
        return xml_ce

    def FoodAndBeverages_xml(self, self_data):
        if not self_data.product_type_foodandbeverages:
            raise UserError(_('Plz select Product Type!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_foodandbeverages,self_data.product_type_foodandbeverages)
        return xml_ce

    def office_xml(self, self_data):
        if not self_data.product_type_office:
            raise UserError(_('Plz select Product Type!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_office,self_data.product_type_office)
        return xml_ce

    def com_xml(self, self_data):
        if not self_data.product_type_com:
            raise UserError(_('Plz select Value!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_com,self_data.product_type_com)
        return xml_ce

    def SoftwareVideoGames_xml(self, self_data):
        if not self_data.product_type_softwarevideoGames:
            raise UserError(_('Plz select Value!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_softwarevideoGames,self_data.product_type_softwarevideoGames)
        return xml_ce

    def Sport_xml(self, self_data):
        if not self_data.product_type_sports:
            raise UserError(_('Plz select Value!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_sports,self_data.product_type_sports)
        return xml_ce

    def sportsmemorabilia_xml(self, self_data):
        if not self_data.product_type_sportsmemorabilia:
            raise UserError(_('Plz select Value!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_sportsmemorabilia,self_data.product_type_sportsmemorabilia)
        return xml_ce

    def tiresandwheels_xml(self, self_data):
        if not self_data.product_type_tiresandwheels:
            raise UserError(_('Plz select Value!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_tiresandwheels,self_data.product_type_tiresandwheels)
        return xml_ce

    def toys_xml(self, self_data):
        if not self_data.product_type_toys:
            raise UserError(_('Plz select Value!!'))
        xml_ce = '''<%s>
                   </%s>'''%(self_data.product_type_toys,self_data.product_type_toys)
        return xml_ce

    def import_image(self, product_ids):
        sale_shop_obj = self.env['sale.shop']
        
        message_count=1
        shop_ids = sale_shop_obj.search([('amazon_shop','=',True)])
        if not shop_ids:
            return False
        
        instance_obj = shop_ids.amazon_instance_id
        xml_information=''
        xml_information+="""<?xml version="1.0" encoding="utf-8"?>
                        <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
                        <Header>
                            <DocumentVersion>1.01</DocumentVersion>
                            <MerchantIdentifier>%s</MerchantIdentifier>
                        </Header>
                    <MessageType>ProductImage</MessageType>
                    """%(instance_obj.aws_merchant_id)
        for product in product_ids:
                image_location=''
                for each_product in product.prod_listing_ids:
                    product_data = each_product.product_id
                    if not each_product.product_id.name:
                        raise UserError(_('Please enter Product SKU for Image Feed "%s"'% (product_data.name)))
                    
                    for imagedata in product_data.image_ids:
                        if not image_location:
                            raise UserError(_('Image location not found for this product"%s"'% (product_data.name)))
                        xml_information += """<Message>
                                                <MessageID>%s</MessageID>
                                                <OperationType>Update</OperationType>
                                                    <ProductImage>
                                                        <SKU>%s</SKU>
                                                        <ImageType>Main</ImageType>
                                                        <ImageLocation>%s</ImageLocation>
                                                        </ProductImage></Message>
                                                 """ % (message_count, each_product.product_id.default_code, imagedata.url)
                        message_count += 1
                        
                xml_information +="""</AmazonEnvelope>"""
                product_submission_id = amazon_api_obj.call(shop_ids, 'POST_PRODUCT_IMAGE_DATA',xml_information)
                if product_submission_id.get('FeedSubmissionId',False):
                    time.sleep(80)
                    amazon_api_obj.call(instance_obj, 'GetFeedSubmissionResult',product_submission_id.get('FeedSubmissionId',False))
                    product.write({'feed_result': product_submission_id.get('FeedSubmissionId')})
                    return True



    def upload_inventory(self, product_ids):
        sale_shop_obj = self.env['sale.shop']
        #Form Parent XML
        xml_data=""
        shop_ids = sale_shop_obj.search([('amazon_shop','=',True)])
        if not shop_ids:
            return False
        message_count = 1
        #Get all the Child
        merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(shop_ids[0].amazon_instance_id.aws_merchant_id)
        message_type = '<MessageType>Inventory</MessageType>'
        for product in product_ids:
            for each_product in product.prod_listing_ids:
                product_data = each_product.product_id
                if not each_product.product_id.asin:
                    logger.info('  NO ASIN FOR SKU: %s',each_product.product_id.default_code)
                    continue
                
                if not each_product.product_id.default_code:
                    raise UserError(_('Please enter Product SKU for Image Feed "%s"'% (product_data.name)))

                logger.info('  OUTGOING: %s',product_data.outgoing_qty)
                if product_data.qty_override != 0 and product_data.qty_override != False:
                    inventory = int(product_data.qty_override)
                else:
                    inventory = int(product_data.qty_available)
                     
                lead_time = int(product_data.sale_delay)
                if inventory < 1:
                    inventory = 0
                if lead_time <= 0:
                    lead_time = 1
                
                ### REMOVE ANY ITEM WITH ERROR FROM INVENTORY
#                 if  product_data.amazon_has_error == True:
#                     inventory = 0
#                       
                logger.info('Product ID: %s   SKU: %s    STOCK:  %s    LEAD TIME:  %s',each_product.product_id.id, each_product.product_id.default_code, inventory,lead_time)
                
                if each_product.fulfillment_by != 'AFN':
                    update_xml_data = '''<SKU>%s</SKU>
                                        <Quantity>%s</Quantity><FulfillmentLatency>%s</FulfillmentLatency>'''%(each_product.product_id.default_code, inventory,lead_time)
                else:
                    update_xml_data = '''<SKU>%s</SKU>
                                        <FulfillmentCenterID>AMAZON_NA</FulfillmentCenterID>
                                        <Lookup>FulfillmentNetwork</Lookup>
                                        <SwitchFulfillmentTo>AFN</SwitchFulfillmentTo>'''%(each_product.product_id.default_code)
                xml_data += '''<Message>
                            <MessageID>%s</MessageID><OperationType>Update</OperationType>
                            <Inventory>%s</Inventory></Message>
                        '''% (message_count,update_xml_data)
               
        #Uploading Product Inventory Feed
                message_count+=1
        
        
        main_val = """
                <?xml version="1.0" encoding="utf-8"?>
                <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
                <Header>
                <DocumentVersion>1.01</DocumentVersion>
                """+merchant_string+"""
                </Header>
                """+message_type+xml_data+"""
                """
        main_val += """</AmazonEnvelope>"""
        
        
        product_submission_id = amazon_api_obj.call(shop_ids[0], 'POST_INVENTORY_AVAILABILITY_DATA', main_val)
        logger.info(' INVENTORY SUBMISSION ID: %s                       ', product_submission_id)
        product.write({'last_inventory_feed': product_submission_id.get('FeedSubmissionId')})
        return True


    def upload_pricing(self, product_ids):
        sale_shop_obj = self.env['sale.shop']
        company_obj = self.env['res.company']
        
        shop_ids = sale_shop_obj.search([('amazon_shop','=',True)])
        if not shop_ids:
            return False
        message_count = 1
        merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(shop_ids[0].amazon_instance_id.aws_merchant_id)
        message_type = '<MessageType>Price</MessageType>'

        res_company_ids = company_obj.search([('name','=','Stockton International')])
        if res_company_ids:
            currency = res_company_ids[0].currency_id.name

        start_date = datetime.datetime.now()
        start_date = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        parent_xml_data = ''
        for product in product_ids:
            for each_product in product.prod_listing_ids:
                product_data = each_product.product_id.id
                
                if not each_product.product_id.asin:
                    logger.info('NO ASIN FOR SKU: %s ', each_product.product_id.default_code)
                    continue
                
                if not each_product.product_id.name:
                    each_product.product_id.write({'asin': False})
                    continue

                if 0 < each_product.product_id.amazon_price_new:
                    each_product.product_id.write({'price_amazon_current': float(product_data.amazon_price_new), 'amazon_price_new': False})

                if each_product.cost_final < 0.01:
                    continue

                parent_xml_data += '''<Message><MessageID>%s</MessageID>
                                    <Price>
                                    <SKU>%s</SKU>
                                    <StandardPrice currency="%s">%s</StandardPrice>''' % (
                message_count, each_product.product_id.default_code, currency, each_product.product_id.price_amazon_current)
                
                
                #CLOSE THE ENTRY FOR THIS ITEM    
                parent_xml_data += '''</Price></Message>'''
                message_count = message_count + 1

        str += """
                <?xml version="1.0" encoding="utf-8"?>
                <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
                <Header>
                <DocumentVersion>1.01</DocumentVersion>
                """+merchant_string+"""
                </Header>
                """+message_type + parent_xml_data+"""
                """
        str += """</AmazonEnvelope>"""

        os.chdir("/tmp")
        text_file = open("xml_price.txt", "w")
        text_file.write(str)
        text_file.close()

        product_submission_id = amazon_api_obj.call(shop_ids[0], 'POST_PRODUCT_PRICING_DATA', str)
        feed_sub_id = product_submission_id.get('FeedSubmissionId',False)
        if feed_sub_id:
            logger.info('PRICE FEED SUBMISSION ID: %s',feed_sub_id)
            self.write({'last_price_feed': feed_sub_id, 'last_repriced': datetime.datetime.now()})
            time.sleep(10)
            submission_results = amazon_api_obj.call(shop_ids[0], 'GetFeedSubmissionResult',product_submission_id.get('FeedSubmissionId',False))
            logger.info('Submission_results: %s',submission_results)
            return True
        return False
    
    def upload_shipping(self, product_ids):
        #Form Parent XML_ids
        logger.info('UPDATING SHIPPING --')
        
        sale_shop_obj = self.env['sale.shop']
        shop_ids = sale_shop_obj.search([('amazon_shop','=',True)])
        if not shop_ids:
            return False
        xml_data=''
        message = ''
        main_xml = """<?xml version="1.0" encoding="utf-8"?>
                            <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
                            <Header>
                            <DocumentVersion>1.02</DocumentVersion>
                            <MerchantIdentifier>%s</MerchantIdentifier>
                            </Header>
                            <MessageType>Override</MessageType>"""%(shop_ids[0].amazon_instance_id.aws_merchant_id)
        message_count = 1
        for product in product_ids:
            for each_product in product.prod_listing_ids:
                product_data = each_product.product_id
                shipping_price = product_data.shipping_override
                logger.info('    SHIPPING SKU: %s',product_data.default_code)
                logger.info('    SHIPPING PRICE: %s',shipping_price)
                
                if shipping_price > 0 or product_data.list_price < 20.00 :
                    xml_data += '''<Message>
                        <MessageID>%s</MessageID><OperationType>Update</OperationType>
                        <Override>
                            <SKU>%s</SKU>
                            <ShippingOverride>
                                <ShipOption>Std Cont US Street Addr</ShipOption>
                                <Type>Exclusive</Type>
                                <ShipAmount currency="USD">%s</ShipAmount>
                            </ShippingOverride>
                        </Override></Message>'''%(message_count,product_data.default_code,shipping_price)
                    message_count+=1

        #Uploading Product Inventory Feed
        message += main_xml + xml_data + """</AmazonEnvelope>"""

        product_submission_id = amazon_api_obj.call(shop_ids[0], 'POST_PRODUCT_OVERRIDES_DATA_',message)
        if product_submission_id != None and product_submission_id.get('FeedSubmissionId',False):
            logger.info('    SHIPPING FEED SUBMISSION ID: %s',product_submission_id.get('FeedSubmissionId',False))
            time.sleep(80)
            submission_results = amazon_api_obj.call(shop_ids[0], 'GetFeedSubmissionResult',product_submission_id.get('FeedSubmissionId',False))
            logger.info('SHIPPING FEED SUBMISSION Result ID: %s'%(submission_results,))
        else:
            logger.info(message)
        return False


    name = fields.Char('Name',size=64,required=True)
    last_inventory_feed = fields.Char('Last Inventory Feed', size=64, )
    last_price_feed = fields.Text('Last Pricing Feed')
    last_repriced = fields.Datetime('Last Time Priced')
    reprice_min = fields.Integer('Repricing Period (Minutes)')
    product_data = fields.Selection([
                                ('ClothingAccessories', 'ClothingAccessories'),
                                ('ProductClothing', 'ProductClothing'),
                                ('Miscellaneous', 'Miscellaneous'),
                                ('CameraPhoto', 'CameraPhoto'),
                                ('Home', 'Home'),
                                ('Sports', 'Sports'),
                                ('SportsMemorabilia', 'SportsMemorabilia'),
                                ('EntertainmentCollectibles', 'EntertainmentCollectibles'),
                                ('HomeImprovement', 'HomeImprovement'),
                                ('Tools', 'Tools'),
                                ('FoodAndBeverages', 'FoodAndBeverages'),
                                ('Gourmet', 'Gourmet'),
                                ('Jewelry', 'Jewelry'),
                                ('Health', 'Health'),
                                ('CE','CE'),
                                ('Computers', 'Computers'),
                                ('SWVG', 'SWVG'),
                                ('Wireless', 'Wireless'),
                                ('Beauty', 'Beauty'),
                                ('Office', 'Office'),
                                ('MusicalInstruments', 'MusicalInstruments'),
                                ('AutoAccessory', 'AutoAccessory'),
                                ('PetSupplies', 'PetSupplies'),
                                ('ToysBaby', 'ToysBaby'),
                                ('TiresAndWheels', 'TiresAndWheels'),
                                ('Music', 'Music'),
                                ('Video', 'Video'),
                                ('Lighting', 'Lighting'),
                                ('LargeAppliances', 'LargeAppliances'),
                                ('FBA', 'FBA'),
                                ('Toys', 'Toys'),
                                ('GiftCards', 'GiftCards'),
                                ('LabSupplies', 'LabSupplies'),
                                ('RawMaterials', 'RawMaterials'),
                                ('PowerTransmission', 'PowerTransmission'),
                                ('Industrial', 'Industrial'),
                                ('Shoes', 'Shoes'),
                                ('Motorcycles', 'Motorcycles'),
                                ('MaterialHandling', 'MaterialHandling'),
                                ('MechanicalFasteners', 'MechanicalFasteners'),
                                ('FoodServiceAndJanSan', 'FoodServiceAndJanSan'),
                                ('WineAndAlcohol', 'WineAndAlcohol'),
                                ('EUCompliance', 'EUCompliance'),
                                ('Books', 'Books')], 'Product Type',Required=True)
    product_type_clothingaccessories = fields.Selection([('ClothingAccessories', 'ClothingAccessories')],'ClothingAccessories')
    product_type_ce =fields.Selection([
                    ('Antenna', 'Antenna'),
                    ('AudioVideoAccessory', 'AudioVideoAccessory'),
                    ('AVFurniture', 'AVFurniture'),
                    ('BarCodeReader', 'BarCodeReader'),
                    ('CEBinocular', 'CEBinocular'),
                    ('CECamcorder', 'CECamcorder'),
                    ('CameraBagsAndCases', 'CameraBagsAndCases'),
                    ('CEBattery','CEBattery'),
                    ('CEBlankMedia','CEBlankMedia'),
                    ('CableOrAdapter','CableOrAdapter'),
                    ('CECameraFlash', 'CECameraFlash'),
                    ('CameraLenses', 'CameraLenses'),
                    ('CameraOtherAccessories', 'CameraOtherAccessories'),
                    ('CameraPowerSupply', 'CameraPowerSupply'),
                    ('CarAlarm', 'CarAlarm'),
                    ('CarAudioOrTheater', 'CarAudioOrTheater'),
                    ('CarElectronics', 'CarElectronics'),
                    ('ConsumerElectronics', 'ConsumerElectronics'),
                    ('CEDigitalCamera', 'CEDigitalCamera'),
                    ('DigitalPictureFrame', 'DigitalPictureFrame'),
                    ('DigitalVideoRecorder', 'DigitalVideoRecorder'),
                    ('DVDPlayerOrRecorder', 'DVDPlayerOrRecorder'),
                    ('CEFilmCamera', 'CEFilmCamera'),
                    ('GPSOrNavigationAccessory', 'GPSOrNavigationAccessory'),
                    ('GPSOrNavigationSystem', 'GPSOrNavigationSystem'),
                    ('HandheldOrPDA', 'HandheldOrPDA'),
                    ('Headphones', 'Headphones'),
                    ('HomeTheaterSystemOrHTIB', 'HomeTheaterSystemOrHTIB'),
                    ('KindleAccessories', 'KindleAccessories'),
                    ('KindleEReaderAccessories', 'KindleEReaderAccessories'),
                    ('KindleFireAccessories', 'KindleFireAccessories'),
                    ('MediaPlayer', 'MediaPlayer'),
                    ('MediaPlayerOrEReaderAccessory', 'MediaPlayerOrEReaderAccessory'),
                    ('MediaStorage', 'MediaStorage'),
                    ('MiscAudioComponents', 'MiscAudioComponents'),
                    ('PC', 'PC'),
                    ('PDA', 'PDA'),
                    ('Phone', 'Phone'),
                    ('PhoneAccessory', 'PhoneAccessory'),
                    ('PhotographicStudioItems', 'PhotographicStudioItems'),
                    ('PortableAudio', 'PortableAudio'),
                    ('PortableAvDevice', 'PortableAvDevice'),
                    ('PowerSuppliesOrProtection', 'PowerSuppliesOrProtection'),
                    ('RadarDetector', 'RadarDetector'),
                    ('RadioOrClockRadio', 'RadioOrClockRadio'),
                    ('ReceiverOrAmplifier', 'ReceiverOrAmplifier'),
                    ('RemoteControl', 'RemoteControl'),
                    ('Speakers', 'Speakers'),
                    ('StereoShelfSystem', 'StereoShelfSystem'),
                    ('CETelescope', 'CETelescope'),
                    ('Television', 'Television'),
                    ('Tuner', 'Tuner'),
                    ('TVCombos', 'TVCombos'),
                    ('TwoWayRadio', 'TwoWayRadio'),
                    ('VCR', 'VCR'),
                    ('CEVideoProjector', 'CEVideoProjector'),
                    ('VideoProjectorsAndAccessories', 'VideoProjectorsAndAccessories'), ], 'CE Types')
    
    product_type_com = fields.Selection([
                    ('CarryingCaseOrBag', 'CarryingCaseOrBag'),
                    ('ComputerAddOn', 'ComputerAddOn'),
                    ('ComputerComponent', 'ComputerComponent'),
                    ('ComputerCoolingDevice', 'ComputerCoolingDevice'),
                    ('ComputerDriveOrStorage', 'ComputerDriveOrStorage'),
                    ('ComputerInputDevice', 'ComputerInputDevice'),
                    ('ComputerProcessor', 'ComputerProcessor'),
                    ('ComputerSpeaker', 'ComputerSpeaker'),
                    ('Computer', 'Computer'),
                    ('FlashMemory', 'FlashMemory'),
                    ('InkOrToner', 'InkOrToner'),
                    ('Keyboards', 'Keyboards'),
                    ('MemoryReader', 'MemoryReader'),
                    ('Monitor', 'Monitor'),
                    ('Motherboard', 'Motherboard'),
                    ('NetworkingDevice', 'NetworkingDevice'),
                    ('NotebookComputer', 'NotebookComputer'),
                    ('PersonalComputer', 'PersonalComputer'),
                    ('Printer', 'Printer'),
                    ('RamMemory', 'RamMemory'),
                    ('Scanner', 'Scanner'),
                    ('SoundCard', 'SoundCard'),
                    ('SystemCabinet', 'SystemCabinet'),
                    ('SystemPowerDevice', 'SystemPowerDevice'),
                    ('TabletComputer', 'TabletComputer'),
                    ('VideoCard', 'VideoCard'),
                    ('VideoProjector', 'VideoProjector'),
                    ('Webcam', 'Webcam')], 'Computer Types')
    
    product_type_auto_accessory = fields.Selection([
                    ('AutoAccessoryMisc', 'AutoAccessoryMisc'),
                    ('AutoPart', 'AutoPart'),
                    ('PowersportsPart', 'PowersportsPart'),
                    ('PowersportsVehicle', 'PowersportsVehicle'),
                    ('ProtectiveGear', 'ProtectiveGear'),
                    ('Helmet', 'Helmet'),
                    ('RidingApparel', 'RidingApparel'), ], 'Auto Accessory Types')
    
    product_type_sports = fields.Selection([
                    ('SportingGoods', 'SportingGoods'),
                    ('GolfClubHybrid', 'GolfClubHybrid'),
                    ('GolfClubIron', 'GolfClubIron'),
                    ('GolfClubPutter', 'GolfClubPutter'),
                    ('GolfClubWedge', 'GolfClubWedge'),
                    ('GolfClubWood', 'GolfClubWood'),
                    ('GolfClubs', 'GolfClubs'), ], 'sports Types')
    
    product_type_foodandbeverages = fields.Selection([
                    ('Food', 'Food'),
                    ('HouseholdSupplies', 'HouseholdSupplies'),
                    ('Beverages', 'Beverages'),
                    ('HardLiquor', 'HardLiquor'),
                    ('AlcoholicBeverages', 'AlcoholicBeverages'),
                    ('Wine', 'Wine')], 'Food And Beverages Types')
    
    product_type_softwarevideoGames = fields.Selection([
                    ('Software', 'Software'),
                    ('HandheldSoftwareDownloads', 'HandheldSoftwareDownloads'),
                    ('SoftwareGames', 'SoftwareGames'),
                    ('VideoGames', 'VideoGames'),
                    ('VideoGamesAccessories', 'VideoGamesAccessories'),
                    ('VideoGamesHardware', 'VideoGamesHardware')], 'Software Video Games Types')
    
    product_type_light = fields.Selection([
                    ('LightsAndFixtures', 'LightsAndFixtures'),
                    ('LightingAccessories', 'LightingAccessories'),
                    ('LightBulbs', 'LightBulbs')], 'Light Types')
    
    product_type_tools = fields.Selection([
                    ('GritRating', 'GritRating'),
                    ('Horsepower', 'Horsepower'),
                    ('Diameter', 'Diameter'),
                    ('Length', 'Length'),
                    ('Width', 'Width'),
                    ('Height', 'Height'),
                    ('Weight','Weight')], 'Tools Types')
    
    product_type_toys = fields.Selection([
                    ('ToysAndGames', 'ToysAndGames'),
                    ('Hobbies', 'Hobbies'),
                    ('CollectibleCard', 'CollectibleCard'),
                    ('Costume', 'Costume')], 'Toys Types')
    
    product_type_jewelry = fields.Selection([
                    ('Watch', 'Watch'),
                    ('FashionNecklaceBraceletAnklet', 'FashionNecklaceBraceletAnklet'),
                    ('FashionRing', 'FashionRing'),
                    ('FashionEarring', 'FashionEarring'),
                    ('FashionOther', 'FashionOther'),
                    ('FineNecklaceBraceletAnklet', 'FineNecklaceBraceletAnklet'),
                    ('FineRing', 'FineRing'),
                    ('FineEarring', 'FineEarring'),
                    ('FineOther', 'FineOther')], 'Food And Beverages Types')
    
    product_type_home = fields.Selection([
                    ('BedAndBath', 'BedAndBath'),
                    ('FurnitureAndDecor', 'FurnitureAndDecor'),
                    ('Kitchen', 'Kitchen'),
                    ('OutdoorLiving', 'OutdoorLiving'),
                    ('SeedsAndPlants', 'SeedsAndPlants'),
                    ('Art', 'Art'),
                    ('Home', 'Home')], 'Home Types')
    
    product_type_miscellaneous = fields.Selection([('MiscType', 'MiscType')], 'Misc Types')
    product_type_Video = fields.Selection([
                    ('VideoDVD', 'VideoDVD'),
                    ('VideoVHS','VideoVHS')], 'Video Types')
    product_type_petsupplies = fields.Selection([
                    ('PetSuppliesMisc', 'PetSuppliesMisc')], 'Petsupplies Types')
    product_type_toys_baby = fields.Selection([
                    ('ToysAndGames', 'ToysAndGames'),
                    ('BabyProducts', 'BabyProducts')], 'Toys n Baby Types')
    product_type_beauty = fields.Selection([
                    ('BeautyMisc', 'BeautyMisc')], 'Beauty Types')
    product_type_shoes = fields.Selection([
                    ('ClothingType', 'ClothingType')], 'Shoes Types')
    
    product_type_wirelessaccessories = fields.Selection([
                    ('WirelessAccessories', 'WirelessAccessories'),
                    ('WirelessDownloads', 'WirelessDownloads'),], 'Wireless Types')
    
    product_type_cameraphoto = fields.Selection([
                    ('FilmCamera', 'FilmCamera'),
                    ('Camcorder', 'Camcorder'),
                    ('DigitalCamera', 'DigitalCamera'),
                    ('DigitalFrame', 'DigitalFrame'),
                    ('Binocular', 'Binocular'),
                    ('SurveillanceSystem', 'SurveillanceSystem'),
                    ('Telescope', 'Telescope'),
                    ('Microscope', 'Microscope'),
                    ('Darkroom', 'Darkroom'),
                    ('Lens', 'Lens'),
                    ('LensAccessory', 'LensAccessory'),
                    ('Filter', 'Filter'),
                    ('Film', 'Film'),
                    ('BagCase', 'BagCase'),
                    ('BlankMedia', 'BlankMedia'),
                    ('PhotoPaper', 'PhotoPaper'),
                    ('Cleaner', 'Cleaner'),
                    ('Flash', 'Flash'),
                    ('TripodStand', 'TripodStand'),
                    ('Lighting', 'Lighting'),
                    ('Projection', 'Projection'),
                    ('PhotoStudio', 'PhotoStudio'),
                    ('LightMeter', 'LightMeter'),
                    ('PowerSupply', 'PowerSupply'),
                    ('OtherAccessory', 'OtherAccessory'), ], 'Camera n Photo')
    
    product_sub_type_ce = fields.Selection([
                    ('Antenna', 'Antenna'),
                    ('AVFurniture', 'AVFurniture'),
                    ('BarCodeReader', 'BarCodeReader'),
                    ('CEBinocular', 'CEBinocular'),
                    ('CECamcorder', 'CECamcorder'),
                    ('CameraBagsAndCases', 'CameraBagsAndCases'),
                    ('Battery', 'Battery'),
                    ('BlankMedia', 'BlankMedia'),
                    ('CableOrAdapter', 'CableOrAdapter'),
                    ('CECameraFlash', 'CECameraFlash'),
                    ('CameraLenses', 'CameraLenses'),
                    ('CameraOtherAccessories', 'CameraOtherAccessories'),
                    ('CameraPowerSupply', 'CameraPowerSupply'),
                    ('CarAudioOrTheater', 'CarAudioOrTheater'),
                    ('CarElectronics', 'CarElectronics'),
                    ('CEDigitalCamera', 'CEDigitalCamera'),
                    ('DigitalPictureFrame', 'DigitalPictureFrame'),
                    ('CECarryingCaseOrBag', 'CECarryingCaseOrBag'),
                    ('CombinedAvDevice', 'CombinedAvDevice'),
                    ('Computer', 'Computer'),
                    ('ComputerDriveOrStorage', 'ComputerDriveOrStorage'),
                    ('ComputerProcessor', 'ComputerProcessor'),
                    ('ComputerVideoGameController', 'ComputerVideoGameController'),
                    ('DigitalVideoRecorder', 'DigitalVideoRecorder'),
                    ('DVDPlayerOrRecorder', 'DVDPlayerOrRecorder'),
                    ('CEFilmCamera', 'CEFilmCamera'),
                    ('FlashMemory', 'FlashMemory'),
                    ('GPSOrNavigationAccessory', 'GPSOrNavigationAccessory'),
                    ('GPSOrNavigationSystem', 'GPSOrNavigationSystem'),
                    ('HandheldOrPDA', 'HandheldOrPDA'),
                    ('HomeTheaterSystemOrHTIB', 'HomeTheaterSystemOrHTIB'),
                    ('Keyboards', 'Keyboards'),
                    ('MemoryReader', 'MemoryReader'),
                    ('Microphone', 'Microphone'),
                    ('Monitor', 'Monitor'),
                    ('MP3Player', 'MP3Player'),
                    ('MultifunctionOfficeMachine', 'MultifunctionOfficeMachine'),
                    ('NetworkAdapter', 'NetworkAdapter'),
                    ('NetworkMediaPlayer', 'NetworkMediaPlayer'),
                    ('NetworkStorage', 'NetworkStorage'),
                    ('NetworkTransceiver', 'NetworkTransceiver'),
                    ('NetworkingDevice', 'NetworkingDevice'),
                    ('NetworkingHub', 'NetworkingHub'),
                    ('Phone', 'Phone'),
                    ('PhoneAccessory', 'PhoneAccessory'),
                    ('PhotographicStudioItems', 'PhotographicStudioItems'),
                    ('PointingDevice', 'PointingDevice'),
                    ('PortableAudio', 'PortableAudio'),
                    ('PortableAvDevice', 'PortableAvDevice'),
                    ('PortableElectronics', 'PortableElectronics'),
                    ('Printer', 'Printer'),
                    ('PrinterConsumable', 'PrinterConsumable'),
                    ('ReceiverOrAmplifier', 'ReceiverOrAmplifier'),
                    ('RemoteControl', 'RemoteControl'),
                    ('SatelliteOrDSS', 'SatelliteOrDSS'),
                    ('Scanner', 'Scanner'),
                    ('SoundCard', 'SoundCard'),
                    ('Speakers', 'Speakers'),
                    ('CETelescope', 'CETelescope'),
                    ('SystemCabinet', 'SystemCabinet'),
                    ('SystemPowerDevice', 'SystemPowerDevice'),
                    ('Television', 'Television'),
                    ('TwoWayRadio', 'TwoWayRadio'),
                    ('VCR', 'VCR'),
                    ('VideoCard', 'VideoCard'),
                    ('VideoProjector', 'VideoProjector'),
                    ('VideoProjectorsAndAccessories', 'VideoProjectorsAndAccessories'),
                    ('Webcam', 'Webcam')], 'Product Sub Type')
    product_type_sportsmemorabilia = fields.Selection([
                    ('SportsMemorabilia','SportsMemorabilia')],'Sports Memorabilia')
    product_type_health = fields.Selection([
                    ('HealthMisc','HealthMisc'),
                    ('PersonalCareAppliances','PersonalCareAppliances')],'Health')
    battery_chargecycles = fields.Integer('Battery Charge Cycles')
    battery_celltype = fields.Selection([
                    ('NiCAD','NiCAD'),
                    ('NiMh','NiMh'),
                    ('alkaline','alkaline'),
                    ('aluminum_oxygen','aluminum_oxygen'),
                    ('lead_acid','lead_acid'),
                    ('lead_calcium','lead_calcium'),
                    ('lithium','lithium'),
                    ('lithium_ion','lithium_ion'),
                    ('lithium_manganese_dioxide','lithium_manganese_dioxide'),
                    ('lithium_metal','lithium_metal'),
                    ('lithium_polymer','lithium_polymer'),
                    ('manganese','manganese'),
                    ('polymer','polymer'),
                    ('silver_oxide','silver_oxide'),
                    ('zinc','zinc')],'Battery Cell Type')
    power_plugtype = fields.Selection([
                    ('type_a_2pin_jp','type_a_2pin_jp'),
                    ('type_e_2pin_fr','type_e_2pin_fr'),
                    ('type_j_3pin_ch','type_j_3pin_ch'),
                    ('type_a_2pin_na','type_a_2pin_na'),
                    ('type_ef_2pin_eu','type_ef_2pin_eu'),
                    ('type_k_3pin_dk','type_k_3pin_dk'),
                    ('type_b_3pin_jp','type_b_3pin_jp'),
                    ('type_f_2pin_de','type_f_2pin_de'),
                    ('type_l_3pin_it','type_l_3pin_it'),
                    ('type_b_3pin_na','type_b_3pin_na'),
                    ('type_g_3pin_uk','type_g_3pin_uk'),
                    ('type_m_3pin_za','type_m_3pin_za'),
                    ('type_c_2pin_eu','type_c_2pin_eu'),
                    ('type_h_3pin_il','type_h_3pin_il'),
                    ('type_n_3pin_br','type_n_3pin_br'),
                    ('type_d_3pin_in','type_d_3pin_in'),
                    ('type_i_3pin_au','type_i_3pin_au')],'Power Plug Type')
    
    power_source=fields.Selection([
                    ('AC','AC'),
                    ('DC','DC'),
                    ('Battery','Battery'),
                    ('AC & Battery','AC & Battery'),
                    ('Solar','Solar'),
                    ('fuel_cell','Fuel Cell'),
                    ('Kinetic','Kinetic')],'Power Source')
    wattage = fields.Integer('Wattage')
    
    product_type_music = fields.Selection([
                    ('MusicPopular','MusicPopular'),
                    ('MusicClassical','MusicClassical')],'Music')
    product_type_office = fields.Selection([
                    ('ArtSupplies','ArtSupplies'),
                    ('EducationalSupplies','EducationalSupplies'),
                    ('OfficeProducts','OfficeProducts'),
                    ('PaperProducts','PaperProducts'),
                    ('WritingInstruments','WritingInstruments')],'Office')
    variation_data = fields.Selection([
                    ('Solar','Solar'),
                    ('Solar','Solar')],'VariationData')
    hand_orientation = fields.Selection([
                    ('Solar','Solar'),
                    ('Solar','Solar')],'HandOrientation')
    input_device_design_style = fields.Selection([
                    ('Solar','Solar'),
                    ('Solar','Solar')],'InputDeviceDesignStyle')
    keyboard_description = fields.Char('Keyboard Description',size=64)
    product_type_tiresandwheels = fields.Selection([
                    ('Tires','Tires'),
                    ('Wheels','Wheels')],'Tires And Wheels')
    product_type_giftcard = fields.Selection([
                    ('ItemDisplayHeight','ItemDisplayHeight'),
                    ('ItemDisplayLength','ItemDisplayLength'),
                    ('ItemDisplayWidth','ItemDisplayWidth'),
                    ('ItemDisplayWeight','ItemDisplayWeight')],'Gift Card')
    product_type_musicalinstruments = fields.Selection([
                    ('BrassAndWoodwindInstruments','BrassAndWoodwindInstruments'),
                    ('Guitars','Guitars'),
                    ('InstrumentPartsAndAccessories','InstrumentPartsAndAccessories'),
                    ('KeyboardInstruments','KeyboardInstruments'),
                    ('MiscWorldInstruments','MiscWorldInstruments'),
                    ('PercussionInstruments','PercussionInstruments'),
                    ('SoundAndRecordingEquipment','SoundAndRecordingEquipment'),
                    ('StringedInstruments','StringedInstruments')],'MusicalInstruments Type')
    
    model_number = fields.Integer('Model Number')
    voltage = fields.Integer('Voltage')
    wattage_com = fields.Integer('Wattage')
    wireless_input_device_protocol = fields.Selection([
                    ('Solar','Solar'),
                    ('Solar','Solar')],'Wireless InputDevice Protocol')
    wireless_input_device_technology = fields.Selection([
                    ('Solar','Solar'),
                    ('Solar','Solar')],'Wireless InputDevice Technology')
    prod_listing_ids = fields.One2many('products.amazon.listing.upload', 'listing_id','Product Listing')
    cablelength = fields.Char('Cabel Length',size=64)
    operating_system = fields.Char('Operating System',size=64)
    power_source_gp = fields.Char('Power Source',size=64)
    screen_size = fields.Char('Screen Size',size=64)
    total_ethernet_ports = fields.Char('Total Ethernet Ports',size=64)
    wireless_type = fields.Char('Wireless Type',size=64)
    battery_cell_type_gp = fields.Char('Battery Cell Type',size=64)
    battery_charge_cycles_gp = fields.Integer('Battery Charge Cycles')
    battery_power_gpnav = fields.Char('Battery Power',size=64)
    box_contents_gp = fields.Char('Box Contents',size=64)
    cable_length_gp = fields.Char('Cable Length',size=64)
    color_screen_gp = fields.Boolean('Wireless Type')
    duration_ofmap_service_gp = fields.Char('Duration Of Map Service',size=64)
    operatingsystem_gp = fields.Char('Operating System',size=64)
    video_processor_gp = fields.Char('Video Processor',size=64)
    efficiencys_gp = fields.Char('Efficiency',size=64)
    finish_typeh_gp = fields.Char('Finish Type',size=64)
    internet_applications_gp = fields.Char('Internet Applications',size=64)
    emory_slots_available_gp = fields.Char('Memory Slots Available',size=64)
    power_plug_type_gp = fields.Char('Battery Charge Cycles',size=64)
    powersource_gpnav = fields.Char('Power Source',size=64)
    processorbrand_gp = fields.Char('Processor Brand',size=64)
    screensize_gp = fields.Char('Screen_Size',size=64)
    remotecontroldescription_gp = fields.Char('Remote Control Descriptionpe',size=64)
    removablememory_gp = fields.Char('Removable Memory',size=64)
    screenresolution_gp = fields.Char('Screen Resolution',size=64)
    subscriptiontermnamer_gp = fields.Char('Subscription TermName',size=64)
    trafficfeatures_gp = fields.Char('Traffic Features',size=64)
    softwareincluded_gp = fields.Char('Software Included',size=64)
    totalethernetports_gp = fields.Char('Total Ethernet Ports',size=64)
    totalfirewireports_gp = fields.Char('Total Fire wire Ports',size=64)
    totalhdmiports_gp = fields.Char('Total Hdmi Ports',size=64)
    totalsvideooutports_gp = fields.Integer('Total SVideo OutPorts')
    wirelesstechnology_gp = fields.Char('Wireless Technology',size=64)
    total_usb_ports_gp = fields.Char('Total USB Ports',size=64)
    waypointstype_gp = fields.Char('Waypoints Type',size=64)
    colorscreen_hpda = fields.Boolean('ColorScreen')
    hardrivesize_hpda = fields.Integer('Hard Drive Size')
    memory_slots_available_hpda = fields.Char('Memory Slots Available',size=64)
    memory_slots_available_gp = fields.Char('Memory Slots Available',size=64)
    operating_system_hpda = fields.Char('Operating System',size=64)
    power_source_hpda = fields.Char('Power Source',size=64)
    processor_type_hpda = fields.Char('Processor Type',size=64)
    processor_speed_hpda = fields.Char('Processor Speed',size=64)
    RAMsize_hpda = fields.Char('RAMSize',size=64)
    screen_size_hpda = fields.Char('Screen Size',size=64)
    screen_resolution_hpda = fields.Char('Screen Resolution',size=64)
    softwareincluded_hpda = fields.Char('Software Included',size=64)
    wirelesstechnology_hpda = fields.Char('Wireless Technology',size=64)
    amplifiertype_headphone = fields.Char('Amplifiertype',size=64)
    battery_celltype_headphone = fields.Char('Battery Celltype',size=64)
    batterychargecycles_headphone = fields.Char('Battery Chargecycles',size=64)
    batterypower_headphone = fields.Char('Battery Power',size=64)
    cable_length_headphone = fields.Char('Cable Length',size=64)
    controltype_headphone = fields.Char('Control Type',size=64)
    fittype_headphone = fields.Char('Fit Type',size=64)
    headphoneearcupmotion_headphone = fields.Char('Headphone Earcup Motion',size=64)
    noisereductionlevel_headphone = fields.Char('Noise Reduction Level',size=64)
    power_plug_type_headphone = fields.Char('Power Plug Type',size=64)
    shape_headphone = fields.Char('Shape',size=64)
    powersource_headphone = fields.Char('Power Source',size=64)
    totalcomponentinports_headphone = fields.Char('Total Component In Ports',size=64)
    wirelesstechnology_headphone = fields.Char('Wireless Technology',size=64)
    variationdata_net = fields.Char('Variation Data',size=64)
    additional_features_net = fields.Char('Additional Features',size=64)
    additional_functionality_net = fields.Char('Additional Functionality',size=64)
    ipprotocol_standards_net = fields.Char('IP ProtocolStandards',size=64)
    lanportbandwidth_net = fields.Char('LAN Port Bandwidth',size=64)
    lan_port_number_net = fields.Char('LAN Port Number',size=64)
    maxdownstreamtransmissionrate_net = fields.Char('Max Downstream Transmission Rate',size=64)
    maxupstreamtransmissionRate_net = fields.Char('Max Upstream Transmission Rate',size=64)
    model_number_net = fields.Char('Model Number',size=64)
    modem_type_net = fields.Char('Modem Type',size=64)
    network_adapter_type_type_net = fields.Char('Network Adapter Type',size=64)
    operating_system_compatability_net = fields.Char('Operating System Compatability',size=64)
    securityprotocol_net = fields.Char('Security Protocol',size=64)
    simultaneous_sessions_net = fields.Char('Simultaneous Sessions',size=64)
    voltage_net = fields.Char('Voltage',size=64)
    wattage_net = fields.Char('Wattage',size=64)
    wirelessdatatransferrate_net = fields.Char('Wireless Data Transfer Rate',size=64)
    wirelessroutertransmissionband_net = fields.Char('Wireless Router Transmission Band',size=64)
    wirelesstechnology_net = fields.Char('Wireless Technology',size=64)
    variationdata_scanner = fields.Char('Variation Data',size=64)
    hasgreyscale_scanner = fields.Char('Has Grey Scale',size=64)
    lightsourcetype_scanner = fields.Char('Battery Chargecycles',size=64)
    maxinputsheetcapacity_scanner = fields.Integer('Max Input Sheet Capacity')
    maxprintresolutionblackwhite_scanner = fields.Char('Max Print Resolution BlackWhite',size=64)
    maxprintresolutioncolor_scanner = fields.Char('Max Print Resolution Color',size=64)
    maxprintspeedblackwhite_scanner = fields.Char('Max Print Speed BlackWhite',size=64)
    maxprintspeedcolor_scanner = fields.Char('Max Print Speed Color',size=64)
    maxscanningsize_scanner = fields.Char('Max scanning size',size=64)
    minscanningsize_scanner = fields.Char('Min Scanning Size',size=64)
    printermediasizemaximum_scanner = fields.Char('Printer Media Size Maximum',size=64)
    printeroutputtype_scanner = fields.Char('Printer Output Type',size=64)
    printerwirelesstype_scanner = fields.Char('Printer Wireless Type',size=64)
    printing_media_type_scanner = fields.Char('Printing Media Type',size=64)
    printingtechnology_scanner = fields.Char('Printing Technology',size=64)
    scanrate_scanner_scanner = fields.Char('Scan Rate',size=64)
    scannerresolution_scanner = fields.Char('Scanner Resolution',size=64)
    variationdata_printer = fields.Char('Variation Data',size=64)
    hasgreyscale_printer = fields.Char('Has Grey Scale',size=64)
    lightsourcetype_printer = fields.Char('Battery Chargecycles',size=64)
    maxinputsheetcapacity_printer = fields.Integer('Max Input Sheet Capacity')
    maxprintresolutionblackwhite_printer = fields.Char('Max Print Resolution BlackWhite',size=64)
    maxprintresolutioncolor_printer = fields.Char('Max Print Resolution Color',size=64)
    maxprintspeedblackwhite_printer = fields.Char('Max Print Speed BlackWhite',size=64)
    maxprintspeedcolor_printer = fields.Char('Max Print Speed Color',size=64)
    maxscanningsize_printer = fields.Char('Max scanning size',size=64)
    minscanningsize_printer = fields.Char('Min Scanning Size',size=64)
    printermediasizemaximum_printer = fields.Char('Printer Media Size Maximum',size=64)
    printeroutputtype_printer = fields.Char('Printer Output Type',size=64)
    printerwirelesstype_printer = fields.Char('Printer Wireless Type',size=64)
    printing_media_type_printer = fields.Char('Printing Media Type',size=64)
    printingtechnology_printer = fields.Char('Printing Technology',size=64)
    scanrate_scanner_printer = fields.Char('Scan Rate',size=64)
    scannerresolution_printer = fields.Char('Scanner Resolution',size=64)
    shop_id = fields.Many2one('sale.shop', string="Shop")


class ProductsAmazonListingUpload(models.Model):
    _name = "products.amazon.listing.upload"
    
    def _get_bom_stock(self):
        for record in self:
            record.bom_stock_list = record.product_id.bom_stock_list
        
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.price = self.product_id.with_context(pricelist=self.listing_id.shop_id.pricelist_id.id).price

    is_new_listing = fields.Boolean('New')
    listing_id = fields.Many2one('upload.amazon.products', string='Listing Name')
    product_id = fields.Many2one('product.product', string='Product Name')
    product_asin = fields.Many2one('amazon.product.listing', string='Listing')
    fulfillment_by = fields.Selection([
                                       ('MFN','Fulfilled by Merchant(MFN)'),
                                       ('AFN','Fulfilled by Amazon(AFN)')],'Fulfillment By', default="MFN")
    bom_stock_list = fields.Float(compute='_compute_get_bom_stock', type="float", string="Bom Stock")
    price = fields.Float(string="Price")

