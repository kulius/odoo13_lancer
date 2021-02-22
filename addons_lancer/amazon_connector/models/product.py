# -*- coding: utf-8 -*-
import logging
from odoo.api import model
logger = logging.getLogger('amazon')
import time
from datetime import  datetime
from odoo import api, fields, models, _
from odoo.addons.amazon_connector.amazon_api import amazonerp_osv as amazon_api_obj
from odoo.exceptions import UserError


class outer_material_type(models.Model):
    _name = 'outer.material.type'
    
    outer_material = fields.Char(string='Outer Material Type')
    tmpl_material_id = fields.Many2one('product.template',string="Outer Material")
    p_material_id = fields.Many2one('product.product',string="Outer Material")
    
class special_features(models.Model):
    _name = 'special.features'
    
    special_feature = fields.Char(string='Special Feature')
    special_features_id = fields.Many2one('product.template',string="Special Features")    
    p_special_feature_id = fields.Many2one('product.product',string="Special Features")
    
class material_composition(models.Model):
    _name = 'material.composition'
    
    material_compo = fields.Char(string='Material Composition')
    tmpl_material_compo = fields.Many2one('product.template',string="Composition Material")
    p_material_compo = fields.Many2one('product.product',string="Composition Composition")


class ProductCategory(models.Model):
    _inherit = "product.category"
    
    amazon_category = fields.Boolean(string='Amazon Category')
    amazon_cat_id = fields.Char(string="Amazon Category ID")
    shop_ids = fields.Many2many('sale.shop', 'categ_amazon_shop_rel', 'categ_amazon_id', 'shop_id', string="Shops")
#     shop_ids = fields.One2many('sale.shop', 'shop_amazon_categ_id', string="Shops")
    
    def create_amazon_category(self, shops, categ_list):
        logger.info("Create Category From List")
        
        # create category from list of category dict
        # categ_list : List of category_info list
        if isinstance(categ_list, dict):
            categ_list = [categ_list]
        for categ in categ_list:
#             print"categ",categ
            parents = categ.get('browsePathById', False)
            p_id = False
            if parents:
                p_datas = parents.split(',')
                if len(p_datas) >= 2:
                    parent_values = p_datas[:-1]
                    if parent_values:
                        parent_id = parent_values[len(parent_values)-1]
                        p_ids = self.search([('amazon_cat_id', '=', parent_id)])
                        if p_ids:
                            p_id = p_ids[0].id
            
            c_ids = self.search([('amazon_cat_id', '=', categ.get('browseNodeId', False))])    
            if c_ids:
                self.env.cr.execute("select categ_amazon_id from categ_amazon_shop_rel where categ_amazon_id = %s and shop_id = %s"%(c_ids[0].id, shops.id))
                if not self.env.cr.fetchone():
                    self.env.cr.execute("insert into categ_amazon_shop_rel values(%s, %s)"%(c_ids[0].id, shops.id,))
                continue
            cat_vals = {
                'amazon_category' : True,
                'amazon_cat_id' : categ.get('browseNodeId', False),
                'name' : categ.get('browseNodeName', False),
                'parent_id' : p_id
            }
            try:
                c_id = self.create(cat_vals)
                logger.info("Created Category : %s with ID %s"%(c_id.name, c_id.id,))
                self.env.cr.execute("select categ_amazon_id from categ_amazon_shop_rel where categ_amazon_id = %s and shop_id = %s"%(c_id.id, shops.id))
                if not self.env.cr.fetchone():
                    self.env.cr.execute("insert into categ_amazon_shop_rel values(%s, %s)"%(c_id.id, shops.id,))
                self.env.cr.commit()
            except Exception as e:
                logger.info('Error %s', e, exc_info=True)
                pass
    
    def price_compute(self, price_type, uom=False, currency=False, company=False):
        print ("======price_compute======>",self.env.context)
        # TDE FIXME: delegate to template or not ? fields are reencoded here ...
        # compatibility about context keys used a bit everywhere in the code
        if not uom and self._context.get('uom'):
            uom = self.env['product.uom'].browse(self._context['uom'])
        if not currency and self._context.get('currency'):
            currency = self.env['res.currency'].browse(self._context['currency'])

        products = self
        if price_type == 'standard_price':
            # standard_price field can only be seen by users in base.group_user
            # Thus, in order to compute the sale price from the cost for users not in this group
            # We fetch the standard price as the superuser
            products = self.with_context(force_company=company and company.id or self._context.get('force_company', self.env.user.company_id.id)).sudo()

        prices = dict.fromkeys(self.ids, 0.0)
        for product in products:
            prices[product.id] = product[price_type] or 0.0
            if price_type == 'list_price':
                prices[product.id] += product.price_extra

            if uom:
                prices[product.id] = product.uom_id._compute_price(prices[product.id], uom)

            # Convert from current user company currency to asked one
            # This is right cause a field cannot be in more than one currency
            if currency:
                prices[product.id] = product.currency_id.compute(prices[product.id], currency)

        return prices
            


class AmazonProductsMaster(models.Model):
    _name = "amazon.products.master"

    name =fields.Char('Product Name', size=64)
    product_asin= fields.Char('ASIN',size=10)
    product_category=  fields.Char('Category', size=64)
    product_id=fields.Many2one('product.product', 'Product')
    amazon_product_attributes= fields.Text('Extra Product Details')

class AmazonProductLlisting(models.Model):
    _name = "amazon.product.listing"
    
        
#     def cal_diff_price(self,cr,uid,ids,args1=None,args2=None,context=None):
#         vals={}
#         amt=0.0
#         for rec in self.browse(cr,uid,ids):
#             
#             currency_id=self.pool.get('res.currency').search(cr,uid,[('name','=',rec.currency_id.name)])[0]
#             currency_obj=self.pool.get('res.currency').browse(cr,uid,currency_id)
#             if rec.product_id.lst_price and currency_obj:
#                 if currency_obj.rate:
#                     amt=rec.product_id.lst_price*currency_obj.rate
#             vals[rec.id]=amt
#         return vals

#     def default_get(self, cr ,uid, fields, context=None):
#         x=super(amazon_product_listing,self).default_get(cr,uid,fields,context=context) 
#         self.get_name(cr,uid,context=context)
#         print x
#         print context
#         return True


    def get_data(self,vals):
        prod_obj=self.env['product.product']
        if self._context.get('default_product_id'):
            prod_ids = prod_obj.browse(self._context.get('default_product_id'))
            if vals=='name':
                name=prod_ids.name
                return name
            elif vals == 'desp':
                desp=prod_ids.amazon_desc
                return desp
            elif vals== 'asin':
                asin=prod_ids.asin
                return asin
            elif vals== 'upc':
                upc=prod_ids.upc
                return upc
            elif vals == 'prod_id':
                prod_id=prod_ids.id
                return prod_id
    
    def get_listn(self):
        if self._context.get('new_lstn'):
            new_lstn=self._context.get('new_lstn')
            return new_lstn
    
    name = fields.Char('Name',size=64,required=True)
    default_code = fields.Char('SKU',size=64)
    asin = fields.Char('ASIN',size=64)
    fulfilled_by = fields.Char('Fulfilled By')
    product_id = fields.Many2one('product.product', string='Product Name',ondelete='cascade')
    condition = fields.Char('Condition')
    amazon_condition = fields.Selection([('New','New'),('UsedLikeNew','Used Like New'),('UsedVeryGood','Used Very Good'),('UsedGood','Used Good'),('UsedAcceptable','Used Acceptable'),('CollectibleLikeNew','Collectible Like New'),('CollectibleVeryGood','Collectible Very Good'),('CollectibleGood','Collectible Good'),('CollectibleAcceptable','Collectible Acceptable'),('Refurbished','Refurbished'),('Club','Club')],'Condition')
    stock_status = fields.Char('Supply Type')
    currency_id = fields.Many2one('res.currency','Currency')
    prod_dep = fields.Text('Product Description' ,store=True)
    price = fields.Float('Price')
    title = fields.Text('Title')
    code_type = fields.Char('UPC/ISBN',size=20)
    fulfillment_by = fields.Selection([
        ('MFN','Fulfilled by Merchant(MFN)'),
        ('AFN','Fulfilled by Amazon(AFN)')],'Fulfillment By')
    shop_id = fields.Many2one('sale.shop','Shop')
    quantity = fields.Float('Quantity')
    listing_id = fields.Char('Listing ID')
    new_lstn = fields.Boolean('New Listing')
   
    
class BulletPoint(models.Model):
    _name="bullet.point"
    
    bullet = fields.Char('Bullet Point')
    template_id = fields.Many2one('product.template', string="Bullet template")
    
class SearchTerms(models.Model):
    _name="search.terms"
    
    searchterm = fields.Char('Search Term')
    searchterm_temp_id = fields.Many2one('product.template', string="SearchTerm template")
    
# class ItemType(models.Model):
#     _name="item.types"
#     
#     itemtype = fields.Char('Item Type')
#     itemtype_temp_id = fields.Many2one('product.template', string="ItemType template")
    
class OuterMaterial(models.Model):
    _name="outer.material"
    
    material_type = fields.Char('Item Type')
    material_temp_id = fields.Many2one('product.product', string="Material template")

class ProductProduct(models.Model):
    _inherit='product.product'



    def Product_Clothing_xml(self,product,parentage):
        print
        message_information=''
        if not product.product_type_clothingaccessories:
            raise UserError(_('Error'),_('Plz select Product Type'))
    
        message_information +="""<ClassificationData>"""
        if product.size_cloth:
            message_information +="""<Size>%s</Size>"""%(product.size_cloth)
        if product.color_cloth:
            message_information +="""<Color>%s</Color>"""%(product.color_cloth)
#         if product.variationtheme_cloth:
#             message_information +="""<VariationTheme>%s</VariationTheme>"""%(product.variationtheme_cloth)
        
        if product.department_cloth:
            message_information +="""<Department>%s</Department>"""%(product.department_cloth)
        if product.material_cloth_pp:
            message_information +="""<MaterialAndFabric>%s</MaterialAndFabric>"""%(product.material_cloth_pp)
        if product.furdescription_cloth_pp:
            message_information +="""<FurDescription>%s</FurDescription>"""%(product.furdescription_cloth_pp)
        if product.materialopacity_cloth_pp:
            message_information +="""<MaterialOpacity>%s</MaterialOpacity>"""%(product.materialopacity_cloth_pp)
        if product.fabricwash_cloth_pp:
            message_information +="""<FabricWash>%s</FabricWash>"""%(product.fabricwash_cloth_pp)
        if product.patternstyle_cloth_pp:
            message_information +="""<PatternStyle>%s</PatternStyle>"""%(product.patternstyle_cloth_pp)
        if product.apparelclosuretype_cloth_pp:
            message_information +="""<ApparelClosureType>%s</ApparelClosureType>"""%(product.apparelclosuretype_cloth_pp)
        if product.occasionandlifestyle_cloth_pp:
            message_information +="""<OccasionAndLifestyle>%s</OccasionAndLifestyle>"""%(product.occasionandlifestyle_cloth_pp)
        if product.stylename_cloth_pp:
            message_information +="""<StyleName>%s</StyleName>"""%(product.stylename_cloth_pp)
        if product.stylenumber_cloth_pp:
            message_information +="""<StyleNumber>%s</StyleNumber>"""%(product.stylenumber_cloth_pp)
        if product.collartype_cloth_pp:
            message_information +="""<CollarType>%s</CollarType>"""%(product.collartype_cloth_pp)
        if product.sleevetype_cloth_pp:
            message_information +="""<SleeveType>%s</SleeveType>"""%(product.sleevetype_cloth_pp)
        if product.cufftype_cloth_pp:
            message_information +="""<CuffType>%s</CuffType>"""%(product.cufftype_cloth_pp)
        if product.pocketdescription_cloth_pp:
            message_information +="""<PocketDescription>%s</PocketDescription>"""%(product.pocketdescription_cloth_pp)
        if product.frontpleattype_cloth_pp:
            message_information +="""<FrontPleatType>%s</FrontPleatType>"""%(product.frontpleattype_cloth_pp)
        if product.topstyle_cloth_pp:
            message_information +="""<TopStyle>%s</TopStyle>"""%(product.topstyle_cloth_pp)
        if product.bottomstyle_cloth_pp:
            message_information +="""<BottomStyle>%s</BottomStyle>"""%(product.bottomstyle_cloth_pp)
        if product.waistsize_cloth_pp:
            message_information +="""<WaistSize>%s</WaistSize>"""%(product.waistsize_cloth_pp)
        if product.inseamlength_cloth_pp:
            message_information +="""<InseamLength>%s</InseamLength>"""%(product.inseamlength_cloth_pp)
        if product.sleevelength_cloth_pp:
            message_information +="""<SleeveLength>%s</SleeveLength>"""%(product.sleevelength_cloth_pp)
        if product.necksize_cloth_pp:
            message_information +="""<NeckSize>%s</NeckSize>"""%(product.necksize_cloth_pp)
        if product.neckstyle_cloth_pp:
            message_information +="""<NeckStyle>%s</NeckStyle>"""%(product.neckstyle_cloth_pp)
        if product.chestsize_cloth_pp:
            message_information +="""<ChestSize>%s</ChestSize>"""%(product.chestsize_cloth_pp)
        if product.cupsize_cloth:
            message_information +="""<CupSize>%s</CupSize>"""%(product.cupsize_cloth)
            
        if product.underwiretype_cloth:
            message_information +="""<UnderwireType>%s</UnderwireType>"""%(product.underwiretype_cloth)
        if product.shoewidth_cloth:
            message_information +="""<ShoeWidth>%s</ShoeWidth>"""%(product.shoewidth_cloth)
        if product.legdiameter_cloth:
            message_information +="""<LegDiameter>%s</LegDiameter>"""%(product.legdiameter_cloth)
        if product.legstyle_cloth:
            message_information +="""<LegStyle>%s</LegStyle>"""%(product.legstyle_cloth)
        if product.beltstyle_cloth:
            message_information +="""<BeltStyle>%s</BeltStyle>"""%(product.beltstyle_cloth)
        if product.straptype_cloth:
            message_information +="""<StrapType>%s</StrapType>"""%(product.straptype_cloth)
        if product.toestyle_cloth:
            message_information +="""<ToeStyle>%s</ToeStyle>"""%(product.toestyle_cloth)
        if product.theme_cloth:
            message_information +="""<Theme>%s</Theme>"""%(product.theme_cloth)
        if product.isstainresistant_cloth:
            message_information +="""<IsStainResistant>%s</IsStainResistant>"""%(product.isstainresistant_cloth)
        if product.numberofpieces_cloth:
            message_information +="""<NumberOfPieces>%s</NumberOfPieces>"""%(product.numberofpieces_cloth)
        message_information+="""</ClassificationData></%s>"""%(product.product_type_clothingaccessories)
        return message_information
        
    def Product_Lighting_xml(self,product):
        message_information=''
        if not product.product_type_light:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        message_information="""<%s>"""%(product.product_type_light)
