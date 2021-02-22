# -*- coding: utf-8 -*-
import urllib.request
import base64
import time
import logging
import os
# from odoo.addons.resource.models.resource import seconds
logger = logging.getLogger('__name__')
from odoo import api, fields, models, _
from datetime import timedelta, datetime
from odoo.addons.amazon_connector.amazon_api import amazonerp_osv as amazon_api_obj
from threading import Thread, Lock
import pytz
from pytz import timezone
from dateutil import tz
# import sys
# reload(sys)
# sys.setdefaultencoding('latin-1')
class SaleShop(models.Model):
    _inherit = "sale.shop"
    
    
    def import_product_scheduler(self, cron_mode=True):
        store_obj = self.env['sale.shop']
        store_ids = store_obj.search([('amazon_shop','=',True),('auto_import_products','=',True)])
        if store_ids:
            store_ids.sorted(reverse=True)
            store_ids.import_amazon_product()
        return True
    
    def import_FBAInventory_scheduler(self, cron_mode=True):
        store_obj = self.env['sale.shop']
        store_ids = store_obj.search([('amazon_shop','=',True)])
        if store_ids:
            store_ids.sorted(reverse=True)
            store_ids.import_amazon_FBA_Inventory()
        return True
    
    def import_Inventory_scheduler(self, cron_mode=True):
        store_obj = self.env['sale.shop']
        store_ids = store_obj.search([('amazon_shop','=',True)])
        if store_ids:
            store_ids.sorted(reverse=True)
            store_ids.import_amazon_inventory()
        return True
    
    def import_orders_amazon_scheduler(self, cron_mode=True):
        print("import productp=====")
        try:
            store_obj = self.env['sale.shop']
            store_ids = store_obj.search([('amazon_shop','=',True),('auto_import_order','=',True)])
            if store_ids:
                store_ids.sorted(reverse=True)
                store_ids.amazon_import_orders()
        except :
            pass
        return True
    
    def update_amazon_orders_scheduler(self, cron_mode=True):
        print("import productp=====")
        store_obj = self.env['sale.shop']
        store_ids = store_obj.search([('amazon_shop','=',True),('auto_import_order','=',True)])
        if store_ids:
            store_ids.sorted(reverse=True)
            store_ids.update_amazon_orders()
        return True
    
    def export_product_scheduler(self, cron_mode=True):
        print("import productp=====")
        store_obj = self.env['sale.shop']
        store_ids = store_obj.search([('amazon_shop','=',True)])
        if store_ids:
            store_ids.sorted(reverse=True)
            store_ids.export_amazon_products()
        return True
    
    def update_product_scheduler(self, cron_mode=True):
        print("import productp=====")
        store_obj = self.env['sale.shop']
        store_ids = store_obj.search([('amazon_shop','=',True)])
        if store_ids:
            store_ids.sorted(reverse=True)
            store_ids.with_context({'from_update_product':True}).export_amazon_products()
        return True
    
    def update_price_scheduler(self, cron_mode=True):
        print("import productp=====")
        store_obj = self.env['sale.shop']
        store_ids = store_obj.search([('amazon_shop','=',True),('auto_update_price','=',True)])
        if store_ids:
            store_ids.sorted(reverse=True)
            store_ids.update_amazonPrice()
        return True
    
    def upload_inventory_scheduler(self, cron_mode=True):
        print("import productp=====")
        store_obj = self.env['sale.shop']
        store_ids = store_obj.search([('amazon_shop','=',True),('auto_update_inventory','=',True)])
        if store_ids:
            store_ids.sorted(reverse=True)
            store_ids.update_amazonInventory()
        return True
    
    def importAmazoncategory(self):
        print ("importAmazoncategoryyyyyyyyyyyyyyyyy")
        # Import amazon browse node(category)
        amazon_obj = self.env['amazon.log']
        logger.info("Importing Category from Amazon...............")
        for amazon_marketplace in self:
            try:
                StartDate = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + '.000Z'
                
                # First we need to request for Product report it will return request return id
                RequestReportData = amazon_api_obj.call(amazon_marketplace, 'RequestReport', '_GET_XML_BROWSE_TREE_DATA_', StartDate)
                if RequestReportData.get('ReportProcessingStatus', False):
                    if RequestReportData.get('ReportProcessingStatus') == '_SUBMITTED_':
                        if RequestReportData.get('ReportRequestId'):
                            time.sleep(120)
                            
                            # Once we get request report id then we need to be call GetReportList to get reort id for requested browse node report
                            logger.info("ReportRequestId %s", RequestReportData.get('ReportRequestId'))
                            GetReportRequestListData = amazon_api_obj.call(amazon_marketplace, 'GetReportRequestList', RequestReportData.get('ReportRequestId'), '_GET_XML_BROWSE_TREE_DATA_')
                            if GetReportRequestListData.get('Error'):
                                continue
                            if GetReportRequestListData.get('status') == '_DONE_NO_DATA_':
                                continue
                            while not GetReportRequestListData.get('GeneratedReportId', False):
                                time.sleep(120)
                                GetReportRequestListData = amazon_api_obj.call(amazon_marketplace, 'GetReportRequestList', RequestReportData.get('ReportRequestId'), '_GET_XML_BROWSE_TREE_DATA_')
                                logger.info("GetReportRequestList ID %s", GetReportRequestListData.get('GeneratedReportId'))
                                if GetReportRequestListData.get('status') == '_DONE_NO_DATA_':
                                    break
                                if GetReportRequestListData.get('Error'):
                                    break
                            
                            if GetReportRequestListData and GetReportRequestListData.get('GeneratedReportId', False):
                                # Once will get report id will need to be call GetReport API to get browse node tree
                                logger.info("GetReportRequestListData GeneratedReportId %s", GetReportRequestListData.get('GeneratedReportId'))
                                reportData = amazon_api_obj.call(amazon_marketplace, 'GetReport', GetReportRequestListData['GeneratedReportId'], '_GET_XML_BROWSE_TREE_DATA_')
                                print ("=====reportDatareportData====>",reportData)
                                if isinstance(reportData, dict):
                                    while reportData.get('Error'):
                                        logger.info("in while ----------------->")
                                        reportData = amazon_api_obj.call(amazon_marketplace, 'GetReport', GetReportRequestListData['GeneratedReportId'], '_GET_XML_BROWSE_TREE_DATA_')
    #                                     logger.info("reportData %s", len(reportData))
                                for data in reportData:
                                    logger.info("data ----------------->%s",len(data))
                                    self.env['product.category'].create_amazon_category(amazon_marketplace, categ_list=data)
            except Exception as e:
                print ("eeeeeeeeeeeeeeeeee", e)
                sequence_id = self.env['ir.sequence'].next_by_code('amazon.log')
                ctx = self._context.copy()
                ctx.update({'log_sequence':sequence_id})
                ir_model_obj = self.env['ir.model']
                model_ids = ir_model_obj.search([('model','=','product.category')])
                log_vals = {'name':sequence_id,
                            'res_model_id':model_ids.id,
                            'description':e,
                            'log_type':'import_browsenode',
        #                     'res_id':,
                            'marketplace_id':amazon_marketplace.id,
                            'create_date':datetime.today()}
                amazon_obj.create(log_vals)
            self.env.cr.commit()
        return True
    
    def getCategoryByAsin(self, asin):
        # Get Category By Asin From Amazon
        # Param Asin: Asin of Product
        # return categ_id
        prodcateg_obj = self.env['product.category']
        response_category = amazon_api_obj.call(self, 'GetProductCategoriesForASIN', asin)
        logger.info("response_category ........................%s", response_category)
        print("========response_categoryresponse_category",response_category)
        if response_category.get('Error', False):
            return False
        prodcateg_ids = prodcateg_obj.search([('amazon_cat_id', '=', response_category.get('ProductCategoryId', False))])
        if prodcateg_ids:
            amazon_categ_id = prodcateg_ids[0].id
        else:
            parent = False
            if response_category.get('Parent', False):
                parent_ids = prodcateg_obj.search([('amazon_cat_id', '=', response_category.get('Parent').get('ProductCategoryId', False))])
                if parent_ids:
                    parent = parent_ids[0].id
                else:
                    parent = prodcateg_obj.create({
                        'amazon_category' : True,
                        'amazon_cat_id' : response_category.get('Parent').get('ProductCategoryId', False),
                        'name' : response_category.get('Parent').get('ProductCategoryName', False),
                    })
                    parent = parent.id
                    
            amazon_categ_id = prodcateg_obj.create({
                        'amazon_category' : True,
                    'amazon_cat_id' : response_category.get('ProductCategoryId', False),
                    'name' : response_category.get('ProductCategoryName', False),
                    'parent_id': parent
        })
        logger.info("amazon_categ_id ........................%s", amazon_categ_id)
        self.env.cr.commit()
        return amazon_categ_id
    
    def getCategoryBySKU(self, sku):
        prodcateg_obj = self.env['product.category']
        response_category = amazon_api_obj.call(self, 'GetProductCategoriesForSKU', sku)
        print("========response_categoryresponse_categoryresponse_categoryresponse_category",response_category)
        logger.info("response_category ........................%s", response_category)
        while response_category.get('Error', False):
            time.sleep(30)
            response_category = amazon_api_obj.call(self, 'GetProductCategoriesForSKU', sku)
            print("========response_categoryresponse_categoryresponse_categoryresponse_category",response_category)
            logger.info("Again response_category ........................%s", response_category)
        prodcateg_ids = prodcateg_obj.search([('amazon_cat_id', '=', response_category.get('ProductCategoryId', False))])
        if prodcateg_ids:
            amazon_categ_id = prodcateg_ids[0]
        else:
            parent = False
            if response_category.get('Parent', False):
                parent_ids = prodcateg_obj.search([('amazon_cat_id', '=', response_category.get('Parent').get('ProductCategoryId', False))])
                if parent_ids:
                    parent = parent_ids[0].id
                else:
                    parent = prodcateg_obj.create({
                        'amazon_category' : True,
                        'amazon_cat_id' : response_category.get('Parent').get('ProductCategoryId', False),
                        'name' : response_category.get('Parent').get('ProductCategoryName', False),
                    })
                    parent = parent.id
                    
            amazon_categ_id = prodcateg_obj.create({
                        'amazon_category' : True,
                    'amazon_cat_id' : response_category.get('ProductCategoryId', False),
                    'name' : response_category.get('ProductCategoryName', False),
                    'parent_id': parent
        })
        logger.info("amazon_categ_id ........................%s", amazon_categ_id)
        self.env.cr.commit()
        return amazon_categ_id
    
    def get_matching_product(self, get_list=[], prod_data_list='', prod_sku_asin_dict=''):#, prod_sku_asin_dict=''        
        prod_obj = self.env['product.product']
        prod_temp_obj = self.env['product.template']
        prod_att_obj = self.env['product.attribute']
        prod_att_val_obj = self.env['product.attribute.value']
        product_listing_obj = self.env['amazon.product.listing']
        prod_vals = {}
        print("get_list>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",get_list)
        if len(get_list) <= 0:
            return True
        response_list = amazon_api_obj.call(self, 'GetMatchingProductForId', get_list)
#         logger.info("response_list ........................%s", response_list)
        for response in response_list:
            print("response>>>>>>>>>",response)
            sellerSKU = False
            if response == 'Code':
                return True
            if not response.get('parent_asin'):
                sellerSKU = response.get('SellerSKU')
            if response.get('parent_asin'):
                response = amazon_api_obj.call(self, 'GetMatchingProductForId', [response.get('parent_asin')], 'ASIN')[0]
                print("responseother",response)
                
            prodtempl_vals = {}
            title = ''
            asin = ''
#             default_code = ''
#             print("prod_skuprodskuasindictasin_dict",prod_sku_asin_dict)
            list_price = ''
            listing_id = False
            quantity = 0
            name = ''
#             try:
            sku = response.get('SellerSKU')
            print("sku",sku)
            asin = response.get('asin')
            logger.info("prod_data_list.get(sku)........................%s", prod_data_list.get(sku))
            logger.info("response.......................%s", response)
            logger.info("prod_name.......................%s", prod_data_list.get(sku).get('name') if prod_data_list.get(sku) else False)
            list_price = float(prod_data_list.get(sku).get('list_price').strip()) if (prod_data_list.get(sku) and  prod_data_list.get(sku).get('list_price')) else 0.00
            print("list_priceeeeee",list_price)
#             listing_id =prod_data_list.get(sku) and  prod_data_list.get(sku).get('listing_id').strip() or False
#             quantity = prod_data_list.get(sku) and prod_data_list.get(sku).get('quantity') and float(prod_data_list.get(sku).get('quantity')) or 0.0
            name = prod_data_list.get(sku) and prod_data_list.get(sku).get('name').strip() or response.get('Label')
            
            # Preparing and creating product variants
            attributes =[]
            variant_list = []
            product_tmpl_ids = prod_temp_obj.search(['|','|',('amazon_sku','=',sku),('default_code','=',sku),('tmp_asin','=',response.get('asin'))])
            if not product_tmpl_ids:
                if response.get('attributes'):
                    for attribute in response.get('attributes').keys():
                        print("attribute",attribute)
                        attribute_ids = prod_att_obj.search([('name','=',attribute)])
                        print("attribute_ids",attribute_ids)
                        if attribute_ids:
                            attribute_id = attribute_ids[0]
                        else:
                            attribute_id = prod_att_obj.create({'name':attribute})
                            print("attribute_id,",attribute_id)
                        attribute_values = []
                        for value in response.get('attributes').get(attribute):
                            print("value",value)
                            att_value_ids = prod_att_val_obj.search([('name','=',value),('attribute_id','=',attribute_id.id)])
                            print("att_value_ids",att_value_ids)
                            if not att_value_ids:
                                attribute_val_id = prod_att_val_obj.create({'attribute_id':attribute_id.id, 'name':value})
                                print("attribute_val_id",attribute_val_id)
                            else:
                                attribute_val_id = att_value_ids[0]
                            
                            if attribute_val_id.id not in attribute_values:
                                attribute_values.append(attribute_val_id.id)
                        variant_list.append((0,0,{'attribute_id':attribute_id.id,
                                              'value_ids':[(6, 0, attribute_values)]
                                              }))
                print("variant_list",variant_list)
                prodtempl_vals.update({'attribute_line_ids':variant_list or False,})
            
#        
                                
            # TO get Amazon Attributes and Prepare Dictionary
            print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",prod_data_list.get(sku))
            prodtempl_vals.update({'tmp_asin':response.get('asin', False),'feature' : response.get('features', False)})
            for attr in response.get('AttributeSets', []):
                if 'SmallImageURL' in attr:
                    img_url = attr.get('SmallImageURL', False)
                    if img_url:
                        try:
                            (filename, header) = urllib.request.urlretrieve(img_url)
                            f = open(filename, 'rb')
                            img = base64.encodestring(f.read())
                            prodtempl_vals.update({'image':img})
                            f.close()
                        except:
                            pass
                       
                prodtempl_vals.update({
                   'product_group': attr.get('ProductGroup', False),
                   'package_dimension_length': attr.get('PackageDimensionsLength') and float(attr.get('PackageDimensionsLength')) or 0,
                   'label': attr.get('Label', False),
                   'product_type_name': attr.get('ProductTypeName', False),
                   'small_image_height': attr.get('SmallImageHeight') and int(attr.get('SmallImageHeight')) or 0,
                   'package_quantity': attr.get('PackageQuantity', 0),
                   'item_dimension_weight': attr.get('ItemDimensionsWeight')  and float(attr.get('ItemDimensionsWeight')) or 0,
                   'brand_name':attr.get('Brand', False),
                   'studio':attr.get('Studio', False),
                   'amazon_manufacturer':attr.get('Manufacturer', False),
                   'publisher':attr.get('Publisher', False),
                   'package_dimension_width': attr.get('PackageDimensionsWidth') and float(attr.get('PackageDimensionsWidth')) or 0,
                   'package_dimension_weight': attr.get('PackageDimensionsWeight') and float(attr.get('PackageDimensionsWeight')) or 0,
                   'color': attr.get('Color', False),
                   'package_dimension_height': attr.get('PackageDimensionsHeight') and float(attr.get('PackageDimensionsHeight')) or 0,
                   'small_image_url': attr.get('SmallImageURL', False),
                   'binding': attr.get('Binding', False),
                   'small_image_width': attr.get('SmallImageWidth') and float(attr.get('SmallImageWidth')),
                   'amazon_product':True,
                   
                   
                })
            if prod_data_list.get(sku):
                if prod_data_list.get(sku).get('fulfillment-channel') == 'AMAZON_NA':
                    prodtempl_vals.update({'fulfillment_by':'FBA'})
            #             if sellerSKU:
#                 if prod_data_list.get(sellerSKU).get('merchant-shipping-group')=='Nationwide Prime':
#                     prodtempl_vals.update({'is_prime':True})   
            title = response.get('Title', False)  
            if not name:
                name =  prodtempl_vals.get('label') 
            if not title:
                name =  prodtempl_vals.get('label')
            prodtempl_vals.update({
                'name' : name or response.get('Title', False),
                'amazon_price' : response.get('Amount') or list_price,
                'default_code': sku,
                'amazon_sku':sku,
                'type' : 'product',
                'tmp_asin':asin,
            })
            # To Add Route of Product
#             prodtempl_vals.update({'route_ids' : [(6, 0, [1])]})
                
# Get Category for Product
#             if response.get('parent_asin'):
#                 print"amazon_categ_id"
#                 amazon_categ_id = self.getCategoryByAsin(sku)
#             else:
# #             if not amazon_categ_id:
#                 print"amazon_categ_id22"
#                 amazon_categ_id = self.getCategoryBySKU(sku)
#             if isinstance(amazon_categ_id, list):
#                 cat_id = amazon_categ_id[0]
#             else:
#                 cat_id = amazon_categ_id
#             prodtempl_vals['amazon_categ_id'] = cat_id.id
            
#             if not cat_id:
#                 continue
            product_tmpl_ids = prod_temp_obj.search(['|','|',('amazon_sku','=',sku),('default_code','=',sku),('tmp_asin','=',response.get('asin'))])      
# Create a  Template of Product is not available
            print("product_tmpl_ids",product_tmpl_ids)
            if not product_tmpl_ids:
                logger.info('prodtempl_vals-----------------------  %s', prodtempl_vals)
                product_tmpl_id = prod_temp_obj.create(prodtempl_vals).id
#                 logger.info("product_tmpl_id %s", product_tmpl_id)
                print("productproduct_tmpl_id",product_tmpl_id)
                value = []
                product_ids = prod_obj.search([('product_tmpl_id', '=', product_tmpl_id)])
                if product_ids:
                    prod_id_var = False
                    for product_data in product_ids:
                        print("product_data",product_data)
                        prod_val_ids = product_data.product_template_attribute_value_ids.ids
                        print("prod_val_ids,",prod_val_ids)
                        asin_var = ''
                        for product_info in response.get('variant_info'):
                            print("product_info",product_info)
                            sku = prod_sku_asin_dict.get(product_info.get('asin'))
                            print("skuskuskuskusku",sku)
                            default_code = sku[0]
                            print("defaultcodedefaultcode",default_code)
                            flag = 1
                            for p_val in product_data.product_template_attribute_value_ids:
                                print("p_valp_valp_val",p_val)
                                print ("kkkkkkkkkkkkkkkkkkkkk",p_val.name)
                                if product_info.get(p_val.attribute_id.name) != p_val.name:
                                    flag = 0
                            print("flagflag",flag)
                            if flag == 1:
                                product_id = prod_obj.search([('default_code','=',default_code)])
                                print('------product_id for attribute checking---->>>',product_id)
                                if not product_id:
                                    asin_var = product_info.get('asin')
                                    list_price = float(prod_data_list.get(default_code).get('list_price').strip()) if (prod_data_list.get(default_code) and  prod_data_list.get(default_code).get('list_price')) else 0.00
                                    print("list_priceeeeee",list_price)
                                    product_data.write({'default_code':default_code,'amazon_standard_price' : list_price or response.get('Amount'),'asin':asin_var, 'amazon_active_prod':True})
#                                 if prod_data_list.get(sku):
#                                     if prod_data_list.get(sku).get('merchant-shipping-group',False) == 'Nationwide Prime':
#                                         product_data.write({'is_prime':True})
                        
            else:
#                 product_tmpl_ids.write(prodtempl_vals)
                product_tmpl_id = product_tmpl_ids.id
#                 logger.info('prodtempl_vals-----------------------  %s', prodtempl_vals)
#                 value = []
#                 product_ids = prod_obj.search([('product_tmpl_id', '=', product_tmpl_id)])
#                 if product_ids:
#                     prod_id_var = False
#                     for product_data in product_ids:
#                         print("product_data",product_data)
#                         prod_val_ids = product_data.attribute_value_ids.ids
#                         print("prod_val_ids,",prod_val_ids)
#                         asin_var = ''
#                         for product_info in response.get('variant_info'):
#                             print("product_info",product_info)
#                             sku = prod_sku_asin_dict.get(product_info.get('asin'))
#                             print("skuskuskuskusku",sku)
#                             default_code = sku[0]
#                             print("defaultcodedefaultcode",default_code)
# #                             flag = 1
# #                             for p_val in product_data.attribute_value_ids:
# #                                 print("p_valp_valp_val",p_val)
# #                                 print ("kkkkkkkkkkkkkkkkkkkkk",p_val.name)
# #                                 if product_info.get(p_val.attribute_id.name) != p_val.name:
# #                                     flag = 0
# #                             if flag == 1:
# #                                 asin_var = product_info.get('asin')
# #                                 print("keysssssssss0",prod_sku_asin_dict.keys())
# #                                 print("product_infommmmmmmmmMMMMMMMMMMMMMMMMMMM",product_info.get('asin'))
#                             product_id = prod_obj.search([('default_code','=',default_code)])
#                             print('------product_idattribute checking---->>>',product_id)
#                             if product_id:
#                                 list_price = float(prod_data_list.get(default_code).get('list_price').strip()) if (prod_data_list.get(default_code) and  prod_data_list.get(default_code).get('list_price')) else 0.00
#                                 print("list_priceeeeee222222",list_price)
#                                 product_id.write({'default_code':default_code,'amazon_standard_price' : list_price or response.get('Amount'),'asin':asin_var, 'amazon_active_prod':True})
#                     erttt

#                             self.env.cr.commit()
#             else:
#                 product_tmpl_ids[0].write(prodtempl_vals)
#                 product_tmpl_id = product_tmpl_ids[0].id
            self.env.cr.commit()
        return True
    
    def import_amazon_product(self):
        print ("import_amazon_productttttttttttt")
        # Import amazon products
        for amazon_marketplace in self:
#             try:
                print ("selfcontext", self._context)
                if self._context.get('last_date_of_product_import'):
                    # sdate = datetime.strptime(self._context.get('last_date_of_product_import'), "%Y-%m-%d %H:%M:%S")
                    sdate = self._context.get('last_date_of_product_import')
                    StartDate = sdate.strftime("%Y-%m-%dT%H:%M:%S") + '.000Z'

                    # sdate = datetime.strptime(sdate, "%Y-%m-%d %H:%M:%S")
                    #
                    # StartDate = sdate.strftime("%Y-%m-%dT%H:%M:%S") + '.000Z'
                elif amazon_marketplace.last_date_of_product_import:
                    last_import_time = datetime.strptime(amazon_marketplace.last_date_of_product_import, "%Y-%m-%d %H:%M:%S")
                    StartDate = last_import_time.strftime("%Y-%m-%dT%H:%M:%S") + '.000Z'
                else:
                    StartDate = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + '.000Z'
                
                # First we need to request for browse node report it will return request return id
                print ("=====StartDate=====>",StartDate)
                RequestReportData = amazon_api_obj.call(amazon_marketplace, 'RequestReport', '_GET_MERCHANT_LISTINGS_DATA_', StartDate)
                if RequestReportData.get('ReportProcessingStatus', False):
                    if RequestReportData.get('ReportProcessingStatus') == '_SUBMITTED_':
                        if RequestReportData.get('ReportRequestId'):
                            time.sleep(20)
                            
                            # Once we get request report id then we need to be call GetReportList to get reort id for requested browse node report
                            logger.info("ReportRequestId %s", RequestReportData.get('ReportRequestId'))
                            GetReportRequestListData = amazon_api_obj.call(amazon_marketplace, 'GetReportRequestList', RequestReportData.get('ReportRequestId'), '_GET_MERCHANT_LISTINGS_DATA_')
                            if GetReportRequestListData.get('Error'):
                                continue
                            if GetReportRequestListData.get('status') == '_DONE_NO_DATA_':
                                continue
                            while not GetReportRequestListData.get('GeneratedReportId', False):
                                time.sleep(20)
                                GetReportRequestListData = amazon_api_obj.call(amazon_marketplace, 'GetReportRequestList', RequestReportData.get('ReportRequestId'), '_GET_MERCHANT_LISTINGS_DATA_')
                                logger.info("GetReportRequestListData Status %s", GetReportRequestListData.get('GeneratedReportId'))
                                if GetReportRequestListData.get('status') == '_DONE_NO_DATA_':
                                    break
                                if GetReportRequestListData.get('Error'):
                                    break
                
                            if GetReportRequestListData and GetReportRequestListData.get('GeneratedReportId', False):
                                time.sleep(30)
                                
                                # Once will get report id will need to be call GetReport API to get browse node tree
                                product_list, prod_data_list,prod_sku_asin_dict = amazon_api_obj.call(amazon_marketplace, 'GetReport', GetReportRequestListData.get('GeneratedReportId'), '_GET_MERCHANT_LISTINGS_DATA_')
                                lenght_prod = len(product_list)
                                logger.info('Products Count...........: %s', lenght_prod)
                                # logger.info('prod_data_list...........: %s', prod_data_list)
                                i = 0
                                last = 0
                                count = 0
                                
                                # allow only 10 product to get product info from amazon
                                for i in range(0, lenght_prod, 5):
                                    last = i + 5
                                    count = count +1
                                    logger.info('last...........: %s', last)
                                    logger.info('product_list...........: %s', product_list[i: last])
                                    if count == 26:
                                        count = 0
                                        time.sleep(30)
                                    amazon_marketplace.get_matching_product(product_list[i: last], prod_data_list, prod_sku_asin_dict)
                                # Remaining product data to get
                                rem = lenght_prod % 5
                                if rem > 0:
                                    logger.info('product_listnest...........: %s', product_list[last: last + rem])
                                    amazon_marketplace.get_matching_product(product_list[last: last + rem], prod_data_list, prod_sku_asin_dict)
                                    # self.env.cr.commit()
    #                                 amazon_marketplace.import_inventory()