#         message_information+="""<VariationData>"""
#         if product.parentage_li:
#             message_information +="""<Parentage>%s</Parentage>"""%(product.parentage_li)
#         if product.variation_theme_li:
#             variation_theme=product.variation_theme_li
#             message_information +="""<VariationTheme>%s</VariationTheme></VariationData>"""%(variation_theme)
#         elif product.variation_bulb:
#             message_information +="""<VariationTheme>%s</VariationTheme></VariationData>"""%(product.variation_bulb)
        if product.airflowcapacity_li_pp:
            message_information +="""<AirFlowCapacity>%s</AirFlowCapacity>"""%(product.airflowcapacity_li_pp)
        if product.basediameter_li_pp:
            message_information +="""<BaseDiameter>%s</BaseDiameter>"""%(product.basediameter_li_pp)
        if product.battery_li_pp:
            message_information +="""<Battery>%s</Battery>"""%(product.battery_li_pp)
        if product.bulbdiameter_li_pp:
            message_information +="""<BulbDiameter>%s</BulbDiameter>"""%(product.bulbdiameter_li_pp)
        if product.bulblength_li_pp:
            message_information +="""<BulbLength>%s</BulbLength>"""%(product.bulblength_li_pp)
        if product.bulblifespan_li_pp:
            message_information +="""<BulbLifeSpan>%s</BulbLifeSpan>"""%(product.bulblifespan_li_pp)
        if product.bulbpowerfactor_li_pp:
            message_information +="""<BulbPowerFactor>%s</BulbPowerFactor>"""%(product.bulbpowerfactor_li_pp)
        if product.bulbspecialfeatures_li_pp:
            message_information +="""<BulbSpecialFeatures>%s</BulbSpecialFeatures>"""%(product.bulbspecialfeatures_li_pp)
        if product.bulbswitchingcycles_li_pp:
            message_information +="""<BulbSwitchingCycles>%s</BulbSwitchingCycles>"""%(product.bulbswitchingcycles_li_pp)
        if product.bulbtype_li_pp:
            message_information +="""<BulbType>%s</BulbType>"""%(product.bulbtype_li_pp)
        if product.bulbwattage_li_pp:
            message_information +="""<BulbWattage>%s</BulbWattage>"""%(product.bulbwattage_li_pp)
        if product.captype_li_pp:
            message_information +="""<CapType>%s</CapType>"""%(product.captype_li_pp)
        if product.certification_li_pp:
            message_information +="""<Certification>%s</Certification>"""%(product.certification_li_pp)
        if product.collection_li_pp:
            message_information +="""<Collection>%s</Collection>"""%(product.collection_li_pp)
        if product.color_li:
            message_information +="""<Color>%s</Color>"""%(product.color_li)
        if product.energy_rating_li_pp:
            message_information +="""<EnergyEfficiencyRating>%s</EnergyEfficiencyRating>"""%(product.energy_rating_li_pp)
        if product.inte_rating_li_pp:
            message_information +="""<InternationalProtectionRating>%s</InternationalProtectionRating>"""%(product.inte_rating_li_pp)
        if product.itemdiameter_li_pp:
            message_information +="""<ItemDiameter>%s</ItemDiameter>"""%(product.itemdiameter_li_pp)
        if product.lightingmethod_li_pp:
            message_information +="""<LightingMethod>%s</LightingMethod>"""%(product.lightingmethod_li_pp)
        if product.lithium_content_li_pp:
            message_information +="""<LithiumBatteryEnergyContent>%s</LithiumBatteryEnergyContent>"""%(product.lithium_content_li_pp)
        if product.lithium_voltage_li_pp:
            message_information +="""<LithiumBatteryVoltage>%s</LithiumBatteryVoltage>"""%(product.lithium_voltage_li_pp)
        if product.lithium_weight_li_pp:
            message_information +="""<LithiumBatteryWeight>%s</LithiumBatteryWeight>"""%(product.lithium_weight_li_pp)
        if product.material_li:
            message_information +="""<Material>%s</Material>"""%(product.material_li)
        if product.numberofblades_li_pp:
            message_information +="""<NumberOfBlades>%s</NumberOfBlades>"""%(product.numberofblades_li_pp)
        if product.numberofbulbsockets_li_pp:
            message_information +="""<NumberOfBulbSockets>%s</NumberOfBulbSockets>"""%(product.numberofbulbsockets_li_pp)
        if product.plugtype_li_pp:
            message_information +="""<PlugType>%s</PlugType>"""%(product.plugtype_li_pp)
        if product.powersource_li_pp:
            message_information +="""<PowerSource>%s</PowerSource>"""%(product.powersource_li_pp)
        if product.specialfeatures_li_pp:
            message_information +="""<SpecialFeatures>%s</SpecialFeatures>"""%(product.specialfeatures_li_pp)
        if product.mercury_bulb_pp:
            message_information +="""<MercuryContent>%s</MercuryContent>"""%(product.mercury_bulb_pp)
        if product.specificuses_li_pp:
            message_information +="""<SpecificUses>%s</SpecificUses>"""%(product.specificuses_li_pp)
        if product.stylename_li_pp:
            message_information +="""<StyleName>%s</StyleName>"""%(product.stylename_li_pp)
        if product.switchstyle_li_pp:
            message_information +="""<SwitchStyle>%s</SwitchStyle>"""%(product.switchstyle_li_pp)
        if product.voltage_li:
            message_information +="""<Voltage>%s</Voltage>"""%(product.voltage_li)
        if product.volume_li_pp:
            message_information +="""<Volume>%s</Volume>"""%(product.volume_li_pp)
        if product.wattage_li:
            message_information +="""<Wattage>%s</Wattage>"""%(product.wattage_li)
        message_information += """</%s>"""%(product.product_type_light)
        return message_information
    
    def Product_Beauty_xml(self,product):
        message_information=''
        if not product.product_type_beauty:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        message_information="""<%s>"""%(product.product_type_light)
#         message_information+="""<VariationData>"""
#         if product.parentage_li:
#             message_information +="""<Parentage>%s</Parentage>"""%(product.parentage_li)
#         if product.var_theme_beauty:
#             variation_theme=product.var_theme_beauty
#             message_information +="""<VariationTheme>%s</VariationTheme></VariationData>"""%(variation_theme)
        
        if product.size_beauty:
            message_information +="""<Size>%s</Size>"""%(product.size_beauty)
        if product.color_beauty:
            message_information +="""<Color>%s</Color>"""%(product.color_beauty)
       
        if product.scent_beauty_pp:
            message_information +="""<Scent>%s</Scent>"""%(product.scent_beauty_pp)
        if product.capacity_beauty:
            message_information +="""<Capacity>%s</Capacity>"""%(product.capacity_beauty)
        if product.unit_count_beauty_pp:
            message_information +="""<UnitCount>%s</UnitCount>"""%(product.unit_count_beauty_pp)
        if product.uom_beauty_pp:
            message_information +="""<unitOfMeasure>%s</unitOfMeasure>"""%(product.uom_beauty_pp)
        if product.count_beauty_pp:
            message_information +="""<Count>%s</Count>"""%(product.count_beauty_pp)
        if product.no_of_items_beauty_pp:
            message_information +="""<NumberOfItems>%s</NumberOfItems>"""%(product.no_of_items_beauty_pp)
        if product.battry_average_life_beauty_pp:
            message_information +="""<BatteryAverageLife>%s</BatteryAverageLife>"""%(product.battry_average_life_beauty_pp)
        if product.battry_charge_time_beauty_pp:
            message_information +="""<BatteryChargeTime>%s</BatteryChargeTime>"""%(product.battry_charge_time_beauty_pp)
        if product.battry_descriptn_beauty_pp:
            message_information +="""<BatteryDescription>%s</BatteryDescription>"""%(product.battry_descriptn_beauty_pp)
        if product.battry_power_beauty_pp:
            message_information +="""<BatteryPower>%s</BatteryPower>"""%(product.battry_power_beauty_pp)
        if product.skin_type_beauty_pp:
            message_information +="""<SkinType>%s</SkinType>"""%(product.skin_type_beauty_pp)
        if product.skin_tone_beauty_pp:
            message_information +="""<SkinTone>%s</SkinTone>"""%(product.skin_tone_beauty_pp)
        if product.hair_type_beauty_pp:
            message_information +="""<HairType>%s</HairType>"""%(product.hair_type_beauty_pp)
        if product.ingredients_beauty_pp:
            message_information +="""<Ingredients>%s</Ingredients>"""%(product.ingredients_beauty_pp)
        if product.mrf_warrant_type_beauty_pp:
            message_information +="""<ManufacturerWarrantyType>%s</ManufacturerWarrantyType>"""%(product.mrf_warrant_type_beauty_pp)
        if product.material_type_beauty_pp:
            message_information +="""<MaterialType>%s</MaterialType>"""%(product.material_type_beauty_pp)
        if product.warnings_beauty:
            message_information +="""<Warnings>%s</Warnings>"""%(product.warnings_beauty)
        if product.flavor_beauty:
            message_information +="""<Flavor>%s</Flavor>"""%(product.flavor_beauty)
        if product.pattern_name_beauty:
            message_information +="""<PatternName>%s</PatternName>"""%(product.pattern_name_beauty)
        if product.is_adult_product_beauty:
            if product.is_adult_product_beauty==True:
                adult_product_beauty=1
            else:
                adult_product_beauty=0
            message_information +="""<IsAdultProduct>%s</IsAdultProduct>"""%(adult_product_beauty)
        if product.target_gender_beauty_pp:
            message_information +="""<TargetGender>%s</TargetGender>"""%(product.target_gender_beauty_pp)
        if product.seller_description_beauty:
            message_information +="""<SellerWarrantyDescription>%s<SellerWarrantyDescription>"""%(product.seller_description_beauty)
       
        message_information += """</%s>"""%(product.product_type_light)
        return message_information
    
    def Product_Tools_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_tools:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_tools)
        return xml_ce

    def Product_MusicalInstruments_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_musicalinstruments:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_musicalinstruments)
        return xml_ce

    def Product_PetSupplies_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_petsupplies:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_petsupplies)
        return xml_ce
    

    def Product_ce_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_ce:
            raise UserError(_('Error'), _('Plz select CE Product Type!!'))
        xml_ce = '''<%s>
                        <PowerSource>AC</PowerSource>
                   </%s>'''%(product.product_type_ce,product.product_type_ce)
        return xml_ce


    def Product_Jewelry_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_jewelry:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_jewelry)
        return xml_ce

    def Product_Health_xml(self,product):
        message_information=''
        print(">>>>>>>>>>>>>>>>>>>",product)
        first_tag=product.product_data
        if not product.product_type_health:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_health)
        return xml_ce
    def Product_Shoes_xml(self,product):
        message_information=''
        print(">>>>>>>>>>>>>>>>>>>",product)
        first_tag=product.product_data
        if not product.product_type_shoes:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_shoes)
        return xml_ce

    def Product_Auto_xml(self,product):
        message_information=''
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_auto_accessory:
            raise UserError(_('Error'), _('Plz select AutoAccessory Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_auto_accessory)
        return xml_ce
    
    def Product_ToysBaby_xml(self,product):
        message_information=''
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_toys_baby:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_toys_baby)
        return xml_ce
    
    def Product_CameraPhoto_xml(self,product):
        message_information=''
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_cameraphoto:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_cameraphoto)
        return xml_ce
    
    def Product_Wireless_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_wirelessaccessories:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_wirelessaccessories)
        return xml_ce

    def Product_FoodAndBeverages_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_foodandbeverages:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_foodandbeverages)
        return xml_ce
    
    def Product_Computers_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_com:
            raise UserError(_('Error'), _('Plz select Value!!'))
        xml_ce = '''%s'''%(product.product_type_com)
        return xml_ce

    def Product_Video_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_softwarevideoGames:
            raise UserError(_('Error'), _('Plz select Value!!'))
        xml_ce = '''%s'''%(product.product_type_softwarevideoGames)
        return xml_ce

    def Product_Sport_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_sports:
            raise UserError(_('Error'), _('Plz select Value!!'))
        xml_ce = '''%s'''%(product.product_type_sports)
        return xml_ce

    def Product_sportsmemorabilia_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_sportsmemorabilia:
            raise UserError(_('Error'), _('Plz select Value!!'))
        xml_ce = '''%s'''%(product.product_type_sportsmemorabilia)
        return xml_ce

    def Product_tiresandwheels_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_tiresandwheels:
            raise UserError(_('Error'), _('Plz select Value!!'))
        xml_ce = '''%s'''%(product.product_type_tiresandwheels)
        return xml_ce

    def Product_toys_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_toys:
            raise UserError(_('Error'), _('Plz select Value!!'))
        xml_ce = '''<%s>"toys"
                   </%s>'''%(product.product_type_toys,product.product_type_toys)
        return xml_ce

    size_pp = fields.Char(string='Size')
    color_pp = fields.Char(string='Color')
    Flavor_pp = fields.Char('Flavor')

    warnings_home_pp = fields.Char('Warnings')
    fabrictype_home_pp = fields.Char('FabricType')

    batterypower_headphone_pp = fields.Char('Battery Power',size=64)

    lithium_voltage_li_pp  =  fields.Char('LithiumBatteryVoltage',size=64)
    lithium_content_li_pp  =  fields.Char('LithiumBatteryEnergyContent',size=64)
    lithium_weight_li_pp  =  fields.Char('LithiumBatteryWeight',size=64)

    operatingsystem_gp_pp = fields.Char('Operating System',size=64)

    lithiumbatterypackaging_wire_pp = fields.Selection([('batteries_contained_in_equipment','batteries_contained_in_equipment'),('batteries_only','batteries_only'),('batteries_packed_with_equipment','batteries_packed_with_equipment')],'LithiumBatteryPackaging')

    color_temp_map_pp = fields.Char(string='Color Temp Map')
    department_temp_name_pp = fields.Char(string='Department Temp Name')
    color_map_pp = fields.Char(string='Color Map')
    department_name_pp = fields.Char(string='Department Name')

    size_map = fields.Selection([('XXXXX-Small','XXXXX-Small'),('XXXX-Small','XXXX-Small'),('XXX-Small','XXX-Small'),('XX-Small','XX-Small'),('X-Small','X-Small'),('Small','Small'),('Medium','Medium'),('Large','Large'),
                                                   ('X-Large','X-Large'),('XX-Large','XX-Large'),('XXX-Large','XXX-Large'),('XXXX-Large','XXXX-Large'),('XXXXX-Large','XXXXX-Large')],string='Size Map',)
    shipping_template_prod = fields.Selection([('nationwide','Nationwide Prime'),('default','Default Amazon Template'),('new_template','New Template'),('regional_prime','Regional Prime (Ground)'),('new_template_cp','New Template-Copy'),('reginal_prime_gd','Regional Prime (Ground + Air)')], string='Shipping Template', default='nationwide')
    style_number = fields.Char(string='Style Number')
    shipping_product = fields.Char(string='Shipping-Template')
    key_product_features = fields.Char(string='Key Product Features')
    closure_type = fields.Char(string='Closure Type')
    collar_type = fields.Char(string='Collar Type')
    fit_type = fields.Char(string='Fit Type')
    sleeve_type = fields.Char(string='Sleeve Type')
#     special_features = fields.Char(string='Special Features')
    style_product = fields.Char(string='Style')
    style_name = fields.Char(string='Style Name')
    neck_size = fields.Char(string='Neck Size')
    neck_size_uom =fields.Char(string='Neck Size Unit Of Measure')
    neck_style = fields.Char(string='NeckStyle')
    pattern_style = fields.Char(string='Pattern Style')
    special_size_type = fields.Char(string='Special Size Type')
    sleeve_length = fields.Char(string='SleeveLength')
    sleeve_length_uom = fields.Char(string='Sleeve Length Unit Of Measure')
    
    material_type = fields.Char(string='material Type')


    outer_material_type = fields.One2many('outer.material.type','p_material_id',string='Outer Material Type')
    material_composition = fields.One2many('material.composition','p_material_compo',string='Outer Material Type')
    special_features = fields.One2many('special.features','p_special_feature_id',string='Special Features')

    diameter_home_pp = fields.Char('Diameter')
    # amazon_export = fields.Boolean(string='To be Exported')
    # amazon_product = fields.Boolean(string='Amazon Product')
    # amazon_sku = fields.Char(string='ASIN')
    # amazon_fba_sku = fields.Char(string='Amazon FBA SKU')
    # tmp_asin = fields.Char('ASIN')
    # upc_temp = fields.Char(string='UPC',size=64)
    # ean_barcode = fields.Char('EAN/Barcode')
    # isbn_temp = fields.Char('ISBN')
    # variation_data  =  fields.Selection([('parent','parent'),('child','child')],'Parentage')
    # item_type = fields.Char(string='Item Type', help="Data Should be in this Format casual-formal")
    standard_temp_product = fields.Selection([('EAN','EAN'),('UPC','UPC'),('ASIN','ASIN'),('ISBN','ISBN')], string='Standard Product')

    publisher_pp = fields.Char(string='Publisher')

    def _get_amazon_product_model_count(self):
        market_p_ids = []
        for market in self:
            market_p_ids = self.env['amazon.log'].search([('res_model_id.model', '=', 'product.product'),('res_id','=',self[0].id)])
            market.amazon_product_model_count = len(market_p_ids)
    
    def action_view_amazon_log(self):
        amazon_log = []
        amazon_log_ids = self.env['amazon.log'].search([('res_model_id.model', '=', 'product.product'),('res_id','=',self[0].id)])
        print( "amazon_logprooduct", amazon_log_ids)
        if amazon_log_ids:
            amazon_log_ids = list(amazon_log_ids._ids)
            print ("=========amazon_log_ids=============", amazon_log_ids)
        imd = self.env['ir.model.data']
        list_view_id = imd.xmlid_to_res_id('amazon_connector.view_amazon_log_tree')
        form_view_id = imd.xmlid_to_res_id('amazon_connector.view_amazon_log_form')
        result = {
                "type": "ir.actions.act_window",
                "res_model": "amazon.log",
                "views": [[list_view_id, "tree"], [form_view_id, "form"]],
                "domain": [["id", "in", amazon_log_ids]],
                "context":{'group_by':['marketplace_id', 'log_type', 'name']}
        }
        if len(amazon_log_ids) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = amazon_log_ids[0]
        return result
    
    def _get_prices(self):
        for rec in self:
            rec.product_shop_price_ids = [(0,0, {'shop_id': 1, 'price': 300})]

    amazon_prodlisting_ids = fields.One2many('amazon.product.listing', 'product_id', string='Product Listing')
    asin = fields.Char('Asin',size=64)
    upc = fields.Char('UPC')
    isbn = fields.Char('ISBN')
    manufacturer_part = fields.Char(string='Manufacturer Part Number')
    amazon_active_prod = fields.Boolean('Amazon Product')
#     amazon_product = fields.Boolean('Amazon Product')
    qty_override = fields.Float('Quantity Override')
    amazon_price_new = fields.Float('Amazon New Price')
    price_amazon_current = fields.Float('Amazon Current Price')
    updated_data = fields.Boolean('Updated', default=False)
    amazon_standard_price = fields.Float('Amazon Price')
    amazon_fba_price = fields.Float('Amazon FBA Price')
    # For Log
    amazon_product_model_count = fields.Integer(string='Amazon Log View', compute=_get_amazon_product_model_count)
    product_shop_price_ids = fields.One2many('product.shop.price', 'product_id', string="Prices", compute="_get_prices")
#     standard_product = fields.Selection([('EAN','EAN'),('UPC','UPC'),('ASIN','ASIN'),('ISBN','ISBN')], string='Standard Product')
    shipping_weight = fields.Char('Shipping Weight')
    shipping_weight_uom = fields.Selection([('LB','LB'),('OZ','OZ'),('KG','KG'),('GR','GR')],string='Shipping weight uom')
    style_name = fields.Char(string='Style Name')
    material_type = fields.Char(string='Material Type')
    amazon_afn_sku = fields.Char(string='Amazon AFN SKU')
    fulfillment_channel = fields.Selection([('MFN','Fulfilled by Merchant(MFN)'),('FBA','Fulfilled by Amazon(FBA)')],'Fulfillment By')
#     material_type = fields.One2many('outer.material','material_temp_id',string='Material Type')


    ######################################baby#############

    seating_capacity_by_pp  = fields.Char('SeatingCapacity')
    seat_interior_width_by_pp  = fields.Char('SeatInteriorWidth')
    seat_height_by_pp  = fields.Char('SeatHeight')
    seat_back_interior_height_by_pp  = fields.Char('SeatBackInteriorHeight')
    safety_warning_by_pp  = fields.Char('SafetyWarning')
    battery_description_by_pp  = fields.Char('BatteryDescription')
    battery_power_by_pp  = fields.Char('BatteryPower')
    bottle_nipple_type_by_pp  = fields.Char('BottleNippleType')
    bottle_type_by_pp  = fields.Char('BottleType')
    carrier_weight_by_pp = fields.Char('CarrierWeight')
    car_seat_weight_group_eu_by_pp  = fields.Char('CarSeatWeightGroupEU')
    color_name_by_pp  = fields.Char('ColorName')
    folded_size_by_pp  = fields.Char('FoldedSize')
    is_dishwasher_safe_by_pp  = fields.Boolean('IsDishwasherSafe')
    item_depth_by_pp  = fields.Char('ItemDepth')
    # manufacturer_warranty_description_by_pp  = fields.Char('ManufacturerWarrantyDescription')
    material_type_free_by_pp = fields.Char('MaterialTypeFree')
    maximum_anchoring_weight_capacity_by_pp  = fields.Char('MaximumAnchoringWeightCapacity')
    maximum_height_recommendation_by_pp  = fields.Char('MaximumHeightRecommendation')
    minimum_height_recommendation_by_pp  = fields.Char('MinimumHeightRecommendation')
    maximum_manufacturer_age_recommended_by_pp  = fields.Char('MaximumManufacturerAgeRecommended')
    minimum_manufacturer_age_recommended_by_pp  = fields.Char('MinimumManufacturerAgeRecommended')
    maximum_item_width_by_pp  = fields.Char('MaximumItemWidth')
    maximum_range_indoors_by_pp  = fields.Char('MaximumRangeIndoors')
    maximum_range_open_space_by_pp  = fields.Char('MaximumRangeOpenSpace')
    maximum_weight_recommendation_by_pp  = fields.Char('MaximumWeightRecommendation')
    minimum_weight_recommendation_by_pp  = fields.Char('MinimumWeightRecommendation')
    operation_mode_by_pp  = fields.Char('OperationMode')
    orientation_by_pp  = fields.Char('Orientation')
    


    ######################################  Clothing And Accessories###################3
    # cloth_pp = fields.Boolean('Clothing And Accessories')
    # size_cloth = fields.Char('Size')
    department_cloth_pp = fields.Char('Department')
    cloth_type_pp = fields.Selection([('Shirt','Shirt'),('Sweater','Sweater'),('Pants','Pants'),('Shorts','Shorts'),('Skirt','Skirt'),('Dress','Dress'),('Suit','Suit'),('Blazer','Blazer'),('Outerwear','Outerwear'),('SocksHosiery','SocksHosiery'),('Underwear','Underwear'),('Bra','Bra'),('Shoes','Shoes'),('Hat','Hat'),('Bag','Bag'),('Accessory','Accessory'),('Jewelry','Jewelry'),('Sleepwear','Sleepwear'),('Swimwear','Swimwear'),('PersonalBodyCare','PersonalBodyCare'),('HomeAccessory','HomeAccessory'),('NonApparelMisc','NonApparelMisc')],string='ClothingType',default='Shirt')
    size_tem_map_pp = fields.Selection([('XXXXX-Small','XXXXX-Small'),('XXXX-Small','XXXX-Small'),('XXX-Small','XXX-Small'),('XX-Small','XX-Small'),('X-Small','X-Small'),('Small','Small'),('Medium','Medium'),('Large','Large'),('X-Large','X-Large'),('XX-Large','XX-Large'),('XXX-Large','XXX-Large'),('XXXX-Large','XXXX-Large'),('XXXXX-Large','XXXXX-Large')],string='Size Map',)

    material_cloth_pp = fields.Char('MaterialAndFabric')
    furdescription_cloth_pp = fields.Char('FurDescription')
    materialopacity_cloth_pp = fields.Char('MaterialOpacity')
    fabricwash_cloth_pp = fields.Char('FabricWash')
    patternstyle_cloth_pp = fields.Char('PatternStyle')
    apparelclosuretype_cloth_pp = fields.Char('ApparelClosureType')
    occasionandlifestyle_cloth_pp = fields.Char('OccasionAndLifestyle')
    # stylename_cloth_pp = fields.Char('StyleName')
    stylenumber_cloth_pp = fields.Char('StyleNumber')
    collartype_cloth_pp = fields.Char('CollarType')
    sleevetype_cloth_pp = fields.Char('SleeveType')
    cufftype_cloth_pp = fields.Char('CuffType')
    pocketdescription_cloth_pp = fields.Char('PocketDescription')
    frontpleattype_cloth_pp = fields.Char('FrontPleatType')
    topstyle_cloth_pp = fields.Char('TopStyle')
    bottomstyle_cloth_pp = fields.Char('BottomStyle')
    waistsize_cloth_pp = fields.Char('WaistSize')
    inseamlength_cloth_pp = fields.Char('InseamLength')
    sleevelength_cloth_pp = fields.Char('SleeveLength')
    necksize_cloth_pp = fields.Char('NeckSize')
    neckstyle_cloth_pp = fields.Char('NeckStyle')
    chestsize_cloth_pp = fields.Char('ChestSize')