#             except Exception as e:  
#                 print ("eeeeeeeeeeeeeeeeee", e)
#                 amazon_obj = self.env['amazon.log']
#                 sequence_id = self.env['ir.sequence'].next_by_code('amazon.log')
#                 ctx = self._context.copy()
#                 ctx.update({'log_sequence':sequence_id})
#                 ir_model_obj = self.env['ir.model']
#                 model_ids = ir_model_obj.search([('model','=','product.product')])
#                 log_vals = {'name':sequence_id,
#                             'res_model_id':model_ids.id,
#                             'description':e,
#                             'log_type':'import_product',
#         #                     'res_id':,
#                             'marketplace_id':amazon_marketplace.id,
#                             'create_date':datetime.today()}
#                 amazon_obj.create(log_vals)
        self.env.cr.commit()              
        return True
    
    def ImportInventory(self, get_list=[], prod_data_list='',marketplace=''):
        # print("get_listget_list",get_list)
        # print("prod_data_listprod_data_list",prod_data_list)
        product_obj = self.env['product.product']
        inventory_obj = self.env['stock.change.product.qty']
        # print("get_listget_listget_listget_list",get_list)
        for sku in get_list:
            print("sku",sku)
            prod_ids = product_obj.search([('default_code', '=', sku)])
            print("prod_ids",prod_ids, prod_ids.product_tmpl_id)
            data = prod_data_list.get(sku).get('quantity')
            print("data================adttttttttttttttttttttttttasdtttttt ",data)
            print("prod_data_list.get(sku).get('quantity')prod_data_list.get(sku).get('quantity') ",prod_data_list.get(sku).get('quantity'))
            if prod_ids:
                inventory_id = inventory_obj.create({
                       'location_id' : marketplace.warehouse_id.lot_stock_id.id,
                       'new_quantity' : prod_data_list.get(sku).get('quantity'),
                       'product_id' : prod_ids[0].id,
                        'product_tmpl_id' : prod_ids.product_tmpl_id.id,
                   })
                print("inventory_id",inventory_id)
                inventory_id.change_product_qty()
                self.env.cr.commit()
        return True
    
    def import_amazon_inventory(self):
        for amazon_marketplace in self:
            # try:
                StartDate = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + '.000Z'
                # First we need to request for browse node report it will return request return id
                print("=====StartDate=====>",StartDate)
                RequestReportData = amazon_api_obj.call(amazon_marketplace, 'RequestReport', '_GET_MERCHANT_LISTINGS_DATA_', StartDate)
                if RequestReportData.get('ReportProcessingStatus', False):
                    if RequestReportData.get('ReportProcessingStatus') == '_SUBMITTED_':
                        if RequestReportData.get('ReportRequestId'):
                            time.sleep(20)
                            # Once we get request report id then we need to be call GetReportList to get reort id for requested browse node report
                            logger.info("ReportRequestId %s", RequestReportData.get('ReportRequestId'))
                            GetReportRequestListData = amazon_api_obj.call(amazon_marketplace, 'GetReportRequestList', RequestReportData.get('ReportRequestId'), '_GET_MERCHANT_LISTINGS_DATA_')
                            if GetReportRequestListData.get('Error'):
                                continue
                            if GetReportRequestListData.get('status') == '_DONE_NO_DATA_':
                                continue
                            while not GetReportRequestListData.get('GeneratedReportId', False):
                                time.sleep(20)
                                GetReportRequestListData = amazon_api_obj.call(amazon_marketplace, 'GetReportRequestList', RequestReportData.get('ReportRequestId'), '_GET_MERCHANT_LISTINGS_DATA_')
                                logger.info("GetReportRequestListData Status %s", GetReportRequestListData.get('GeneratedReportId'))
                                if GetReportRequestListData.get('status') == '_DONE_NO_DATA_':
                                    break
                                if GetReportRequestListData.get('Error'):
                                    break
                
                            if GetReportRequestListData and GetReportRequestListData.get('GeneratedReportId', False):
                                time.sleep(30)
                                
                                # Once will get report id will need to be call GetReport API to get browse node tree
                                product_list, prod_data_list,prod_sku_asin_dict = amazon_api_obj.call(amazon_marketplace, 'GetReport', GetReportRequestListData.get('GeneratedReportId'), '_GET_MERCHANT_LISTINGS_DATA_')
                                amazon_marketplace.ImportInventory(product_list,prod_data_list,amazon_marketplace)
                                self.env.cr.commit()
            # except Exception as e:
            #     print ("eeeeeeee", e)
            #     amazon_obj = self.env['amazon.log']
            #     sequence_id = self.env['ir.sequence'].next_by_code('amazon.log')
            #     ctx = self._context.copy()
            #     ctx.update({'log_sequence':sequence_id})
            #     ir_model_obj = self.env['ir.model']
            #     model_ids = ir_model_obj.search([('model','=','stock.quant')])
            #     log_vals = {'name':sequence_id,
            #                 'res_model_id':model_ids.id,
            #                 'description':e,
            #                 'log_type':'import_inventory',
            # #                     'res_id':,
            #                 'marketplace_id':amazon_marketplace.id,
            #                 'create_date':datetime.today()}
            #     amazon_obj.create(log_vals)
            # self.env.cr.commit()
        return True
    
    def ImportAFNInventory(self, get_list=[], prod_data_list='',marketplace=''):
        print("get_listget_list",get_list)
        print("prod_data_listprod_data_list",prod_data_list)
        product_obj = self.env['product.product']
        inventory_obj = self.env['stock.change.product.qty']
        print("get_listget_listget_listget_list",get_list)
        for sku in get_list:
            print("sku",sku)
            prod_ids = product_obj.search([('default_code', '=', sku)])
            print("prod_ids",prod_ids)
            data = prod_data_list.get(sku).get('quantity')
            print("data================adttttttttttttttttttttttttasdtttttt ",data)
            print("prod_data_list.get(sku).get('quantity')prod_data_list.get(sku).get('quantity') ",prod_data_list.get(sku).get('quantity'))
            if prod_ids.fulfillment_by == 'FBA':
                inventory_id = inventory_obj.create({
                       'location_id' : marketplace.afn_warehouse.lot_stock_id.id,
                       'new_quantity' : prod_data_list.get(sku).get('quantity'),
                       'product_id' : prod_ids[0].id,
                   })
                print("inventory_id",inventory_id)
                inventory_id.change_product_qty()
                self.env.cr.commit()
        return True
    
    def import_amazon_FBA_Inventory(self):
        for amazon_marketplace in self:
            # try:
                StartDate = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + '.000Z'
                # First we need to request for browse node report it will return request return id
                print("=====StartDate=====>",StartDate)
                RequestReportData = amazon_api_obj.call(amazon_marketplace, 'RequestReport', '_GET_AFN_INVENTORY_DATA_', StartDate)
                if RequestReportData.get('ReportProcessingStatus', False):
                    if RequestReportData.get('ReportProcessingStatus') == '_SUBMITTED_':
                        if RequestReportData.get('ReportRequestId'):
                            time.sleep(20)
                            # Once we get request report id then we need to be call GetReportList to get reort id for requested browse node report
                            logger.info("ReportRequestId %s", RequestReportData.get('ReportRequestId'))
                            GetReportRequestListData = amazon_api_obj.call(amazon_marketplace, 'GetReportRequestList', RequestReportData.get('ReportRequestId'), '_GET_AFN_INVENTORY_DATA_')
                            if GetReportRequestListData.get('Error'):
                                continue
                            if GetReportRequestListData.get('status') == '_DONE_NO_DATA_':
                                continue
                            while not GetReportRequestListData.get('GeneratedReportId', False):
                                time.sleep(20)
                                GetReportRequestListData = amazon_api_obj.call(amazon_marketplace, 'GetReportRequestList', RequestReportData.get('ReportRequestId'), '_GET_AFN_INVENTORY_DATA_')
                                logger.info("GetReportRequestListData Status %s", GetReportRequestListData.get('GeneratedReportId'))
                                if GetReportRequestListData.get('status') == '_DONE_NO_DATA_':
                                    break
                                if GetReportRequestListData.get('Error'):
                                    break
                
                            if GetReportRequestListData and GetReportRequestListData.get('GeneratedReportId', False):
                                time.sleep(30)
                                
                                # Once will get report id will need to be call GetReport API to get browse node tree
                                product_list, prod_data_list,prod_sku_asin_dict = amazon_api_obj.call(amazon_marketplace, 'GetReport', GetReportRequestListData.get('GeneratedReportId'), '_GET_AFN_INVENTORY_DATA_')
                                amazon_marketplace.ImportAFNInventory(product_list,prod_data_list,amazon_marketplace)
                                self.env.cr.commit()
            # except Exception as e:
            #     print ("eeeeeeee", e)
            #     amazon_obj = self.env['amazon.log']
            #     sequence_id = self.env['ir.sequence'].next_by_code('amazon.log')
            #     ctx = self._context.copy()
            #     ctx.update({'log_sequence':sequence_id})
            #     ir_model_obj = self.env['ir.model']
            #     model_ids = ir_model_obj.search([('model','=','stock.quant')])
            #     log_vals = {'name':sequence_id,
            #                 'res_model_id':model_ids.id,
            #                 'description':e,
            #                 'log_type':'import_inventory',
            # #                     'res_id':,
            #                 'marketplace_id':amazon_marketplace.id,
            #                 'create_date':datetime.today()}
            #     amazon_obj.create(log_vals)
            # self.env.cr.commit()
        return True
        
    def createservicelineAmazonOrder(self, saleorderid, each_result):
        print("each_resulteach_resulteach_resulteach_result",each_result)
        sale_order_line_obj = self.env['sale.order.line']
        if each_result.get('ShippingPrice') and float(each_result.get('ShippingPrice'))>0.00:
            shiporderlinevals = {
                'order_id': saleorderid.id,
                'product_id': self.shipment_fee_product_id.id,
                'name': 'shipment',
                'product_uom_qty': 1,
                'product_uom' : self.shipment_fee_product_id.uom_id.id or 5,
                'price_unit': float(each_result.get('ShippingPrice', 0.00)),
            }
            shipping_line_ids = sale_order_line_obj.search([('order_id', '=', saleorderid.id), ('product_id', '=', self.shipment_fee_product_id.id)])
            if shipping_line_ids:
                shipping_line_ids.write({'price_unit': shipping_line_ids[0].price_unit + float(each_result.get('ShippingPrice', 0.00))})
                shiplineid = shipping_line_ids[0].id
            else:
                shiplineid = sale_order_line_obj.create(shiporderlinevals)
            logger.info('Shipment Line Created with ID : %s', shiplineid)
            
        if each_result.get('GiftWrapPrice', 0) and float(each_result.get('GiftWrapPrice'))>0.00:   
            gift_serviceline = {
                'order_id': saleorderid.id,
                'product_id': self.gift_wrapper_fee_product_id.id,
                'name': 'gift',
                'product_uom_qty': 1,
                'product_uom' : self.gift_wrapper_fee_product_id.uom_id.id or 5,
                'price_unit': float(each_result.get('GiftWrapPrice', 0.00)),
                'description': float(each_result.get('GiftMessageText', 0.00)),
            }
            gift_line_ids = sale_order_line_obj.search([('order_id', '=', saleorderid.id), ('product_id', '=', self.gift_wrapper_fee_product_id.id)])
            if gift_line_ids:
                gift_line_ids.write({'price_unit': gift_line_ids[0].price_unit + float(each_result.get('GiftWrapPrice', 0.00))})
                giftlineid = gift_line_ids[0].id
            else:
                giftlineid = sale_order_line_obj.create(gift_serviceline)
            logger.info('Gift Line Created with ID : %s', giftlineid)
        
        if each_result.get('PromotionDiscount',0) and float(each_result.get('PromotionDiscount'))>0.00:   
            promotion_dicount_serviceline = {
                'order_id': saleorderid.id,
                'name': 'promotion',
                'product_id': self.promotion_discount_product_id.id,
                'product_uom' : self.promotion_discount_product_id.uom_id.id or 5,
                'product_uom_qty': 1,
                'price_unit': float(each_result.get('PromotionDiscount', 0.00)),
            }
            promotion_line_ids = sale_order_line_obj.search([('order_id', '=', saleorderid.id), ('product_id', '=', self.promotion_discount_product_id.id)])
            if promotion_line_ids:
                promotion_line_ids.write({'price_unit': promotion_line_ids[0].price_unit + float(each_result.get('PromotionDiscount', 0.00))})
                promotionlineid = promotion_line_ids[0].id
            else:
                promotionlineid = sale_order_line_obj.create(promotion_dicount_serviceline)
            logger.info('promotion Discount Line Created with ID : %s', promotionlineid)
            
        if each_result.get('ShippingDiscount', 0.00)and float(each_result.get('ShippingDiscount'))>0.00:   
            shipment_discount_serviceline = {
                'order_id': saleorderid.id,
                'name': 'ship Discount',
                'product_id': self.shipment_discount_product_id.id,
                'product_uom_qty': 1,
                'product_uom' : self.shipment_discount_product_id.uom_id.id or 5,
                'price_unit': float(each_result.get('ShippingDiscount', 0.00)),
            }
            shipment_line_ids = sale_order_line_obj.search([('order_id', '=', saleorderid.id), ('product_id', '=', self.shipment_discount_product_id.id)])
            if shipment_line_ids:
                shipment_line_ids.write({'price_unit': shipment_line_ids[0].price_unit + float(each_result.get('ShippingDiscount', 0.00))})
                ship_disc_lineid = shipment_line_ids[0].id
            else:
                ship_disc_lineid = sale_order_line_obj.create(shipment_discount_serviceline)
            logger.info('Shipment Discount Line Created with ID : %s', ship_disc_lineid)
        return True
    
    def manageAmazonOrderLine(self, order_id, order_item_results):
        # manage lines for Order
        product_obj = self.env['product.product']
        sale_order_line_obj = self.env['sale.order.line']
        supplierinfo_obj = self.env['product.supplierinfo']
        lines = []
        tax_amount = False
        for each_result in order_item_results:
            print("each_resulteach_resulteach_result",each_result)
            orderlinevals = {}
            if float(each_result.get('QuantityOrdered')) < 1:
                continue
            
            # Check for Product available in odoo or not
            product_sku = each_result.get('SellerSKU', '')
            logger.info('=product_sku====== : %s', product_sku)
            product_search_ids = product_obj.search(['|',('default_code', '=', product_sku),('amazon_afn_sku', '=', product_sku), ('active', '=', True)])
            logger.info('=product_search_ids= with ID : %s', product_search_ids.amazon_fba_price)
            if not product_search_ids:
                if order_id.shop_id.product_import_condition==True:
                    self.create_amazonorder_product(product_sku)
                    product_search_ids = product_obj.search(['|',('default_code', '=', product_sku),('amazon_afn_sku', '=', product_sku),('active', '=', True)])
                else:
                    continue
            logger.info('=product_search_ids= with ID : %s', product_search_ids)
            if product_search_ids:
                orderlinevals.update({
                    'product_id': product_search_ids[0].id,
                    'name': each_result.get('Title', ''),
                    'product_uom': product_search_ids[0].uom_id.id,
                })
                logger.info('=orderlinevals : %s', orderlinevals)
            else:
                product_search_ids = product_obj.create({
                    'name': each_result.get('Title', ''),
                    'default_code': product_sku
                })
                orderlinevals.update({
                    'product_id': product_search_ids.id,
                    'name' : product_sku + each_result.get('Title', ''),
                    'product_uom': product_search_ids.uom_id.id,
                })
                logger.info('=orderlinevals : %s', orderlinevals)
#             info_ids = supplierinfo_obj.search([('product_tmpl_id', '=', product_search_ids[0].id)])
#             if info_ids and product_search_ids[0].route_ids[0].name == 'Drop Shipping':
#                 flow = 'direct_delivery'
#                 proc = 'make_to_order'
            print("each_result.get('Amount'):",each_result.get('Amount'))
            print("order_idorder_idorder_id",order_id)
            print("order_idorder_idorder_id",order_id.fullfillment_method)
            if each_result.get('Amount'):
                orderlinevals.update({'price_unit': float(each_result.get('Amount', False)) / float(each_result.get('QuantityOrdered')),})
            elif each_result.get('Amount')==None:
                if order_id.fullfillment_method=='AFN':
                    orderlinevals.update({'price_unit': product_search_ids[0].amazon_fba_price / float(each_result.get('QuantityOrdered')),})
                if order_id.fullfillment_method=='MFN':
                    orderlinevals.update({'price_unit': float(product_search_ids[0].amazon_standard_price) / float(each_result.get('QuantityOrdered')),})
            orderlinevals.update({
                'order_id': order_id.id,
                'order_item_id': each_result.get('OrderItemId', False),
                'product_uom_qty': float(each_result.get('QuantityOrdered', False)),
#                 'price_unit': float(each_result.get('Amount', False)) / float(each_result.get('QuantityOrdered')),
                'asin': each_result.get('ASIN', False),
                'new_tax_amount': float(each_result['ItemTax']),
#                 'tax_id': []
            })
            print("orderlinevalsABCABC",orderlinevals)
            tax_id = []
            if float(each_result.get('ItemTax',0)) > 0.0:
                tax_id = self.getTaxesAccountID(each_result,order_id,orderlinevals.get('price_unit'))
                print("tax_idtax_idtax_id",tax_id)
                if tax_id[0]:
                    orderlinevals['tax_id'] = [(6, 0, tax_id)]
                    print("sfddddddddfdssfdfd")
                else:
                    orderlinevals['tax_id'] =[]
            else:
                print("jjjjjjjjjjjjjjjjjjjjjjjjjjjjjj")
                orderlinevals['tax_id'] =[]
#             self.env['sale.order.line'].create(orderlinevals)
            oline = sale_order_line_obj.create(orderlinevals)
            print("olineolineoline",oline)
            self.env.cr.commit()
#             tax_amount =+ float(each_result['ItemTax'])
#             print("tax_amounttax_amounttax_amounttax_amounttax_amount",tax_amount)
            lines.append(oline)
            logger.info('Order Line CreatcreateOrdered with ID : %s', oline)      
#             order_id.write({'amount_tax':tax_amount})
            self.env.cr.commit()
#             self.createservicelineAmazonOrder(order_id, each_result)
        return lines
    
    def getTaxesAccountID(self,each_result,order_id,unit_price):
        accounttax_obj = self.env['account.tax']
        accounttax_id = False
        shop_data = self.browse(self._ids)
        print("unit_priceunit_price",unit_price)
#         if hasattr(each_result ,'tax_percent') and float(each_result['tax_percent']) > 0.0:
        print("order_id.partner_id",order_id.partner_id.country_id.name)
        print("order_id.partner_id.state_id.name",order_id.partner_id.state_id.name)
        price = unit_price*int(each_result.get('QuantityOrdered'))
        print("amountamount",price)
        amount = float(each_result['ItemTax'])*100/price
        print("amountamountamountamountamount",amount)
        if not order_id.partner_id.state_id:
            accounttax_id = False
        else:
            acctax_ids = accounttax_obj.search([('amazon_country_id','=',order_id.partner_id.country_id.id),('type_tax_use', '=', 'sale'),('amazon_state_id', '=', order_id.partner_id.state_id.id)])
            print("acctax_idsacctax_ids",acctax_ids)
            if acctax_ids:
                accounttax_id = acctax_ids[0].id
            if not acctax_ids:
                print("Ddfdffff",order_id.partner_id.name)
                accounttax_id = accounttax_obj.create({'name':order_id.partner_id.state_id.name +' Sales Tax','type_tax_use':'sale','amazon_country_id':order_id.partner_id.country_id.id,'amazon_state_id':order_id.partner_id.state_id.id,'amount':amount})
                accounttax_id = accounttax_id.id
#             else:
#                 accounttax_id = False    
        return accounttax_id
    
    def manageAmazonOrderWorkflowBasedonOdoo(self, saleorderid, resultval):
        invoice_obj = self.env['account.move']
        invoice_refund_obj = self.env['account.move.reversal']
        return_obj = self.env['stock.return.picking']
        return_line_obj = self.env['stock.return.picking.line']
        # Make Order Confirm
#        
#         if resultval.get('OrderStatus', False) == 'Canceled':
#             if saleorderid.state in ['draft']:
#                 saleorderid.action_cancel()
#                 
#             if saleorderid.state in ['progress', 'done', 'manual']:
#                 invoice_ids = saleorderid.invoice_ids
#                 for invoice in invoice_ids:
#                     refund_ids = invoice_obj.search([('origin', '=', invoice.number)])
#                     if not refund_ids:
#                         if invoice.state == 'paid' :
#                             refund_invoice_id = invoice_refund_obj.create(dict(
#                                 description='Refund To %s' % (invoice.partner_id.name),
#                                 date=datetime.date.today(),
#                                 filter_refund='refund'
#                             ))
#                             refund_invoice_id.invoice_refund()
#                             saleorderid.write({'is_refund':True})
#                         else:
#                             invoice.action_cancel()
#                      
#                 for picking in saleorderid.picking_ids:       
#                     if picking.state not in ('done'):
#                         picking.action_cancel()
#                     else:
#                         ctx = self._context.copy()
#                         ctx.update({'active_id' : picking.id})
#                         res = return_obj.with_context(ctx).default_get(['product_return_moves', 'move_dest_exists'])
#                         res.update({'invoice_state':'2binvoiced'})
#                         return_id = return_obj.with_context(ctx).create({'invoice_state':'none'})
#                         for record in res['product_return_moves']:
#                             record.update({'wizard_id': return_id.id})
#                             return_line_obj.with_context(ctx).create(record)
#                         pick_id_return, type = return_id.with_context(ctx)._create_returns()
#                         pick_id_return.force_assign()
#                         pick_id_return.action_done()
#         
#             # Make Order Cancel                
#             saleorderid.action_cancel()
#             logger.info('Order[%s] is Cancelled', saleorderid)
        if resultval.get('FulfillmentChannel')=='MFN':
            print ("MFNMFNMFNMFNMFN" )
        elif resultval.get('FulfillmentChannel')=='AFN':
            if self.amazon_workflow_id.validate_order:
                if saleorderid.state in ['draft']:
                    saleorderid.action_confirm()
                print ("inside validate order")
    
            # if complete shipment is activated in workflow
            if self.amazon_workflow_id.complete_shipment:
                print ("inside Complete Shipment", saleorderid.state)
                if saleorderid.state in ['draft']:
                    saleorderid.action_confirm()
                for picking_id in saleorderid.picking_ids:
    
                    # If still in draft => confirm and assign
                    if picking_id.state == 'draft':
                        picking_id.action_confirm()
                    if picking_id.state != 'done':
                        picking_id.button_validate()
                        wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, picking_id.id)]})
                        wiz.process()