################### Beauty #################

    # size_beauty = fields.Integer('Size')
    # capacity_beauty_pp = fields.Char('Capacity')
    # color_beauty = fields.Char('Colour')
    scent_beauty_pp = fields.Char('Scent')
    pattern_name_beauty_pp = fields.Char('Pattern Name')
    unit_count_beauty_pp = fields.Integer('Unit Count')
    uom_beauty_pp = fields.Char('Unit Of Measure')
    count_beauty_pp = fields.Integer('Count')
    no_of_items_beauty_pp = fields.Integer('Number Of Items')
    battry_average_life_beauty_pp = fields.Char('Battery Average Life')
    battry_charge_time_beauty_pp = fields.Char('Battery Charge Time')
    battry_descriptn_beauty_pp = fields.Char('Battery Description')
    battry_power_beauty_pp = fields.Integer('Battery Power')
    skin_type_beauty_pp = fields.Char('Skin Type')
    skin_tone_beauty_pp = fields.Char('Skin Tone')
    hair_type_beauty_pp = fields.Char('Hair Type')
    ingredients_beauty_pp = fields.Char('Ingredients')
    mrf_warrant_type_beauty_pp = fields.Char('Manufacturer Warranty Type')
    material_type_beauty_pp = fields.Char('Material Type')
    # warnings_beauty = fields.Char('Warnings')
    # flavor_beauty = fields.Char('Flavor')
    # is_adult_product_beauty_pp = fields.Boolean('IsAdultProduct')
    # seller_description_beauty_pp = fields.Char('SellerWarrantyDescription')
    target_gender_beauty_pp = fields.Selection([('male','Male'),('female','Female'),('unisex','Unisex')])
    
    ####################Tools#########################
    
    power_source_t_pp = fields.Selection([('battery-powered', 'battery-powered'),('gas-powered', 'gas-powered'),('hydraulic-powered', 'hydraulic-powered'),('air-powered', 'air-powered'),('corded-electric', 'corded-electric')], 'PowerSource')

    number_of_items_inpackage_t_pp = fields.Char('NumberOfItemsInPackage')
    ############################# Home Improvement######################

    battery_average_life_hi_pp = fields.Char('BatteryAverageLife')
    battery_average_life_standby_hi_pp = fields.Char('BatteryAverageLifeStandby')
    battery_charge_time_hi_pp = fields.Char('BatteryChargeTime')
    battery_type_lithium_ion_hi_pp = fields.Char('BatteryTypeLithiumIon')
    battery_type_lithium_metal_hi_pp = fields.Char('BatteryTypeLithiumMetal')
    country_of_origin_hi_pp = fields.Char('CountryOfOrigin')
    item_display_area_hi_pp = fields.Char('ItemDisplayArea')
    # lithium_battery_energy_content_hi = fields.Char('LithiumBatteryEnergyContent')
    # lithium_battery_packaging_hi = fields.Selection([('batteries_contained_in_equipment','batteries_contained_in_equipment'),('batteries_only','batteries_only'),('batteries_packed_with_equipment','batteries_packed_with_equipment')],'LithiumBatteryPackaging')
    # lilthium_battery_voltage_hi = fields.Char('LithiumBatteryVoltage')
    # lithium_battery_weight_hi = fields.Char('LithiumBatteryWeight')
    mfr_warranty_description_labor_hi_pp = fields.Char('MfrWarrantyDescriptionLabor')
    mfr_warranty_description_parts_hi_pp = fields.Char('MfrWarrantyDescriptionParts')
    mfr_warranty_description_type_hi_pp = fields.Char('MfrWarrantyDescriptionType')
    number_of_lithium_ion_cells_hi_pp = fields.Char('NumberOfLithiumIonCells')
    number_of_lithium_metal_cells_hi_pp = fields.Char('NumberOfLithiumMetalCells')
    # warnings_hi = fields.Char('Warnings')
    # fabric_type_hi = fields.Char('FabricType')
    import_designation_hi_pp = fields.Char('ImportDesignation')
    accessory_connection_type_hi_pp = fields.Char('AccessoryConnectionType')
    battery_capacity_hi_pp = fields.Char('BatteryCapacity')
    blade_edge_hi_pp = fields.Char('BladeEdge')
    blade_length_hi_pp = fields.Char('BladeLength')
    compatible_devices_hi_pp = fields.Char('CompatibleDevices')
    compatible_fastener_range_hi_pp = fields.Char('CompatibleFastenerRange')
    cooling_method_hi_pp = fields.Char('CoolingMethod')
    cooling_wattage_hi_pp = fields.Char('CoolingWattage')
    corner_radius_hi_pp = fields.Char('CornerRadius')
    coverage_hi_pp = fields.Char('Coverage')
    cut_type_hi_pp = fields.Char('CutType')
    cutting_width_hi_pp = fields.Char('CuttingWidth')
    device_type_hi_pp = fields.Char('DeviceType')
    display_style_hi_pp = fields.Char('DisplayStyle')
    energy_consumption_hi_pp = fields.Char('EnergyConsumption')
    energy_efficiency_ratio_cooling_hi_pp = fields.Char('EnergyEfficiencyRatioCooling')
    environmental_description_hi_pp = fields.Char('EnvironmentalDescription')
    eu_energy_efficiency_class_heating_hi_pp = fields.Char('EuEnergyEfficiencyClassHeating')
    eu_energy_label_efficiency_class_hi_pp = fields.Char('EuEnergyLabelEfficiencyClass')
    external_testing_certification_hi_pp = fields.Char('ExternalTestingCertification')

    flush_type_hi_pp = fields.Char('FlushType')
    folded_knife_size_hi_pp = fields.Char('FoldedKnifeSize')
    grit_rating_hi_pp = fields.Char('GritRating')
    handle_material_hi_pp = fields.Char('HandleMaterial')
    inside_diameter_hi_pp = fields.Char('InsideDiameter')
    heater_wattage_hi_pp = fields.Char('HeaterWattage')
    laser_beam_color_hi_pp = fields.Char('LaserBeamColor')
    maximum_power_hi_pp = fields.Char('MaximumPower')
    measurement_accuracy_hi_pp = fields.Char('MeasurementAccuracy')
    measurement_system_hi_pp = fields.Char('MeasurementSystem')

    minimum_efficiency_reporting_value_hi_pp = fields.Char('MinimumEfficiencyReportingValue')
    number_of_basins_hi_pp = fields.Char('NumberOfBasins')
    number_of_holes_hi_pp = fields.Char('NumberOfHoles')
    number_of_items_hi_pp = fields.Char('NumberOfItems')
    outside_diameter_hi_pp = fields.Char('OutsideDiameter')
    performance_description_hi_pp = fields.Char('PerformanceDescription')
    recycled_content_percentage_hi_pp = fields.Char('RecycledContentPercentage')
    speed_hi_pp = fields.Char('Speed')
    rough_in_hi_pp = fields.Char('RoughIn')
    spout_height_hi_pp = fields.Char('SpoutHeight')

    spout_reach_hi_pp = fields.Char('SpoutReach')
    thread_size_hi_pp = fields.Char('ThreadSize')
    tool_tip_description_hi_pp = fields.Char('ToolTipDescription')
    torque_hi_pp = fields.Char('Torque')
    uv_protection_hi_pp = fields.Char('UVProtection')
    viewing_area_hi_pp = fields.Char('ViewingArea')
    # size_hi = fields.Char('Size')
    bulb_type_hi_pp = fields.Char('BulbType')
    center_length_hi_pp = fields.Char('CenterLength')
    brightness_hi_pp = fields.Char('Brightness')

    # color_hi = fields.Char('Color')
    color_map_hi_pp = fields.Char('ColorMap')
    head_style_hi_pp = fields.Char('HeadStyle')
    material_hi_pp = fields.Char('Material')
    display_volume_hi_pp = fields.Char('DisplayVolume')
    display_length_hi_pp = fields.Char('DisplayLength')
    manufacturer_warranty_description_hi_pp = fields.Char('ManufacturerWarrantyDescription')
    plug_format_hi_pp = fields.Char('PlugFormat')
    plug_profile_hi_pp = fields.Char('PlugProfile')
    power_source_hi_pp = fields.Char('PowerSource')

    cutting_diameter_hi_pp = fields.Char('CuttingDiameter')
    customer_package_type_hi_pp = fields.Char('CustomerPackageType')
    display_diameter_hi_pp = fields.Char('DisplayDiameter')
    display_weight_hi_pp = fields.Char('DisplayWeight')
    display_width_hi_pp = fields.Char('DisplayWidht')
    display_height_hi_pp = fields.Char('DisplayHeight')
    horsepower_hi_pp = fields.Char('Horsepower')
    minimum_age_hi_pp = fields.Char('MinimumAge')
    customer_restriction_type_hi_pp = fields.Char('CustomerRestrictionType')

    seller_warranty_description_hi_pp = fields.Char('SellerWarrantyDescription')
    switch_style_hi_pp = fields.Char('SwitchStyle')
    switch_type_hi_pp = fields.Char('SwitchType')
    voltage_hi_pp = fields.Char('Voltage')
    wattage_hi_pp = fields.Char('Wattage')
    # customer_packageType_hi = fields.Char('CustomerPackageType')
    base_diameter_hi_pp = fields.Char('BaseDiameter')
    beam_angle_hi_pp = fields.Char('BeamAngle')
    blade_color_hi_pp = fields.Char('BladeColor')
    circuit_breaker_type_hi_pp = fields.Char('CircuitBreakerType')

    efficiency_hi_pp = fields.Char('Efficiency')
    international_protection_rating_hi_pp = fields.Char('InternationalProtectionRating')
    light_source_operating_life_hi_pp = fields.Char('LightSourceOperatingLife')
    lighting_method_hi_pp = fields.Char('LightingMethod')
    maximum_compatible_light_source_wattage_hi_pp = fields.Char('MaximumCompatibleLightSourceWattage')
    number_of_blades_hi_pp = fields.Char('NumberOfBlades')
    number_of_light_sources_hi_pp = fields.Char('NumberOfLightSources')
    shade_diameter_hi_pp = fields.Char('ShadeDiameter')
    shade_material_type_hi_pp = fields.Char('ShadeMaterialType')
    short_product_description_hi_pp = fields.Char('ShortProductDescription')

    start_up_time_description_hi_pp = fields.Char('StartUpTimeDescription')
    strands_hi_pp = fields.Char('Strands')
    tubing_outside_Diameter_hi_pp = fields.Char('TubingOutsideDiameter')
    legal_compliance_certification_metadata_hi_pp = fields.Char('LegalComplianceCertificationMetadata')
    legal_compliance_certification_date_of_issue_hi_pp = fields.Datetime('LegalComplianceCertificationDateOfIssue')
    legal_compliance_certification_expiration_date_hi_pp = fields.Datetime('LegalComplianceCertificationExpirationDate')
    power_plug_type_hi_pp = fields.Char('PowerPlugType')

    base_width_hi_pp = fields.Char('BaseWidth')
    capacity_hi_pp = fields.Char('Capacity')
    control_type_hi_pp = fields.Char('ControlType')
    drain_type_hi_pp = fields.Char('DrainType')
    form_factor_hi_pp = fields.Char('FormFactor')
    gauge_string_hi_pp = fields.Char('GaugeString')
    handle_type_hi_pp = fields.Char('HandleType')
    input_power_hi_pp = fields.Char('InputPower')
    mounting_type_hi_pp = fields.Char('MountingType')
    number_of_settings_hi_pp = fields.Char('NumberOfSettings')
    roll_quantity_hi_pp = fields.Char('RollQuantity')

    r_value_hi_pp  = fields.Char('R Value')


    #########################RamMateraial#########################

    wire_diameter_string_rm_pp = fields.Char('WireDiameterString')
    void_volume_percentage_rm_pp = fields.Char('VoidVolumePercentage')
    upper_temperature_rating_rm_pp = fields.Char('UpperTemperatureRating')
    upper_bubbling_pressure_rm_pp = fields.Char('UpperBubblingPressure')
    tubing_wall_type_rm_pp = fields.Char('TubingWallType')
    tolerance_held_rm_pp = fields.Char('ToleranceHeld')
    thread_diameter_string_rm_pp = fields.Char('ThreadDiameterString')
    tensile_strength_rm_pp = fields.Char('TensileStrength')
    standard_construction_rm_pp = fields.Char('StandardConstruction')
    slot_width_rm_pp = fields.Char('SlotWidth')
    slot_depth_rm_pp = fields.Char('SlotDepth')
    shim_type_rm_pp = fields.Char('ShimType')
    notch_width_rm_pp = fields.Char('NotchWidth')
    notch_depth_rm_pp = fields.Char('NotchDepth')
    metal_construction_type_rm_pp = fields.Char('MetalConstructionType')
    mesh_opening_size_rm_pp = fields.Char('MeshOpeningSize')
    mesh_openin_shape_rm_pp = fields.Char('MeshOpeningShape')
    mesh_number_rm_pp = fields.Char('MeshNumber')
    mesh_form_rm_pp = fields.Char('MeshForm')
    mesh_count_rm_pp = fields.Char('MeshCount')
    maximum_pressure_rm_pp = fields.Char('MaximumPressure')
    air_entry_pressure_rm_pp = fields.Char('AirEntryPressure')
    backing_type_rm_pp = fields.Char('BackingType')
    ball_type_rm_pp = fields.Char('BallType')
    compatible_with_tube_gauge_rm_pp = fields.Char('CompatibleWithTubeGauge')
    corner_style_rm_pp = fields.Char('CornerStyle')
    disc_diameter_string_rm_pp = fields.Char('DiscDiameterString')
    durometer_hardness_rm_pp = fields.Char('DurometerHardness')
    exterior_finish_rm_pp = fields.Char('ExteriorFinish')
    foam_structure_rm_pp = fields.Char('FoamStructure')
    grade_rating_rm_pp = fields.Char('GradeRating')
    hole_count_rm_pp = fields.Char('HoleCount')
    inside_diameter_string_rm_pp = fields.Char('InsideDiameterString')
    inside_diameter_tolerance_string_rm_pp = fields.Char('InsideDiameterToleranceString')
    item_diameter_tolerance_string_rm_pp = fields.Char('ItemDiameterToleranceString')
    item_hardness_rm_pp = fields.Char('ItemHardness')
    item_length_tolerance_string_rm_pp = fields.Char('ItemLengthToleranceString')
    item_shape_rm_pp = fields.Char('ItemShape')
    item_temper_rm_pp= fields.Char('ItemTemper')
    item_thickness_tolerance_string_rm_pp = fields.Char('ItemThicknessToleranceString')
    item_width_tolerance_string_rm_pp = fields.Char('ItemWidthToleranceString')
    lower_bubbling_pressure_rm_pp = fields.Char('LowerBubblingPressure')



    #######################33Wireless###############################33

    wireless_accessory_pp = fields.Boolean('Wireless Accessory')
    lithiumbatterypackaging_wire_pp = fields.Selection([('batteries_contained_in_equipment','batteries_contained_in_equipment'),('batteries_only','batteries_only'),('batteries_packed_with_equipment','batteries_packed_with_equipment')],'LithiumBatteryPackaging')