#                     picking_id.action_assign()
#                     picking_id.force_assign()
#                     picking_id.do_transfer()
    
            # if create_invoice is activated in workflow
            if self.amazon_workflow_id.create_invoice:
                if not saleorderid.invoice_ids:
                    saleorderid.action_invoice_create()
    
            # if validate_invoice is activated in workflow
            if self.amazon_workflow_id.validate_invoice:
                print ("inside validate invoice")
                if saleorderid.state == 'draft':
                    saleorderid.action_confirm()
    
                if not saleorderid.invoice_ids:
                    saleorderid.action_invoice_create()
    
                for invoice_id in saleorderid.invoice_ids:
                    if invoice_id.state == 'draft':
                        invoice_id.action_invoice_open()
    
            # if register_payment is activated in workflow
            if self.amazon_workflow_id.register_payment:
                print ("inside register_payment invoice")
                if saleorderid.state == 'draft':
                    saleorderid.action_confirm()
                if not saleorderid.invoice_ids:
                    saleorderid.action_invoice_create()
                for invoice_id in saleorderid.invoice_ids:
                    if invoice_id.state == 'draft':
                        invoice_id.action_invoice_open()
                    if invoice_id.state not in ['paid'] and invoice_id.invoice_line_ids:
                        invoice_id.pay_and_reconcile(
                            self.amazon_workflow_id and self.amazon_workflow_id.sale_journal or self.env['account.journal'].search(
                                [('type', '=', 'bank')], limit=1), invoice_id.amount_total)

        return True
    
    def manageAmazonOrderWorkflow(self, saleorderid, resultval):
        logger.info('OrderStatus----------->%s', resultval.get('OrderStatus'))
#         logger.info('OrderStatus----------->', resultval.get('OrderStatus'))
        invoice_obj = self.env['account.move']
        invoice_refund_obj = self.env['account.move.reversal']
        return_obj = self.env['stock.return.picking']
        return_line_obj = self.env['stock.return.picking.line']
        # Make Order Confirm
        if saleorderid.state in ['draft', 'sent']:
            saleorderid.action_confirm()
        
        # if Amazon Order Status is shipped then in odoo create invoice and 
        # pay invoice and also picking create and transfer picking   
#         if resultval.get('OrderStatus', False) == 'pending':
#             if not saleorderid.invoice_ids:
#                 saleorderid.with_context({'from_amazon':True}).action_invoice_create()
#             logger.info('Order[%s] is pending', saleorderid)
         
        if resultval.get('OrderStatus', False) == 'Shipped':
            if not saleorderid.invoice_ids:
                saleorderid.with_context({'from_amazon':True}).action_invoice_create()
            for invoice_id in saleorderid.invoice_ids:
                if invoice_id.state =='draft' and invoice_id.invoice_line_ids:
                    invoice_id.action_invoice_open()
                if invoice_id.state =='open' and invoice_id.invoice_line_ids:
                    invoice_id.pay_and_reconcile(self.amazon_workflow_id and self.amazon_workflow_id.sale_journal.id or self.env['account.journal'].search([('type', '=', 'bank')], limit=1), invoice_id.amount_total)
            for picking in saleorderid.picking_ids:
                if picking.state not in ['cancel', 'done']:
                    logger.info('Picking state 1111111%s', picking.state)
                    if picking.state =='draft':
                        picking.action_confirm()
                        picking.action_assign()
                    logger.info('Picking state22222 %s', picking.state)
                    if picking.state in ['confirmed','partially_available']:
                        picking.force_assign()
#                     picking.do_transfer()
                    saleorderid
#                     logger.info('saleorderid approval status %s', saleorderid.so_approval_status)
                    picking.do_transfer()
                logger.info('Picking state3333 %s', picking.state)
#             saleorderid.action_done()
            logger.info('Order[%s] is shipped', saleorderid)
         
        # if Amazon Ortder status is Unshipped create invoice and pay invoice           
        if resultval.get('OrderStatus', False) == 'Unshipped':
            print ("unshippedstatus", resultval.get('OrderStatus', False))
            if not saleorderid.invoice_ids:
                saleorderid.with_context({'from_amazon':True}).action_invoice_create()
            for invoice_id in saleorderid.invoice_ids:
                if invoice_id.state not in ['paid']:
                    invoice_id.action_invoice_open()
                    invoice_id.pay_and_reconcile(self.amazon_workflow_id and self.amazon_workflow_id.sale_journal.id or self.env['account.journal'].search([('type', '=', 'bank')], limit=1), invoice_id.amount_total)
            logger.info('Order[%s] is Unshipped', saleorderid)
        # if Amazon Order Status is Cancelled then make sale Order cancel, if invoice id created and they are in draft simple cancel those.
        # but if invoice is not in draft need to refund invoice
        # if picking is in draft cancel picking
        # if Picking not draft invoice create return shipment
        if resultval.get('OrderStatus', False) == 'Canceled':
            if saleorderid.state in ['draft']:
                saleorderid.action_cancel()
                
            if saleorderid.state in ['progress', 'done', 'manual']:
                invoice_ids = saleorderid.invoice_ids
                for invoice in invoice_ids:
                    refund_ids = invoice_obj.search([('origin', '=', invoice.number)])
                    if not refund_ids:
                        if invoice.state == 'paid' :
                            refund_invoice_id = invoice_refund_obj.create(dict(
                                description='Refund To %s' % (invoice.partner_id.name),
                                date=datetime.date.today(),
                                filter_refund='refund'
                            ))
                            refund_invoice_id.invoice_refund()
                            saleorderid.write({'is_refund':True})
                        else:
                            invoice.action_cancel()
                     
                for picking in saleorderid.picking_ids:       
                    if picking.state not in ('done'):
                        picking.action_cancel()
                    else:
                        ctx = self._context.copy()
                        ctx.update({'active_id' : picking.id})
                        res = return_obj.with_context(ctx).default_get(['product_return_moves', 'move_dest_exists'])
                        res.update({'invoice_state':'2binvoiced'})
                        return_id = return_obj.with_context(ctx).create({'invoice_state':'none'})
                        for record in res['product_return_moves']:
                            record.update({'wizard_id': return_id.id})
                            return_line_obj.with_context(ctx).create(record)
                        pick_id_return, type = return_id.with_context(ctx)._create_returns()
                        pick_id_return.force_assign()
                        pick_id_return.action_done()
        
            # Make Order Cancel                
            saleorderid.action_cancel()
            logger.info('Order[%s] is Cancelled', saleorderid)
        return True
    
    def create_amazonorder_product(self, sku):
        print ("contexct0",self._context)
        if self._context.get('listing'):
            if self._context.get('listing').get(sku):
                self.get_matching_product([sku], {sku : self._context.get('listing').get(sku)})
        for amazon_marketplace in self:
            StartDate = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + '.000Z'
            RequestReportData = amazon_api_obj.call(amazon_marketplace, 'RequestReport', '_GET_MERCHANT_LISTINGS_DATA_', StartDate)
            if RequestReportData.get('ReportProcessingStatus', False):
                if RequestReportData.get('ReportProcessingStatus') == '_SUBMITTED_':
                    if RequestReportData.get('ReportRequestId'):
                        time.sleep(20)
                        
                        # Once we get request report id then we need to be call GetReportList to get reort id for requested browse node report
                        logger.info("ReportRequestId %s", RequestReportData.get('ReportRequestId'))
                        GetReportRequestListData = amazon_api_obj.call(amazon_marketplace, 'GetReportRequestList', RequestReportData.get('ReportRequestId'), '_GET_MERCHANT_LISTINGS_DATA_')
                        logger.info("GetReportRequestListData Status %s", GetReportRequestListData.get('GeneratedReportId'))
                        while not GetReportRequestListData.get('GeneratedReportId', False):
                            time.sleep(20)
                            GetReportRequestListData = amazon_api_obj.call(amazon_marketplace, 'GetReportRequestList', RequestReportData.get('ReportRequestId'), '_GET_MERCHANT_LISTINGS_DATA_')
                            logger.info("GetReportRequestListData Status %s", GetReportRequestListData.get('GeneratedReportId'))
            
                        if GetReportRequestListData and GetReportRequestListData.get('GeneratedReportId', False):
                            time.sleep(30)
                            
                            # Once will get report id will need to be call GetReport API to get browse node tree
                            product_list, prod_data_list,prod_sku_asin_dict = amazon_api_obj.call(amazon_marketplace, 'GetReport', GetReportRequestListData.get('GeneratedReportId'), '_GET_MERCHANT_LISTINGS_DATA_')
                            logger.info("sku %s", sku)
#                             logger.info("prod_data_list.get(sku) %s", prod_data_list.get(sku),prod_sku_asin_dict)
                            if prod_data_list.get(sku):
                                self.get_matching_product([sku], {sku : prod_data_list.get(sku)},prod_sku_asin_dict)
                                self.with_context({'listing': prod_data_list})
                            else:
                                self.get_matching_product([sku], {},prod_sku_asin_dict)
                                
    def AmazonCreateOrders(self, resultvals):
        # Prepare Order Dictionary and Create Orderimpoe
        partner_obj = self.env['res.partner']
        product_obj = self.env['product.product']
        saleorder_obj = self.env['sale.order']
        delivery_carrier = self.env['delivery.carrier']
        model_obj = self.env['ir.model']
        log_obj = self.env['amazon.log']
#         saleorderid = False
        count = 1
        for resultval in resultvals:
            print("resultvalresultval",resultval)
            if resultval != {} and resultval.get('AmazonOrderId'):
                if resultval.get('OrderStatus')=='Pending'or resultval.get('OrderStatus')=='Canceled':
                    continue
                saleorderids = saleorder_obj.search([('amazon_order_id', '=', resultval.get('AmazonOrderId'))])
                logger.info('Search for Order : %s', saleorderids)
                logger.info('Order Date : %s', resultval.get('PurchaseDate'))
                if not saleorderids:
                # Get Order Item Detail from Amazon using AmazonOrderID
                    order_item_results = amazon_api_obj.call(self, 'ListOrderItems', resultval.get('AmazonOrderId'))
                    logger.info('Order Line Result----- : %s', order_item_results)
                    if len(order_item_results) and  order_item_results[0].get('Error'):
                        while order_item_results[0].get('Error'):
                            order_item_results = amazon_api_obj.call(self, 'ListOrderItems', resultval.get('AmazonOrderId'))
                            logger.info('Order Line Result----- : %s', order_item_results)
                    if resultval.get('Name'):
                        partner = partner_obj.with_context({'shop':self}).managepartner(resultval)
                        print("partnerpartner1111",partner)
                    else:
                        partner = self.partner_id
                        print("partnerpartner1145555",partner)
                    do = False
                    if resultval.get('PurchaseDate', False):
                        logger.info('PurchaseDate : %s', resultval.get('PurchaseDate'))
                        do = datetime.strptime(resultval.get('PurchaseDate'), "%Y-%m-%dT%H:%M:%S.%fZ")
                        print("dododo",do)
                        tz_name = self.env.context.get('tz') or self.env.user.tz
                        print("tz_name",tz_name)
                        today_utc = pytz.timezone(tz_name).localize(do, is_dst=False)
                        print("today_utc",today_utc)
                        do = today_utc.astimezone(pytz.timezone('UTC'))
                        print("dododo",do)
                        do = do - timedelta(hours=16,minutes=30)
                        
                    l_ship_date = False
                    if resultval.get('LatestShipDate', False):
                        l_ship_date = datetime.strptime(resultval.get('EarliestShipDate'), "%Y-%m-%dT%H:%M:%Sz")
                        tz_name = self.env.context.get('tz') or self.env.user.tz
                        today_utc = pytz.timezone(tz_name).localize(l_ship_date, is_dst=False)
                        l_ship_date = today_utc.astimezone(pytz.timezone('UTC'))
                        l_ship_date = l_ship_date - timedelta(hours=16,minutes=30)
                        print("l_ship_datel_ship_date",l_ship_date)

                    e_ship_date = False
                    if resultval.get('EarliestShipDate', False):
                        e_ship_date = datetime.strptime(resultval.get('EarliestShipDate'), "%Y-%m-%dT%H:%M:%Sz")
                        tz_name = self.env.context.get('tz') or self.env.user.tz
                        today_utc = pytz.timezone(tz_name).localize(e_ship_date, is_dst=False)
                        e_ship_date = today_utc.astimezone(pytz.timezone('UTC'))
                        e_ship_date = e_ship_date - timedelta(hours=16,minutes=30)
                        print("e_ship_datee_ship_date",e_ship_date)
                    ordervals = {
#                         'name': str((resultval.get('FulfillmentChannel') and (resultval.get('FulfillmentChannel') + '_')  or '') + resultval.get('AmazonOrderId', False) + (self.suffix and ('_' + self.prefix) or '')),
                        'partner_id': partner.id,
                        'date_order': do,
#                         'ext_payment_method': resultval.get('PaymentMethod'),
#                         'payment_method':payment_id.id,
                        'amazon_order_id': resultval.get('AmazonOrderId', False),
                        'fullfillment_method': str(resultval.get('FulfillmentChannel', False)),
                        'ship_service': resultval.get('ShipServiceLevel', False),
                        'ship_category' : resultval.get('ShipmentServiceLevelCategory', False),
                        'late_ship_date' : l_ship_date,
                        'shipped_by_amazon' : resultval.get('ShippedByAmazonTFM', False),
                        'order_type' : resultval.get('OrderType', False),
                        'amazon_order_status' : resultval.get('OrderStatus', False),
                        'earlier_ship_date' : e_ship_date,
                        'amazon_payment_method' : resultval.get('PaymentMethod', False),
                        'amazon_order': True,
                        'item_shipped': resultval.get('NumberOfItemsShipped') or '0',
                        'item_unshipped': resultval.get('NumberOfItemsUnshipped')or '0',
                        'carrier_id': False, #carrier_id and carrier_id.id or False,
                        'is_prime': resultval.get('IsPrime') == 'true' and True or False,
                        'shop_id' : self.id,
                        'team_id':self.amazon_sales_channel.id,
                        'pricelist_id' : self.pricelist_id.id,
                        'picking_policy': self.amazon_workflow_id and self.amazon_workflow_id.picking_policy or 'direct',
                        'state': 'draft',
                        'fiscal_position_id':self.amazon_fiscal_pid.id or False
                    }
                    if resultval.get('PaymentMethod'):
                        payment_ids = self.env['account.payment.method'].search([('code','=',resultval.get('PaymentMethod')),('payment_type','=','inbound')])
                        if payment_ids:
                            payment_id = payment_ids[0]
                        if not payment_ids:
                            payment_id = self.env['account.payment.method'].create({'payment_type':'inbound','name':resultval.get('PaymentMethod'), 'code':resultval.get('PaymentMethod')})
                        ordervals.update({'payment_method':payment_id.id})
                    print("ordervals",ordervals)
                    if resultval.get('FulfillmentChannel')=='AFN':
                        ordervals.update({'warehouse_id': self.afn_warehouse.id, 'name':('FBA' and ('FBA' + '_')  or '') + resultval.get('AmazonOrderId', False)})
                    else: 
                        ordervals.update({'warehouse_id': self.warehouse_id.id, 'name':('FBM' and ('FBM' + '_')  or '') + resultval.get('AmazonOrderId', False)})
                    if not len(order_item_results):
                        time.sleep(10)
                        order_item_results = amazon_api_obj.call(self, 'ListOrderItems', resultval['AmazonOrderId'])
                        if not order_item_results:
                            return False
                    print("ordervalsordervalsordervals",ordervals)
                    print("self.idself.idself.id",self.id)
                    saleorderid = saleorder_obj.create(ordervals)
                    saleorderid.onchange_partner_id()
                    
                    logger.info('Order Created with ID : %s', saleorderid)
                    # create line for Orders
                    if order_item_results:
                        self.manageAmazonOrderLine(saleorderid, order_item_results)
                else:
                    saleorderid = saleorderids[0]
                logger.info('%s Order Created with ID : %s ---> %s--->%s', count, saleorderid, resultval.get('AmazonOrderId'), resultval.get('OrderStatus'))
                count = count + 1
                if saleorderid.order_line:
                    if self.based_on_odoo_workflow:
                        self.manageAmazonOrderWorkflowBasedonOdoo(saleorderid, resultval)