#     variationdata_wire = fields.Selection([('parent','parent'),('child','child')],'VariationData')
    # variationtheme_wire = fields.Selection([('Color','Color')],'VariationTheme')
    # color_wire = fields.Char('Color')
    additionalfeatures_wire_pp = fields.Char('AdditionalFeatures')
    solar_wire_pp = fields.Boolean('Solar')
    refillable_wire_pp = fields.Boolean('Refillable')
    extended_wire_pp = fields.Boolean('Extended')
    slim_wire_pp = fields.Boolean('Slim')
    auxiliary_wire_pp = fields.Boolean('Auxiliary')
    batterytype_wire_pp = fields.Char('BatteryType')
    antennatype_wire_pp = fields.Char('AntennaType')
    manufacturername_wire_pp = fields.Char('ManufacturerName')
    keywords_wire_pp = fields.Char('Keywords')
    itempackagequantity_wire_pp = fields.Char('ItemPackageQuantity')
    headsettype_wire_pp = fields.Selection([('one-ear','one-ear'),('two-ear','two-ear')],'HeadsetType')
    headsetstyle_wire_pp = fields.Selection([('over-the-ear','over-the-ear'),('behind-the-ear','behind-the-ear'),('in-the-ear','in-the-ear')],'HeadsetStyle')
    
    talk_time_wire_pp = fields.Char('TalkTime')
    standby_time_wire_pp = fields.Char('StandbyTime')
    charging_time_wire_pp = fields.Char('ChargingTime')
    # batterypower_headphone
    compatible_phone_models_wire_pp = fields.Char('CompatiblePhoneModels')
    prepaid_features_wire_pp = fields.Char('PrepaidFeatures')
    phone_type_wire_pp = fields.Char('PhoneType')
    phone_style_wire_pp = fields.Char('PhoneStyle')
    # operatingsystem_gp
    # power_plug_type_hi
        
    ###############################wirelessDownloads#################3333
    wirelessdownloads_wire_pp = fields.Boolean('WirelessDownloads')
    applicationversion_wire_pp = fields.Char('ApplicationVersion')



    ####################Sports#############################

    model_year_s_pp  =  fields.Char('ModelYear',size=64)
    customizable_template_name_s_pp  =  fields.Char('CustomizableTemplateName',size=64)
    is_customizable_s_pp  =  fields.Boolean('IsCustomizable')
    grip_size_s_pp  =  fields.Char('GripSize',size=64)
    diving_hood_thickness_s_pp  =  fields.Char('DivingHoodThickness',size=64)
    design_s_pp  =  fields.Char('Design',size=64)
    age_gender_category_s_pp  =  fields.Char('AgeGenderCategory',size=64)
    bike_rim_size_s_pp  =  fields.Char('BikeRimSize',size=64)
    boot_size_s_pp  =  fields.Char('BootSize',size=64)
    calf_size_s_pp  =  fields.Char('CalfSize',size=64)

    ##########################SportsMemo###########################

    packaging_sm_pp  =  fields.Char('Packaging',size=64)
    game_used_sm_pp  =  fields.Char('GameUsed',size=64)
    player_name_sm_pp  =  fields.Char('PlayerName',size=64)
    authenticated_by_sm_pp  =  fields.Char('AuthenticatedBy',size=64)
    authenticity_certificate_number_sm_pp  =  fields.Char('AuthenticityCertificateNumber',size=64)
    signed_by_sm_pp  =  fields.Char('SignedBy',size=64)
    autographed_sm_pp  =  fields.Char('Autographed',size=64)
    jersey_type_sm_pp  =  fields.Char('JerseyType',size=64)
    league_name_sm_pp  =  fields.Char('LeagueName',size=64)
    season_sm_pp  =  fields.Char('Season',size=64)
    sport_sm_pp  =  fields.Char('Sport',size=64)
    team_name_sm_pp  =  fields.Char('TeamName',size=64)
    uniform_number_sm_pp  =  fields.Char('UniformNumber',size=64)
    whats_in_the_box_sm_pp  =  fields.Char('WhatsInTheBox',size=64)
    year_sm_pp  =  fields.Char('Year',size=64)
    is_very_high_value_sm_pp  =  fields.Boolean('IsVeryHighValue')




    #################Gourmet#######################

    unit_count_g_pp  =  fields.Char('UnitCount')
    item_specialty_g_pp  =  fields.Char('ItemSpecialty')
    organic_certification_g_pp  =  fields.Char('OrganicCertification')
    kosher_certification_g_pp  =  fields.Char('KosherCertification')
    nutritional_facts_g_pp  =  fields.Char('NutritionalFacts')
    country_produced_in_g_pp  =  fields.Char('CountryProducedIn')
    identity_package_type_g_pp  =  fields.Char('IdentityPackageType')
    can_ship_in_original_container_g_pp  =  fields.Char('CanShipInOriginalContainer')


    #####################PowerTransmission#######################
    
    wire_diameter_pt_pp = fields.Char('WireDiameter',size=64)
    trade_size_name_pt_pp = fields.Char('TradeSizeName',size=64)
    strand_type_pt_pp = fields.Char('StrandType',size=64)
    spring_wind_direction_pt_pp = fields.Char('SpringWindDirection',size=64)
    spring_rate_pt_pp = fields.Char('SpringRate',size=64)
    slide_travel_distance_pt_pp = fields.Char('SlideTravelDistance',size=64)
    set_screw_thread_type_pt_pp = fields.Char('SetScrewThreadType',size=64)
    outer_ring_width_pt_pp = fields.Char('OuterRingWidth',size=64)
    number_of_teeth_pt_pp = fields.Char('NumberOfTeeth',size=64)
    active_coils_pt_pp = fields.Char('ActiveCoils',size=64)
    axial_misalignment_pt_pp = fields.Char('AxialMisalignmentn',size=64)
    belt_cross_section_pt_pp = fields.Char('BeltCrossSection',size=64)
    belt_width_pt_pp = fields.Char('BeltWidth',size=64)
    body_outside_diameter_pt_pp = fields.Char('BodyOutsideDiameter',size=64)
    compressed_length_pt_pp = fields.Char('CompressedLength',size=64)
    deflection_angle_pt_pp = fields.Char('DeflectionAngle',size=64)
    face_width_pt_pp = fields.Char('FaceWidth ',size=64)
    flange_outside_diameter_pt_pp = fields.Char('FlangeOutsideDiameter ',size=64)
    flange_thickness_pt_pp = fields.Char('FlangeThickness ',size=64)
    guide_support_type_pt_pp = fields.Char('GuideSupportType ',size=64)
    item_pitch_pt_pp = fields.Char('ItemPitch ',size=64)
    key_way_depth_pt_pp = fields.Char('KeyWayDepth ',size=64)
    key_way_sidth_pt_pp = fields.Char('KeyWayWidth ',size=64)
    leg_length_pt_pp = fields.Char('LegLength ',size=64)
    load_capacity_pt_pp = fields.Char('LoadCapacity ',size=64)
    maximum_angular_misalignment_pt_pp = fields.Char('MaximumAngularMisalignment ',size=64)
    maximum_parallel_misalignment_pt_pp = fields.Char('MaximumParallelMisalignment ',size=64)
    maximum_rotational_speed_pt_pp = fields.Char('MaximumRotationalSpeed ',size=64)
    maximum_spring_compression_load_pt_pp = fields.Char('MaximumSpringCompressionLoad ',size=64)
    maximum_tension_load_pt_pp = fields.Char('MaximumTensionLoad ',size=64)
    maximum_torque_pt_pp = fields.Char('MaximumTorque ',size=64)
    minimum_spring_Compression_load_pt_pp = fields.Char('MinimumSpringCompressionLoad ',size=64)
    number_of_bands_pt_pp = fields.Char('NumberOfBands ',size=64)
    number_of_grooves_pt_pp = fields.Char('NumberOfGrooves ',size=64)



    #####################PetSupply#######################

    breed_recommendation_pp =  fields.Char('BreedRecommendation',size=64)
    battery_cell_composition_pp =  fields.Char('BatteryCellComposition',size=64)
    battery_form_factor_ps_pp =  fields.Char('BatteryFormFactor',size=64)
    closure_type_ps_pp =  fields.Char('ClosureType',size=64)
    contains_food_or_beverage_ps_pp =  fields.Char('ContainsFoodOrBeverage',size=64)
    color_specification_ps_pp =  fields.Char('ColorSpecification',size=64)
    dog_size_ps_pp =  fields.Char('DogSize',size=64)
    external_certification_ps_pp =  fields.Char('ExternalCertification',size=64)
    fill_material_type_ps_pp =  fields.Char('FillMaterialType',size=64)
    girth_size_ps_pp =  fields.Char('GirthSize',size=64)
    height_recommendation_ps_pp =  fields.Char('HeightRecommendation',size=64)
    health_benefits_ps_pp =  fields.Char('HealthBenefits',size=64)
    included_components_ps_pp =  fields.Char('IncludedComponents',size=64)
    includes_ac_adapter_ps_pp =  fields.Boolean('IncludesAcAdapter')
    inner_material_type_ps_pp =  fields.Char('InnerMaterialType',size=64)
    is_expiration_dated_product_ps_pp =  fields.Boolean('IsExpirationDatedProduct')
    is_portable_ps_pp =  fields.Boolean('IsPortable')
    item_display_diameter_ps_pp =  fields.Char('ItemDisplayDiameter',size=64)
    item_form_ps_pp =  fields.Char('ItemForm',size=64)
    item_thickness_ps_pp =  fields.Char('ItemThickness',size=64)
    light_output_luminance_ps_pp =  fields.Char('LightOutputLuminance',size=64)
    max_ordering_quantity_ps_pp =  fields.Char('MaxOrderingQuantity',size=64)
    maximum_age_recommendation_ps_pp =  fields.Char('MaximumAgeRecommendation',size=64)
    mfg_warranty_description_labor_ps_pp =  fields.Char('MfgWarrantyDescriptionLabor',size=64)
    mfg_warranty_description_parts_ps_pp =  fields.Char('MfgWarrantyDescriptionParts',size=64)
    mfg_warranty_description_type_ps_pp =  fields.Char('MfgWarrantyDescriptionType',size=64)
    minimum_age_recommendation_ps_pp =  fields.Char('MinimumAgeRecommendation',size=64)
    nutrition_facts_ps_pp =  fields.Char('NutritionFacts',size=64)
    outer_material_type_ps_pp =  fields.Char('OuterMaterialType',size=64)
    pattern_name_ps_pp =  fields.Char('PatternName',size=64)
    pet_life_stage_ps_pp =  fields.Char('PetLifeStage',size=64)
    pet_type_ps_pp =  fields.Char('PetType',size=64)
    product_feature_ps_pp =  fields.Char('ProductFeature',size=64)
    product_sample_received_date_ps_pp =  fields.Char('ProductSampleReceivedDate',size=64)
    recommended_uses_for_product_ps_pp =  fields.Char('RecommendedUsesForProduct',size=64)
    scent_name_ps_pp =  fields.Char('ScentName',size=64)
    storage_instructions_ps_pp =  fields.Char('StorageInstructions',size=64)
    tank_size_ps_pp =  fields.Char('TankSize',size=64)
    width_size_ps_pp =  fields.Char('WidthSize',size=64)
    model_name_ps_pp =  fields.Char('ModelName',size=64)
    material_features_ps_pp =  fields.Char('MaterialFeatures',size=64)

    legal_compliance_certification_regulatory_organization_name_pp =  fields.Char('LegalComplianceCertificationRegulatoryOrganizationName',size=64)
    legal_compliance_certification_certifying_authority_name_ps_pp =  fields.Char('LegalComplianceCertificationCertifyingAuthorityName',size=64)
    legal_compliance_certification_geographic_jurisdiction_ps_pp =  fields.Char('LegalComplianceCertificationGeographicJurisdiction',size=64)
    legal_compliance_certification_status_ps_pp =  fields.Selection([('compliant','compliant'),('noncompliant','noncompliant'),('exempt','exempt')],'LegalComplianceCertificationStatus')
    legal_compliance_certification_Value_ps_pp =  fields.Char('LegalComplianceCertificationValue',size=64)





    ########################light##################   
     
    airflowcapacity_li_pp  =  fields.Char('AirFlowCapacity',size=64)
    basediameter_li_pp  =  fields.Char('BaseDiameter',size=64)
    battery_li_pp  =  fields.Char('Battery',size=64)
    bulbdiameter_li_pp =  fields.Char('BulbDiameter',size=64)
    bulblength_li_pp  =  fields.Char('BulbLength',size=64)
    bulblifespan_li_pp  =  fields.Char('BulbLifeSpan',size=64)
    bulbpowerfactor_li_pp  =  fields.Char('BulbPowerFactor',size=64)
    bulbspecialfeatures_li_pp  =  fields.Text('BulbSpecialFeatures',size=64)
    bulbswitchingcycles_li_pp =  fields.Char('BulbSwitchingCycles',size=64)
    bulbtype_li_pp  =  fields.Char('BulbType',size=64)
    bulbwattage_li_pp =  fields.Char('BulbWattage',size=64)
    captype_li_pp  =  fields.Char('CapType',size=64)
    certification_li_pp  =  fields.Char('Certification',size=64)
    collection_li_pp  =  fields.Char('Collection',size=64)
    # color_li  =  fields.Char('Color',size=64)
    energy_rating_li_pp  =  fields.Char('EnergyEfficiencyRating',size=64)
    inte_rating_li_pp  =  fields.Char('InternationalProtectionRating',size=64)
    itemdiameter_li_pp  =  fields.Char('ItemDiameter',size=64)
    lightingmethod_li_pp  =  fields.Char('LightingMethod',size=64)
    lithium_content_li_pp  =  fields.Char('LithiumBatteryEnergyContent',size=64)
    lithium_voltage_li_pp  =  fields.Char('LithiumBatteryVoltage',size=64)
    lithium_weight_li_pp  =  fields.Char('LithiumBatteryWeight',size=64)
    # material_li_pp  =  fields.Char('Material',size=64)
    numberofblades_li_pp  =  fields.Char('NumberOfBlades',size=64)
    numberofbulbsockets_li_pp  =  fields.Char('NumberOfBulbSockets',size=64)
    plugtype_li_pp  =  fields.Char('PlugType',size=64)
    powersource_li_pp  =  fields.Char('PowerSource',size=64)
    specialfeatures_li_pp  =  fields.Char('SpecialFeatures',size=64)
    specificuses_li_pp  =  fields.Char('SpecificUses',size=64)
    stylename_li_pp  =  fields.Char('StyleName',size=64)
    switchstyle_li_pp  =  fields.Char('SwitchStyle',size=64)
    # voltage_li_pp  =  fields.Char('Voltage',size=64)
    volume_li_pp  =  fields.Char('Volume',size=64)
    # wattage_li_pp  =  fields.Char('Wattage',size=64)
    

    mercury_bulb_pp = fields.Char('MercuryContent')
    more_attributes_pp = fields.Boolean('More Attributes')



    ##################### CameraPhoto ########################


    camera_type_cp_pp = fields.Selection([('point-and-shoot','point-and-shoot'),('slr','slr'),('instant','instant'),('single-use','single-use'),('large-format','large-format'),('medium-format','medium-format'),('rangefinder','rangefinder'),('field','field'),('monorail','monorail'),('kids','kids'),('3-d','3-d'),('micro','micro'),('panorama','panorama'),('passport-and-id','passport-and-id'),('underwater','underwater'),('security-cameras','security-cameras'),('dummy-cameras','dummy-cameras'),('web-cameras','web-cameras'),('mirror-image-cameras','mirror-image-cameras'),('dome-cameras','dome-cameras'),('spy-cameras','spy-cameras'),('pinhole-cameras','pinhole-cameras'),('miniature-cameras','miniature-cameras'),('pen-cameras','pen-cameras'),('camcorder','camcorder'),('digital-camera','digital-camera'),('large-format','large-format'),('medium-format','medium-format'),('universal','universal'),('other','other')],'CameraType')

    has_image_stabilizer_cp_pp = fields.Boolean('HasImageStabilizer')
    display_technology_cp_pp = fields.Char('DisplayTechnology',size=64)
    manufacturer_cp_pp = fields.Char('Manufacturer',size=64)
    model_number_cp_pp = fields.Char('ModelNumber',size=64)
    mfr_part_number_cp_pp = fields.Char('MfrPartNumber',size=64)
    auto_focus_technology_cp_pp = fields.Char('AutoFocusTechnology',size=64)
    film_speed_range_cp_pp = fields.Char('FilmSpeedRange',size=64)
    memory_Storage_Capacity_cp_pp = fields.Char('MemoryStorageCapacity',size=64)
    memory_technology_cp_pp = fields.Char('MemoryTechnology',size=64)

    # in filmcam
    film_format_cp_pp = fields.Selection([('aps','aps'),('16mm','16mm'),('35mm','35mm'),('110','110'),('120','120'),('2x3','2x3'),('4x5','4x5'),('8x10','8x10'),('10x12','10x12'),('16x20','16x20')],'FilmFormat')
    film_management_features_cp_pp = fields.Char('FilmManagementFeatures',size=64)

    # in otherAcc
    camera_accessories_cp_pp = fields.Selection([('mounting-brackets','mounting-brackets'),('power-adapter','power-adapter'),('cable','cable'),('sun-shield','sun-shield'),('camera-controller','camera-controller'),('transmitters','transmitters'),('zoom-lens','zoom-lens'),('pinhole-lens','pinhole-lens'),('close-up-accessories','close-up-accessories'),('viewfinders','viewfinders'),('motor-drives','motor-drives'),('remote-controls','remote-controls'),('cables-and-cords','cables-and-cords'),('other-camera-accessories','other-camera-accessories')],'CameraAccessories')

    camcorder_accessories_cp_pp = fields.Selection([('remote-controls','remote-controls'),('cables-and-cords','cables-and-cords'),('other-camcorder-accessories','other-camcorder-accessories')],'CamcorderAccessories')