#                     else:
#                         self.manageAmazonOrderWorkflow(saleorderid, resultval)
#                 else:
#                     if resultval.get('OrderStatus') == 'Canceled':
#                         saleorderid.action_cancel()
#                         logger.info('Order [%s] is Cancelled', saleorderid)
            self.env.cr.commit()
        return True
    
    def amazon_import_orders(self):
        for amazon_marketplace_obj in self:
            sale_order_obj = self.env['sale.order']
#             amazon_marketplace_obj.import_FBA_order_product()
#             orders = amazon_api_obj.call(amazon_marketplace_obj, 'GetOrder', ['026-2599874-3088304'])
#             logger.info("orders--------- %s", orders)
            try:
                if self._context.get('last_amazon_order_import_date'):
                    sdate = datetime.strptime(str(self._context.get('last_amazon_order_import_date')), "%Y-%m-%d %H:%M:%S")
                    sdate = sdate.replace(hour=0, minute=0, second=0)
                    sdate = sdate + timedelta(days=1,hours=4)
                    createdAfter = sdate.strftime("%Y-%m-%dT%H:%M:%S") + 'Z'
                elif amazon_marketplace_obj.last_amazon_order_import_date:
                    sdate = datetime.strptime(amazon_marketplace_obj.last_amazon_order_import_date, "%Y-%m-%d %H:%M:%S")
                    sdate = sdate.replace(hour=0, minute=0, second=0)
                    sdate = sdate + timedelta(days=1,hours=4)
                    print("sdatesdatesdatesdate",sdate)
                    createdAfter = sdate.strftime("%Y-%m-%dT%H:%M:%S") + 'Z'
                else:
                    earlier = datetime.now() - timedelta(days=120)
                    earlier_str = earlier.strftime("%Y-%m-%dT%H:%M:%S")
                    createdAfter = earlier_str + 'Z'
                    
                # Get Order From Amazon
                logger.info("createdAfter--------- %s", createdAfter)
                results = amazon_api_obj.call(amazon_marketplace_obj, 'ListOrders', createdAfter, False)
                logger.info("Orders------------------------- %s", len(results))
                if len(results) >= 1: 
                    error = results[0].get('Error')
                    if error:
                        continue
                if results:
                    amazon_marketplace_obj.AmazonCreateOrders(results)
                    last_dictionary = results[-1]
                    while last_dictionary.get('NextToken', False):
                        next_token = last_dictionary.get('NextToken', False)
                        del results[-1]
                        time.sleep(5)
                        # Get Next Page Order if available
                        result_next_token = amazon_api_obj.call(amazon_marketplace_obj, 'ListOrdersByNextToken', next_token)
                        logger.info("Order result_next_token--------- %s", len(result_next_token))
                        amazon_marketplace_obj.AmazonCreateOrders(result_next_token)
                        last_dictionary = result_next_token[-1]
                        if last_dictionary.get('NextToken', False) == False:
                            break
                sale_order_id = sale_order_obj.search([('amazon_order','=',True)],order="create_date desc", limit=1)
                print("sale_order_id",sale_order_id)
                if sale_order_id:
                    date_str = time.strftime(sale_order_id.date_order)
                    print("date_str",date_str)
                    date_str = datetime.strptime(sale_order_id.date_order, "%Y-%m-%d %H:%M:%S")
                    print("datetime_str",date_str)
                    user_tz = self.env.user.tz or pytz.utc
                    local_zone = pytz.timezone(user_tz)
                    last_amazon_import_date = pytz.utc.localize(date_str).astimezone(local_zone)
                    last_amazon_import_date = last_amazon_import_date - timedelta(hours=1,minutes=30)
                    print("last_amazon_import_date",last_amazon_import_date)
                    amazon_marketplace_obj.write({'last_amazon_order_import_date':last_amazon_import_date})
                    
                else:
                    date_str = time.strftime('%Y-%m-%d 00:00:00')
                    date_str = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    user_tz = self.env.user.tz or pytz.utc
                    local_zone = pytz.timezone(user_tz)
                    last_amazon_import_date = pytz.utc.localize(date_str).astimezone(local_zone)
                    last_amazon_import_date = last_amazon_import_date - timedelta(hours=1,minutes=30)
                    amazon_marketplace_obj.write({'last_amazon_order_import_date':last_amazon_import_date})
    #             self.env.cr.execute("UPDATE sale_shop SET last_amazon_order_import_date='%s' where id=%d" % (time.strftime('%Y-%m-%d %H:%M:%S'), amazon_marketplace_obj.id))
            except Exception as e:
                print ("eeeeeeeeeeeeeee", e)
                amazon_obj = self.env['amazon.log']
                sequence_id = self.env['ir.sequence'].next_by_code('amazon.log')
                ctx = self._context.copy()
                ctx.update({'log_sequence':sequence_id})
                ir_model_obj = self.env['ir.model']
                model_ids = ir_model_obj.search([('model','=','sale.order')])
                log_vals = {'name':sequence_id,
                            'res_model_id':model_ids.id,
                            'description':e,
                            'log_type':'import_order',
        #                     'res_id':,
                            'marketplace_id':amazon_marketplace_obj.id,
                            'create_date':datetime.today()}
                amazon_obj.create(log_vals)
            self.env.cr.commit() 
        return True


    def import_FBA_order_product(self):
        # Import amazon products
        for amazon_marketplace in self:
            # First we need to request for browse node report it will return request return id   
            StartDate = time.strftime("2015-%m-%dT%H:%M:%S", time.gmtime()) + '.000Z'
            RequestReportData = amazon_api_obj.call(amazon_marketplace, 'RequestReport', '_GET_AMAZON_FULFILLED_SHIPMENTS_DATA_',StartDate)
            if RequestReportData.get('ReportProcessingStatus', False):
                if RequestReportData.get('ReportProcessingStatus') == '_SUBMITTED_':
                    if RequestReportData.get('ReportRequestId'):
                        time.sleep(20)
                        # Once we get request report id then we need to be call GetReportList to get reort id for requested browse node report
                        logger.info("ReportRequestId %s", RequestReportData.get('ReportRequestId'))
                        GetReportRequestListData = amazon_api_obj.call(amazon_marketplace, 'GetReportRequestList', RequestReportData.get('ReportRequestId'), '_GET_AMAZON_FULFILLED_SHIPMENTS_DATA_')
                        if GetReportRequestListData.get('Error'):
                            continue
                        if GetReportRequestListData.get('status') == '_DONE_NO_DATA_':
                            continue
                        while not GetReportRequestListData.get('GeneratedReportId', False):
                            time.sleep(20)
                            GetReportRequestListData = amazon_api_obj.call(amazon_marketplace, 'GetReportRequestList', RequestReportData.get('ReportRequestId'), '_GET_AMAZON_FULFILLED_SHIPMENTS_DATA_')
                            logger.info("GetReportRequestListData Status %s", GetReportRequestListData.get('GeneratedReportId'))
                            if GetReportRequestListData.get('status') == '_DONE_NO_DATA_':
                                break
                            if GetReportRequestListData.get('Error'):
                                break
             
                        if GetReportRequestListData and GetReportRequestListData.get('GeneratedReportId', False):
                            time.sleep(30)
                            # Once will get report id will need to be call GetReport API to get browse node tree
                            prod_data_list = amazon_api_obj.call(amazon_marketplace, 'GetReport', GetReportRequestListData.get('GeneratedReportId'), '_GET_AMAZON_FULFILLED_SHIPMENTS_DATA_')
                            print ("prod_data_list", prod_data_list)
                            
                            logger.info('Products Count...........: %s', prod_data_list)
        return True

    
    def _my_value(self, location_id, product_id):
        self.env.cr.execute(
            'select sum(product_qty) '\
            'from stock_move '\
            'where location_id NOT IN  %s '\
            'and location_dest_id = %s '\
            'and product_id  = %s '\
            'and state = %s ', tuple([(location_id,), location_id, product_id, 'done']))
        wh_qty_recieved = self.env.cr.fetchone()[0] or 0.0
        # this gets the value which is sold and confirmed
        argumentsnw = [location_id, (location_id,), product_id, ('done',)]  # this will take reservations into account
        self.env.cr.execute(
            'select sum(product_qty) '\
            'from stock_move '\
            'where location_id = %s '\
            'and location_dest_id NOT IN %s '\
            'and product_id  = %s '\
            'and state in %s ', tuple(argumentsnw))
        qty_with_reserve = self._cr.fetchone()[0] or 0.0
        qty_available = wh_qty_recieved - qty_with_reserve
        return qty_available
    
    def form_update_inventory_xml(self, product_ids):
        # form Inventory Update XML
        inventory_xml = ''
        merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(self.amazon_instance_id.aws_merchant_id)
        location_id = self.warehouse_id.lot_stock_id.id
        message_information = ''
        message_id = 1
        
        # Added product and message id in xml
        for each_product in product_ids:
            message_information += """<Message><MessageID>%s</MessageID><OperationType>Update</OperationType><Inventory><SKU>%s</SKU><Quantity>%s</Quantity></Inventory></Message>""" % (message_id, each_product.default_code, int(each_product.qty_available))
            message_id = message_id + 1
            
        # add shop credential and set header and append product information for inventory update
        if message_information:
            inventory_xml =  """<?xml version="1.0" encoding="utf-8"?><AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd"><Header><DocumentVersion>1.01</DocumentVersion>%s</Header><MessageType>Inventory</MessageType>%s</AmazonEnvelope>"""%(merchant_string.encode("utf-8"), message_information.encode("utf-8"))
        return inventory_xml
    
    
    def xml_format(self, message_type, merchant_string, message_data):
        print("========message_datamessage_datamessage_data====>>>>>>>",message_data)
        return """<?xml version="1.0" encoding="utf-8"?>
            <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
            <Header>
            <DocumentVersion>1.01</DocumentVersion>%s
            </Header>%s%s
            </AmazonEnvelope>"""%(merchant_string.encode(), message_type.encode(), message_data.encode())
    
    
#             base64string= base64.encodestring(('%s:%s' %(key,value)).encode()).decode().replace('\n','')
    def update_inventory_on_amazon(self):
        #Update Inventory On Amazon
        prodcut_listing_obj = self.env['amazon.product.listing']
        
        for marketplace_instance_obj in self:
            if self._context.get('product_ids'):
                listing_ids = self._context.get('product_ids')
            else:
                listing_ids = prodcut_listing_obj.search([('shop_id','=',marketplace_instance_obj.id)])
            if listing_ids:
                inventory_xml = marketplace_instance_obj.form_update_inventory_xml(product_ids)
                if inventory_xml:
                    results = amazon_api_obj.call(marketplace_instance_obj, 'POST_INVENTORY_AVAILABILITY_DATA', inventory_xml[0])
                    if results.get('FeedSubmissionId',False):
                        time.sleep(70)
                        submission_results = amazon_api_obj.call(marketplace_instance_obj, 'GetFeedSubmissionResult',results.get('FeedSubmissionId',False))
                        if results.get('FeedSubmissionId', False):
                            logger.info("FeedSubmissionId %s", results.get('FeedSubmissionId'))
                            time.sleep(30)
                            submission_results = amazon_api_obj.call(self, 'GetFeedSubmissionResult', results.get('FeedSubmissionId', False))
                            logger.info("FeedSubbmission Result ID %s", submission_results)
#                         if submission_results.get('MessagesWithError',False) == '0':
#                             self.log(1, "Inventory Updated Successfully")
#                         else:
#                             if submission_results.get('ResultDescription',False):
#                                 error_message = submission_results.get('ResultDescription',False)
#                                 error_message = str(error_message).replace("'"," ")
#                                 self.log(1, error_message)
        self.write({'last_amazon_inventory_export_date':time.strftime('%Y-%m-%d %H:%M:%S')})
        return True
    
    def upload_zero_inventory_on_amazon(self):
        product_obj = self.env['product.product']
        
        for marketplace in self:
            message_count = 1
            merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(marketplace.amazon_instance_id.aws_merchant_id)
            message_type = '<MessageType>Inventory</MessageType>'
            str=""
            xml_data = ''
            if self._context.get('product_ids'):
                product_ids = self._context.get('product_ids')
                product_ids = product_obj.browse(product_ids)
            else:
                product_ids = product_obj.search([('asin','!=',False),('active','=',True)])

            for product_info in product_ids:
                if product_info.type == 'service':
                    continue
                if not product_info.name:
                    raise UserError(_('Error'), _('Please enter Product SKU for Image Feed "%s"'% (product_info.name)))
                
                parent_sku = product_info.default_code
                latency = 1
                if product_info.supplier_name and product_info.supplier_name.comment:
                    latency = product_info.supplier_name.comment

                inventory = 0
                fulfillment_by = 'MFN'
                if fulfillment_by != 'AFN':
                    update_xml_data = '''<SKU>%s</SKU>
                                        <Quantity>%s</Quantity>
                                        <FulfillmentLatency>%s</FulfillmentLatency>'''%(parent_sku,inventory,latency)
                else:
                    update_xml_data = '''<SKU>%s</SKU>
                                        <FulfillmentCenterID>AMAZON_NA</FulfillmentCenterID>
                                        <Lookup>FulfillmentNetwork</Lookup>
                                        <SwitchFulfillmentTo>AFN</SwitchFulfillmentTo>'''%(parent_sku)
                xml_data += '''<Message>
                            <MessageID>%s</MessageID><OperationType>Update</OperationType>
                            <Inventory>%s</Inventory></Message>
                        '''% (message_count,update_xml_data)

                #Uploading Product Inventory Feed
                message_count+=1
            str = """<?xml version="1.0" encoding="utf-8"?>
                    <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
                    <Header>
                    <DocumentVersion>1.01</DocumentVersion>
                    """+merchant_string+"""
                    </Header>
                    """+message_type+xml_data+"""
                    """
            str +="""</AmazonEnvelope>"""

            product_submission_id = amazon_api_obj.call(marketplace, 'POST_INVENTORY_AVAILABILITY_DATA',str)
            print ("********************",product_submission_id)
            if not product_submission_id.get('FeedSubmissionId',False):
                product_submission_id = amazon_api_obj.call(marketplace, 'POST_INVENTORY_AVAILABILITY_DATA',str)
                time.sleep(80)
                submission_results = amazon_api_obj.call(marketplace, 'GetFeedSubmissionResult',product_submission_id.get('FeedSubmissionId',False))
                print ("===submission_results====>",submission_results)
            else:
                time.sleep(80)
                submission_results = amazon_api_obj.call(marketplace, 'GetFeedSubmissionResult',product_submission_id.get('FeedSubmissionId',False))
                print ("===submission_results====>",submission_results)
        return True
    
    def form_update_image_xml(self, recent_image_ids):
        print ("recent_image_ids",recent_image_ids)
        #FORM update image xml for product
        upload_image_xml =''
        merchant_string = "<MerchantIdentifier>%s</MerchantIdentifier>" % (self.amazon_instance_id.aws_merchant_id)
        message_information = ''
        message_id = 1
        for each_image_id in recent_image_ids:
            print( "each_image_id",each_image_id)
            message_information +=  """<Message><MessageID>%s</MessageID><OperationType>Update</OperationType><ProductImage><SKU>%s</SKU><ImageType>Main</ImageType><ImageLocation>%s</ImageLocation></ProductImage></Message>""" % (message_id, each_image_id.product_id.default_code, each_image_id.amazon_url_location)
            message_id += 1
        if message_information:
            upload_image_xml = """<?xml version="1.0" encoding="utf-8"?>
                                <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
                                    <Header>
                                        <DocumentVersion>1.01</DocumentVersion>""" + merchant_string.encode("utf-8") + """
                                    </Header>
                                    <MessageType>ProductImage</MessageType>""" + message_information.encode("utf-8") + """
                                </AmazonEnvelope>"""
        return upload_image_xml

    def update_images_on_amazon(self):
        prodcut_listing_obj = self.env['amazon.product.listing']
        product_image_obj = self.env['product.images']
        product_obj = self.env['product.product']
        print("contexcts", self._context)
        recent_image_ids = []
        for marketplace_instance_obj in self:
            listing_id = prodcut_listing_obj.search([('shop_id','=',marketplace_instance_obj.id), ('product_id.amazon_prod_status', '=', 'active'), ('product_id.amazon_export', '=', True)])
            product_ids = [listing.product_id.id for listing in listing_id]
            recent_image_ids = product_image_obj.search([('write_date', '>', self.last_amazon_image_export_date), ('product_id', 'in', product_ids)])
            upload_image_xml = marketplace_instance_obj.form_update_image_xml(recent_image_ids)
            if upload_image_xml:
                results = amazon_api_obj.call(marketplace_instance_obj, 'POST_PRODUCT_IMAGE_DATA', upload_image_xml)
                if results.get('FeedSubmissionId', False):
                    logger.info("FeedSubmissionId %s", results.get('FeedSubmissionId'))
                    time.sleep(30)
                    submission_results = amazon_api_obj.call(self, 'GetFeedSubmissionResult', results.get('FeedSubmissionId', False))
                    logger.info("FeedSubbmission Result ID %s", submission_results)