# 
    # in powrsspply
    camera_power_supply_type_cp_pp = fields.Selection([('batteries-general','batteries-general'),('disposable-batteries','disposable-batteries'),('rechargeable-Batteries','rechargeable-Batteries'),('external-batteries','external-batteries'),('adapters-general','adapters-general'),('ac-adapters','ac-adapters'),('dc-adapters','dc-adapters'),('battery-chargers','battery-chargers'),('ac-power-supply','ac-power-supply'),('dc-power-supply','dc-power-supply'),('other-power-supplies','other-power-supplies'),('battery-packs-general','battery-packs-general'),('dedicated-battery-packs','dedicated-battery-packs'),('other-batteries-and-packs','other-batteries-and-packs')],'CameraPowerSupplyType')

    # in Projctn
    projection_type_cp_pp = fields.Selection([('video-projectors','video-projectors'),('large-format-projectors','large-format-projectors'),('medium-format-projectors','medium-format-projectors'),('multimedia-projectors','multimedia-projectors'),('opaque-projectors','opaque-projectors')],'ProjectionType')
    projector_lenses_cp_pp  = fields.Selection([('35mm','35mm'),('large-format','large-format'),('medium-format','medium-format'),('normal','normal'),('telephoto','telephoto'),('wide-angle','wide-angle'),('zoom','zoom'),('other-projector-lenses','other-projector-lenses')],'ProjectorLenses') 
    projection_screens_cp_pp = fields.Selection([('fast-fold-screens','fast-fold-screens'),('free-standing-floor-screens','free-standing-floor-screens'),('rear-projection-screens','rear-projection-screens'),('tabletop-screens','tabletop-screens'),('tripod-mounted-screens','tripod-mounted-screens'),('wall-and-ceiling-electric-screens','wall-and-ceiling-electric-screens'),('other-projection-screens','other-projection-screens')],'ProjectionScreens')

    # in photostidio
    storage_and_presentation_materials_cp_pp = fields.Selection([('hanging-bars','hanging-bars'),('pages-general','pages-general'),('negative-and-unmounted-slides-pages','negative-and-unmounted-slides-pages'),('mounted-slides-sleeves','mounted-slides-sleeves'),('prints-sleeves','prints-sleeves'),('other-media-sleeves','other-media-sleeves'),('negatives-boxes','negatives-boxes'),('slides-boxes','slides-boxes'),('prints-boxes','prints-boxes'),('other-boxes','other-boxes'),('portfolios','portfolios'),('presentation-boards','presentation-boards'),('professional-photo-albums','professional-photo-albums'),('other-professional-albums','other-professional-albums'),('sectional-frames','sectional-frames'),('digital-frames','digital-frames'),('other-professional-frames','other-professional-frames')],'StorageAndPresentationMaterials')


    studio_supplies_cp_pp = fields.Selection([('mounting-press','mounting-press'),('mat-boards-general','mat-boards-general'),('pressure-sensitive-boards','pressure-sensitive-boards'),('laminating-machines','laminating-machines'),('other-copystands','other-copystands')],'StudioSupplies')

    photo_backgrounds_cp_pp = fields.Selection([('ceiling-to-floor','ceiling-to-floor'),('collapsible-discs','collapsible-discs'),('free-standing','free-standing'),('graduated','graduated'),('wall-mounted','wall-mounted'),('other-background-styles','other-background-styles')],'PhotoBackgrounds')

    # in Light Meter
    meter_type_cp_pp = fields.Selection([('flash','flashr'),('ambient-and-flash','ambient-and-flash'),('spot','spot'),('color','color')],'MeterType')

    meter_display_cp_pp  = fields.Selection([('analog','analog'),('digital','digital'),('led','led'),('match-needle','match-needle')],'MeterDisplay')

    # in otherAcc, SurveillanceSystem 
    night_vision_cp_pp  = fields.Boolean('NightVision')

    # in filmcam, digtl cam, binoclr, Lens
    focus_type_cp_pp  = fields.Selection([('auto-focus','auto-focus'),('manual-focus','manual-focus'),('manual-and-auto-focus','manual-and-auto-focus'),('focus-free','focus-free')],'FocusType')

    # in filmcam, digtl cam,
    lens_thread_cp_pp = fields.Char('LensThread',size=64)

    # in filmcam, camcorder, digtlcam, SurveillanceSystem, Filter, other
    durability_cp_pp = fields.Char('Durability',size=64)

    # in filmcam, camcorder, digtlcam, binoclr, SurveillanceSystem, Microscope, Lens, BagCase
    features_cp_pp = fields.Char('Features',size=64)



    #############################Gift Cards#############################33
    genre_gift_pp = fields.Char('Genre')
    targetgender_gift_pp = fields.Selection([('male','male'),('female','female'),('unisex','unisex')],'TargetGender')
    itemdisplayheight_gift_pp = fields.Char('ItemDisplayHeight')
    itemdisplaywidth_gift_pp = fields.Char('ItemDisplayWidth')

    ######################home################

    numberofpieces_home_pp = fields.Char('NumberOfPieces')



    ##########################Toys AND games####################
    
    Flavor_pp = fields.Char('Flavor')
    assembly_instructions_tg_pp = fields.Char('AssemblyInstructions')
    assembly_time_tg_pp = fields.Datetime('AssemblyTime')
    edition_tg_pp = fields.Char('Edition')
    is_assembly_required_tg_pp = fields.Boolean('IsAssemblyRequired')
    manufacturer_safety_warning_tg_pp = fields.Char('ManufacturerSafetyWarning')
    weight_recommendation_tg_pp = fields.Char('WeightRecommendation')
    number_of_players_tg_pp = fields.Char('NumberOfPlayers')
    part_number_tg_pp = fields.Char('PartNumber')
    size_map_tg_pp = fields.Char('SizeMap')
    subject_character_tg_pp = fields.Char('SubjectCharacter')
    isadultproduct_toys_tg_pp = fields.Boolean('IsAdultProduct')

    engine_type_tg_pp = fields.Char('EngineType')
    awards_won_tg_pp = fields.Char('AwardsWon')
    color_map_tg_pp = fields.Char('color_map')
    directions_tg_pp = fields.Char('Directions')
    number_of_control_channels_tg_pp = fields.Char('NumberOfControlChannels')
    frequency_bands_supported_tg_pp = fields.Char('FrequencyBandsSupported')
    language_tg_pp = fields.Char('language')
    includes_remote_tg_pp = fields.Char('IncludesRemote')
    power_source_type_tg_pp = fields.Char('PowerSourceType')
    recommended_use_tg_pp = fields.Char('RecommendedUse')
    remote_control_technology_tg_pp = fields.Char('RemoteControlTechnology')
    rail_gauge_tg_pp = fields.Char('RailGauge')
    region_of_origin_tg_pp = fields.Char('RegionOfOrigin')
    drive_system_tg_pp = fields.Char('DriveSystem')
    fuel_capacity_tg_pp = fields.Char('FuelCapacity')
    fuel_type_tg_pp = fields.Char('FuelType')
    material_composition_tg_pp = fields.Char('MaterialComposition')
    care_instructions_tg_pp = fields.Char('CareInstructions')
    handle_height_tg_pp = fields.Char('HandleHeight')
    seat_length_tg_pp = fields.Char('SeatLength')
    seat_width_tg_pp = fields.Char('SeatWidth')
    tire_material_tg_pp = fields.Char('TireMaterial')
    tire_diameter_tg_pp = fields.Char('TireDiameter')
    style_keywords_tg_pp = fields.Char('StyleKeywords')
    warranty_description_tg_pp = fields.Char('WarrantyDescription')
    scale_name_tg_pp = fields.Char('ScaleName')
    specification_met_tg_pp = fields.Boolean('SpecificationMet')

    specific_uses_for_product_tg_pp = fields.Char('SpecificUsesForProduct')
    material_type_tg_pp = fields.Char('MaterialType')

    active_surface_area_tg_pp = fields.Char('ActiveSurfaceArea')
    wing_area_tg_pp = fields.Char('WingArea')
    collection_name_tg_pp = fields.Char('CollectionName')
    initial_print_run_rarity_tg_pp = fields.Char('InitialPrintRunRarity')
    # specific_uses_for_product = fields.Char('specific_uses_for_product')
    brake_style_tg_pp = fields.Char('BrakeStyle')
    drive_system_tg_pp = fields.Char('DriveSystem')
    frame_material_type_tg_pp = fields.Char('FrameMaterialType')
    fuel_capacity_tg_pp = fields.Char('FuelCapacity')
    # fuel_type_tg_pp = fields.Char('FuelType')
    maximum_range_tg_pp = fields.Char('MaximumRange')
    maximum_speed_tg_pp = fields.Char('MaximumSpeed')
    motor_type_tg_pp = fields.Char('MotorType')
    display_size_tg_pp = fields.Char('DisplaySize')
    display_type_tg_pp = fields.Char('DisplayType')
    engine_displacement_tg_pp = fields.Char('EngineDisplacement')
    liquid_volume_tg_pp = fields.Char('LiquidVolume')
    movement_type_tg_pp = fields.Char('MovementType')
    surface_recommendation_tg_pp = fields.Char('SurfaceRecommendation')
    radio_bands_supported_tg_pp = fields.Char('RadioBandsSupported')
    rail_type_tg_pp = fields.Char('RailType')
    scale_tg_pp = fields.Char('Scale')
    suspension_type_tg_pp = fields.Char('SuspensionType')
    tire_type_tg_pp = fields.Char('TireType')
    wheel_diameter_tg_pp = fields.Char('WheelDiameter')
    wheel_type_tg_pp = fields.Char('WheelType')

    collection_tg_pp = fields.Char('Collection')
    rarity_tg_pp = fields.Char('Rarity')
    card_number_tg_pp = fields.Char('CardNumber')
    card_type_tg_pp = fields.Char('CardType')

    educational_objective_tg_pp = fields.Char('EducationalObjective')

    number_of_frequency_channels_tg_pp = fields.Char('NumberOfFrequencyChannels')
    is_electric_tg_pp = fields.Char('IsElectric')
    animal_type_tg_pp = fields.Char('AnimalType')
    skill_level_tg_pp = fields.Char('SkillLevel')
    toy_award_name_tg_pp = fields.Char('ToyAwardName')
    publisher_contributor_tg_pp = fields.Char('PublisherContributor')
    distribution_designation_tg_pp = fields.Char('DistributionDesignation')
    country_string_tg_pp = fields.Char('CountryString')


    #####################FoodServicesAndJanSan##############################

    item_volume_fs_pp = fields.Char('ItemVolume',size=64)
    holding_time_fs_pp = fields.Char('HoldingTime',size=64)
    heat_time_fs_pp = fields.Char('HeatTime',size=64)
    graduation_range_fs_pp = fields.Char('GraduationRange',size=64)
    graduation_interval_fs_pp = fields.Char('GraduationInterval',size=64)
    extension_length_fs_pp = fields.Char('ExtensionLength',size=64)
    current_rating_fs_pp = fields.Char('CurrentRating',size=64)
    coolant_consumption_rate_fs_pp = fields.Char('CoolantConsumptionRate',size=64)
    coolant_capacity_fs_pp = fields.Char('CoolantCapacity',size=64)
    cap_size_fs_pp = fields.Char('CapSize',size=64)
    age_range_description_fs_pp = fields.Char('AgeRangeDescription',size=64)

    ################## LabSupply ########

    chamber_depth_ls_pp = fields.Char('ChamberDepth',size=64)
    chamber_height_ls_pp = fields.Char('ChamberHeight',size=64)
    chamber_width_ls_pp = fields.Char('ChamberWidth',size=64)
    heated_element_dimensions_pp = fields.Char('HeatedElementDimensions',size=64)
    heater_surface_material_type_pp = fields.Char('HeaterSurfaceMaterialType',size=64)
    heating_element_type_pp = fields.Char('HeatingElementType',size=64)


    ############### Large Appliances ##################

    battery_life_la_pp = fields.Char('BatteryLife',size=64)
    # in cookoven: 
    burner_type_la_pp = fields.Char('BurnerType',size=64)
    drawer_type_la_pp = fields.Char('DrawerType',size=64)
    # fuel_type_la_pp = fields.Char('FuelType',size=64)
    # in cookoven, microoven:
    racks_la_pp = fields.Char('Racks',size=64)
    # in ref:
    freezer_capacity_la_pp = fields.Char('FreezerCapacity',size=64)
    ice_capacity_la_pp = fields.Char('IceCapacity',size=64)

    installation_type_la_pp = fields.Char('InstallationType',size=64)
    item_thickness_la_pp = fields.Char('ItemThickness',size=64)


    ################## Computers #######################

    assembly_required_pp = fields.Boolean('AssemblyRequired')
    manufacturer_warranty_type_pp = fields.Char('ManufacturerWarrantyType',size=64)

    hand_orientation_pp = fields.Selection([('Solar','Solar'),('Solar','Solar')],'HandOrientation')
    input_device_design_style_pp = fields.Selection([('Solar','Solar'),('Solar','Solar')],'InputDeviceDesignStyle')
    keyboard_description_pp = fields.Char('Keyboard Description',size=64)

    model_number_pp = fields.Char('Model Number')
   
    wireless_input_device_protocol_pp = fields.Selection([('Solar','Solar'),('Solar','Solar')],'Wireless InputDevice Protocol')
    wireless_input_device_technology_pp = fields.Selection([('Solar','Solar'),('Solar','Solar')],'Wireless InputDevice Technology')

    additional_features_net_pp = fields.Char('Additional Features',size=64)
    additional_functionality_net_pp = fields.Char('Additional Functionality',size=64)
    ipprotocol_standards_net_pp = fields.Char('IP ProtocolStandards',size=64)
    lanportbandwidth_net_pp = fields.Char('LAN Port Bandwidth',size=64)
    lan_port_number_net_pp = fields.Char('LAN Port Number',size=64)
    maxdownstreamtransmissionrate_net_pp = fields.Char('Max Downstream Transmission Rate',size=64)
    maxupstreamtransmissionRate_net_pp = fields.Char('Max Upstream Transmission Rate',size=64)
    model_number_net_pp = fields.Char('Model Number',size=64)
    modem_type_net_pp = fields.Char('Modem Type',size=64)
    network_adapter_type_type_net_pp = fields.Char('Network Adapter Type',size=64)
    operating_system_compatability_net_pp = fields.Char('Operating System Compatability',size=64)
    securityprotocol_net_pp = fields.Char('Security Protocol',size=64)
    simultaneous_sessions_net_pp = fields.Char('Simultaneous Sessions',size=64)
    # voltage_net = fields.Char('Voltage',size=64)
    # wattage_net= fields.Char('Wattage',size=64)
    wirelessdatatransferrate_net_pp = fields.Char('Wireless Data Transfer Rate',size=64)
    wirelessroutertransmissionband_net_pp = fields.Char('Wireless Router Transmission Band',size=64)
    wirelesstechnology_net_pp = fields.Char('Wireless Technology',size=64)
    