#                     if submission_results.get('MessagesWithError', False) == '0':
#                         self.log(1, 'Images Updated Successfully')
#                     else:
#                         if submission_results.get('ResultDescription', False):
#                             error_message = submission_results.get('ResultDescription', False)
#                             error_message = str(error_message).replace("'", " ")
        self._cr.execute("UPDATE stock_warehouse SET last_amazon_image_export_date='%s' where id=%d" % (time.strftime('%Y-%m-%d %H:%M:%S'), self[0].id))
        return True
    
    def upload_shipping_price(self):
        product_obj = self.env['product.product']
        for marketplace in self:
            message=''
            xml_data=''
            
            if self._context.get('prodduct_ids'):
                prod_id = product_obj.browse(self._context.get('prodduct_ids'))
            else:
                prod_id = product_obj.search([])
            main_str = """<?xml version="1.0" encoding="utf-8"?>
                                <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
                                <Header>
                                <DocumentVersion>1.02</DocumentVersion>
                                <MerchantIdentifier>A2OIS37VLRG8C5</MerchantIdentifier>
                                </Header>
                                <MessageType>Override</MessageType>"""
            message_count = 1
            for product_data in prod_id:
                for supplier_id in product_data.seller_ids:
                    prize = supplier_id.name.estimated_shipping_price
                    if prize:
                        xml_data += '''<Message>
                            <MessageID>%s</MessageID><OperationType>Update</OperationType>
                            <Override>
                                <SKU>%s</SKU>
                                <ShippingOverride>
                                <ShipAmount currency="USD">%s</ShipAmount></ShippingOverride></Override></Message>'''%(message_count, product_data.default_code, prize)
                        message_count+=1
    
        #Uploading Product Inventory Feed
            message += main_str + xml_data + """</AmazonEnvelope>"""
            product_submission_id = amazon_api_obj.call(marketplace, 'POST_PRODUCT_OVERRIDES_DATA',message)
            print( product_submission_id)
            if product_submission_id.get('FeedSubmissionId',False):
                time.sleep(80)
                submission_results = amazon_api_obj.call(marketplace, 'GetFeedSubmissionResult',product_submission_id.get('FeedSubmissionId',False))
                print (submission_results)
        return True
    
    def form_order_update_xml(self, orders):
        message_information = ''
        message_id = 1
        for order in orders:
            if not order.shipping_service1:
                print ("Need to select Shipping Services")
            for each_line in order.order_line:
                if not each_line.product_id.type == 'service' and order.picking_ids:
                    item_string = '''<Item><AmazonOrderItemCode>%s</AmazonOrderItemCode>
                                    <Quantity>%s</Quantity></Item>''' % (each_line.order_item_id, int(each_line.product_uom_qty))
                    
                    earlier = datetime.now() - timedelta(minutes=10)
                    earlier_str = earlier.strftime("%Y-%m-%dT%H:%M:%S")
                    fulfillment_date_concat = str(earlier_str) + '-00:00'
                    message_information += """<Message>
                                           <MessageID>%s</MessageID>
                                           <OperationType>Update</OperationType>
                                           <OrderFulfillment><AmazonOrderID>%s</AmazonOrderID>
                                           <FulfillmentDate>%s</FulfillmentDate>
                                           <FulfillmentData>
                                           <CarrierName>%s</CarrierName>
                                           <ShippingMethod>%s</ShippingMethod>
                                           <ShipperTrackingNumber></ShipperTrackingNumber>
                                           </FulfillmentData>%s</OrderFulfillment>
                                               </Message>""" % (message_id, order.amazon_order_id, fulfillment_date_concat, order.shipping_service1, order.shipping_service1, item_string.encode("utf-8"))
                                              # general for all (message_id, order.amazon_order_id, fulfillment_date_concat, order.picking_ids[0].carrier_id.name.split(' ')[0], order.picking_ids[0].carrier_id.name.split(' ')[0], order.picking_ids[0].carrier_tracking_ref, item_string.encode("utf-8"))
                    message_id = message_id + 1
#         form_order_xml = """<?xml version="1.0" encoding="utf-8"?><AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd"><Header><DocumentVersion>1.01</DocumentVersion><MerchantIdentifier>M_SELLERON_82825133</MerchantIdentifier></Header><MessageType>OrderFulfillment</MessageType>""" + message_information.encode("utf-8") + """</AmazonEnvelope>"""
        form_order_xml = """<?xml version="1.0" encoding="utf-8"?><AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd"><Header><DocumentVersion>1.01</DocumentVersion><MerchantIdentifier>%s</MerchantIdentifier></Header><MessageType>OrderFulfillment</MessageType>%s</AmazonEnvelope>"""%(self.amazon_instance_id.aws_merchant_id, message_information.encode("utf-8"),)
        return form_order_xml
    
    def update_amazon_orders(self):
        saleorder_obj = self.env['sale.order']
        for marketplace in self:
            saleorder_ids = []
            if self._context.get('order_ids'):
                saleorder_ids = saleorder_obj.browse(self._context.get('order_ids'))
            else:
                last_amazon_update_order_export_date = marketplace.last_amazon_update_order_export_date
                saleorder_ids = saleorder_obj.search([('state', '=', 'done'), ('shop_id', '=', marketplace.id), ('amazon_order_id', '!=', False), ('shipping_service1', '!=', False)])
#             saleorder_ids = saleorder_obj.search([('id', '=', 1003)])
            print ("===========saleorder_ids=====>",saleorder_ids)
            if saleorder_ids:
                form_order_xml = marketplace.form_order_update_xml(saleorder_ids)  
                print( "=======>",form_order_xml)
                logger.info("Order Update status XML Feed %s", form_order_xml)
                if form_order_xml:
                    results = amazon_api_obj.call(self, 'POST_ORDER_FULFILLMENT_DATA', form_order_xml[0])
                    if results.get('FeedSubmissionId', False):
                        logger.info("FeedSubmissionId %s", results.get('FeedSubmissionId'))
                        time.sleep(30)
                        submission_results = amazon_api_obj.call(self, 'GetFeedSubmissionResult', results.get('FeedSubmissionId', False))
                        logger.info("FeedSubbmission Result ID %s", submission_results)
#                         if submission_results.get('Error') == None:
#                             submission_id = results.get('FeedSubmissionId')
#                             order.write({'shipping_submission_feedid' : submission_id})
#                         else:
#                             if submission_results.get('ResultDescription', False):
#                                 error_message = submission_results.get('ResultDescription', False)
#                                 error_message = str(error_message).replace("'", " ")
            self.env.cr.execute("UPDATE sale_shop SET last_amazon_update_order_export_date='%s' where id=%d" % (time.strftime('%Y-%m-%d %H:%M:%S'), marketplace.id))
        return True
    
    def cancel_amazon_orders(self, cancel_reason=''):
        sale_obj = self.env['sale.order']
        for marketplace in self:
            if self._context.get('active_ids'):
                order_ids = self._context.get('active_ids')
                order_ids = sale_obj.browse(order_ids)
            else:
                order_ids = sale_obj.search([('state', '=', 'cancel')])
            for sale_id in order_ids:
                amazon_orderlisting_ids= sale_id.amazon_orderlisting_ids
                for amazon_orderlisting_id in amazon_orderlisting_ids:
                    instance_obj = amazon_orderlisting_id.shop_id.amazon_instance_id
                    data = """<?xml version="1.0"?>
                    <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                    xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
                    <Header>
                    <DocumentVersion>1.01</DocumentVersion>
                    </Header>
                    <MessageType>OrderAcknowledgement</MessageType>
                    <Message>
                    <MessageID>1</MessageID>
                    <OrderAcknowledgement>
                    <AmazonOrderID>"""+ sale_id.amazon_order_id+ """"</AmazonOrderID>
                    <StatusCode>Failure</StatusCode>
                    <CancelReason>"""+cancel_reason+"""</CancelReason>
                    </OrderAcknowledgement>
                    </Message>
                    </AmazonEnvelope>"""
                    print ("data", data)
                    if data:
                        os.chdir("/tmp")
                        text_file = open("cancel_amazon.txt", "w")
                        text_file.write(data)
                        text_file.close()
                        self.__logger.info('data %s', data)
                        results = amazon_api_obj.call(sale_id.shop_id, ' _POST_ORDER_ACKNOWLEDGEMENT_DATA_',data)
                        self.__logger.info('results %s', results)
                        os.chdir("/tmp")
                        text_file = open("cancel_amazon_results.txt", "w")
                        text_file.write(results)
                        text_file.close()
        return True
    
    def update_amazon_product_price(self):
        product_listing_obj = self.env['amazon.product.listing']
        
        for marketplace in self:
            product_tem_ids = prod_tmpl_obj.search([('amazon_product','=',True),('amazon_export','=',True)],offset, 5000, 'id')
            for product_tem in product_tem_ids:
                message_id = 1
                price_string = ''
                merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(marketplace.amazon_instance_id.aws_merchant_id)
                price_str = """<MessageType>Price</MessageType>"""
                for amazon_list_data in listing_ids:
                    
                    data = amazon_list_data.product_id.with_context(pricelist=marketplace.pricelist_id.id, price_data=6000).price
                    print ("====amazon_list_data.price========>",data)
                
                
#                 
                    if float(amazon_list_data.price) != 0.0:
                        price_string +="""<Message><MessageID>%s</MessageID><Price><SKU>%s</SKU><StandardPrice currency="%s">%.2f</StandardPrice></Price></Message>"""% (message_id, amazon_list_data.default_code, marketplace.res_currency.name,amazon_list_data.price)
                        message_id += 1

                    price_data = marketplace.xml_format(price_str, merchant_string, price_string)
                    results = amazon_api_obj.call(marketplace, 'POST_PRODUCT_PRICING_DATA',price_data[0].replace('\n',''))
                    if results.get('FeedSubmissionId', False):
                         logger.info("FeedSubmissionId %s", results.get('FeedSubmissionId'))
                         time.sleep(60)
                         submission_results = amazon_api_obj.call(self, 'GetFeedSubmissionResult', results.get('FeedSubmissionId', False))
                         logger.info("FeedSubbmission Result ID %s", submission_results)
    
    #Export Product on amazon
    
    def export_simple_product(self, product_tem_data,marketplace): 
        release_date = datetime.now()
        product_obj = self.env['product.product']
        merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(marketplace.amazon_instance_id.aws_merchant_id)
        release_date = release_date.strftime("%Y-%m-%dT%H:%M:%S")
        date_string = """<LaunchDate>%s</LaunchDate>
                 <ReleaseDate>%s</ReleaseDate>"""%(release_date,release_date)
        message_information = ''
        message_id = 1
        standard_product_string=''
        desc = ''
        bullet_points = ''
        item_type = product_tem_data.item_type
        if product_tem_data.name:
            title = product_tem_data.name
        product_str = """<MessageType>Product</MessageType>
                        <PurgeAndReplace>false</PurgeAndReplace>"""
#         print "product_str", product_str
        
#                 if not product_tem_data.tmp_asin:
#                     raise UserError(_('Error'), _('ASIN Required!!'))
        if product_tem_data.ean_barcode:
            standard_product_string = """
                <StandardProductID>
                <Type>EAN</Type>
                <Value>%s</Value>
                </StandardProductID>
                """%(product_tem_data.ean_barcode)
        if product_tem_data.upc_temp:
            standard_product_string = """
            <StandardProductID>
            <Type>UPC</Type>
            <Value>%s</Value>
            </StandardProductID>
            """%(product_tem_data.upc_temp)
        if product_tem_data.tmp_asin:
            standard_product_string = """
            <StandardProductID>
            <Type>ASIN</Type>
            <Value>%s</Value>
            </StandardProductID>
            """%(product_tem_data.tmp_asin)
        
        message_information +="""<Message><MessageID>%s</MessageID>
                                                <OperationType>Update</OperationType>
                                                <Product>
                                                <SKU>%s</SKU>%s
                                                <ProductTaxCode>A_GEN_NOTAX</ProductTaxCode>
                                                %s<DescriptionData>
                                                <Title><![CDATA[%s]]></Title>"""%(message_id,product_tem_data.amazon_sku,standard_product_string,date_string,title)
#         print"message_information",message_information
        if product_tem_data.brand_name:
            message_information += """<Brand><![CDATA[%s]]></Brand>"""%(product_tem_data.brand_name)
       
        if product_tem_data.description_sale:
            sale_description = product_tem_data.description_sale
            if sale_description:
                message_information += """<Description><![CDATA[%s]]></Description>"""%(sale_description)
        bullets = ''
        if product_tem_data.bullet_point:
            for bullet_point in product_tem_data.bullet_point:
                bullets += """<BulletPoint><![CDATA[%s]]></BulletPoint>"""%(bullet_point.bullet)
            message_information += bullets
            
        if product_tem_data.amazon_manufacturer:
            message_information +="""<Manufacturer><![CDATA[%s]]></Manufacturer>"""%(product_tem_data.amazon_manufacturer)
#                 message_information += desc
        search_term = ''
        if product_tem_data.search_keywords:
            for searchterm_data in product_tem_data.search_keywords:
                search_term += """<SearchTerms><![CDATA[%s]]></SearchTerms>""" %(searchterm_data.searchterm)
            message_information += search_term
            
        if product_tem_data.item_type:  
            message_information += """<ItemType>%s</ItemType>""" %(item_type)
        message_information +="""<IsGiftWrapAvailable>false</IsGiftWrapAvailable>"""
        message_information +="""<IsGiftMessageAvailable>false</IsGiftMessageAvailable>"""