#     variationdata_scanner = fields.Char('Variation Data',size=64)
    hasgreyscale_scanner_pp = fields.Char('Has Grey Scale',size=64)
    lightsourcetype_scanner_pp = fields.Char('Battery Chargecycles',size=64)
    maxinputsheetcapacity_scanner_pp = fields.Integer('Max Input Sheet Capacity')
    maxprintresolutionblackwhite_scanner_pp = fields.Char('Max Print Resolution BlackWhite',size=64)
    maxprintresolutioncolor_scanner_pp  =  fields.Char('Max Print Resolution Color',size=64)
    maxprintspeedblackwhite_scanner_pp  =  fields.Char('Max Print Speed BlackWhite',size=64)
    maxprintspeedcolor_scanner_pp  =  fields.Char('Max Print Speed Color',size=64)
    maxscanningsize_scanner_pp  =  fields.Char('Max scanning size',size=64)
    minscanningsize_scanner_pp  =  fields.Char('Min Scanning Size',size=64)
    printermediasizemaximum_scanner_pp  =  fields.Char('Printer Media Size Maximum',size=64)
    printeroutputtype_scanner_pp  =  fields.Char('Printer Output Type',size=64)
    printerwirelesstype_scanner_pp  =  fields.Char('Printer Wireless Type',size=64)
    printing_media_type_scanner_pp  =  fields.Char('Printing Media Type',size=64)
    printingtechnology_scanner_pp  =  fields.Char('Printing Technology',size=64)
    scanrate_scanner_scanner_pp  =  fields.Char('Scan Rate',size=64)
    scannerresolution_scanner_pp  =  fields.Char('Scanner Resolution',size=64)
    
   

    

    def ExportVarients(self,products,instance,message_id):
#         print"message_id"
        message_information = ''
        for product in products:
            merchant_string = ''
            standard_product_string = ''
            merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(instance.amazon_instance_id.aws_merchant_id)
            message_id = message_id+1
            product_sku = product.default_code
            if product.name:
                title = product.name
            product_str = """<MessageType>Product</MessageType>
                            <PurgeAndReplace>false</PurgeAndReplace>"""
            if product.description_sale:
                sale_description = product.description_sale
                if sale_description:
                    desc = "<Description><![CDATA[%s]]></Description>"%(sale_description)
#             if not product.asin:
#                 raise UserError(_('Error'), _('ASIN or EAN Required!!'))
            if product.ean_barcode:
                standard_product_string = """
                    <StandardProductID>
                    <Type>EAN</Type>
                    <Value>%s</Value>
                    </StandardProductID>
                    """%(product.ean_barcode)
            elif product.upc:
                standard_product_string = """
                <StandardProductID>
                <Type>UPC</Type>
                <Value>%s</Value>
                </StandardProductID>
                """%(product.upc)
            elif product.isbn:
                standard_product_string = """
                <StandardProductID>
                <Type>ISBN</Type>
                <Value>%s</Value>
                </StandardProductID>
                """%(product.isbn)
            else:
                standard_product_string = """
                <StandardProductID>
                <Type>ASIN</Type>
                <Value>%s</Value>
                </StandardProductID>
                """%(product.asin)
            message_information += """<Message><MessageID>%s</MessageID>
                                        <OperationType>Update</OperationType>
                                        <Product>
                                        <SKU>%s</SKU>%s
                                        <DescriptionData>
                                        <Title><![CDATA[%s]]></Title>"""%(message_id,product_sku,standard_product_string,title)
            if product.brand_name:
                message_information += """<Brand><![CDATA[%s]]></Brand>"""%(product.brand_name)
#             message_information +="""<MSRP currency="EUR">10000</MSRP>"""
            if product.description_sale:
                message_information += """<Description><![CDATA[%s]]></Description>"""%(product.description_sale)
            if product.shipping_weight:
                message_information += '<ShippingWeight unitOfMeasure="%s">%s</ShippingWeight>'%(product.shipping_weight_uom, product.shipping_weight)
            if product.amazon_manufacturer:
                message_information +="""<Manufacturer><![CDATA[%s]]></Manufacturer>"""%(product.amazon_manufacturer)
            if product.manufacturer_part:
                message_information +="""<MfrPartNumber><![CDATA[%s]]></MfrPartNumber>"""%(product.manufacturer_part)
            if product.amazon_categ_id:
                message_information += """<RecommendedBrowseNode>%s</RecommendedBrowseNode>""" %(product.amazon_categ_id.amazon_cat_id)
            
            xml_product_type =''
            if product_tem_data.product_data == 'AutoAccessory':
               xml_product_type = self.Product_Auto_xml(product_tem_data,)
            elif product_tem_data.product_data == 'Baby':
               xml_product_type += self.Product_ToysBaby_xml(product_tem_data)
            elif product_tem_data.product_data == 'CameraPhoto':
                xml_product_type += self.Product_CameraPhoto_xml(product_tem_data)
            elif product_tem_data.product_data == 'Clothing':
                xml_product_type += self.Product_Clothing_xml(product_tem_data)
            elif product_tem_data.product_data == 'CE':
                xml_product_type += self.Product_ce_xml(product_tem_data)
            elif product_tem_data.product_data == 'Computers':
                xml_product_type += self.Product_Computers_xml(product_tem_data)
            elif product_tem_data.product_data == 'FoodAndBeverages':
                xml_product_type += self.Product_FoodAndBeverages_xml(product_tem_data)
            elif product_tem_data.product_data == 'Gourmet':
                xml_product_type +=self.Product_Gourmet_xml(product_tem_data)
                #xml_product_type += products.product_data
            elif product_tem_data.product_data == 'Health':
                xml_product_type += self.Product_Health_xml(product_tem_data)
            elif product_tem_data.product_data == 'HomeImprovement':
                xml_product_type += self.Product_HomeImprovement_xml(product_tem_data)
            elif product_tem_data.product_data == 'FoodServiceAndJanSan':
                xml_product_type += self.Product_FoodServiceAndJanSan_xml(product_tem_data)
            elif product_tem_data.product_data == 'LabSupplies':
                xml_product_type += self.Product_LabSupplies_xml(product_tem_data)
            elif product_tem_data.product_data == 'PowerTransmission':
                xml_product_type += self.Product_PowerTransmission_xml(product_tem_data)
            elif product_tem_data.product_data == 'RawMaterials':
                xml_product_type += self.Product_RawMaterials_xml(product_tem_data)
            elif product_tem_data.product_data == 'Jewelry':
                xml_product_type += self.Product_Jewelry_xml(product_tem_data)
            elif product_tem_data.product_data == 'Lighting':
                xml_product_type += self.Product_Lighting_xml(product_tem_data)
            elif product_tem_data.product_data == 'MusicalInstruments':
                xml_product_type += self.Product_MusicalInstruments_xml(product_tem_data)
            elif product_tem_data.product_data == 'PetSupplies':
                xml_product_type += self.Product_PetSupplies_xml(product_tem_data)
            elif product_tem_data.product_data == 'Shoes':
                xml_product_type += self.Product_Shoes_xml(product_tem_data)
            elif product_tem_data.product_data == 'Wireless':
                xml_product_type += self.Product_Wireless_xml(product_tem_data)
            elif product_tem_data.product_data == 'Sports':
                xml_product_type += self.Product_Sport_xml(product_tem_data)
            elif product_tem_data.product_data == 'SportsMemorabilia':
                xml_product_type += self.Product_sportsmemorabilia_xml(product_tem_data)
            elif product_tem_data.product_data == 'TiresAndWheels':
                xml_product_type += self.Product_tiresandwheels_xml(product_tem_data)
            elif product_tem_data.product_data == 'Tools':
                xml_product_type += self.Product_Tools_xml(product_tem_data)
            elif product_tem_data.product_data == 'Toys':
                xml_product_type += self.Product_toys_xml(product_tem_data)
            elif product_tem_data.product_data == 'Video':
                xml_product_type += self.Product_Video_xml(product_tem_data)
            elif product_tem_data.product_data == 'LargeAppliances':
                xml_product_type += self.Product_LargeAppliances_xml(product_tem_data)
            
            if product.attribute_value_ids:
                variationtheme = ''
                tag = ''
                size = False
                color = False
                size_color = ''
                if product.variationtheme=='Size-Color':
                    for variation in product.attribute_value_ids:
                        if variation.attribute_id.name.lower()=='size':
                            size = variation.name
                        elif variation.attribute_id.name.lower()=='color':
                            color = variation.name
                    size_color += """<Size>%s</Size>
                                    <Color>%s</Color>"""%(size,color)
                elif product.variationtheme=='SizeColor':
                    for variation in product.attribute_value_ids:
                        if variation.attribute_id.name.lower()=='size':
                            size = variation.name
                        elif variation.attribute_id.name.lower()=='color':
                            color = variation.name
                    size_color += """<Size>%s</Size>
                                    <Color>%s</Color>"""%(size,color)
                                    
                elif product.variationtheme=='ColorSize':
                    for variation in product.attribute_value_ids:
                        if variation.attribute_id.name.lower()=='size':
                            size = variation.name
                        elif variation.attribute_id.name.lower()=='color':
                            color = variation.name
                    size_color += """<Color>%s</Color>
                                    <Size>%s</Size>
                                    """%(color,size)
                                    
                elif product.variationtheme=='Size':
                    for variation in product.attribute_value_ids:
                        if variation.attribute_id.name.lower()=='size':
                            size = variation.name
                    size_color += """<Size>%s</Size>"""%(size)
                            
                elif product.variationtheme=='Color':
                    for variation in product.attribute_value_ids:
                        if variation.attribute_id.name.lower()=='color':
                            color = variation.name
                    size_color += """<Color>%s</Color>"""%(color)
#                     if variationtheme:
#                         variationtheme = variationtheme+'-'+variation.attribute_id.name
#                     else:
#                         variationtheme = variation.attribute_id.name
                