#         print"message_information",message_information
        if product_tem_data.amazon_categ_id:
            message_information += """<RecommendedBrowseNode>%s</RecommendedBrowseNode>"""%(product_tem_data.amazon_categ_id.amazon_cat_id)
        message_information +="""</DescriptionData>"""
        productData=''
        
        xml_product_type =''
        classification = ''
        if product_tem_data.product_data == 'AutoAccessory':
           xml_product_type = prod_tmpl_obj.Auto_xml(product_tem_data)
        elif product_tem_data.product_data == 'Baby':
           xml_product_type += prod_tmpl_obj.ToysBaby_xml(product_tem_data)
        elif product_tem_data.product_data == 'CameraPhoto':
            xml_product_type += prod_tmpl_obj.CameraPhoto_xml(product_tem_data)
        elif product_tem_data.product_data == 'Clothing':
            xml_product_type += ''
            classification = prod_tmpl_obj.Clothing_xml(product_tem_data)
        elif product_tem_data.product_data == 'CE':
            xml_product_type += prod_tmpl_obj.ce_xml(product_tem_data)
        elif product_tem_data.product_data == 'Computers':
            xml_product_type += prod_tmpl_obj.Computers_xml(product_tem_data)
        elif product_tem_data.product_data == 'FoodAndBeverages':
            xml_product_type += prod_tmpl_obj.FoodAndBeverages_xml(product_tem_data)
        elif product_tem_data.product_data == 'Gourmet':
            xml_product_type +=prod_tmpl_obj.Gourmet_xml(product_tem_data)
            #xml_product_type += products.product_data
        elif product_tem_data.product_data == 'Health':
            xml_product_type += prod_tmpl_obj.Health_xml(product_tem_data)
        elif product_tem_data.product_data == 'HomeImprovement':
            xml_product_type += prod_tmpl_obj.HomeImprovement_xml(product_tem_data)
        elif product_tem_data.product_data == 'FoodServiceAndJanSan':
            xml_product_type += prod_tmpl_obj.FoodServiceAndJanSan_xml(product_tem_data)
        elif product_tem_data.product_data == 'LabSupplies':
            xml_product_type += prod_tmpl_obj.LabSupplies_xml(product_tem_data)
        elif product_tem_data.product_data == 'PowerTransmission':
            xml_product_type += prod_tmpl_obj.PowerTransmission_xml(product_tem_data)
        elif product_tem_data.product_data == 'RawMaterials':
            xml_product_type += prod_tmpl_obj.RawMaterials_xml(product_tem_data)
        elif product_tem_data.product_data == 'Jewelry':
            xml_product_type += prod_tmpl_obj.Jewelry_xml(product_tem_data)
        elif product_tem_data.product_data == 'Lighting':
            xml_product_type += prod_tmpl_obj.Lighting_xml(product_tem_data)
        elif product_tem_data.product_data == 'MusicalInstruments':
            xml_product_type += prod_tmpl_obj.MusicalInstruments_xml(product_tem_data)
        elif product_tem_data.product_data == 'PetSupplies':
            xml_product_type += prod_tmpl_obj.PetSupplies_xml(product_tem_data)
        elif product_tem_data.product_data == 'Shoes':
            xml_product_type += prod_tmpl_obj.Shoes_xml(product_tem_data)
        elif product_tem_data.product_data == 'Wireless':
            xml_product_type += prod_tmpl_obj.Wireless_xml(product_tem_data)
        elif product_tem_data.product_data == 'Sports':
            xml_product_type += prod_tmpl_obj.Sport_xml(product_tem_data)
        elif product_tem_data.product_data == 'SportsMemorabilia':
            xml_product_type += prod_tmpl_obj.sportsmemorabilia_xml(product_tem_data)
        elif product_tem_data.product_data == 'TiresAndWheels':
            xml_product_type += prod_tmpl_obj.tiresandwheels_xml(product_tem_data)
        elif product_tem_data.product_data == 'Tools':
            xml_product_type += prod_tmpl_obj.Tools_xml(product_tem_data)
        elif product_tem_data.product_data == 'Toys':
            xml_product_type += prod_tmpl_obj.toys_xml(product_tem_data)
        elif product_tem_data.product_data == 'Video':
            xml_product_type += prod_tmpl_obj.Video_xml(product_tem_data)
        elif product_tem_data.product_data == 'LargeAppliances':
            xml_product_type += prod_tmpl_obj.LargeAppliances_xml(product_tem_data) 
#                 
        if xml_product_type:
            message_information +="""</DescriptionData>
                                <ProductData>
                                <%s>
                               <ProductType>
                                <%s>
                                </%s>
                               </ProductType>
                              </%s>
                              </ProductData>
                              """
        if not xml_product_type:
            message_information +="""</DescriptionData>
                                <ProductData>%s
                                <%s>
                              """%(classification)
            
        message_information +="""</%s>
                          </ProductData>
                          """%(productData)
        message_information += """</Product>
                                        </Message>"""                         
        product_data_xml = marketplace.xml_format(product_str, merchant_string, message_information)
        print("<<<<<<<<<<<<<<<<product_template_xml>>>>>>>>>>>>>>>",product_data_xml)
        if product_data_xml:
            product_submission_id = amazon_api_obj.call(marketplace, 'POST_PRODUCT_DATA',product_data_xml[0])
            print("product_<<<<template>>>>>submission_id",product_submission_id)
            price = product_obj.StandardSalePrice([],marketplace,product_tem_data)
            image = product_obj.UpdateAmazonImages([],marketplace,product_tem_data)
#             inventory = product_obj.UpdateAmazonInventory([],marketplace,product_tem_data)
            amazon_exp = product_tem_data.write({'amazon_export': False})

    def export_amazon_products(self):
        product_listing_obj = self.env['amazon.product.listing']
        prod_tmpl_obj = self.env['product.template']
        product_obj = self.env['product.product']
        for marketplace in self:
            standard_product_string = ''
            merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(marketplace.amazon_instance_id.aws_merchant_id)
            offset = 0
            print("merchant_string",merchant_string)
            if self._context.get('product_ids'):
                product_tem_ids = prod_tmpl_obj.browse(self._context.get('product_ids'))
            elif self._context.get('from_update_product'):
#           ei      prod_id = product_obj.browse(self._context.get('prodduct_ids'))
                product_tem_ids = prod_tmpl_obj.search([('amazon_product','=',True),('amazon_export','=',False),('write_date','>',marketplace.last_product_update_date)])
                print("product_tem_ids",product_tem_ids)
            else:
                product_tem_ids = prod_tmpl_obj.search([('amazon_product','=',True),('amazon_export','=',True)])
            if not product_tem_ids: break
            offset += len(product_tem_ids)
            release_date = datetime.now()
            release_date = release_date.strftime("%Y-%m-%dT%H:%M:%S")
            date_string = """<LaunchDate>%s</LaunchDate>
                     <ReleaseDate>%s</ReleaseDate>"""%(release_date,release_date)
            message_information = ''
            message_id = 1
            for product_tem_data in product_tem_ids:
                if not product_tem_data.attribute_line_ids:
                    self.export_simple_product(product_tem_data,marketplace)
                else:
                    desc = ''
                    bullet_points = ''
                    item_type = product_tem_data.item_type
                    if product_tem_data.name:
                        title = product_tem_data.name
                    product_str = """<MessageType>Product</MessageType>
                                    <PurgeAndReplace>false</PurgeAndReplace>"""
                    print ("product_str", product_str)
                    
                    if product_tem_data.description_sale:
                        sale_description = product_tem_data.description_sale
                        if sale_description:
                            desc = """<Description><![CDATA[%s]]></Description>"""%(sale_description)
    
    #                 if not product_tem_data.tmp_asin:
    #                     raise UserError(_('Error'), _('ASIN Required!!'))
                    if product_tem_data.ean_barcode:
                        standard_product_string = """
                            <StandardProductID>
                            <Type>EAN</Type>
                            <Value>%s</Value>
                            </StandardProductID>
                            """%(product_tem_data.ean_barcode)
                    elif product_tem_data.upc_temp:
                        standard_product_string = """
                        <StandardProductID>
                        <Type>UPC</Type>
                        <Value>%s</Value>
                        </StandardProductID>
                        """%(product_tem_data.upc_temp)
                    else:
                        standard_product_string = """
                        <StandardProductID>
                        <Type>ASIN</Type>
                        <Value>%s</Value>
                        </StandardProductID>
                        """%(product_tem_data.tmp_asin)
                    
                    message_information += """<Message><MessageID>%s</MessageID>
                                                <OperationType>Update</OperationType>
                                                <Product>
                                                <SKU>%s</SKU>
                                                <ProductTaxCode>A_GEN_NOTAX</ProductTaxCode>
                                                %s<DescriptionData>
                                                <Title><![CDATA[%s]]></Title>"""%(message_id,product_tem_data.amazon_sku,date_string,title)
                    
                    if product_tem_data.brand_name:
                        message_information += """<Brand>%s</Brand>"""%(product_tem_data.brand_name)
                        
                    message_information += desc
                    bullets = ''
                    if product_tem_data.bullet_point:
                        for bullet_point in product_tem_data.bullet_point:
                            bullets += """<BulletPoint><![CDATA[%s]]></BulletPoint>"""%(bullet_point.bullet)
                        message_information += bullets
                        
                    if product_tem_data.amazon_manufacturer:
                        message_information +="""<Manufacturer><![CDATA[%s]]></Manufacturer>"""%(product_tem_data.amazon_manufacturer)
    #                 message_information += desc
                    search_term = ''
                    if product_tem_data.search_keywords:
                        for searchterm_data in product_tem_data.search_keywords:
                            search_term += """<SearchTerms><![CDATA[%s]]></SearchTerms>""" %(searchterm_data.searchterm)
                        message_information += search_term
                        
                    item_type = ''
                    if product_tem_data.item_type:  
                        message_information += """<ItemType>%s</ItemType>""" %(product_tem_data.item_type)
                    message_information +="""<IsGiftWrapAvailable>false</IsGiftWrapAvailable>"""
                    message_information +="""<IsGiftMessageAvailable>false</IsGiftMessageAvailable>"""
                    if product_tem_data.amazon_categ_id:
                        message_information += """<RecommendedBrowseNode>%s</RecommendedBrowseNode>""" %(product_tem_data.amazon_categ_id.amazon_cat_id)
                        
    #                 message_information +="""<MSRP currency="%s">%s</MSRP>""" %(marketplace.res_currency.name, product_tem_data.list_price)
#                     if product_tem_data.attribute_line_ids:
#                         variationtheme = ''
#                         for variation in product_tem_data.attribute_line_ids:
#                             if variationtheme:
#                                 variationtheme = variationtheme +'-'+variation.attribute_id.name
#                             else:
#                                 variationtheme = variation.attribute_id.name  
                                
                                
                    xml_product_type =''
                    classification = ''
                    if product_tem_data.product_data == 'AutoAccessory':
                       xml_product_type = prod_tmpl_obj.Auto_xml(product_tem_data)
                    elif product_tem_data.product_data == 'Baby':
                       xml_product_type += prod_tmpl_obj.ToysBaby_xml(product_tem_data)
                    elif product_tem_data.product_data == 'CameraPhoto':
                        xml_product_type += prod_tmpl_obj.CameraPhoto_xml(product_tem_data)
                    elif product_tem_data.product_data == 'Clothing':
                        xml_product_type += ''
                        classification = prod_tmpl_obj.Clothing_xml(product_tem_data)
                    elif product_tem_data.product_data == 'CE':
                        xml_product_type += prod_tmpl_obj.ce_xml(product_tem_data)
                    elif product_tem_data.product_data == 'Computers':
                        xml_product_type += prod_tmpl_obj.Computers_xml(product_tem_data)
                    elif product_tem_data.product_data == 'FoodAndBeverages':
                        xml_product_type += prod_tmpl_obj.FoodAndBeverages_xml(product_tem_data)
                    elif product_tem_data.product_data == 'Gourmet':
                        xml_product_type +=prod_tmpl_obj.Gourmet_xml(product_tem_data)
                        #xml_product_type += products.product_data
                    elif product_tem_data.product_data == 'Health':
                        xml_product_type += prod_tmpl_obj.Health_xml(product_tem_data)
                    elif product_tem_data.product_data == 'HomeImprovement':
                        xml_product_type += prod_tmpl_obj.HomeImprovement_xml(product_tem_data)
                    elif product_tem_data.product_data == 'FoodServiceAndJanSan':
                        xml_product_type += prod_tmpl_obj.FoodServiceAndJanSan_xml(product_tem_data)
                    elif product_tem_data.product_data == 'LabSupplies':
                        xml_product_type += prod_tmpl_obj.LabSupplies_xml(product_tem_data)
                    elif product_tem_data.product_data == 'PowerTransmission':
                        xml_product_type += prod_tmpl_obj.PowerTransmission_xml(product_tem_data)
                    elif product_tem_data.product_data == 'RawMaterials':
                        xml_product_type += prod_tmpl_obj.RawMaterials_xml(product_tem_data)
                    elif product_tem_data.product_data == 'Jewelry':
                        xml_product_type += prod_tmpl_obj.Jewelry_xml(product_tem_data)
                    elif product_tem_data.product_data == 'Lighting':
                        xml_product_type += prod_tmpl_obj.Lighting_xml(product_tem_data)
                    elif product_tem_data.product_data == 'MusicalInstruments':
                        xml_product_type += prod_tmpl_obj.MusicalInstruments_xml(product_tem_data)
                    elif product_tem_data.product_data == 'PetSupplies':
                        xml_product_type += prod_tmpl_obj.PetSupplies_xml(product_tem_data)
                    elif product_tem_data.product_data == 'Shoes':
                        xml_product_type += prod_tmpl_obj.Shoes_xml(product_tem_data)
                    elif product_tem_data.product_data == 'Wireless':
                        xml_product_type += prod_tmpl_obj.Wireless_xml(product_tem_data)
                    elif product_tem_data.product_data == 'Sports':
                        xml_product_type += prod_tmpl_obj.Sport_xml(product_tem_data)
                    elif product_tem_data.product_data == 'SportsMemorabilia':
                        xml_product_type += prod_tmpl_obj.sportsmemorabilia_xml(product_tem_data)
                    elif product_tem_data.product_data == 'TiresAndWheels':
                        xml_product_type += prod_tmpl_obj.tiresandwheels_xml(product_tem_data)
                    elif product_tem_data.product_data == 'Tools':
                        xml_product_type += prod_tmpl_obj.Tools_xml(product_tem_data)
                    elif product_tem_data.product_data == 'Toys':
                        xml_product_type += prod_tmpl_obj.toys_xml(product_tem_data)
                    elif product_tem_data.product_data == 'Video':
                        xml_product_type += prod_tmpl_obj.Video_xml(product_tem_data)
                    elif product_tem_data.product_data == 'LargeAppliances':
                        xml_product_type += prod_tmpl_obj.LargeAppliances_xml(product_tem_data) 
                        
                    if xml_product_type:   
                        message_information +="""  </DescriptionData>
                                                        <ProductData>
                                                        <%s>
                                                       <ProductType>
                                                        <%s>
                                                        <VariationData>
                                                        <Parentage>parent</Parentage>
                                                        <VariationTheme>%s</VariationTheme> 
                                                        </VariationData>
                                                        </%s>
                                                       </ProductType>
                                                      </%s>
                                                      </ProductData>
                                                      """%(product_tem_data.product_data,xml_product_type,product_tem_data.variationtheme,xml_product_type,product_tem_data.product_data)
                    if not xml_product_type: 
                        message_information +="""  </DescriptionData>
                                                        <ProductData>
                                                        <%s>
                                                        <VariationData>
                                                        <Parentage>parent</Parentage>
                                                        <VariationTheme>%s</VariationTheme> 
                                                        </VariationData>
                                                        <ClassificationData>
                                                        <ClothingType>%s</ClothingType>      
                                                         <Department>%s</Department>  
                                                        <ColorMap>%s</ColorMap>
                                                        </ClassificationData>
                                                      </%s>
                                                      """%(product_tem_data.product_data,product_tem_data.variationtheme,product_tem_data.cloth_type,product_tem_data.department_temp_name,product_tem_data.product_data)
                        
                    message_information += """</ProductData>
                                                </Product>
                                                </Message>"""
                    product_ids = product_obj.search([('product_tmpl_id','=',product_tem_data.id)])
                    if product_ids:
                        message_information1 = product_obj.ExportVarients(product_ids,marketplace,message_id)
                          
                        message_information += message_information1
#                         print"message_information????????",message_information
                    product_data_xml = marketplace.xml_format(product_str, merchant_string, message_information)
                    print("<<<<<<<<<<<<<<<<product_template_xml>>>>>>>>>>>>>>>",product_data_xml)
                    logger.info("product_template_xml%s"%(product_data_xml))
                    if product_data_xml:
                        product_submission_id = amazon_api_obj.call(marketplace, 'POST_PRODUCT_DATA',product_data_xml[0])
                        print("product_<<<<template>>>>>submission_id",product_submission_id)
                        if product_submission_id:
                            if product_tem_data.amazon_export:
                                variant = product_obj.RelateVarients(product_ids,marketplace,product_tem_data)
#                                 inventory = product_obj.UpdateAmazonInventory(product_ids,marketplace,product_tem_data)
                                price = product_obj.StandardSalePrice(product_ids,marketplace,product_tem_data)
                                image = product_obj.UpdateAmazonImages(product_ids,marketplace,product_tem_data)
#                                 amazon_exp = product_tem_data.write({'amazon_export': False})
                       
    def update_amazonPrice(self):
        prod_tmpl_obj = self.env['product.template']
        product_obj = self.env['product.product']
        for marketplace in self:
            if self.env.context.get('product_tmpl_ids'):
                product_tem_ids = self.env.context.get('product_tmpl_ids')
            else:
                product_tem_ids = prod_tmpl_obj.search([('amazon_product','=',True),('amazon_export','=',False)])
            for product_temp in product_tem_ids:
                product_ids = product_obj.search([('product_tmpl_id','=',product_temp.id)])
                price = product_obj.StandardSalePrice(product_ids,marketplace,product_temp)

    def update_amazonInventory(self):
        prod_tmpl_obj = self.env['product.template']
        product_obj = self.env['product.product']
        quant_obj = self.env['stock.quant']
        for marketplace in self:
            query = "select product_id, sum(qty) from stock_quant where write_date >'%s' and qty>0 GROUP BY product_id"%(marketplace.last_inventory_update_date)
            print ("QUERY------------->",query)
            self.env.cr.execute(query)
            products = self.env.cr.fetchall()
            print("products",products)
            
            product_ids = len(products)
            print("product_idsproduct_ids",product_ids)
            i = 15
            last = 0
            for i in range(0, product_ids, 15):
                last = i + 15
                price = marketplace.UpdateInventory(products[i: last],marketplace)
                
#             print"iiiiiiiii", i
#             print"laststttt", last
#             prod_list = [product_obj.browse(product[0]) for product in products[i: last] ]
#             print"prod_list",prod_list
#             ettt
#             for product in products:
#                 product_id = product_obj.browse(product[0])
#                 qty = int(product[1])
#                 print"qty",qty
#                 if product_id.amazon_product==True and qty >0.0:
#                     print"product_id",product_id
#                     price = product_obj.UpdateInventory(product_id,marketplace,qty)
                    
                    
    def UpdateInventory(self,products,instance):
        print("products",products)
        product_obj = self.env['product.product']
        str=''
        merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(instance.amazon_instance_id.aws_merchant_id)
        message_information = ''
        message_id = False
        message_information += """<MessageType>Inventory</MessageType>"""
        for product in products:
            message_id = message_id +1
            product_id = product_obj.browse(product[0])
            print("product_id",product_id)
            qty = int(product[1])
            print("qty",qty)
            if product_id.amazon_product==True and product_id.amazon_export==False and qty >0.0:
                message_information += """<Message>
                                        <MessageID>%s</MessageID>
                                        <OperationType>Update</OperationType>
                                        <Inventory>
                                        <SKU>%s</SKU>"""%(message_id, product_id.default_code)
                message_information += """<Quantity>%s</Quantity>"""%(qty)
                                    
                message_information += """<FulfillmentLatency>1</FulfillmentLatency> 
                                    </Inventory>
                                    </Message>"""
        str = """<?xml version="1.0" encoding="utf-8" ?>
<AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amznenvelope.xsd">
<Header>
<DocumentVersion>1.01</DocumentVersion>"""+merchant_string+"""
            </Header>
            """+message_information+"""
            """
        str +="""</AmazonEnvelope>"""
        print("str",str)
        if str:
            relation_submission_id = amazon_api_obj.call(instance, 'POST_INVENTORY_AVAILABILITY_DATA',str)
            print("inventory_submission_id",relation_submission_id)
            instance.write({'last_inventory_update_date':datetime.now()})
            
    def UpdateRealInventory(self,products,instance,qty):
        print("products",products)
        product_obj = self.env['product.product']
        str=''
        merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(instance.amazon_instance_id.aws_merchant_id)
        message_information = ''
        message_id = False
        message_information += """<MessageType>Inventory</MessageType>"""
        for product_id in products:
            message_id = message_id +1
            if product_id.amazon_product==True and product_id.amazon_export==False and qty >0.0:
                message_information += """<Message>
                                        <MessageID>%s</MessageID>
                                        <OperationType>Update</OperationType>
                                        <Inventory>
                                        <SKU>%s</SKU>"""%(message_id, product_id.default_code)
                message_information += """<Quantity>%s</Quantity>"""%(qty)
                                    
                message_information += """<FulfillmentLatency>1</FulfillmentLatency> 
                                    </Inventory>
                                    </Message>"""
        str = """<?xml version="1.0" encoding="utf-8" ?>
<AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amznenvelope.xsd">
<Header>
<DocumentVersion>1.01</DocumentVersion>"""+merchant_string+"""
            </Header>
            """+message_information+"""
            """
        str +="""</AmazonEnvelope>"""
        print("str",str)
        errrtt
        if str:
            relation_submission_id = amazon_api_obj.call(instance, 'POST_INVENTORY_AVAILABILITY_DATA',str)
            print("inventory_submission_id",relation_submission_id)
            instance.write({'last_inventory_update_date':datetime.now()})
                
                
    def update_amazonImages(self):
        prod_tmpl_obj = self.env['product.template']
        product_obj = self.env['product.product']
        for marketplace in self:
            product_tem_ids = prod_tmpl_obj.search([('amazon_product','=',True),('amazon_export','=',False)])
            for product_temp in product_tem_ids:
                product_ids = product_obj.search([('product_tmpl_id','=',product_temp.id)])
                price = product_obj.UpdateAmazonImages(product_ids,marketplace,product_temp)
    
    # Button Methods of Form ....................................................................
    def action_get_amazon_log(self):
        amazon_log_ids = self.env['amazon.log'].search([('marketplace_id', '=', self[0].id)])
        print ("amazon_log", amazon_log_ids)
        if amazon_log_ids:
            amazon_log_ids = list(amazon_log_ids._ids)
        imd = self.env['ir.model.data']
        list_view_id = imd.xmlid_to_res_id('amazon_connector.view_amazon_log_tree')
        form_view_id = imd.xmlid_to_res_id('amazon_connector.view_amazon_log_form')
        result = {
                "type": "ir.actions.act_window",
                "res_model": "amazon.log",
                "views": [[list_view_id, "tree"], [form_view_id, "form"]],
                "domain": [["id", "in", amazon_log_ids]],
        }
        if len(amazon_log_ids) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = amazon_log_ids[0]
        return result
    
    #Compute Methods........................................................
    def _get_amazon_log_count(self):
        market_p_ids = []
        for market in self:
            market_p_ids = self.env['amazon.log'].search([('marketplace_id', '=', market.id)])
            market.amazon_log_count = len(market_p_ids)
        return True
    
    
    def get_proxy_server(self):
        proxy_data={}
        if self.proxy_server_type and self.proxy_server_url and self.proxy_server_port:
            url=self.proxy_server_url
            if len(url.split("//"))==2:
                proxy_data={self.proxy_server_type:"%s:%s"%(self.proxy_server_url,self.proxy_server_port)}                          
            else:
                proxy_data={self.proxy_server_type:"%s://%s:%s"%(self.proxy_server_type,self.proxy_server_url,self.proxy_server_port)}                          
        return proxy_data
    
    # Default Methods ............................................................................
     
    def _get_promotion_product(self):
        product = self.env.ref('amazon_connector.promotion_discount_product')
        return product.id
     
    def _get_shiment_fee_product(self):
        product = self.env.ref('amazon_connector.shipment_fee_product')
        return product.id
     
    def _get_shipment_discount_product(self):
        product = self.env.ref('amazon_connector.shipment_discount_product')
        return product.id
     
    def _get_gift_wapper_product(self):
        product = self.env.ref('amazon_connector.gift_wrapper_fee_product')
        return product.id
     
    def _get_guest_partner_id(self):
        quest_customer = self.env.ref('amazon_connector.res_customer_guest_customer')
        print ("quest_customer", quest_customer.id)
        return quest_customer.id
     
    def _default_warehouse_id(self):
        warehouse = self.env.user.company_id.id
        print ("warehouse", warehouse)
        warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', warehouse)], limit=1)
        return warehouse_ids and warehouse_ids[0]
     
    def _default_company_id(self):
        return self.env.user.company_id.id
    
    def _get_make_order_checked(self):
        stock_route_obj = self.env['stock.location.route']
        route_ids = stock_route_obj.search([('name', '=', 'Make To Order')])
        return route_ids.ids

#     Dashboard fields
    color = fields.Integer(string='Color Index')
#    MarketPlace amazon Information
    amazon_instance_id = fields.Many2one('amazon.seller.instance', string='Instance', readonly=True)
    aws_market_place_id = fields.Char(string="Market Place ID", size=64)
    domain = fields.Selection([("ca", "Canada"),
                                ("com.mx", "Mexico"),
                                ("com", "US"),
                                ("fr", "France"),
                                ("de", "Germany"),
                                ("it", "Italy"),
                                ("es", "Spain"),
                                ("co.uk", "UK"),
                                ("com.br", "Brazil"),
                                ("cn", "China"),
                                ("co.jp", "Japan"),
                                ("in", "india")], string="Domain" , size=64)               
    domain_name = fields.Char(string="Domain Name")
    res_country = fields.Many2one("res.country", string="Country")
    res_lang = fields.Many2one("res.lang", string="Language")
    res_currency = fields.Many2one("res.currency", string="Currency")
    amazon_shop = fields.Boolean(string='Amazon Shop', readonly=True)
    
    # product configuration fields
    product_import_condition = fields.Boolean(string="Create New Product if Product not in System while import order", default=True)
    route_ids = fields.Many2many('stock.location.route', 'shop_route_rel', 'shop_id', 'route_id', string='Routes', default=_get_make_order_checked, domain=[('product_selectable', '=', True)],
                                    help="Depending on the modules installed, this will allow you to define the route of the product: whether it will be bought, manufactured, MTO/MTS,...")
    # promotion_discount_product_id = fields.Many2one('product.product', string="Promotion Discount", domain="[('type', '=', 'service')]", default=_get_promotion_product)
    # shipment_fee_product_id = fields.Many2one('product.product', string="Shipment Fee", domain="[('type', '=', 'service')]", default=_get_shiment_fee_product)
    # shipment_discount_product_id = fields.Many2one('product.product', string="Shipment Discount", domain="[('type', '=', 'service')]", default=_get_shipment_discount_product)
    # gift_wrapper_fee_product_id = fields.Many2one('product.product', string="Gift Wrapper Fee", domain="[('type', '=', 'service')]", default=_get_gift_wapper_product)

    promotion_discount_product_id = fields.Many2one('product.product', string="Promotion Discount", domain="[('type', '=', 'service')]")
    shipment_fee_product_id = fields.Many2one('product.product', string="Shipment Fee", domain="[('type', '=', 'service')]")
    shipment_discount_product_id = fields.Many2one('product.product', string="Shipment Discount", domain="[('type', '=', 'service')]")
    gift_wrapper_fee_product_id = fields.Many2one('product.product', string="Gift Wrapper Fee", domain="[('type', '=', 'service')]")

#     SETTLEMENT REPORT 

    proxy_server_type=fields.Selection([('http','Http'),('https','Https'),('ftp','Ftp')],string='Server Type')
    proxy_server_url=fields.Char('URL')
    proxy_server_port=fields.Char('Port')
    
    settlement_report_journal_id = fields.Many2one('account.journal',string='Settlement Report Journal')
    is_default_odoo_sequence_in_sales_order=fields.Boolean("Is default Odoo Sequence in Sales Orders ?")
    ending_balance_account_id=fields.Many2one('account.account',string="Ending Balance Account")
    ending_balance_description=fields.Char("Ending Balance Description")
    invoice_tmpl_id=fields.Many2one("mail.template",string="Invoice Template")# for auto_send_invoice
    refund_tmpl_id=fields.Many2one("mail.template",string="Refund Template")
    global_channel_id = fields.Many2one('global.channel.ept',string='Global Channel')
    

    # Order Configuration fields
    prefix = fields.Char(string='Prefix')
    suffix = fields.Char(string='Suffix')
    # partner_id = fields.Many2one('res.partner', string='Customer', default=_get_guest_partner_id)
    amazon_sales_channel = fields.Many2one('crm.team', string='Amazon Sales Channel')
    partner_id = fields.Many2one('res.partner', string='Customer')
    company_id = fields.Many2one('res.company', string='Company', default=_default_company_id)
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist') 
    based_on_odoo_workflow = fields.Boolean(string="Order workflow based on odoo") 
    amazon_workflow_id = fields.Many2one('amazon.order.workflow', string="Order Workflow")
     
    # stock Configuration
    on_fly_update_stock = fields.Boolean(string="Update on Shop at time of Odoo Inventory Change")
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', default=_default_warehouse_id)
    
    # Schedular Configuration
    auto_import_order = fields.Boolean(string="Auto Import Order", default=True)
    auto_import_products = fields.Boolean(string="Auto Import Products", default=True)
    auto_update_inventory = fields.Boolean(string="Auto Update Inventory", default=True)
    auto_update_order_status = fields.Boolean(string="Auto Update Order Status", default=True)
    auto_update_price = fields.Boolean(string="Auto Update Price", default=True)
    
    # Import last date
    last_date_of_product_import = fields.Datetime(string='Last Product Import Date')
    last_amazon_inventory_export_date = fields.Datetime(string='Last Inventory Export Time')
    last_amazon_catalog_export_date = fields.Datetime(string='Last Inventory Export Time')
    last_amazon_image_export_date = fields.Datetime(string='Last Image Export Time')
    last_amazon_order_import_date = fields.Datetime(string='Last Order Import  Time')
    last_amazon_update_order_export_date = fields.Datetime(string='Last Order Update  Time')
    amazon_margin = fields.Float(string='Amazon Margin', size=64)
    auto_import_amazon = fields.Boolean(string='Auto Import')
    
    last_product_update_date = fields.Datetime(string='Last product update date')
    last_inventory_update_date = fields.Datetime(string='Last inventory update date')
    last_price_update_date = fields.Datetime(string='Last price update date')
    last_image_update_date = fields.Datetime(string='Last image update date')
    
    # Log Information
    
    amazon_log_count = fields.Integer(string="Marketplace Count", compute=_get_amazon_log_count)
    report_update = fields.Datetime(string='Last Actionable Order Update')
    report_id = fields.Char(string='Report ID', size=100)
    update_qty = fields.Integer(string='Update Quantity', size=100)
    requested_report_id = fields.Char(string='Requested Report ID', size=100)
    upc = fields.Text(string='UPC')
    active_shop = fields.Boolean(string="Active Amazon Shop",default=False)
    
    
    fulfillment_channel = fields.Selection([('FBM', 'Fulfilled By Amazon'), ('FBA', 'Fulfilled By Amazon'), ('SFP', 'Seller Fulfilled Prime')], string='Fulfillment Channnel')
    amazon_categ_id = fields.Many2one('product.category', string="Categories")
    write_date = fields.Datetime('write Date')
    afn_warehouse = fields.Many2one('stock.warehouse', string='AFN Location')
    amazon_fiscal_pid = fields.Many2one('account.fiscal.position', string='Amazon Fiscal Postion')
    settlement_report_last_sync_on = fields.Datetime("Settlement Report Last Sync Time")
    
    
    