#                 if tag:
#                     tag=tag+'\n<'+variation.attribute_id.name + '>' + variation.name + '</'+variation.attribute_id.name + '>'
#                 else:
#                     tag='<'+variation.attribute_id.name + '>' + variation.name + '</'+variation.attribute_id.name + '>'
#             material_type = "100% Luxury Egyptian Cotton"
            message_information +="""</DescriptionData>
                                            <ProductData>
                                            <%s>
                                            <Parentage>child</Parentage>
                                            <VariationData>
                                                <VariationTheme>%s</VariationTheme>%s
                                            </VariationData>
                                            <Material>%s</Material>
                                            </%s>
                                          </ProductData>
                                          """%(product.variationtheme,size_color,product.material_type)
            message_information += """</Product>
                                        </Message>"""
#         logger.info("message_information%s"%(message_information))
#         print"message_informationmessage_information",message_information
        return message_information

    def RelateVarients(self,products,instance,template):
            str=''
            merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(instance.amazon_instance_id.aws_merchant_id)
            message_information = ''
            message_id = 1
            message_information += """<MessageType>Relationship</MessageType>
                                        <Message>
                                        <MessageID>%s</MessageID>
                                        <OperationType>Update</OperationType>
                                        <Relationship>
                                        <ParentSKU>%s</ParentSKU>
                                        """%(message_id,template.amazon_sku)
            for product in products:
                message_information += """<Relation>
                                    <SKU>%s</SKU>
                                    <Type>Variation</Type>
                                    </Relation>
                                    """%(product.default_code)
                                    
            message_information += """</Relationship>
                                    </Message>"""
                                    
            str = """
                <?xml version="1.0" encoding="utf-8" ?>
<AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amznenvelope.xsd">
<Header>
<DocumentVersion>1.01</DocumentVersion>
                """+merchant_string+"""
                </Header>
                """+message_information+"""
                """
            str +="""</AmazonEnvelope>"""
            print("str",str)
            if str:
                relation_submission_id = amazon_api_obj.call(instance, 'POST_PRODUCT_RELATIONSHIP_DATA',str)
                print("relation_submission_id",relation_submission_id)
#             relation_data_xml = instance.xml_format(merchant_string, message_information)
#             print"relation_data_xmlrelation_data_xml",relation_data_xml


    def StandardSalePrice(self,products,instance,template):
        str=''
        merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(instance.amazon_instance_id.aws_merchant_id)
        message_information = ''
        message_id = False
        message_information += """<MessageType>Price</MessageType>
                                """
        print("instanceinstanceinstance",instance)                        
        for product in products:
            message_id = message_id +1
            offer = ''
            if self.env.context.get('price_list_id'):
                product_rule = self.env.context.get('price_list_id')._compute_price_rule([(product, 1, False)])
                print("product_ruleproduct_rule111111111111111",product_rule)
            else:
                product_rule = instance.pricelist_id._compute_price_rule([(product, 1, False)])
                print("product_ruleproduct_rule",product_rule)
                
            itemprice = False    
            item_date = self.env['product.pricelist.item'].browse(product_rule.get(product.id)[1])
            print("item_date",item_date)
            if item_date:
                start_date = (item_date.date_start)
                if start_date:
                    start_date = datetime.strptime(start_date,'%Y-%m-%d') 
                    start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S.00Z")
                    print("start_date",start_date)
                end_date = (item_date.date_end)
                if end_date:
                    end_date = datetime.strptime(end_date,'%Y-%m-%d') 
                    end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S.00Z")
                itemprice = product_rule.get(product.id)[0]
                print("itemprice",itemprice)
            message_information += """<Message>
                                    <MessageID>%s</MessageID>
                                    <Price>
                                    <SKU>%s</SKU>
                                    <StandardPrice currency="%s">%s</StandardPrice>
                                """%(message_id, product.default_code,instance.res_currency.name, product.amazon_standard_price)

            if itemprice!=0.0 and itemprice < product.amazon_standard_price:
                offer = """<Sale>
                            <StartDate>%s</StartDate>
                            <EndDate>%s</EndDate>
                             <SalePrice currency="%s">%s</SalePrice>
                            </Sale>"""%(start_date,end_date,instance.res_currency.name, itemprice)
                print("offer",offer)
            if offer:
                message_information += """%s"""%(offer)
            message_information += """</Price>
                                    </Message>"""
                                
        if template:
            message_id = message_id +1
            offer = ''
            if self.env.context.get('price_list_id'):
                product_rule = self.env.context.get('price_list_id')._compute_price_rule([(template, 1, False)])
            else:
                product_rule = instance.pricelist_id._compute_price_rule([(template, 1, False)])
                
            item_date = self.env['product.pricelist.item'].browse(product_rule.get(template.id)[1])
            print("item_date",item_date)
            itemprice = False
            if item_date:
                start_date = item_date.date_start
                print("start_date",start_date)
                if start_date:
                    start_date = datetime.strptime(start_date,'%Y-%m-%d') 
                    start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S.00Z")
                    print("start_date",start_date)
                end_date = (item_date.date_end)
                if end_date:
                    end_date = datetime.strptime(end_date,'%Y-%m-%d') 
                    end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S.00Z")
                itemprice = product_rule.get(template.id)[0]
                print("itemprice",itemprice)
            message_information += """<Message>
                                    <MessageID>%s</MessageID>
                                    <Price>
                                    <SKU>%s</SKU>
                                    <StandardPrice currency="%s">%s</StandardPrice>"""%(message_id, template.amazon_sku,instance.res_currency.name,template.tem_standard_price)
            if itemprice!=0.0 and itemprice < template.tem_standard_price:
                offer = """<Sale>
                            <StartDate>%s</StartDate>
                            <EndDate>%s</EndDate>
                             <SalePrice currency="%s">%s</SalePrice>
                            </Sale>"""%(start_date,end_date,instance.res_currency.name, itemprice)
                print("offer",) 
            if offer:
                message_information += """%s"""%(offer)
            message_information += """</Price>
                                </Message>
                                """
                                
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
            relation_submission_id = amazon_api_obj.call(instance, 'POST_PRODUCT_PRICING_DATA',str)
            print("price_submission_id",relation_submission_id)
            
 
            
    def UpdateAmazonInventory(self,products,instance,template):
        str=''
        merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(instance.amazon_instance_id.aws_merchant_id)
        message_information = ''
        message_id = False
        message_information += """<MessageType>Inventory</MessageType>
                                    """
        for product in products:
            message_id = message_id +1
            message_information += """<Message>
                                    <MessageID>%s</MessageID>
                                    <OperationType>Update</OperationType>
                                    <Inventory>
                                    <SKU>%s</SKU>"""%(message_id, product.default_code)
            if product.qty_available >0:
                quantity = int(product.qty_available)
                print("quantity",quantity)
                message_information += """<Quantity>%s</Quantity>"""%(quantity)
                                
            message_information += """<FulfillmentLatency>1</FulfillmentLatency> 
                                    </Inventory>
                                    </Message>"""
                                
        if template:
            message_id = message_id +1
            message_information += """<Message>
                                    <MessageID>%s</MessageID>
                                    <OperationType>Update</OperationType>
                                    <Inventory>
                                    <SKU>%s</SKU>"""%(message_id, template.amazon_sku)
            if template.qty_available >0:
                quantity = int(template.qty_available)
                print("quantity",quantity)
                message_information += """<Quantity>%s</Quantity>"""%(quantity)
                                
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
            
            

    def UpdateAmazonImages(self,products,instance,template):
        str=''
        print("products",products)
        merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(instance.amazon_instance_id.aws_merchant_id)
        message_information = ''
        message_id = False
        message_information += """<MessageType>ProductImage</MessageType>"""
        
        for product in products:
            image_count= False
            for image in product.image_ids:
                message_id = message_id +1
                image_count = image_count+1
                if image_count==1:
                    imagetype = """<ImageType>Main</ImageType>"""
                elif image_count==2:  
                     imagetype = """<ImageType>PT1</ImageType>"""
                elif image_count==3:  
                     imagetype = """<ImageType>PT2</ImageType>"""
                elif image_count==4:  
                     imagetype = """<ImageType>PT3</ImageType>"""
                elif image_count==5:  
                     imagetype = """<ImageType>PT4</ImageType>"""
                elif image_count==6:  
                     imagetype = """<ImageType>PT5</ImageType>"""
                elif image_count==7:  
                     imagetype = """<ImageType>PT6</ImageType>"""
                else:  
                     imagetype = """<ImageType>PT7</ImageType>"""
                message_information += """<Message>
                                <MessageID>%s</MessageID>
                                <OperationType>Update</OperationType>
                                <ProductImage>
                                <SKU>%s</SKU>%s
                                <ImageLocation>%s</ImageLocation>
                                </ProductImage>
                                </Message>"""%(message_id, product.default_code,imagetype,image.url)
                                
        if not products:
            product = self.env['product.product'].search([('product_tmpl_id','=',template.id)])
            if product:
                image_count= False
                for iamge in product.image_ids:
                    message_id = message_id +1
                    image_count = image_count+1
                    if image_count==1:
                        imagetype = """<ImageType>Main</ImageType>"""
                    elif image_count==2:  
                         imagetype = """<ImageType>PT1</ImageType>"""
                    elif image_count==3:  
                         imagetype = """<ImageType>PT2</ImageType>"""
                    elif image_count==4:  
                         imagetype = """<ImageType>PT3</ImageType>"""
                    elif image_count==5:  
                         imagetype = """<ImageType>PT4</ImageType>"""
                    elif image_count==6:  
                         imagetype = """<ImageType>PT5</ImageType>"""
                    else:  
                        imagetype = """<ImageType>PT6</ImageType>"""
                    message_information += """<Message>
                                        <MessageID>%s</MessageID>
                                        <OperationType>Update</OperationType>
                                        <ProductImage>
                                        <SKU>%s</SKU>%s
                                        <ImageLocation>%s</ImageLocation>
                                        </ProductImage>
                                        </Message>"""%(message_id, product.amazon_sku,imagetype,iamge.url)
                                
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
            image_submission_id = amazon_api_obj.call(instance, 'POST_PRODUCT_IMAGE_DATA',str)
            print("image_submission_id",image_submission_id)
        

#     @api.multi
#     def price_compute(self, price_type, uom=False, currency=False, company=False):
#         # TDE FIXME: delegate to template or not ? fields are reencoded here ...
#         # compatibility about context keys used a bit everywhere in the code
#         if not uom and self._context.get('uom'):
#             uom = self.env['product.uom'].browse(self._context['uom'])
#         if not currency and self._context.get('currency'):
#             currency = self.env['res.currency'].browse(self._context['currency'])
#  
#         products = self
#         print("product",products)
#         if price_type == 'standard_price':
#             # standard_price field can only be seen by users in base.group_user
#             # Thus, in order to compute the sale price from the cost for users not in this group
#             # We fetch the standard price as the superuser
#             products = self.with_context(force_company=company and company.id or self._context.get('force_company', self.env.user.company_id.id)).sudo()
#  
#         prices = dict.fromkeys(self.ids, 0.0)
#         for product in products:
#             prices[product.id] = product[price_type] or 0.0
#             print("prices[product.id]",prices[product.id])
#             if price_type == 'list_price':
#                 prices[product.id] += product.price_extra
#             if price_type == 'amazon_standard_price':
#                 print("price_type",price_type)
#                 if not product.attribute_value_ids:
#                     print("product.attribute_value_ids",product.attribute_value_ids)
#                     prices[product.id] = product.tem_standard_price
#  
#             if uom:
#                 prices[product.id] = product.uom_id._compute_price(prices[product.id], uom)
#  
#             # Convert from current user company currency to asked one
#             # This is right cause a field cannot be in more than one currency
#             if currency:
#                 prices[product.id] = product.currency_id.compute(prices[product.id], currency)
#  
#         return prices
    
    
#     @api.multi
#     def name_get(self):
#         # TDE: this could be cleaned a bit I think
# 
#         def _name_get(d):
#             name = d.get('name', '')
#             code = self._context.get('display_default_code', False) and d.get('default_code', False) or False
#             if code:
#                 name = '%s' % (code,name)
#             return (d['id'], name)
# 
#         partner_id = self._context.get('partner_id')
#         if partner_id:
#             partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
#         else:
#             partner_ids = []
# 
#         # all user don't have access to seller and partner
#         # check access and use superuser
#         self.check_access_rights("read")
#         self.check_access_rule("read")
# 
#         result = []
#         for product in self.sudo():
#             # display only the attributes with multiple possible values on the template
#             variable_attributes = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped('attribute_id')
#             variant = product.attribute_value_ids._variant_name(variable_attributes)
# 
#             name = variant and "%s (%s)" % (product.name, variant) or product.name
#             sellers = []
#             if partner_ids:
#                 sellers = [x for x in product.seller_ids if (x.name.id in partner_ids) and (x.product_id == product)]
#                 if not sellers:
#                     sellers = [x for x in product.seller_ids if (x.name.id in partner_ids) and not x.product_id]
#             if sellers:
#                 for s in sellers:
#                     seller_variant = s.product_name and (
#                         variant and "%s (%s)" % (s.product_name, variant) or s.product_name
#                         ) or False
#                     mydict = {
#                               'id': product.id,
#                               'name': seller_variant or name,
#                               'default_code': s.product_code or product.default_code,
#                               }
#                     temp = _name_get(mydict)
#                     if temp not in result:
#                         result.append(temp)
#             else:
#                 mydict = {
#                           'id': product.id,
#                           'name': name,
#                           'default_code': product.default_code,
#                           }
#                 result.append(_name_get(mydict))
#         return result
        


class ProductShopPrice(models.Model):
    _name = 'product.shop.price'
    
    shop_id = fields.Many2one('sale.shop', string="Shop")
    price = fields.Float(string="Price")
    product_id = fields.Many2one('product.product', string="Product")
    
    
    
class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"
    
    base = fields.Selection([
        ('list_price', 'Public Price'),
        ('standard_price', 'Cost'),
        ('pricelist', 'Other Pricelist'),
        ('amazon_standard_price', 'Amazon Price')], "Based on",
        default='list_price', required=True,
        help='Base price for computation.\n'
             'Public Price: The base price will be the Sale/public Price.\n'
             'Cost Price : The base price will be the cost price.\n'
             'Other Pricelist : Computation of the base price based on another Pricelist.')

            
            
