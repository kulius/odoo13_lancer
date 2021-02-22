import logging
from odoo.api import model
logger = logging.getLogger('amazon')
import time
from datetime import  datetime
from odoo import api, fields, models, _
from odoo.addons.amazon_connector.amazon_api import amazonerp_osv as amazon_api_obj
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    amazon_categ_id = fields.Many2one('product.category',string="Amazon Category")
    
    def _calculate_amazon_margin(self, name, arg):
        shop_obj = self.env['sale.shop']
        manufacturer_obj = self.env['manufacturer.master']
        margin_obj = self.env['margin.calculation']
        res = {}
        for data_prod in self:
            standard_price=data_prod.standard_price
            margin=60
            amazon_shop_id=shop_obj.search([('amazon_shop','=',True)])
            if len(amazon_shop_id):
                get_amazon_margin = amazon_shop_id[0].amazon_margin
                if get_amazon_margin != 0.0:
                    margin=get_amazon_margin
            margin_ids = margin_obj.search([('shop_id','=',amazon_shop_id)])
            for sin_id in margin_ids:
                if (float(data_prod.standard_price) >=float(sin_id.cost_up) and float(data_prod.standard_price)<=float(sin_id.cost_to)):
                        margin = sin_id.per
                        print('Your Amazon margin is=========================>',margin)
                        break
            margin_val = standard_price * margin/100
            res[data_prod.id] = standard_price + margin_val
            get_additional_margin = (standard_price + margin_val) * 21/100
            
            #added 12% amazon tax
            get_p = margin_val * 0.13636
            ex = 0.13636 * (standard_price + get_additional_margin + margin_val)
            total_valsf = standard_price + get_additional_margin + margin_val + ex
            res[data_prod.id] = total_valsf
        return res
    
    def Clothing_xml(self,product,parentage):
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
        if product.material_cloth:
            message_information +="""<MaterialAndFabric>%s</MaterialAndFabric>"""%(product.material_cloth)
        if product.furdescription_cloth:
            message_information +="""<FurDescription>%s</FurDescription>"""%(product.furdescription_cloth)
        if product.materialopacity_cloth:
            message_information +="""<MaterialOpacity>%s</MaterialOpacity>"""%(product.materialopacity_cloth)
        if product.fabricwash_cloth:
            message_information +="""<FabricWash>%s</FabricWash>"""%(product.fabricwash_cloth)
        if product.patternstyle_cloth:
            message_information +="""<PatternStyle>%s</PatternStyle>"""%(product.patternstyle_cloth)
        if product.apparelclosuretype_cloth:
            message_information +="""<ApparelClosureType>%s</ApparelClosureType>"""%(product.apparelclosuretype_cloth)
        if product.occasionandlifestyle_cloth:
            message_information +="""<OccasionAndLifestyle>%s</OccasionAndLifestyle>"""%(product.occasionandlifestyle_cloth)
        if product.stylename_cloth:
            message_information +="""<StyleName>%s</StyleName>"""%(product.stylename_cloth)
        if product.stylenumber_cloth:
            message_information +="""<StyleNumber>%s</StyleNumber>"""%(product.stylenumber_cloth)
        if product.collartype_cloth:
            message_information +="""<CollarType>%s</CollarType>"""%(product.collartype_cloth)
        if product.sleevetype_cloth:
            message_information +="""<SleeveType>%s</SleeveType>"""%(product.sleevetype_cloth)
        if product.cufftype_cloth:
            message_information +="""<CuffType>%s</CuffType>"""%(product.cufftype_cloth)
        if product.pocketdescription_cloth:
            message_information +="""<PocketDescription>%s</PocketDescription>"""%(product.pocketdescription_cloth)
        if product.frontpleattype_cloth:
            message_information +="""<FrontPleatType>%s</FrontPleatType>"""%(product.frontpleattype_cloth)
        if product.topstyle_cloth:
            message_information +="""<TopStyle>%s</TopStyle>"""%(product.topstyle_cloth)
        if product.bottomstyle_cloth:
            message_information +="""<BottomStyle>%s</BottomStyle>"""%(product.bottomstyle_cloth)
        if product.waistsize_cloth:
            message_information +="""<WaistSize>%s</WaistSize>"""%(product.waistsize_cloth)
        if product.inseamlength_cloth:
            message_information +="""<InseamLength>%s</InseamLength>"""%(product.inseamlength_cloth)
        if product.sleevelength_cloth:
            message_information +="""<SleeveLength>%s</SleeveLength>"""%(product.sleevelength_cloth)
        if product.necksize_cloth:
            message_information +="""<NeckSize>%s</NeckSize>"""%(product.necksize_cloth)
        if product.neckstyle_cloth:
            message_information +="""<NeckStyle>%s</NeckStyle>"""%(product.neckstyle_cloth)
        if product.chestsize_cloth:
            message_information +="""<ChestSize>%s</ChestSize>"""%(product.chestsize_cloth)
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
        
    def Lighting_xml(self,product):
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
        if product.airflowcapacity_li:
            message_information +="""<AirFlowCapacity>%s</AirFlowCapacity>"""%(product.airflowcapacity_li)
        if product.basediameter_li:
            message_information +="""<BaseDiameter>%s</BaseDiameter>"""%(product.basediameter_li)
        if product.battery_li:
            message_information +="""<Battery>%s</Battery>"""%(product.battery_li)
        if product.bulbdiameter_li:
            message_information +="""<BulbDiameter>%s</BulbDiameter>"""%(product.bulbdiameter_li)
        if product.bulblength_li:
            message_information +="""<BulbLength>%s</BulbLength>"""%(product.bulblength_li)
        if product.bulblifespan_li:
            message_information +="""<BulbLifeSpan>%s</BulbLifeSpan>"""%(product.bulblifespan_li)
        if product.bulbpowerfactor_li:
            message_information +="""<BulbPowerFactor>%s</BulbPowerFactor>"""%(product.bulbpowerfactor_li)
        if product.bulbspecialfeatures_li:
            message_information +="""<BulbSpecialFeatures>%s</BulbSpecialFeatures>"""%(product.bulbspecialfeatures_li)
        if product.bulbswitchingcycles_li:
            message_information +="""<BulbSwitchingCycles>%s</BulbSwitchingCycles>"""%(product.bulbswitchingcycles_li)
        if product.bulbtype_li:
            message_information +="""<BulbType>%s</BulbType>"""%(product.bulbtype_li)
        if product.bulbwattage_li:
            message_information +="""<BulbWattage>%s</BulbWattage>"""%(product.bulbwattage_li)
        if product.captype_li:
            message_information +="""<CapType>%s</CapType>"""%(product.captype_li)
        if product.certification_li:
            message_information +="""<Certification>%s</Certification>"""%(product.certification_li)
        if product.collection_li:
            message_information +="""<Collection>%s</Collection>"""%(product.collection_li)
        if product.color_li:
            message_information +="""<Color>%s</Color>"""%(product.color_li)
        if product.energy_rating_li:
            message_information +="""<EnergyEfficiencyRating>%s</EnergyEfficiencyRating>"""%(product.energy_rating_li)
        if product.inte_rating_li:
            message_information +="""<InternationalProtectionRating>%s</InternationalProtectionRating>"""%(product.inte_rating_li)
        if product.itemdiameter_li:
            message_information +="""<ItemDiameter>%s</ItemDiameter>"""%(product.itemdiameter_li)
        if product.lightingmethod_li:
            message_information +="""<LightingMethod>%s</LightingMethod>"""%(product.lightingmethod_li)
        if product.lithium_content_li:
            message_information +="""<LithiumBatteryEnergyContent>%s</LithiumBatteryEnergyContent>"""%(product.lithium_content_li)
        if product.lithium_voltage_li:
            message_information +="""<LithiumBatteryVoltage>%s</LithiumBatteryVoltage>"""%(product.lithium_voltage_li)
        if product.lithium_weight_li:
            message_information +="""<LithiumBatteryWeight>%s</LithiumBatteryWeight>"""%(product.lithium_weight_li)
        if product.material_li:
            message_information +="""<Material>%s</Material>"""%(product.material_li)
        if product.numberofblades_li:
            message_information +="""<NumberOfBlades>%s</NumberOfBlades>"""%(product.numberofblades_li)
        if product.numberofbulbsockets_li:
            message_information +="""<NumberOfBulbSockets>%s</NumberOfBulbSockets>"""%(product.numberofbulbsockets_li)
        if product.plugtype_li:
            message_information +="""<PlugType>%s</PlugType>"""%(product.plugtype)
        if product.powersource_li:
            message_information +="""<PowerSource>%s</PowerSource>"""%(product.powersource_li)
        if product.specialfeatures_li:
            message_information +="""<SpecialFeatures>%s</SpecialFeatures>"""%(product.specialfeatures_li)
        if product.mercury_bulb:
            message_information +="""<MercuryContent>%s</MercuryContent>"""%(product.mercury_bulb)
        if product.specificuses_li:
            message_information +="""<SpecificUses>%s</SpecificUses>"""%(product.specificuses_li)
        if product.stylename_li:
            message_information +="""<StyleName>%s</StyleName>"""%(product.stylename_li)
        if product.switchstyle_li:
            message_information +="""<SwitchStyle>%s</SwitchStyle>"""%(product.switchstyle_li)
        if product.voltage_li:
            message_information +="""<Voltage>%s</Voltage>"""%(product.voltage_li)
        if product.volume_li:
            message_information +="""<Volume>%s</Volume>"""%(product.volume_li)
        if product.wattage_li:
            message_information +="""<Wattage>%s</Wattage>"""%(product.wattage_li)
        message_information += """</%s>"""%(product.product_type_light)
        return message_information
    
    def Beauty_xml(self,product):
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
       
        if product.scent_beauty:
            message_information +="""<Scent>%s</Scent>"""%(product.scent_beauty)
        if product.capacity_beauty:
            message_information +="""<Capacity>%s</Capacity>"""%(product.capacity_beauty)
        if product.unit_count_beauty:
            message_information +="""<UnitCount>%s</UnitCount>"""%(product.unit_count_beauty)
        if product.uom_beauty:
            message_information +="""<unitOfMeasure>%s</unitOfMeasure>"""%(product.uom_beauty)
        if product.count_beauty:
            message_information +="""<Count>%s</Count>"""%(product.count_beauty)
        if product.no_of_items_beauty:
            message_information +="""<NumberOfItems>%s</NumberOfItems>"""%(product.no_of_items_beauty)
        if product.battry_average_life_beauty:
            message_information +="""<BatteryAverageLife>%s</BatteryAverageLife>"""%(product.battry_average_life_beauty)
        if product.battry_charge_time_beauty:
            message_information +="""<BatteryChargeTime>%s</BatteryChargeTime>"""%(product.battry_charge_time_beauty)
        if product.battry_descriptn_beauty:
            message_information +="""<BatteryDescription>%s</BatteryDescription>"""%(product.battry_descriptn_beauty)
        if product.battry_power_beauty:
            message_information +="""<BatteryPower>%s</BatteryPower>"""%(product.battry_power_beauty)
        if product.skin_type_beauty:
            message_information +="""<SkinType>%s</SkinType>"""%(product.skin_type_beauty)
        if product.skin_tone_beauty:
            message_information +="""<SkinTone>%s</SkinTone>"""%(product.skin_tone_beauty)
        if product.hair_type_beauty:
            message_information +="""<HairType>%s</HairType>"""%(product.hair_type_beauty)
        if product.ingredients_beauty:
            message_information +="""<Ingredients>%s</Ingredients>"""%(product.ingredients_beauty)
        if product.mrf_warrant_type_beauty:
            message_information +="""<ManufacturerWarrantyType>%s</ManufacturerWarrantyType>"""%(product.mrf_warrant_type_beauty)
        if product.material_type_beauty:
            message_information +="""<MaterialType>%s</MaterialType>"""%(product.material_type_beauty)
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
        if product.target_gender_beauty:
            message_information +="""<TargetGender>%s</TargetGender>"""%(product.target_gender_beauty)
        if product.seller_description_beauty:
            message_information +="""<SellerWarrantyDescription>%s<SellerWarrantyDescription>"""%(product.seller_description_beauty)
       
        message_information += """</%s>"""%(product.product_type_light)
        return message_information
    
    def Tools_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_tools:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_tools)
        return xml_ce

    def MusicalInstruments_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_musicalinstruments:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_musicalinstruments)
        return xml_ce

    def PetSupplies_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_petsupplies:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_petsupplies)
        return xml_ce
    

    def ce_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_ce:
            raise UserError(_('Error'), _('Plz select CE Product Type!!'))
        xml_ce = '''<%s>
                        <PowerSource>AC</PowerSource>
                   </%s>'''%(product.product_type_ce,product.product_type_ce)
        return xml_ce


    def Jewelry_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_jewelry:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_jewelry)
        return xml_ce

    def Health_xml(self,product):
        message_information=''
        print(">>>>>>>>>>>>>>>>>>>",product)
        first_tag=product.product_data
        if not product.product_type_health:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_health)
        return xml_ce
        
    def Shoes_xml(self,product):
        message_information=''
        print(">>>>>>>>>>>>>>>>>>>",product)
        first_tag=product.product_data
        if not product.product_type_shoes:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_shoes)
        return xml_ce

    def Auto_xml(self,product):
        message_information=''
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_auto_accessory:
            raise UserError(_('Error'), _('Plz select AutoAccessory Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_auto_accessory)
        return xml_ce
    
    def ToysBaby_xml(self,product):
        message_information=''
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_toys_baby:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_toys_baby)
        return xml_ce
    
    def CameraPhoto_xml(self,product):
        message_information=''
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_cameraphoto:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_cameraphoto)
        return xml_ce
    
    def Wireless_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_wirelessaccessories:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_wirelessaccessories)
        return xml_ce

    def FoodAndBeverages_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_foodandbeverages:
            raise UserError(_('Error'), _('Plz select Product Type!!'))
        xml_ce = '''%s'''%(product.product_type_foodandbeverages)
        return xml_ce
    
    def Computers_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_com:
            raise UserError(_('Error'), _('Plz select Value!!'))
        xml_ce = '''%s'''%(product.product_type_com)
        return xml_ce

    def Video_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_softwarevideoGames:
            raise UserError(_('Error'), _('Plz select Value!!'))
        xml_ce = '''%s'''%(product.product_type_softwarevideoGames)
        return xml_ce

    def Sport_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_sports:
            raise UserError(_('Error'), _('Plz select Value!!'))
        xml_ce = '''%s'''%(product.product_type_sports)
        return xml_ce

    def sportsmemorabilia_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_sportsmemorabilia:
            raise UserError(_('Error'), _('Plz select Value!!'))
        xml_ce = '''%s'''%(product.product_type_sportsmemorabilia)
        return xml_ce

    def tiresandwheels_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_tiresandwheels:
            raise UserError(_('Error'), _('Plz select Value!!'))
        xml_ce = '''%s'''%(product.product_type_tiresandwheels)
        return xml_ce

    def toys_xml(self,product):
        print(">>>>>>>>>>>>>>>>>>>",product)
        if not product.product_type_toys:
            raise UserError(_('Error'), _('Plz select Value!!'))
        xml_ce = '''<%s>"toys"
                   </%s>'''%(product.product_type_toys,product.product_type_toys)
        return xml_ce
    
    def _amazon_browse_node_get(self):
        amazon_browse_node_obj = self.env['amazon.browse.node']
        amazon_browse_node_ids = amazon_browse_node_obj.search([], order='browse_node_name')
        amazon_browse_node = amazon_browse_node_obj.read(amazon_browse_node_ids, ['id','browse_node_name'])
        return [(node['browse_node_name'],node['browse_node_name']) for node in amazon_browse_node]

#    def _amazon_instance_get(self, cr, uid, context=None):
#        amazon_instance_obj = self.pool.get('amazon.instance')
#        amazon_instance_ids = amazon_instance_obj.search(cr, uid, [], order='name')
#        amazon_instances = amazon_instance_obj.read(cr, uid, amazon_instance_ids, ['id','name'], context=context)
#        return [(instance['id'],instance['name']) for instance in amazon_instances]

    ''' Assign by default one instance id to selection field on amazon instance '''
#    def _assign_default_amazon_instance(self, cr, uid, context=None):
#        amazon_instance_obj = self.pool.get('amazon.instance')
#        amazon_instance_ids = amazon_instance_obj.search(cr, uid, [], order='name')
#        amazon_instances = amazon_instance_obj.read(cr, uid, amazon_instance_ids, ['id','name'], context=context)
#        if amazon_instances:
#            return amazon_instances[0]['id']
#        else:
#            return False
    def amazon_product_lookup(self):
        """
        Function to search product on amazon based on ListMatchingProduct Operation
        """
        amazon_instance_obj = self.env['amazon.instance']
        for prodcut_lookup in self:
            if not prodcut_lookup.amazon_instance_id:
                raise UserError('Warning !','Please select Amazon Instance and try again.')
            product_query = self.prod_query
            if not product_query:
                raise UserError('Warning !','Please enter Product Search Query and try again')
            product_query = product_query.strip().replace(' ','%')
            prod_query_contextid = self.prod_query_contextid
            productData = False
            try:
                productData = amazon_api_obj.call(amazon_instance_obj, 'ListMatchingProducts',product_query,prod_query_contextid)
                print('productData===--==-',productData)
            except Exception as e:
                raise UserError(_('Error !'),e)
            if productData:
                ### Flushing amazon.products.master data to show new search data ###
                delete_all_prods = self._cr.execute('delete from amazon_products_master where product_id=%s',(self[0].id,))
                for data in productData:
                    keys_val = data.keys()
                    prod_category = ''
                    if 'Binding' in keys_val:
                        prod_category = data['Binding']
                    prodvals = {
                            'name' : data['Title'],
                            'product_asin' : data['ASIN'],
                            'product_category' : prod_category,
                            'product_id' : self[0].id,
                            'amazon_product_attributes' : data
                        }
                    amazon_prod_master_obj = self.pool.get('amazon.products.master')
                    amazon_prod_master_id  = amazon_prod_master_obj.create(prodvals)
            else:
                     raise UserError(_('Warning !'),'No products found on Amazon as per your search query. Please try again')
        return True
    


    def export_inventory(self):
        xml_data=""
        sale_shop_obj = self.env['sale.shop']

        shop_ids = sale_shop_obj.search([('amazon_shop','=',True)])
        amazon_inst_data = shop_ids[0].amazon_instance_id
        message_count = 1

        merchant_string ="<MerchantIdentifier>%s</MerchantIdentifier>"%(amazon_inst_data.aws_merchant_id)
        message_type = '<MessageType>Inventory</MessageType>'
        for product in self:
            if not product.name:
                raise shop_ids(_('Error'), _('Please enter Product SKU for Image Feed "%s"'% (product.name)))

            parent_sku= product.default_code
            inventory = product.bom_stock
            lead_time = product.sale_delay
            #WE MAY WANT TO IMPLEMENT LATER
            #if product.fulfillment_by != 'AFN':
            update_xml_data = '''<SKU>%s</SKU>
                                <Quantity>%s</Quantity><FulfillmentLatency>%s</FulfillmentLatency>'''%(parent_sku,inventory,lead_time)
            xml_data += '''<Message>
                        <MessageID>%s</MessageID><OperationType>Update</OperationType>
                        <Inventory>%s</Inventory></Message>
                    '''% (message_count,update_xml_data)

    #Uploading Product Inventory Feed
            message_count+=1
        str = """
                <?xml version="1.0" encoding="utf-8"?>
                <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
                <Header>
                <DocumentVersion>1.01</DocumentVersion>
                """+merchant_string+"""
                </Header>
                """+message_type+xml_data+"""
                """
        str +="""</AmazonEnvelope>"""

        logger.info('                        API STRING:         %s                ',str)
        product_submission_id = amazon_api_obj.call(amazon_inst_data, 'POST_INVENTORY_AVAILABILITY_DATA',str)
        if product_submission_id.get('FeedSubmissionId',False):
            logger.info('Feed Submission ID: %s',product_submission_id.get('FeedSubmissionId'))
            time.sleep(20)
            submission_results = amazon_api_obj.call(amazon_inst_data, 'GetFeedSubmissionResult',product_submission_id.get('FeedSubmissionId',False))
            logger.info('                       SUBMISSION RESULTS        %s                ',submission_results)
        return True
 


    
    def get_lowest_price_asin(self):
        shop_obj = self.env['sale.shop']
        shop_ids = shop_obj.search([('amazon_shop','=',True)])
        instance_obj = shop_ids.amazon_instance_id
        n = 0
        for product_data in self:
            n += 1
            if n % 10 == 0:
                time.sleep(1)
            if product_data.asin:
                results = amazon_api_obj.call(instance_obj, 'GetLowestOfferListingsForASIN', product_data.asin)
                if results != None:
                    return float(results.get('lowestamount'))
                else:
                    return False
            else:
                raise UserError(('Error'),('Asin is not available for this product'))
        return False
    
    def price_compute(self, price_type, uom=False, currency=False, company=False):
        # TDE FIXME: delegate to template or not ? fields are reencoded here ...
        # compatibility about context keys used a bit everywhere in the code
        if not uom and self._context.get('uom'):
            uom = self.env['product.uom'].browse(self._context['uom'])
        if not currency and self._context.get('currency'):
            currency = self.env['res.currency'].browse(self._context['currency'])

        templates = self
        if price_type == 'standard_price':
            # standard_price field can only be seen by users in base.group_user
            # Thus, in order to compute the sale price from the cost for users not in this group
            # We fetch the standard price as the superuser
            templates = self.with_context(force_company=company and company.id or self._context.get('force_company', self.env.user.company_id.id)).sudo()

        prices = dict.fromkeys(self.ids, 0.0)
        for template in templates:
            if price_type=='amazon_standard_price':
                prices[template.id] = template['tem_standard_price'] or 0.0
            else:
                prices[template.id] = template[price_type] or 0.0

            if uom:
                prices[template.id] = template.uom_id._compute_price(prices[template.id], uom)

            # Convert from current user company currency to asked one
            # This is right cause a field cannot be in more than one currency
            if currency:
                prices[template.id] = template.currency_id.compute(prices[template.id], currency)

        return prices


    is_prime = fields.Boolean('Is Prime')
    fulfillment_by = fields.Selection([('MFN','Fulfilled by Merchant(MFN)'),('FBA','Fulfilled by Amazon(FBA)')],'Fulfillment By')
    style_keywords = fields.Text(string='Style Keywords')
    platinum_keywords = fields.Text(string='Platinum Keywords')
    orderitemid = fields.Char(string='Orderitemid', size=16)
    product_order_item_id = fields.Char(string='Order_item_id', size=256)
    amazon_export = fields.Boolean(string='To be Exported')
    amazon_response = fields.Boolean(string='Amazon response')
    amazon_category = fields.Many2one('product.category',string='Amazon Category')
    amazon_product_category = fields.Char(string='Amazon Category',size=64)
    brand_name = fields.Char(string='Brand',size=64)
    amazon_manufacturer = fields.Char(string='Manufacturer',size=64)
    amazon_updated_price = fields.Float(string='Amazon Updated Price',digits=(16,2))
    amazon_price = fields.Float(string='Amazon Price',digits=(16,2))
    tem_standard_price = fields.Float('Amazon Price')
    upc_temp = fields.Char(string='UPC',size=64)
    ean_barcode = fields.Char('EAN/Barcode')
    isbn_temp = fields.Char('ISBN')
    product_group = fields.Char(string='Product Group',size=64)
    amazon_title = fields.Char(string='Amazon title',size=64)
    amazon_lowest_listing_price = fields.Float(string='Lowest Listing Price')
    bom_stock_list = fields.Float(string='Bom Stock')
    amazon_product = fields.Boolean(string='Amazon Product')
    item_price = fields.Float(string='Item Price')
    item_tax = fields.Float(string='Item taxes')
    shipping_price = fields.Float(string='Shipping price')
    taxes = fields.Float(string='taxes')
    gift_costs = fields.Float(string='gift costs')
    product_group = fields.Char(string='ProductGroup')
    package_dimension_length = fields.Float(string='PackageDimensionsLength')
    label = fields.Char(string='Label')
    product_type_name = fields.Char(string='ProductTypeName')
    small_image_height = fields.Integer(string='SmallImageHeight')
    package_quantity = fields.Integer(string='PackageQuantity')
    item_dimension_weight = fields.Float(string='ItemDimensionsWeight')
    brand = fields.Char(string='Brand')
    studio = fields.Char(string='Studio')
    manufacturer_part = fields.Char(string='Manufacturer Part Number')
    publisher = fields.Char(string='Publisher')
    package_dimension_width = fields.Float(string='PackageDimensionsWidth')
    package_dimension_weight = fields.Float(string='PackageDimensionsWeight')
    color = fields.Char(string='Color')
    package_dimension_height = fields.Float(string='PackageDimensionsHeight')
    small_image_url = fields.Char(string='SmallImageURL')
    binding = fields.Char(string='Bindings')
    small_image_width = fields.Float(string='SmallImageWidth')
    feature = fields.Text(string='Features')
    updated_data = fields.Boolean(string='Updated', default=False)
    amazon_sku = fields.Char(string='ASIN')
    
    color_temp_map = fields.Char(string='Color Temp Map')
    material_temp_type = fields.Char(string='Material Type')
    size = fields.Char(string='Size')
    shipping_template = fields.Selection([('nationwide','Nationwide Prime'),('default','Default Amazon Template'),('new_template','New Template'),('regional_prime','Regional Prime (Ground)'),('new_template_cp','New Template-Copy'),('reginal_prime_gd','Regional Prime (Ground + Air)')], string='Shipping Template', default='nationwide')
    department_temp_name = fields.Char(string='Department Temp Name')
        
    cup_size = fields.Selection([('A','A'),('B','B'),('C','C'),('D','D'),('DD','DD'),('DDD','DDD'),('E','E'),('F','F'),('FF','FF'),('G','G'),('H','H'),('I','I')],string='Cup Size')
    
#     sale_start_date = fields.Datetime('Sale Start Date')
#     sale_end_date = fields.Datetime('Sale End Date')
#     variationtheme = fields.Selection([("Size-Color",'Size-Color'),('Color','Color'),('Size','Size')], string='Select VariationTheme')
    tmp_asin = fields.Char('ASIN')
    bullet_point = fields.One2many('bullet.point','template_id' ,string='Bullet Point')
    search_keywords = fields.One2many('search.terms','searchterm_temp_id',string='SearchTerms Keywords', help="Data should be amazon categories name like Shoes")
    item_type = fields.Char(string='Item Type', help="Data Should be in this Format casual-formal")
    standard_temp_product = fields.Selection([('EAN','EAN'),('UPC','UPC'),('ASIN','ASIN'),('ISBN','ISBN')], string='Standard Product')
    amazon_fba_sku = fields.Char(string='Amazon FBA SKU')
    
    # product_data = fields.Selection([('ProductClothing', 'ProductClothing'),('Clothing', 'Clothing'),('Miscellaneous', 'Miscellaneous'),('CameraPhoto', 'CameraPhoto'),('Home', 'Home'),('Sports', 'Sports'),('SportsMemorabilia', 'SportsMemorabilia'),('EntertainmentCollectibles', 'EntertainmentCollectibles'),('HomeImprovement', 'HomeImprovement'),('Tools', 'Tools'),('FoodAndBeverages', 'FoodAndBeverages'),('Gourmet', 'Gourmet'),('Jewelry', 'Jewelry'),('Health', 'Health'),('CE','CE'),('Computers', 'Computers'),('SWVG', 'SWVG'),('Wireless', 'Wireless'),('Beauty', 'Beauty'),('Office', 'Office'),('MusicalInstruments', 'MusicalInstruments'),('AutoAccessory', 'AutoAccessory'),('PetSupplies', 'PetSupplies'),('Baby', 'Baby'),('TiresAndWheels', 'TiresAndWheels'),('Music', 'Music'),('Video', 'Video'),('Lighting', 'Lighting'),('LargeAppliances', 'LargeAppliances'),('FBA', 'FBA'),('Toys', 'Toys'),('GiftCards', 'GiftCards'),('LabSupplies', 'LabSupplies'),('RawMaterials', 'RawMaterials'),('PowerTransmission', 'PowerTransmission'),('Industrial', 'Industrial'),('Shoes', 'Shoes'),('Motorcycles', 'Motorcycles'),('MaterialHandling', 'MaterialHandling'),('MechanicalFasteners', 'MechanicalFasteners'),('FoodServiceAndJanSan', 'FoodServiceAndJanSan'),('WineAndAlcohol', 'WineAndAlcohol'),('EUCompliance', 'EUCompliance'),('Books', 'Books')], 'Product Data', Required=True, default='Clothing')

    product_data = fields.Selection([('AutoAccessory', 'AutoAccessory'),('Baby', 'Baby'),('Beauty', 'Beauty'),('CameraPhoto', 'CameraPhoto'),('Clothing', 'Clothing'),('CE','CE'),('Computers', 'Computers'),('FoodAndBeverages', 'FoodAndBeverages'),('Gourmet', 'Gourmet'),('Health', 'Health'),('HomeImprovement', 'HomeImprovement'),('FoodServiceAndJanSan', 'FoodServiceAndJanSan'),('LabSupplies', 'LabSupplies'),('PowerTransmission', 'PowerTransmission'),('RawMaterials', 'RawMaterials'),('Jewelry', 'Jewelry'),('Lighting', 'Lighting'),('MusicalInstruments', 'MusicalInstruments'),('PetSupplies', 'PetSupplies'),('Sports', 'Sports'),('SportsMemorabilia', 'SportsMemorabilia'),('TiresAndWheels', 'TiresAndWheels'),('Tools', 'Tools'),('Toys', 'Toys'),('Wireless', 'Wireless'),('LargeAppliances', 'LargeAppliances')], 'Product Data', Required=True, default='Clothing')

    product_type_foodserviceandjansan = fields.Selection([('FoodServiceAndJanSan', 'FoodServiceAndJanSan')], 'FoodServiceAndJanSan Types')

    product_type_rawmaterials = fields.Selection([('CeramicTubing', 'CeramicTubing'),('Ceramics', 'Ceramics'),('MetalBalls', 'MetalBalls'),('MetalMesh', 'MetalMesh'),('MetalTubing', 'MetalTubing'),('Metals', 'Metals'),('PlasticBalls', 'PlasticBalls'),('PlasticMesh', 'PlasticMesh'),('PlasticTubing', 'PlasticTubing'),('Plastics', 'Plastics'),('RawMaterials', 'RawMaterials'),('RollerChain', 'RollerChain'),('Wire', 'Wire')], 'RawMaterials Types')

    product_type_powertransmission = fields.Selection([('BearingsAndBushings', 'BearingsAndBushings'),('Belts', 'Belts'),('CompressionSprings', 'CompressionSprings'),('ExtensionSprings', 'ExtensionSprings'),('FlexibleCouplings', 'FlexibleCouplings'),('Gears', 'Gears'),('RigidCouplings', 'RigidCouplings'),('ShaftCollar', 'ShaftCollar'),('TorsionSprings', 'TorsionSprings'),('LinearGuidesAndRails', 'LinearGuidesAndRails'),('Pulleys', 'Pulleys'),('RollerChain', 'RollerChain'),('CouplingsCollarsAndUniversalJoints', 'CouplingsCollarsAndUniversalJoints'),('Springs', 'Springs'),('Sprockets', 'Sprockets'),('UniversalJoints', 'UniversalJoints')], 'PowerTransmission Types')


    product_type_largeappliances = fields.Selection([('CookingOven', 'CookingOven'),('Dishwasher', 'Dishwasher'),('LaundryAppliance', 'LaundryAppliance'),('MicrowaveOven', 'MicrowaveOven'),('RefrigerationAppliance', 'RefrigerationAppliance')], 'LargeAppliances Types')

    product_type_gourmet = fields.Selection([('GourmetMisc', 'GourmetMisc')], 'Gourmet Types')

    product_type_labsupplies = fields.Selection([('LabSupply', 'LabSupply'),('SafetySupply', 'SafetySupply')], 'LabSupplies Types')

    product_type_foodandbeverages = fields.Selection([('Food', 'Food'),('HouseholdSupplies', 'HouseholdSupplies'),('Beverages', 'Beverages'),('HardLiquor', 'HardLiquor'),('AlcoholicBeverages', 'AlcoholicBeverages'),('Wine', 'Wine')], 'FoodAndBeverages Types')


    # product_type_homeimprovement = fields.Selection([('BuildingMaterials', 'BuildingMaterials'),('Hardware', 'Hardware'),('Electrical', 'Electrical'),('PlumbingFixtures', 'PlumbingFixtures'),('Tools', 'Tools'),('OrganizersAndStorage', 'OrganizersAndStorage'),('MajorHomeAppliances', 'MajorHomeAppliances'),('SecurityElectronics', 'SecurityElectronics')],'HomeImprovement Type')

    product_type_homeimprovement = fields.Selection([('BuildingMaterials', 'BuildingMaterials'),('Hardware', 'Hardware'),('Electrical', 'Electrical'),('PlumbingFixtures', 'PlumbingFixtures')],'HomeImprovement Types')
        
    product_type_clothingaccessories = fields.Selection([('ClothingAccessories', 'ClothingAccessories')],'ClothingAccessories Types')

    product_type_ce = fields.Selection([('Antenna', 'Antenna'),('AudioVideoAccessory', 'AudioVideoAccessory'),('AVFurniture', 'AVFurniture'),('BarCodeReader', 'BarCodeReader'),('CEBinocular', 'CEBinocular'),('CECamcorder', 'CECamcorder'),('CameraBagsAndCases', 'CameraBagsAndCases'),('CEBattery','CEBattery'),('CEBlankMedia','CEBlankMedia'),('CableOrAdapter','CableOrAdapter'),('CECameraFlash', 'CECameraFlash'),('CameraLenses', 'CameraLenses'),('CameraOtherAccessories', 'CameraOtherAccessories'),('CameraPowerSupply', 'CameraPowerSupply'),('CarAlarm', 'CarAlarm'),('CarAudioOrTheater', 'CarAudioOrTheater'),('CarElectronics', 'CarElectronics'),('ConsumerElectronics', 'ConsumerElectronics'),('CEDigitalCamera', 'CEDigitalCamera'),('DigitalPictureFrame', 'DigitalPictureFrame'),('DigitalVideoRecorder', 'DigitalVideoRecorder'),('DVDPlayerOrRecorder', 'DVDPlayerOrRecorder'),('CEFilmCamera', 'CEFilmCamera'),
        ('GPSOrNavigationAccessory', 'GPSOrNavigationAccessory'),('GPSOrNavigationSystem', 'GPSOrNavigationSystem'),('HandheldOrPDA', 'HandheldOrPDA'),('Headphones', 'Headphones'),('HomeTheaterSystemOrHTIB', 'HomeTheaterSystemOrHTIB'),('KindleAccessories', 'KindleAccessories'),('KindleEReaderAccessories', 'KindleEReaderAccessories'),('KindleFireAccessories', 'KindleFireAccessories'),
        ('MediaPlayer', 'MediaPlayer'),('MediaPlayerOrEReaderAccessory', 'MediaPlayerOrEReaderAccessory'),('MediaStorage', 'MediaStorage'),('MiscAudioComponents', 'MiscAudioComponents'),('PC', 'PC'),('PDA', 'PDA'),
        ('Phone', 'Phone'),('PhoneAccessory', 'PhoneAccessory'),('PhotographicStudioItems', 'PhotographicStudioItems'),('PortableAudio', 'PortableAudio'),('PortableAvDevice', 'PortableAvDevice'),('PowerSuppliesOrProtection', 'PowerSuppliesOrProtection'),
        ('RadarDetector', 'RadarDetector'),('RadioOrClockRadio', 'RadioOrClockRadio'),('ReceiverOrAmplifier', 'ReceiverOrAmplifier'),('RemoteControl', 'RemoteControl'),('Speakers', 'Speakers'),('StereoShelfSystem', 'StereoShelfSystem'),
        ('CETelescope', 'CETelescope'),('Television', 'Television'),('Tuner', 'Tuner'),('TVCombos', 'TVCombos'),('TwoWayRadio', 'TwoWayRadio'),('VCR', 'VCR'),('CEVideoProjector', 'CEVideoProjector'),('VideoProjectorsAndAccessories', 'VideoProjectorsAndAccessories'),
        ], 'CE Types')
        
    product_type_com = fields.Selection([('CarryingCaseOrBag', 'CarryingCaseOrBag'),('ComputerAddOn', 'ComputerAddOn'),('ComputerComponent', 'ComputerComponent'),
        ('ComputerCoolingDevice', 'ComputerCoolingDevice'),('ComputerDriveOrStorage', 'ComputerDriveOrStorage'),('ComputerInputDevice', 'ComputerInputDevice'),('ComputerProcessor', 'ComputerProcessor'),
        ('ComputerSpeaker', 'ComputerSpeaker'),('Computer', 'Computer'),('FlashMemory', 'FlashMemory'),('InkOrToner', 'InkOrToner'),
        ('Keyboards', 'Keyboards'),('MemoryReader', 'MemoryReader'),('Monitor', 'Monitor'),('Motherboard', 'Motherboard'),
        ('NetworkingDevice', 'NetworkingDevice'),('NotebookComputer', 'NotebookComputer'),('PersonalComputer', 'PersonalComputer'),('Printer', 'Printer'),
        ('RamMemory', 'RamMemory'),('Scanner', 'Scanner'),('SoundCard', 'SoundCard'),('SystemCabinet', 'SystemCabinet'),
        ('SystemPowerDevice', 'SystemPowerDevice'),('TabletComputer', 'TabletComputer'),('VideoCard', 'VideoCard'),('VideoProjector', 'VideoProjector'),
        ('Webcam', 'Webcam')], 'Computer Types')

    product_type_auto_accessory = fields.Selection([('AutoAccessoryMisc', 'AutoAccessoryMisc'),('AutoPart', 'AutoPart'),('PowersportsPart', 'PowersportsPart'),('PowersportsVehicle', 'PowersportsVehicle'),('ProtectiveGear', 'ProtectiveGear'),('Helmet', 'Helmet'),('RidingApparel', 'RidingApparel')], 'Auto Accessory Types')

    product_type_sports = fields.Selection([('SportingGoods', 'SportingGoods'),('GolfClubHybrid', 'GolfClubHybrid'),('GolfClubIron', 'GolfClubIron'),('GolfClubPutter', 'GolfClubPutter'),('GolfClubWedge', 'GolfClubWedge'),('GolfClubWood', 'GolfClubWood'),('GolfClubs', 'GolfClubs'),
        ], 'Sports Types')


    # product_type_softwarevideoGames = fields.Selection([('Software', 'Software'),('HandheldSoftwareDownloads', 'HandheldSoftwareDownloads'),('SoftwareGames', 'SoftwareGames'),('VideoGames', 'VideoGames'),('VideoGamesAccessories', 'VideoGamesAccessories'),('VideoGamesHardware', 'VideoGamesHardware')], 'Software Video Games Types')

    product_type_light = fields.Selection([('LightsAndFixtures', 'LightsAndFixtures'),('LightingAccessories', 'LightingAccessories'),('LightBulbs', 'LightBulbs')], 'Light Types',track_visibility='onchange')

    product_type_tools = fields.Selection([('GritRating', 'GritRating'),('Horsepower', 'Horsepower'),('Diameter', 'Diameter'),('Length', 'Length'),('Width', 'Width'),('Height', 'Height'),('Weight','Weight')], 'Tools Types')

    product_type_toys = fields.Selection([('ToysAndGames', 'ToysAndGames'),('Hobbies', 'Hobbies'),('CollectibleCard', 'CollectibleCard'),('Costume', 'Costume')], 'Toys Types')

    product_type_jewelry = fields.Selection([('Watch', 'Watch'),('FashionNecklaceBraceletAnklet', 'FashionNecklaceBraceletAnklet'),('FashionRing', 'FashionRing'),
        ('FashionEarring', 'FashionEarring'),('FashionOther', 'FashionOther'),('FineNecklaceBraceletAnklet', 'FineNecklaceBraceletAnklet'),('FineRing', 'FineRing'),('FineEarring', 'FineEarring'),('FineOther', 'FineOther')], 'Jewelry Types')

    # product_type_home = fields.Selection([('BedAndBath', 'BedAndBath'),('FurnitureAndDecor', 'FurnitureAndDecor'),('Kitchen', 'Kitchen'),('OutdoorLiving', 'OutdoorLiving'),('SeedsAndPlants', 'SeedsAndPlants'),('Art', 'Art'),('Home', 'Home')], 'Home Types')

    # product_type_miscellaneous = fields.Selection([('MiscType', 'MiscType')], 'Miscellaneous Types')

    # product_type_Video = fields.Selection([('VideoDVD', 'VideoDVD'),('VideoVHS','VideoVHS')], 'Video Types')
    product_type_petsupplies = fields.Selection([('PetSuppliesMisc', 'PetSuppliesMisc')], 'PetSupplies Types')
    product_type_toys_baby = fields.Selection([('BabyProducts', 'BabyProducts'),('InfantToddlerCarSeat', 'InfantToddlerCarSeat'),('Stroller','Stroller')], 'Baby Product Types')
    product_type_beauty = fields.Selection([('BeautyMisc', 'BeautyMisc')], 'Beauty Types')
    # product_type_shoes = fields.Selection([('ClothingType', 'ClothingType')], 'Shoes Types')

    product_type_wirelessaccessories = fields.Selection([('WirelessAccessories', 'WirelessAccessories'),('WirelessDownloads', 'WirelessDownloads'),
        ], 'WirelessAccessories Types')

    product_type_cameraphoto = fields.Selection([('FilmCamera', 'FilmCamera'),('Camcorder', 'Camcorder'),('DigitalCamera', 'DigitalCamera'),('DigitalFrame', 'DigitalFrame'),('Binocular', 'Binocular'),('SurveillanceSystem', 'SurveillanceSystem'),('Telescope', 'Telescope'),('Microscope', 'Microscope'),('Darkroom', 'Darkroom'),('Lens', 'Lens'),('LensAccessory', 'LensAccessory'),('Filter', 'Filter'),('Film', 'Film'),('BagCase', 'BagCase'),('BlankMedia', 'BlankMedia'),('PhotoPaper', 'PhotoPaper'),('Cleaner', 'Cleaner'),('Flash', 'Flash'),('TripodStand', 'TripodStand'),('Lighting', 'Lighting'),('Projection', 'Projection'),('PhotoStudio', 'PhotoStudio'),('LightMeter', 'LightMeter'),('PowerSupply', 'PowerSupply'),('OtherAccessory', 'OtherAccessory'),], 'CameraPhoto Types')

    product_sub_type_ce = fields.Selection([('Antenna', 'Antenna'),('AVFurniture', 'AVFurniture'),('BarCodeReader', 'BarCodeReader'),
        ('CEBinocular', 'CEBinocular'),('CECamcorder', 'CECamcorder'),('CameraBagsAndCases', 'CameraBagsAndCases'),('Battery', 'Battery'),
        ('BlankMedia', 'BlankMedia'),('CableOrAdapter', 'CableOrAdapter'),('CECameraFlash', 'CECameraFlash'),('CameraLenses', 'CameraLenses'),
        ('CameraOtherAccessories', 'CameraOtherAccessories'),('CameraPowerSupply', 'CameraPowerSupply'),('CarAudioOrTheater', 'CarAudioOrTheater'),('CarElectronics', 'CarElectronics'),
        ('CEDigitalCamera', 'CEDigitalCamera'),('DigitalPictureFrame', 'DigitalPictureFrame'),('CECarryingCaseOrBag', 'CECarryingCaseOrBag'),('CombinedAvDevice', 'CombinedAvDevice'),
        ('Computer', 'Computer'),('ComputerDriveOrStorage', 'ComputerDriveOrStorage'),('ComputerProcessor', 'ComputerProcessor'),('ComputerVideoGameController', 'ComputerVideoGameController'),
        ('DigitalVideoRecorder', 'DigitalVideoRecorder'),('DVDPlayerOrRecorder', 'DVDPlayerOrRecorder'),('CEFilmCamera', 'CEFilmCamera'),('FlashMemory', 'FlashMemory'),
        ('GPSOrNavigationAccessory', 'GPSOrNavigationAccessory'),('GPSOrNavigationSystem', 'GPSOrNavigationSystem'),('HandheldOrPDA', 'HandheldOrPDA'),('HomeTheaterSystemOrHTIB', 'HomeTheaterSystemOrHTIB'),('Keyboards', 'Keyboards'),
        ('MemoryReader', 'MemoryReader'),('Microphone', 'Microphone'),('Monitor', 'Monitor'),('MP3Player', 'MP3Player'),
        ('MultifunctionOfficeMachine', 'MultifunctionOfficeMachine'),('NetworkAdapter', 'NetworkAdapter'),('NetworkMediaPlayer', 'NetworkMediaPlayer'),('NetworkStorage', 'NetworkStorage'),
        ('NetworkTransceiver', 'NetworkTransceiver'),('NetworkingDevice', 'NetworkingDevice'),('NetworkingHub', 'NetworkingHub'),('Phone', 'Phone'),
        ('PhoneAccessory', 'PhoneAccessory'),('PhotographicStudioItems', 'PhotographicStudioItems'),('PointingDevice', 'PointingDevice'),('PortableAudio', 'PortableAudio'),
        ('PortableAvDevice', 'PortableAvDevice'),('PortableElectronics', 'PortableElectronics'),('Printer', 'Printer'),('PrinterConsumable', 'PrinterConsumable'),
        ('ReceiverOrAmplifier', 'ReceiverOrAmplifier'),('RemoteControl', 'RemoteControl'),('SatelliteOrDSS', 'SatelliteOrDSS'),('Scanner', 'Scanner'),
        ('SoundCard', 'SoundCard'),('Speakers', 'Speakers'),('CETelescope', 'CETelescope'),('SystemCabinet', 'SystemCabinet'),
        ('SystemPowerDevice', 'SystemPowerDevice'),('Television', 'Television'),('TwoWayRadio', 'TwoWayRadio'),('VCR', 'VCR'),
        ('VideoCard', 'VideoCard'),('VideoProjector', 'VideoProjector'),('VideoProjectorsAndAccessories', 'VideoProjectorsAndAccessories'),('Webcam', 'Webcam')], 'CE Types')
        
    product_type_sportsmemorabilia = fields.Selection([('SportsMemorabilia','SportsMemorabilia'),('TradingCardsCardsSets','TradingCardsCardsSets'),('TradingCardsGradedCardsInserts','TradingCardsGradedCardsInserts'),('TradingCardsUngradedInserts','TradingCardsUngradedInserts'),('TradingCardsFactorySealed','TradingCardsFactorySealed'),('TradingCardsMiscTradingCards','TradingCardsMiscTradingCards')],'SportsMemorabilia Types')

    product_type_health = fields.Selection([('HealthMisc','HealthMisc'),('PersonalCareAppliances','PersonalCareAppliances'),('PrescriptionDrug','PrescriptionDrug'),('DietarySupplements','DietarySupplements'),('OTCMedication','OTCMedication'),('PrescriptionEyewear','PrescriptionEyewear'),('SexualWellness','SexualWellness'),('MedicalSupplies','MedicalSupplies')],'Health Types')

    product_type_tiresandwheels = fields.Selection([('Tires','Tires'),('Wheels','Wheels'),('TireAndWheelAssemblies','TireAndWheelAssemblies')],'TiresAndWheels Types')

    # product_type_giftcard = fields.Selection([('PhysicalGiftCard','PhysicalGiftCard'),('ElectronicGiftCard','ElectronicGiftCard')],'GiftCard Types')

    product_type_musicalinstruments = fields.Selection([('BrassAndWoodwindInstruments','BrassAndWoodwindInstruments'),('Guitars','Guitars'),
        ('InstrumentPartsAndAccessories','InstrumentPartsAndAccessories'),('KeyboardInstruments','KeyboardInstruments'),('MiscWorldInstruments','MiscWorldInstruments'),('PercussionInstruments','PercussionInstruments'),
        ('SoundAndRecordingEquipment','SoundAndRecordingEquipment'),('StringedInstruments','StringedInstruments')],'MusicalInstruments Type')

    # product_type_music = fields.Selection([('MusicPopular','MusicPopular'),('MusicClassical','MusicClassical')],'Music Types')

    # product_type_office = fields.Selection([('ArtSupplies','ArtSupplies'),('EducationalSupplies','EducationalSupplies'),('OfficeProducts','OfficeProducts'),('PaperProducts','PaperProducts'),('WritingInstruments','WritingInstruments')],'Office Types')




    
    battery_chargecycles = fields.Integer('Battery Charge Cycles')
    battery_celltype = fields.Selection([('NiCAD','NiCAD'),('NiMh','NiMh'),('alkaline','alkaline'),('aluminum_oxygen','aluminum_oxygen'),('lead_acid','lead_acid'),('lead_calcium','lead_calcium'),('lithium','lithium'),('lithium_ion','lithium_ion'),('lithium_manganese_dioxide','lithium_manganese_dioxide'),('lithium_metal','lithium_metal'),('lithium_polymer','lithium_polymer'),('manganese','manganese'),('polymer','polymer'),
        ('silver_oxide','silver_oxide'),('zinc','zinc')],'Battery Cell Type')
        
    power_plugtype = fields.Selection([('type_a_2pin_jp','type_a_2pin_jp'),('type_e_2pin_fr','type_e_2pin_fr'),('type_j_3pin_ch','type_j_3pin_ch'),('type_a_2pin_na','type_a_2pin_na'),('type_ef_2pin_eu','type_ef_2pin_eu'),('type_k_3pin_dk','type_k_3pin_dk'),('type_b_3pin_jp','type_b_3pin_jp'),('type_f_2pin_de','type_f_2pin_de'),('type_l_3pin_it','type_l_3pin_it'),('type_b_3pin_na','type_b_3pin_na'),('type_g_3pin_uk','type_g_3pin_uk'),('type_m_3pin_za','type_m_3pin_za'),('type_c_2pin_eu','type_c_2pin_eu'),
        ('type_h_3pin_il','type_h_3pin_il'),('type_n_3pin_br','type_n_3pin_br'),('type_d_3pin_in','type_d_3pin_in'),('type_i_3pin_au','type_i_3pin_au')],'Power Plug Type')
        
    power_source = fields.Selection([('AC','AC'),('DC','DC'),('Battery','Battery'),
        ('AC & Battery','AC & Battery'),('Solar','Solar'),('fuel_cell','Fuel Cell'),('Kinetic','Kinetic')],'Power Source')

    parentage  =  fields.Selection([('parent','parent'),('child','child')],'Parentage')        
    # wattage = fields.Integer('Wattage')
#     variation_data = fields.Selection([('Solar','Solar'),('Solar','Solar')],'VariationData'),


    ################## Computers #######################

    assembly_required = fields.Boolean('AssemblyRequired')
    manufacturer_warranty_type = fields.Char('ManufacturerWarrantyType',size=64)

    hand_orientation = fields.Selection([('Solar','Solar'),('Solar','Solar')],'HandOrientation')
    input_device_design_style = fields.Selection([('Solar','Solar'),('Solar','Solar')],'InputDeviceDesignStyle')
    keyboard_description = fields.Char('Keyboard Description',size=64)

    model_number = fields.Char('Model Number')
    # voltage = fields.Integer('Voltage')
    # wattage_com = fields.Integer('Wattage')
    wireless_input_device_protocol = fields.Selection([('Solar','Solar'),('Solar','Solar')],'Wireless InputDevice Protocol')
    wireless_input_device_technology = fields.Selection([('Solar','Solar'),('Solar','Solar')],'Wireless InputDevice Technology')

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
    # voltage_net = fields.Char('Voltage',size=64)
    # wattage_net= fields.Char('Wattage',size=64)
    wirelessdatatransferrate_net = fields.Char('Wireless Data Transfer Rate',size=64)
    wirelessroutertransmissionband_net = fields.Char('Wireless Router Transmission Band',size=64)
    wirelesstechnology_net = fields.Char('Wireless Technology',size=64)
    
#     variationdata_scanner = fields.Char('Variation Data',size=64)
    hasgreyscale_scanner = fields.Char('Has Grey Scale',size=64)
    lightsourcetype_scanner = fields.Char('Battery Chargecycles',size=64)
    maxinputsheetcapacity_scanner = fields.Integer('Max Input Sheet Capacity')
    maxprintresolutionblackwhite_scanner = fields.Char('Max Print Resolution BlackWhite',size=64)
    maxprintresolutioncolor_scanner  =  fields.Char('Max Print Resolution Color',size=64)
    maxprintspeedblackwhite_scanner  =  fields.Char('Max Print Speed BlackWhite',size=64)
    maxprintspeedcolor_scanner  =  fields.Char('Max Print Speed Color',size=64)
    maxscanningsize_scanner  =  fields.Char('Max scanning size',size=64)
    minscanningsize_scanner  =  fields.Char('Min Scanning Size',size=64)
    printermediasizemaximum_scanner  =  fields.Char('Printer Media Size Maximum',size=64)
    printeroutputtype_scanner  =  fields.Char('Printer Output Type',size=64)
    printerwirelesstype_scanner  =  fields.Char('Printer Wireless Type',size=64)
    printing_media_type_scanner  =  fields.Char('Printing Media Type',size=64)
    printingtechnology_scanner  =  fields.Char('Printing Technology',size=64)
    scanrate_scanner_scanner  =  fields.Char('Scan Rate',size=64)
    scannerresolution_scanner  =  fields.Char('Scanner Resolution',size=64)
    
    target_gender_beauty = fields.Selection([('male','Male'),('female','Female'),('unisex','Unisex')])
    operatingsystem_gp = fields.Char('Operating System',size=64)
    batterypower_headphone = fields.Char('Battery Power',size=64)

    ############### Large Appliances ##################

    battery_life_la = fields.Char('BatteryLife',size=64)
    # in cookoven: 
    burner_type_la = fields.Char('BurnerType',size=64)
    drawer_type_la = fields.Char('DrawerType',size=64)
    racks_la = fields.Char('Racks',size=64)
    # in ref:
    freezer_capacity_la = fields.Char('FreezerCapacity',size=64)
    ice_capacity_la = fields.Char('IceCapacity',size=64)

    installation_type_la = fields.Char('InstallationType',size=64)
    item_thickness_la = fields.Char('ItemThickness',size=64)

    ################## LabSupply ########

    chamber_depth_ls = fields.Char('ChamberDepth',size=64)
    chamber_height_ls = fields.Char('ChamberHeight',size=64)
    chamber_width_ls = fields.Char('ChamberWidth',size=64)
    heated_element_dimensions = fields.Char('HeatedElementDimensions',size=64)
    heater_surface_material_type = fields.Char('HeaterSurfaceMaterialType',size=64)
    heating_element_type = fields.Char('HeatingElementType',size=64)


    ##################### CameraPhoto ########################


    camera_type_cp = fields.Selection([('point-and-shoot','point-and-shoot'),('slr','slr'),('instant','instant'),('single-use','single-use'),('large-format','large-format'),('medium-format','medium-format'),('rangefinder','rangefinder'),('field','field'),('monorail','monorail'),('kids','kids'),('3-d','3-d'),('micro','micro'),('panorama','panorama'),('passport-and-id','passport-and-id'),('underwater','underwater'),('security-cameras','security-cameras'),('dummy-cameras','dummy-cameras'),('web-cameras','web-cameras'),('mirror-image-cameras','mirror-image-cameras'),('dome-cameras','dome-cameras'),('spy-cameras','spy-cameras'),('pinhole-cameras','pinhole-cameras'),('miniature-cameras','miniature-cameras'),('pen-cameras','pen-cameras'),('camcorder','camcorder'),('digital-camera','digital-camera'),('large-format','large-format'),('medium-format','medium-format'),('universal','universal'),('other','other')],'CameraType')

    has_image_stabilizer_cp = fields.Boolean('HasImageStabilizer')
    display_technology_cp = fields.Char('DisplayTechnology',size=64)
    manufacturer_cp = fields.Char('Manufacturer',size=64)
    model_number_cp = fields.Char('ModelNumber',size=64)
    mfr_part_number_cp = fields.Char('MfrPartNumber',size=64)
    auto_focus_technology_cp = fields.Char('AutoFocusTechnology',size=64)
    film_speed_range_cp = fields.Char('FilmSpeedRange',size=64)
    memory_Storage_Capacity_cp = fields.Char('MemoryStorageCapacity',size=64)
    memory_technology_cp = fields.Char('MemoryTechnology',size=64)

    # in filmcam
    film_format_cp  = fields.Selection([('aps','aps'),('16mm','16mm'),('35mm','35mm'),('110','110'),('120','120'),('2x3','2x3'),('4x5','4x5'),('8x10','8x10'),('10x12','10x12'),('16x20','16x20')],'FilmFormat')
    film_management_features_cp = fields.Char('FilmManagementFeatures',size=64)

    # in otherAcc
    camera_accessories_cp = fields.Selection([('mounting-brackets','mounting-brackets'),('power-adapter','power-adapter'),('cable','cable'),('sun-shield','sun-shield'),('camera-controller','camera-controller'),('transmitters','transmitters'),('zoom-lens','zoom-lens'),('pinhole-lens','pinhole-lens'),('close-up-accessories','close-up-accessories'),('viewfinders','viewfinders'),('motor-drives','motor-drives'),('remote-controls','remote-controls'),('cables-and-cords','cables-and-cords'),('other-camera-accessories','other-camera-accessories')],'CameraAccessories')

    camcorder_accessories_cp  = fields.Selection([('remote-controls','remote-controls'),('cables-and-cords','cables-and-cords'),('other-camcorder-accessories','other-camcorder-accessories')],'CamcorderAccessories')
# 
    # in powrsspply
    camera_power_supply_type_cp = fields.Selection([('batteries-general','batteries-general'),('disposable-batteries','disposable-batteries'),('rechargeable-Batteries','rechargeable-Batteries'),('external-batteries','external-batteries'),('adapters-general','adapters-general'),('ac-adapters','ac-adapters'),('dc-adapters','dc-adapters'),('battery-chargers','battery-chargers'),('ac-power-supply','ac-power-supply'),('dc-power-supply','dc-power-supply'),('other-power-supplies','other-power-supplies'),('battery-packs-general','battery-packs-general'),('dedicated-battery-packs','dedicated-battery-packs'),('other-batteries-and-packs','other-batteries-and-packs')],'CameraPowerSupplyType')

    # in Projctn
    projection_type_cp = fields.Selection([('video-projectors','video-projectors'),('large-format-projectors','large-format-projectors'),('medium-format-projectors','medium-format-projectors'),('multimedia-projectors','multimedia-projectors'),('opaque-projectors','opaque-projectors')],'ProjectionType')
    projector_lenses_cp  = fields.Selection([('35mm','35mm'),('large-format','large-format'),('medium-format','medium-format'),('normal','normal'),('telephoto','telephoto'),('wide-angle','wide-angle'),('zoom','zoom'),('other-projector-lenses','other-projector-lenses')],'ProjectorLenses') 
    projection_screens_cp = fields.Selection([('fast-fold-screens','fast-fold-screens'),('free-standing-floor-screens','free-standing-floor-screens'),('rear-projection-screens','rear-projection-screens'),('tabletop-screens','tabletop-screens'),('tripod-mounted-screens','tripod-mounted-screens'),('wall-and-ceiling-electric-screens','wall-and-ceiling-electric-screens'),('other-projection-screens','other-projection-screens')],'ProjectionScreens')

    # in photostidio
    storage_and_presentation_materials_cp  = fields.Selection([('hanging-bars','hanging-bars'),('pages-general','pages-general'),('negative-and-unmounted-slides-pages','negative-and-unmounted-slides-pages'),('mounted-slides-sleeves','mounted-slides-sleeves'),('prints-sleeves','prints-sleeves'),('other-media-sleeves','other-media-sleeves'),('negatives-boxes','negatives-boxes'),('slides-boxes','slides-boxes'),('prints-boxes','prints-boxes'),('other-boxes','other-boxes'),('portfolios','portfolios'),('presentation-boards','presentation-boards'),('professional-photo-albums','professional-photo-albums'),('other-professional-albums','other-professional-albums'),('sectional-frames','sectional-frames'),('digital-frames','digital-frames'),('other-professional-frames','other-professional-frames')],'StorageAndPresentationMaterials')


    studio_supplies_cp  = fields.Selection([('mounting-press','mounting-press'),('mat-boards-general','mat-boards-general'),('pressure-sensitive-boards','pressure-sensitive-boards'),('laminating-machines','laminating-machines'),('other-copystands','other-copystands')],'StudioSupplies')

    photo_backgrounds_cp  = fields.Selection([('ceiling-to-floor','ceiling-to-floor'),('collapsible-discs','collapsible-discs'),('free-standing','free-standing'),('graduated','graduated'),('wall-mounted','wall-mounted'),('other-background-styles','other-background-styles')],'PhotoBackgrounds')

    # in Light Meter
    meter_type_cp  = fields.Selection([('flash','flashr'),('ambient-and-flash','ambient-and-flash'),('spot','spot'),('color','color')],'MeterType')

    meter_display_cp  = fields.Selection([('analog','analog'),('digital','digital'),('led','led'),('match-needle','match-needle')],'MeterDisplay')

    # in otherAcc, SurveillanceSystem 
    night_vision_cp  = fields.Boolean('NightVision')

    # in filmcam, digtl cam, binoclr, Lens
    focus_type_cp  = fields.Selection([('auto-focus','auto-focus'),('manual-focus','manual-focus'),('manual-and-auto-focus','manual-and-auto-focus'),('focus-free','focus-free')],'FocusType')

    # in filmcam, digtl cam,
    lens_thread_cp = fields.Char('LensThread',size=64)

    # in filmcam, camcorder, digtlcam, SurveillanceSystem, Filter, other
    durability_cp = fields.Char('Durability',size=64)

    # in filmcam, camcorder, digtlcam, binoclr, SurveillanceSystem, Microscope, Lens, BagCase
    features_cp = fields.Char('Features',size=64)


    #####################FoodServicesAndJanSan##############################

    item_volume_fs = fields.Char('ItemVolume',size=64)
    holding_time_fs = fields.Char('HoldingTime',size=64)
    heat_time_fs = fields.Char('HeatTime',size=64)
    graduation_range_fs = fields.Char('GraduationRange',size=64)
    graduation_interval_fs = fields.Char('GraduationInterval',size=64)
    extension_length_fs = fields.Char('ExtensionLength',size=64)
    current_rating_fs = fields.Char('CurrentRating',size=64)
    coolant_consumption_rate_fs = fields.Char('CoolantConsumptionRate',size=64)
    coolant_capacity_fs = fields.Char('CoolantCapacity',size=64)
    cap_size_fs = fields.Char('CapSize',size=64)
    age_range_description_fs = fields.Char('AgeRangeDescription',size=64)


    ####################Sports#############################

    model_year_s  =  fields.Char('ModelYear',size=64)
    customizable_template_name_s  =  fields.Char('CustomizableTemplateName',size=64)
    is_customizable_s  =  fields.Boolean('IsCustomizable')
    grip_size_s  =  fields.Char('GripSize',size=64)
    diving_hood_thickness_s  =  fields.Char('DivingHoodThickness',size=64)
    design_s  =  fields.Char('Design',size=64)
    age_gender_category_s  =  fields.Char('AgeGenderCategory',size=64)
    bike_rim_size_s  =  fields.Char('BikeRimSize',size=64)
    boot_size_s  =  fields.Char('BootSize',size=64)
    calf_size_s  =  fields.Char('CalfSize',size=64)


    ##########################SportsMemo###########################

    packaging_sm  =  fields.Char('Packaging',size=64)
    game_used_sm  =  fields.Char('GameUsed',size=64)
    player_name_sm  =  fields.Char('PlayerName',size=64)
    authenticated_by_sm  =  fields.Char('AuthenticatedBy',size=64)
    authenticity_certificate_number_sm  =  fields.Char('AuthenticityCertificateNumber',size=64)
    signed_by_sm  =  fields.Char('SignedBy',size=64)
    autographed_sm  =  fields.Char('Autographed',size=64)
    jersey_type_sm  =  fields.Char('JerseyType',size=64)
    league_name_sm  =  fields.Char('LeagueName',size=64)
    season_sm  =  fields.Char('Season',size=64)
    sport_sm  =  fields.Char('Sport',size=64)
    team_name_sm  =  fields.Char('TeamName',size=64)
    uniform_number_sm  =  fields.Char('UniformNumber',size=64)
    whats_in_the_box_sm  =  fields.Char('WhatsInTheBox',size=64)
    year_sm  =  fields.Char('Year',size=64)
    is_very_high_value_sm  =  fields.Boolean('IsVeryHighValue')



    #################Gourmet#######################

    unit_count_g  =  fields.Char('UnitCount')
    item_specialty_g  =  fields.Char('ItemSpecialty')
    organic_certification_g  =  fields.Char('OrganicCertification')
    kosher_certification_g  =  fields.Char('KosherCertification')
    nutritional_facts_g  =  fields.Char('NutritionalFacts')
    country_produced_in_g  =  fields.Char('CountryProducedIn')
    identity_package_type_g  =  fields.Char('IdentityPackageType')
    can_ship_in_original_container_g  =  fields.Char('CanShipInOriginalContainer')


    #####################PowerTransmission#######################
    
    wire_diameter_pt = fields.Char('WireDiameter',size=64)
    trade_size_name_pt = fields.Char('TradeSizeName',size=64)
    strand_type_pt = fields.Char('StrandType',size=64)
    spring_wind_direction_pt = fields.Char('SpringWindDirection',size=64)
    spring_rate_pt = fields.Char('SpringRate',size=64)
    slide_travel_distance_pt = fields.Char('SlideTravelDistance',size=64)
    set_screw_thread_type_pt = fields.Char('SetScrewThreadType',size=64)
    outer_ring_width_pt = fields.Char('OuterRingWidth',size=64)
    number_of_teeth_pt = fields.Char('NumberOfTeeth',size=64)
    active_coils_pt = fields.Char('ActiveCoils',size=64)
    axial_misalignment_pt = fields.Char('AxialMisalignmentn',size=64)
    belt_cross_section_pt = fields.Char('BeltCrossSection',size=64)
    belt_width_pt = fields.Char('BeltWidth',size=64)
    body_outside_diameter_pt = fields.Char('BodyOutsideDiameter',size=64)
    compressed_length_pt = fields.Char('CompressedLength',size=64)
    deflection_angle_pt = fields.Char('DeflectionAngle',size=64)
    face_width_pt = fields.Char('FaceWidth ',size=64)
    flange_outside_diameter_pt = fields.Char('FlangeOutsideDiameter ',size=64)
    flange_thickness_pt = fields.Char('FlangeThickness ',size=64)
    guide_support_type_pt = fields.Char('GuideSupportType ',size=64)
    item_pitch_pt = fields.Char('ItemPitch ',size=64)
    key_way_depth_pt = fields.Char('KeyWayDepth ',size=64)
    key_way_sidth_pt = fields.Char('KeyWayWidth ',size=64)
    leg_length_pt = fields.Char('LegLength ',size=64)
    load_capacity_pt = fields.Char('LoadCapacity ',size=64)
    maximum_angular_misalignment_pt = fields.Char('MaximumAngularMisalignment ',size=64)
    maximum_parallel_misalignment_pt = fields.Char('MaximumParallelMisalignment ',size=64)
    maximum_rotational_speed_pt = fields.Char('MaximumRotationalSpeed ',size=64)
    maximum_spring_compression_load_pt = fields.Char('MaximumSpringCompressionLoad ',size=64)
    maximum_tension_load_pt = fields.Char('MaximumTensionLoad ',size=64)
    maximum_torque_pt = fields.Char('MaximumTorque ',size=64)
    minimum_spring_Compression_load_pt = fields.Char('MinimumSpringCompressionLoad ',size=64)
    number_of_bands_pt = fields.Char('NumberOfBands ',size=64)
    number_of_grooves_pt = fields.Char('NumberOfGrooves ',size=64)


    #####################PetSupply#######################

    breed_recommendation =  fields.Char('BreedRecommendation',size=64)
    battery_cell_composition =  fields.Char('BatteryCellComposition',size=64)
    battery_form_factor_ps =  fields.Char('BatteryFormFactor',size=64)
    closure_type_ps =  fields.Char('ClosureType',size=64)
    contains_food_or_beverage_ps =  fields.Char('ContainsFoodOrBeverage',size=64)
    color_specification_ps =  fields.Char('ColorSpecification',size=64)
    dog_size_ps =  fields.Char('DogSize',size=64)
    external_certification_ps =  fields.Char('ExternalCertification',size=64)
    fill_material_type_ps =  fields.Char('FillMaterialType',size=64)
    girth_size_ps =  fields.Char('GirthSize',size=64)
    height_recommendation_ps =  fields.Char('HeightRecommendation',size=64)
    health_benefits_ps =  fields.Char('HealthBenefits',size=64)
    included_components_ps =  fields.Char('IncludedComponents',size=64)
    includes_ac_adapter_ps =  fields.Boolean('IncludesAcAdapter')
    inner_material_type_ps =  fields.Char('InnerMaterialType',size=64)
    is_expiration_dated_product_ps =  fields.Boolean('IsExpirationDatedProduct')
    is_portable_ps =  fields.Boolean('IsPortable')
    item_display_diameter_ps =  fields.Char('ItemDisplayDiameter',size=64)
    item_form_ps =  fields.Char('ItemForm',size=64)
    item_thickness_ps =  fields.Char('ItemThickness',size=64)
    light_output_luminance_ps =  fields.Char('LightOutputLuminance',size=64)
    max_ordering_quantity_ps =  fields.Char('MaxOrderingQuantity',size=64)
    maximum_age_recommendation_ps =  fields.Char('MaximumAgeRecommendation',size=64)
    mfg_warranty_description_labor_ps =  fields.Char('MfgWarrantyDescriptionLabor',size=64)
    mfg_warranty_description_parts_ps =  fields.Char('MfgWarrantyDescriptionParts',size=64)
    mfg_warranty_description_type_ps =  fields.Char('MfgWarrantyDescriptionType',size=64)
    minimum_age_recommendation_ps =  fields.Char('MinimumAgeRecommendation',size=64)
    nutrition_facts_ps =  fields.Char('NutritionFacts',size=64)
    outer_material_type_ps =  fields.Char('OuterMaterialType',size=64)
    pattern_name_ps =  fields.Char('PatternName',size=64)
    pet_life_stage_ps =  fields.Char('PetLifeStage',size=64)
    pet_type_ps =  fields.Char('PetType',size=64)
    product_feature_ps =  fields.Char('ProductFeature',size=64)
    product_sample_received_date_ps =  fields.Char('ProductSampleReceivedDate',size=64)
    recommended_uses_for_product_ps =  fields.Char('RecommendedUsesForProduct',size=64)
    scent_name_ps =  fields.Char('ScentName',size=64)
    storage_instructions_ps =  fields.Char('StorageInstructions',size=64)
    tank_size_ps =  fields.Char('TankSize',size=64)
    width_size_ps =  fields.Char('WidthSize',size=64)
    model_name_ps =  fields.Char('ModelName',size=64)
    material_features_ps =  fields.Char('MaterialFeatures',size=64)
    legal_compliance_certification_regulatory_organization_name =  fields.Char('LegalComplianceCertificationRegulatoryOrganizationName',size=64)
    legal_compliance_certification_certifying_authority_name_ps =  fields.Char('LegalComplianceCertificationCertifyingAuthorityName',size=64)
    legal_compliance_certification_geographic_jurisdiction_ps =  fields.Char('LegalComplianceCertificationGeographicJurisdiction',size=64)
    legal_compliance_certification_status_ps =  fields.Selection([('compliant','compliant'),('noncompliant','noncompliant'),('exempt','exempt')],'LegalComplianceCertificationStatus')
    legal_compliance_certification_Value_ps =  fields.Char('LegalComplianceCertificationValue',size=64)

    
    
    ########################light##################    
    airflowcapacity_li  =  fields.Char('AirFlowCapacity',size=64)
    basediameter_li  =  fields.Char('BaseDiameter',size=64)
    battery_li  =  fields.Char('Battery',size=64)
    bulbdiameter_li  =  fields.Char('BulbDiameter',size=64)
    bulblength_li  =  fields.Char('BulbLength',size=64)
    bulblifespan_li  =  fields.Char('BulbLifeSpan',size=64)
    bulbpowerfactor_li  =  fields.Char('BulbPowerFactor',size=64)
    bulbspecialfeatures_li  =  fields.Text('BulbSpecialFeatures',size=64)
    bulbswitchingcycles_li  =  fields.Char('BulbSwitchingCycles',size=64)
    bulbtype_li  =  fields.Char('BulbType',size=64)
    bulbwattage_li  =  fields.Char('BulbWattage',size=64)
    captype_li  =  fields.Char('CapType',size=64)
    certification_li  =  fields.Char('Certification',size=64)
    collection_li  =  fields.Char('Collection',size=64)
    # color_li  =  fields.Char('Color',size=64)
    energy_rating_li  =  fields.Char('EnergyEfficiencyRating',size=64)
    inte_rating_li  =  fields.Char('InternationalProtectionRating',size=64)
    itemdiameter_li  =  fields.Char('ItemDiameter',size=64)
    lightingmethod_li  =  fields.Char('LightingMethod',size=64)
    lithium_content_li  =  fields.Char('LithiumBatteryEnergyContent',size=64)
    lithium_voltage_li  =  fields.Char('LithiumBatteryVoltage',size=64)
    lithium_weight_li  =  fields.Char('LithiumBatteryWeight',size=64)
    # material_li  =  fields.Char('Material',size=64)
    numberofblades_li  =  fields.Char('NumberOfBlades',size=64)
    numberofbulbsockets_li  =  fields.Char('NumberOfBulbSockets',size=64)
    plugtype_li  =  fields.Char('PlugType',size=64)
    powersource_li  =  fields.Char('PowerSource',size=64)
    specialfeatures_li  =  fields.Char('SpecialFeatures',size=64)
    specificuses_li  =  fields.Char('SpecificUses',size=64)
    stylename_li  =  fields.Char('StyleName',size=64)
    switchstyle_li  =  fields.Char('SwitchStyle',size=64)
    # voltage_li  =  fields.Char('Voltage',size=64)
    volume_li  =  fields.Char('Volume',size=64)
    # wattage_li  =  fields.Char('Wattage',size=64)
    

    mercury_bulb = fields.Char('MercuryContent')
    more_attributes = fields.Boolean('More Attributes')
    
    
################### Beauty #################

    scent_beauty = fields.Char('Scent')
    pattern_name_beauty = fields.Char('Pattern Name')
    unit_count_beauty = fields.Integer('Unit Count')
    uom_beauty = fields.Char('Unit Of Measure')
    count_beauty = fields.Integer('Count')
    no_of_items_beauty = fields.Integer('Number Of Items')
    battry_average_life_beauty = fields.Char('Battery Average Life')
    battry_charge_time_beauty = fields.Char('Battery Charge Time')
    battry_descriptn_beauty = fields.Char('Battery Description')
    battry_power_beauty = fields.Integer('Battery Power')
    skin_type_beauty = fields.Char('Skin Type')
    skin_tone_beauty = fields.Char('Skin Tone')
    hair_type_beauty = fields.Char('Hair Type')
    ingredients_beauty = fields.Char('Ingredients')
    mrf_warrant_type_beauty = fields.Char('Manufacturer Warranty Type')
    material_type_beauty = fields.Char('Material Type')
    is_adult_product_beauty = fields.Boolean('IsAdultProduct')
    
    
            #######################home################
    isstainresistant_home = fields.Boolean('IsStainResistant')
    # material_home = fields.Char('Material')
    numberofsets_home = fields.Char('NumberOfSets')
    shape_home = fields.Char('Shape')
    threadcount_home = fields.Char('ThreadCount')
    variationtheme = fields.Selection([('Size','Size'),
                                       ('Color','Color'),
                                       ('Scent','Scent'),
                                       ('Size-Color','Size-Color'),
                                       ('Size-Scent','Size-Scent'),
                                       ('DisplayLength-DisplayWidth','DisplayLength-DisplayWidth'),
                                       ('DisplayLength-Material','DisplayLength-Material'),
                                       ('DisplayLength-Size','DisplayLength-Size'),
                                       ('DisplayLength-Color','DisplayLength-Color'),
                                       ('DisplayLength-DisplayHeight','DisplayLength-DisplayHeight'),
                                       ('DisplayWidth-Material','DisplayWidth-Material'),
                                       ('DisplayWidth-Size','DisplayWidth-Size'),
                                       ('DisplayWidth-Color','DisplayWidth-Color'),
                                       ('DisplayWidth-DisplayHeight','DisplayWidth-DisplayHeight'),
                                       ('ItemPackageQuantity-Material','ItemPackageQuantity-Material'),
                                       ('ItemPackageQuantity-Size','ItemPackageQuantity-Size'),
                                       ('ItemPackageQuantity-Color','ItemPackageQuantity-Color'),
                                       ('ItemPackageQuantity-DisplayHeight','ItemPackageQuantity-DisplayHeight'),
                                       ('DisplayWeight-ItemPackageQuantity','DisplayWeight-ItemPackageQuantity'),
                                       ('DisplayWeight-Material','DisplayWeight-Material'),
                                       ('DisplayWeight-Size','DisplayWeight-Size'),
                                       ('DisplayWeight-Color','DisplayWeight-Color'),
                                       ('DisplayWeight-DisplayHeight','DisplayWeight-DisplayHeight'),
                                       ('Material-DisplayLength','Material-DisplayLength'),
                                       ('Material-DisplayWidth','Material-DisplayWidth'),
                                       ('Material-Size','Material-Size'),
                                       ('Material-Color','Material-Color'),
                                       ('Material-DisplayHeight','Material-DisplayHeight'),
                                       ('Size-DisplayLength','Size-DisplayLength'),
                                       ('Size-DisplayWidth','Size-DisplayWidth'),
                                       ('Size-DisplayWeight','Size-DisplayWeight'),
                                       ('Size-Material','Size-Material'),
                                       ('Size-Color','Size-Color'),
                                       ('Size-DisplayHeight','Size-DisplayHeight'),
                                       ('Color-DisplayLength','Color-DisplayLength'),
                                       ('Color-DisplayWidth','Color-DisplayWidth'),
                                       ('Color-ItemPackageQuantity','Color-ItemPackageQuantity'),
                                       ('Color-DisplayWeight','Color-DisplayWeight'),
                                       ('Color-Material','Color-Material'),
                                       ('Color-Size','Color-Size'),
                                       ('Color-DisplayHeight','Color-DisplayHeight'),
                                       ('DisplayHeight','DisplayHeight'),
                                       ('Material','Material'),
                                       ('DisplayWeight','DisplayWeight'),
                                       ('DisplayLength','DisplayLength'),
                                       ('ItemPackageQuantity','ItemPackageQuantity'),
                                       ('DisplayLength-PatternName','DisplayLength-PatternName'),
                                       ('DisplayLength-StyleName','DisplayLength-StyleName'),
                                       ('DisplayWidth-PatternName','DisplayWidth-PatternName'),
                                       ('DisplayWidth-StyleName','DisplayWidth-StyleName'),
                                       ('Occasion-PatternName','Occasion-PatternName'),
                                       ('Occasion-ItemPackageQuantity','Occasion-ItemPackageQuantity'),
                                       ('Occasion-Material','Occasion-Material'),
                                       ('Occasion-StyleName','Occasion-StyleName'),
                                       ('Occasion-Size','Occasion-Size'),
                                       ('Occasion-Color','Occasion-Color'),
                                       ('Occasion-DisplayHeight','Occasion-DisplayHeight'),
                                       ('PatternName-DisplayLength','PatternName-DisplayLength'),
                                       ('PatternName-DisplayWidth','PatternName-DisplayWidth'),
                                       ('PatternName-Occasion','PatternName-Occasion'),
                                       ('PatternName-Material','PatternName-Material'),
                                       ('PatternName-StyleName','PatternName-StyleName'),
                                       ('PatternName-Size','PatternName-Size'),
                                       ('PatternName-Color','PatternName-Color'),
                                       ('PatternName-DisplayHeight','PatternName-DisplayHeight'),
                                       ('MatteStyle-Material','MatteStyle-Material'),
                                       ('MatteStyle-StyleName','MatteStyle-StyleName'),
                                       ('MatteStyle-Size','MatteStyle-Size'),
                                       ('MatteStyle-Color','MatteStyle-Color'),
                                       ('ItemPackageQuantity-Occasion','ItemPackageQuantity-Occasion'),
                                       ('ItemPackageQuantity-StyleName','ItemPackageQuantity-StyleName'),
                                       ('DisplayWeight-StyleName','DisplayWeight-StyleName'),
                                       ('Material-PatternName','Material-PatternName'),
                                       ('Material-MatteStyle','Material-MatteStyle'),
                                       ('Material-StyleName','Material-StyleName'),
                                       ('StyleName-DisplayLength','StyleName-DisplayLength'),
                                       ('StyleName-DisplayWidth','StyleName-DisplayWidth'),
                                       ('StyleName-Occasion','StyleName-Occasion'),
                                       ('StyleName-PatternName','StyleName-PatternName'),
                                       ('StyleName-DisplayWeight','StyleName-DisplayWeight'),
                                       ('StyleName-Material','StyleName-Material'),
                                       ('StyleName-Size','StyleName-Size'),
                                       ('StyleName-Color','StyleName-Color'),
                                       ('Size-Occasion','Size-Occasion'),
                                       ('Size-PatternName','Size-PatternName'),
                                       ('Size-MatteStyle','Size-MatteStyle'),
                                       ('Size-StyleName','Size-StyleName'),
                                       ('Color-Occasion','Color-Occasion'),
                                       ('Color-PatternName','Color-PatternName'),
                                       ('Color-MatteStyle','Color-MatteStyle'),
                                       ('Color-StyleName','Color-StyleName'),
                                       ('MatteStyle','MatteStyle'),
                                       ('PatternName','PatternName'),
                                       ('collection-parent','collection-parent'),
                                       ('variation-parent','variation-parent'),
                                       ('base-product','base-product'),
                                       ('Occasion','Occasion'),
                                       ('StyleName','StyleName'),
                                       ('CustomerPackageType','CustomerPackageType'),
                                       ('ColorName-CustomerPackageType','ColorName-CustomerPackageType'),
                                       ('SizeName-CustomerPackageType','SizeName-CustomerPackageType'),
                                       ('SizeName-ColorName-CustomerPackageType','SizeName-ColorName-CustomerPackageType'),
                                       ('StyleName-CustomerPackageType','StyleName-CustomerPackageType'),
                                       ('SizeName-StyleName-CustomerPackageType','SizeName-StyleName-CustomerPackageType'),
                                                             
                                       ],'VariationTheme')
#     size_home = fields.Char('Size'),
#     color_home = fields.Char('Color'),
#     scent_home = fields.Char('Scent'),
    # customerpackagetype_home = fields.Char('CustomerPackageType')
        
    # wattage_watt = fields.Char('Wattage')
    # parentage_watt = fields.Selection([('collection-parent','collection-parent'),
    #                              ('variation-parent','variation-parent'),
    #                              ('base-product','base-product'),
    #                              ('parent','parent'),
    #                              ('child','child')],'Parentage')
            
    lightsourcetype_home = fields.Char('LightSourceType')
    
    
    identitypackagetype_home = fields.Selection([('bulk','bulk'),
                                            ('frustration_free','frustration_free'),
                                            ('traditional','traditional')],'IdentityPackageType')
        
    fabrictype_home = fields.Char('FabricType')    
    mattestyle_home = fields.Char('MatteStyle')
    # itempackagequantity_home = fields.Char('ItemPackageQuantity')
    
    # material_home = fields.Char('Material')
    numberofpieces_home = fields.Char('NumberOfPieces')
    warnings_home = fields.Char('Warnings')
    # wattage_home = fields.Char('Wattage')
    length_home = fields.Char('Length')
    width_home = fields.Char('Width')
    height_home = fields.Char('Height')
    depth_home = fields.Char('Depth')
    diameter_home = fields.Char('Diameter')
    weight_home = fields.Char('Weight')
    
    moistureneeds_home = fields.Selection([('little-to-no-watering','little-to-no-watering'),
                                      ('moderate-watering','moderate-watering'),
                                      ('regular-watering','regular-watering'),
                                      ('constant-watering','constant-watering')],'MoistureNeeds')
    
    numberofsets_home = fields.Char('NumberOfSets')  
    
    
    ################home Art################
    paint_type_art = fields.Char('Paint Type')
    home_art = fields.Boolean('Home Art')
    
    
    
    ############Home Seeds and Plants #################
    sunlightexposure_seed = fields.Selection([('shade','shade'),
                                          ('partial-shade','partial-shade'),
                                          ('partial-sun','partial-sun'),
                                          ('full-sun','full-sun')],'SunlightExposure')
    sunsetclimatezone_seed = fields.Selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),
                                          ('7','7'),('8','8'),('9','9'),('10','10'),('11','11'),('12','12'),('13','13'),('14','14'),
                                          ('15','15'),('16','16'),('17','17'),('18','18'),('19','19'),('20','20'),('21','21'),('22','22'),('23','23'),('24','24')],
                                         'SunsetClimateZone')
    hardinesszone_seed = fields.Selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),
                                          ('7','7'),('8','8'),('9','9'),('10','10'),('11','11')],'USDAHardinessZone')
#     variationtheme_seed = fields.Selection([('Size','Size'),
#                                             ('Color','Color'),
#                                             ('Size-Color','Size-Color'),
#                                             ('StyleName','StyleName'),
#                                             ('CustomerPackageType','CustomerPackageType'),
#                                             ('ColorName-CustomerPackageType','ColorName-CustomerPackageType'),
#                                             ('SizeName-CustomerPackageType','SizeName-CustomerPackageType'),
#                                             ('SizeName-ColorName-CustomerPackageType','SizeName-ColorName-CustomerPackageType'),
#                                             ('StyleName-CustomerPackageType','StyleName-CustomerPackageType'),
#                                             ('SizeName-StyleName-CustomerPackageType','SizeName-StyleName-CustomerPackageType')],'VariationTheme'),
    # size_seed = fields.Char('Size')
    # color_seed = fields.Char('Color')
    # stylename_seed = fields.Char('StyleName')
    # customerpack_seed = fields.Char('CustomerPackageType')
    # seed_plant = fields.Boolean('Seeds and Plants')
    
    ###################Home Outdoor living########################
    # outdoor_living = fields.Boolean('Outdoor Living')
    
    #################Home Kitchen ###############################
    # kitchen = fields.Boolean('Kitchen')
    
    ########################Furniture And Decor #################
    # fur_decor = fields.Boolean('Furniture And Decor')
    
    #############bed and bath#########################
    # bed_bath = fields.Boolean('Bed and Bath')


    ####################Tools#########################
    
    power_source_t = fields.Selection([('battery-powered', 'battery-powered'),('gas-powered', 'gas-powered'),('hydraulic-powered', 'hydraulic-powered'),('air-powered', 'air-powered'),('corded-electric', 'corded-electric')], 'PowerSource')

    number_of_items_inpackage_t = fields.Char('NumberOfItemsInPackage')

    ############################# Home Improvement######################

    battery_average_life_hi = fields.Char('BatteryAverageLife')
    battery_average_life_standby_hi = fields.Char('BatteryAverageLifeStandby')
    battery_charge_time_hi = fields.Char('BatteryChargeTime')
    battery_type_lithium_ion_hi = fields.Char('BatteryTypeLithiumIon')
    battery_type_lithium_metal_hi = fields.Char('BatteryTypeLithiumMetal')
    country_of_origin_hi = fields.Char('CountryOfOrigin')
    item_display_area_hi = fields.Char('ItemDisplayArea')
    # lithium_battery_energy_content_hi = fields.Char('LithiumBatteryEnergyContent')
    # lithium_battery_packaging_hi = fields.Selection([('batteries_contained_in_equipment','batteries_contained_in_equipment'),('batteries_only','batteries_only'),('batteries_packed_with_equipment','batteries_packed_with_equipment')],'LithiumBatteryPackaging')
    # lilthium_battery_voltage_hi = fields.Char('LithiumBatteryVoltage')
    # lithium_battery_weight_hi = fields.Char('LithiumBatteryWeight')
    mfr_warranty_description_labor_hi = fields.Char('MfrWarrantyDescriptionLabor')
    mfr_warranty_description_parts_hi = fields.Char('MfrWarrantyDescriptionParts')
    mfr_warranty_description_type_hi = fields.Char('MfrWarrantyDescriptionType')
    number_of_lithium_ion_cells_hi = fields.Char('NumberOfLithiumIonCells')
    number_of_lithium_metal_cells_hi = fields.Char('NumberOfLithiumMetalCells')
    # warnings_hi = fields.Char('Warnings')
    # fabric_type_hi = fields.Char('FabricType')
    import_designation_hi = fields.Char('ImportDesignation')
    accessory_connection_type_hi = fields.Char('AccessoryConnectionType')
    battery_capacity_hi = fields.Char('BatteryCapacity')
    blade_edge_hi = fields.Char('BladeEdge')
    blade_length_hi = fields.Char('BladeLength')
    compatible_devices_hi = fields.Char('CompatibleDevices')
    compatible_fastener_range_hi = fields.Char('CompatibleFastenerRange')
    cooling_method_hi = fields.Char('CoolingMethod')
    cooling_wattage_hi = fields.Char('CoolingWattage')
    corner_radius_hi = fields.Char('CornerRadius')
    coverage_hi = fields.Char('Coverage')
    cut_type_hi = fields.Char('CutType')
    cutting_width_hi = fields.Char('CuttingWidth')
    device_type_hi = fields.Char('DeviceType')
    display_style_hi = fields.Char('DisplayStyle')
    energy_consumption_hi = fields.Char('EnergyConsumption')
    energy_efficiency_ratio_cooling_hi = fields.Char('EnergyEfficiencyRatioCooling')
    environmental_description_hi = fields.Char('EnvironmentalDescription')
    eu_energy_efficiency_class_heating_hi = fields.Char('EuEnergyEfficiencyClassHeating')
    eu_energy_label_efficiency_class_hi = fields.Char('EuEnergyLabelEfficiencyClass')
    external_testing_certification_hi = fields.Char('ExternalTestingCertification')

    flush_type_hi = fields.Char('FlushType')
    folded_knife_size_hi = fields.Char('FoldedKnifeSize')
    grit_rating_hi = fields.Char('GritRating')
    handle_material_hi = fields.Char('HandleMaterial')
    inside_diameter_hi = fields.Char('InsideDiameter')
    heater_wattage_hi = fields.Char('HeaterWattage')
    laser_beam_color_hi = fields.Char('LaserBeamColor')
    maximum_power_hi = fields.Char('MaximumPower')
    measurement_accuracy_hi = fields.Char('MeasurementAccuracy')
    measurement_system_hi = fields.Char('MeasurementSystem')

    minimum_efficiency_reporting_value_hi = fields.Char('MinimumEfficiencyReportingValue')
    number_of_basins_hi = fields.Char('NumberOfBasins')
    number_of_holes_hi = fields.Char('NumberOfHoles')
    number_of_items_hi = fields.Char('NumberOfItems')
    outside_diameter_hi = fields.Char('OutsideDiameter')
    performance_description_hi = fields.Char('PerformanceDescription')
    recycled_content_percentage_hi = fields.Char('RecycledContentPercentage')
    speed_hi = fields.Char('Speed')
    rough_in_hi = fields.Char('RoughIn')
    spout_height_hi = fields.Char('SpoutHeight')

    spout_reach_hi = fields.Char('SpoutReach')
    thread_size_hi = fields.Char('ThreadSize')
    tool_tip_description_hi = fields.Char('ToolTipDescription')
    torque_hi = fields.Char('Torque')
    uv_protection_hi = fields.Char('UVProtection')
    viewing_area_hi = fields.Char('ViewingArea')
    # size_hi = fields.Char('Size')
    bulb_type_hi = fields.Char('BulbType')
    center_length_hi = fields.Char('CenterLength')
    brightness_hi = fields.Char('Brightness')

    # color_hi = fields.Char('Color')
    color_map_hi  = fields.Char('ColorMap')
    head_style_hi = fields.Char('HeadStyle')
    material_hi = fields.Char('Material')
    display_volume_hi = fields.Char('DisplayVolume')
    display_length_hi = fields.Char('DisplayLength')
    manufacturer_warranty_description_hi = fields.Char('ManufacturerWarrantyDescription')
    plug_format_hi = fields.Char('PlugFormat')
    plug_profile_hi = fields.Char('PlugProfile')
    power_source_hi = fields.Char('PowerSource')

    cutting_diameter_hi = fields.Char('CuttingDiameter')
    customer_package_type_hi = fields.Char('CustomerPackageType')
    display_diameter_hi = fields.Char('DisplayDiameter')
    display_weight_hi = fields.Char('DisplayWeight')
    display_width_hi = fields.Char('DisplayWidht')
    display_height_hi = fields.Char('DisplayHeight')
    horsepower_hi = fields.Char('Horsepower')
    minimum_age_hi = fields.Char('MinimumAge')
    customer_restriction_type_hi = fields.Char('CustomerRestrictionType')

    seller_warranty_description_hi = fields.Char('SellerWarrantyDescription')
    switch_style_hi = fields.Char('SwitchStyle')
    switch_type_hi = fields.Char('SwitchType')
    voltage_hi = fields.Char('Voltage')
    wattage_hi = fields.Char('Wattage')
    # customer_packageType_hi = fields.Char('CustomerPackageType')
    base_diameter_hi = fields.Char('BaseDiameter')
    beam_angle_hi = fields.Char('BeamAngle')
    blade_color_hi = fields.Char('BladeColor')
    circuit_breaker_type_hi = fields.Char('CircuitBreakerType')

    efficiency_hi = fields.Char('Efficiency')
    international_protection_rating_hi = fields.Char('InternationalProtectionRating')
    light_source_operating_life_hi = fields.Char('LightSourceOperatingLife')
    lighting_method_hi = fields.Char('LightingMethod')
    maximum_compatible_light_source_wattage_hi = fields.Char('MaximumCompatibleLightSourceWattage')
    number_of_blades_hi = fields.Char('NumberOfBlades')
    number_of_light_sources_hi = fields.Char('NumberOfLightSources')
    shade_diameter_hi = fields.Char('ShadeDiameter')
    shade_material_type_hi = fields.Char('ShadeMaterialType')
    short_product_description_hi = fields.Char('ShortProductDescription')

    start_up_time_description_hi = fields.Char('StartUpTimeDescription')
    strands_hi = fields.Char('Strands')
    tubing_outside_Diameter_hi = fields.Char('TubingOutsideDiameter')
    legal_compliance_certification_metadata_hi = fields.Char('LegalComplianceCertificationMetadata')
    legal_compliance_certification_date_of_issue_hi = fields.Datetime('LegalComplianceCertificationDateOfIssue')
    legal_compliance_certification_expiration_date_hi = fields.Datetime('LegalComplianceCertificationExpirationDate')
    power_plug_type_hi = fields.Char('PowerPlugType')

    base_width_hi = fields.Char('BaseWidth')
    capacity_hi = fields.Char('Capacity')
    control_type_hi = fields.Char('ControlType')
    drain_type_hi = fields.Char('DrainType')
    form_factor_hi = fields.Char('FormFactor')
    gauge_string_hi = fields.Char('GaugeString')
    handle_type_hi = fields.Char('HandleType')
    input_power_hi = fields.Char('InputPower')
    mounting_type_hi = fields.Char('MountingType')
    number_of_settings_hi = fields.Char('NumberOfSettings')
    roll_quantity_hi = fields.Char('RollQuantity')

    r_value_hi  = fields.Char('R Value')


    #########################RamMateraial#########################

    wire_diameter_string_rm = fields.Char('WireDiameterString')
    void_volume_percentage_rm = fields.Char('VoidVolumePercentage')
    upper_temperature_rating_rm = fields.Char('UpperTemperatureRating')
    upper_bubbling_pressure_rm = fields.Char('UpperBubblingPressure')
    tubing_wall_type_rm = fields.Char('TubingWallType')
    tolerance_held_rm = fields.Char('ToleranceHeld')
    thread_diameter_string_rm = fields.Char('ThreadDiameterString')
    tensile_strength_rm = fields.Char('TensileStrength')
    standard_construction_rm = fields.Char('StandardConstruction')
    slot_width_rm = fields.Char('SlotWidth')
    slot_depth_rm = fields.Char('SlotDepth')
    shim_type_rm = fields.Char('ShimType')
    notch_width_rm = fields.Char('NotchWidth')
    notch_depth_rm = fields.Char('NotchDepth')
    metal_construction_type_rm = fields.Char('MetalConstructionType')
    mesh_opening_size_rm = fields.Char('MeshOpeningSize')
    mesh_openin_shape_rm = fields.Char('MeshOpeningShape')
    mesh_number_rm = fields.Char('MeshNumber')
    mesh_form_rm = fields.Char('MeshForm')
    mesh_count_rm = fields.Char('MeshCount')
    maximum_pressure_rm = fields.Char('MaximumPressure')
    air_entry_pressure_rm = fields.Char('AirEntryPressure')
    backing_type_rm = fields.Char('BackingType')
    ball_type_rm = fields.Char('BallType')
    compatible_with_tube_gauge_rm = fields.Char('CompatibleWithTubeGauge')
    corner_style_rm = fields.Char('CornerStyle')
    disc_diameter_string_rm = fields.Char('DiscDiameterString')
    durometer_hardness_rm = fields.Char('DurometerHardness')
    exterior_finish_rm = fields.Char('ExteriorFinish')
    foam_structure_rm = fields.Char('FoamStructure')
    grade_rating_rm = fields.Char('GradeRating')
    hole_count_rm = fields.Char('HoleCount')
    inside_diameter_string_rm = fields.Char('InsideDiameterString')
    inside_diameter_tolerance_string_rm = fields.Char('InsideDiameterToleranceString')
    item_diameter_tolerance_string_rm = fields.Char('ItemDiameterToleranceString')
    item_hardness_rm = fields.Char('ItemHardness')
    item_length_tolerance_string_rm = fields.Char('ItemLengthToleranceString')
    item_shape_rm = fields.Char('ItemShape')
    item_temper_rm = fields.Char('ItemTemper')
    item_thickness_tolerance_string_rm = fields.Char('ItemThicknessToleranceString')
    item_width_tolerance_string_rm = fields.Char('ItemWidthToleranceString')
    lower_bubbling_pressure_rm = fields.Char('LowerBubblingPressure')




    ######################################baby#############

    seating_capacity_by  = fields.Char('SeatingCapacity')
    seat_interior_width_by  = fields.Char('SeatInteriorWidth')
    seat_height_by  = fields.Char('SeatHeight')
    seat_back_interior_height_by  = fields.Char('SeatBackInteriorHeight')
    safety_warning_by  = fields.Char('SafetyWarning')
    battery_description_by  = fields.Char('BatteryDescription')
    battery_power_by  = fields.Char('BatteryPower')
    bottle_nipple_type_by  = fields.Char('BottleNippleType')
    bottle_type_by  = fields.Char('BottleType')
    carrier_weight_by  = fields.Char('CarrierWeight')
    car_seat_weight_group_eu_by  = fields.Char('CarSeatWeightGroupEU')
    color_name_by  = fields.Char('ColorName')
    folded_size_by  = fields.Char('FoldedSize')
    is_dishwasher_safe_by  = fields.Boolean('IsDishwasherSafe')
    item_depth_by  = fields.Char('ItemDepth')
    # manufacturer_warranty_description_by  = fields.Char('ManufacturerWarrantyDescription')
    material_type_free_by = fields.Char('MaterialTypeFree')
    maximum_anchoring_weight_capacity_by  = fields.Char('MaximumAnchoringWeightCapacity')
    maximum_height_recommendation_by  = fields.Char('MaximumHeightRecommendation')
    minimum_height_recommendation_by  = fields.Char('MinimumHeightRecommendation')
    maximum_manufacturer_age_recommended_by  = fields.Char('MaximumManufacturerAgeRecommended')
    minimum_manufacturer_age_recommended_by  = fields.Char('MinimumManufacturerAgeRecommended')
    maximum_item_width_by  = fields.Char('MaximumItemWidth')
    maximum_range_indoors_by  = fields.Char('MaximumRangeIndoors')
    maximum_range_open_space_by  = fields.Char('MaximumRangeOpenSpace')
    maximum_weight_recommendation_by  = fields.Char('MaximumWeightRecommendation')
    minimum_weight_recommendation_by  = fields.Char('MinimumWeightRecommendation')
    operation_mode_by  = fields.Char('OperationMode')
    orientation_by  = fields.Char('Orientation')
    
    
    ######################################  Clothing And Accessories###################3
    cloth = fields.Boolean('Clothing And Accessories')
    # parentage_cloth = fields.Selection([('parent','parent'),('child','child')],'Parentage')
    # size_cloth = fields.Char('Size')
    # color_cloth = fields.Char('Color')
    # variationtheme_cloth = fields.Selection([('Size','Size'),('Color','Color'),('SizeColor','SizeColor')],'VariationTheme')
    department_cloth = fields.Char('Department')
    cloth_type = fields.Selection([('Shirt','Shirt'),('Sweater','Sweater'),('Pants','Pants'),('Shorts','Shorts'),('Skirt','Skirt'),('Dress','Dress'),('Suit','Suit'),('Blazer','Blazer'),('Outerwear','Outerwear'),('SocksHosiery','SocksHosiery'),('Underwear','Underwear'),('Bra','Bra'),('Shoes','Shoes'),('Hat','Hat'),('Bag','Bag'),('Accessory','Accessory'),('Jewelry','Jewelry'),('Sleepwear','Sleepwear'),('Swimwear','Swimwear'),('PersonalBodyCare','PersonalBodyCare'),('HomeAccessory','HomeAccessory'),('NonApparelMisc','NonApparelMisc')],string='ClothingType',default='Shirt')
    size_tem_map = fields.Selection([('XXXXX-Small','XXXXX-Small'),('XXXX-Small','XXXX-Small'),('XXX-Small','XXX-Small'),('XX-Small','XX-Small'),('X-Small','X-Small'),('Small','Small'),('Medium','Medium'),('Large','Large'),('X-Large','X-Large'),('XX-Large','XX-Large'),('XXX-Large','XXX-Large'),('XXXX-Large','XXXX-Large'),('XXXXX-Large','XXXXX-Large')],string='Size Map',)



    material_cloth = fields.Char('MaterialAndFabric')
    furdescription_cloth = fields.Char('FurDescription')
    materialopacity_cloth = fields.Char('MaterialOpacity')
    fabricwash_cloth = fields.Char('FabricWash')
    patternstyle_cloth = fields.Char('PatternStyle')
    apparelclosuretype_cloth = fields.Char('ApparelClosureType')
    occasionandlifestyle_cloth = fields.Char('OccasionAndLifestyle')
    # stylename_cloth = fields.Char('StyleName')
    stylenumber_cloth = fields.Char('StyleNumber')
    collartype_cloth = fields.Char('CollarType')
    sleevetype_cloth = fields.Char('SleeveType')
    cufftype_cloth = fields.Char('CuffType')
    pocketdescription_cloth = fields.Char('PocketDescription')
    frontpleattype_cloth = fields.Char('FrontPleatType')
    topstyle_cloth = fields.Char('TopStyle')
    bottomstyle_cloth = fields.Char('BottomStyle')
    waistsize_cloth = fields.Char('WaistSize')
    inseamlength_cloth = fields.Char('InseamLength')
    sleevelength_cloth = fields.Char('SleeveLength')
    necksize_cloth = fields.Char('NeckSize')
    neckstyle_cloth = fields.Char('NeckStyle')
    chestsize_cloth = fields.Char('ChestSize')




    cupsize_cloth = fields.Selection([('A','A'),('AA','AA'),('B','B'),('C','C'),('D','D'),
                                   ('DD','DD'),('DDD','DDD'),('E','E'),('EE','EE'),('F','F'),('FF','FF'),
                                   ('G','G'),('GG','GG'),('H','H'),('I','I'),('J','J'),('Free','Free')],'CupSize')
           
    underwiretype_cloth = fields.Char('UnderwireType')
    shoewidth_cloth = fields.Char('ShoeWidth')
    legdiameter_cloth = fields.Char('LegDiameter')
    legstyle_cloth = fields.Char('LegStyle')
    beltstyle_cloth = fields.Char('BeltStyle')
    straptype_cloth = fields.Char('StrapType')
    toestyle_cloth = fields.Char('ToeStyle')
    theme_cloth = fields.Char('Theme')
    isstainresistant_cloth = fields.Char('IsStainResistant')
    # numberofpieces_cloth = fields.Char('NumberOfPieces')
        
    #############################Gift Cards#############################33
    physicalgift_card = fields.Boolean('Physical Gift Cards')
    electronicgift_card = fields.Boolean('Electonic Gift Cards')
    itemdisplayheight_gift = fields.Char('ItemDisplayHeight')
    itemdisplaylength_gift = fields.Char('ItemDisplayLength')
    itemdisplayweight_gift = fields.Char('ItemDisplayWeight')
    itemdisplaywidth_gift = fields.Char('ItemDisplayWidth')
    # color_gift = fields.Char('Color')
    designname_gift = fields.Char('DesignName')
    format_gift = fields.Char('Format')
    genre_gift = fields.Char('Genre')
    # isadultproduct_gift = fields.Char('IsAdultProduct')
    occasiontype_gift = fields.Char('OccasionType')
    state_gift = fields.Char('State')


    targetgender_gift = fields.Selection([('male','male'),('female','female'),('unisex','unisex')],'TargetGender')
    # parentage_gift = fields.Selection([('parent','parent'),('child','child')],'Parentagevariation')
    # variationtheme_gift = fields.Selection([('Denomination','Denomination'),('Denomination-DesignName','Denomination-DesignName'),('StyleName','StyleName')],'VariationTheme')
    denomination_gift = fields.Char('Denomination')
    # stylename_gift = fields.Char('StyleName')


    #######################33Wireless###############################33

    wireless_accessory = fields.Boolean('Wireless Accessory')
    lithiumbatterypackaging_wire = fields.Selection([('batteries_contained_in_equipment','batteries_contained_in_equipment'),('batteries_only','batteries_only'),('batteries_packed_with_equipment','batteries_packed_with_equipment')],'LithiumBatteryPackaging')
#     variationdata_wire = fields.Selection([('parent','parent'),('child','child')],'VariationData')
    # variationtheme_wire = fields.Selection([('Color','Color')],'VariationTheme')
    # color_wire = fields.Char('Color')
    additionalfeatures_wire = fields.Char('AdditionalFeatures')
    solar_wire = fields.Boolean('Solar')
    refillable_wire = fields.Boolean('Refillable')
    extended_wire = fields.Boolean('Extended')
    slim_wire = fields.Boolean('Slim')
    auxiliary_wire = fields.Boolean('Auxiliary')
    batterytype_wire = fields.Char('BatteryType')
    antennatype_wire = fields.Char('AntennaType')
    manufacturername_wire = fields.Char('ManufacturerName')
    keywords_wire = fields.Char('Keywords')
    itempackagequantity_wire = fields.Char('ItemPackageQuantity')
    headsettype_wire = fields.Selection([('one-ear','one-ear'),('two-ear','two-ear')],'HeadsetType')
    headsetstyle_wire = fields.Selection([('over-the-ear','over-the-ear'),('behind-the-ear','behind-the-ear'),('in-the-ear','in-the-ear')],'HeadsetStyle')
    
    talk_time_wire = fields.Char('TalkTime')
    standby_time_wire = fields.Char('StandbyTime')
    charging_time_wire = fields.Char('ChargingTime')
    # batterypower_headphone
    compatible_phone_models_wire = fields.Char('CompatiblePhoneModels')
    prepaid_features_wire = fields.Char('PrepaidFeatures')
    phone_type_wire = fields.Char('PhoneType')
    phone_style_wire = fields.Char('PhoneStyle')
    # operatingsystem_gp
    # power_plug_type_hi
        
    ###############################wirelessDownloads#################3333
    wirelessdownloads_wire = fields.Boolean('WirelessDownloads')
    applicationversion_wire = fields.Char('ApplicationVersion')
        
    ##########################Toys AND games####################
    
    Flavor = fields.Char('Flavor')
    assembly_instructions_tg = fields.Char('AssemblyInstructions')
    assembly_time_tg = fields.Datetime('AssemblyTime')
    edition_tg = fields.Char('Edition')
    is_assembly_required_tg = fields.Boolean('IsAssemblyRequired')
    manufacturer_safety_warning_tg = fields.Char('ManufacturerSafetyWarning')
    weight_recommendation_tg = fields.Char('WeightRecommendation')
    number_of_players_tg = fields.Char('NumberOfPlayers')
    part_number_tg = fields.Char('PartNumber')
    size_map_tg = fields.Char('SizeMap')
    subject_character_tg = fields.Char('SubjectCharacter')
    isadultproduct_toys_tg = fields.Boolean('IsAdultProduct')

    engine_type_tg = fields.Char('EngineType')
    awards_won_tg = fields.Char('AwardsWon')
    color_map_tg = fields.Char('color_map')
    directions_tg = fields.Char('Directions')
    number_of_control_channels_tg = fields.Char('NumberOfControlChannels')
    frequency_bands_supported_tg = fields.Char('FrequencyBandsSupported')
    language_tg = fields.Char('language')
    includes_remote_tg = fields.Char('IncludesRemote')
    power_source_type_tg = fields.Char('PowerSourceType')
    recommended_use_tg = fields.Char('RecommendedUse')
    remote_control_technology_tg = fields.Char('RemoteControlTechnology')
    rail_gauge_tg = fields.Char('RailGauge')
    region_of_origin_tg = fields.Char('RegionOfOrigin')
    drive_system_tg = fields.Char('DriveSystem')
    fuel_capacity_tg = fields.Char('FuelCapacity')
    fuel_type_tg = fields.Char('FuelType')
    material_composition_tg = fields.Char('MaterialComposition')
    care_instructions_tg = fields.Char('CareInstructions')
    handle_height_tg = fields.Char('HandleHeight')
    seat_length_tg = fields.Char('SeatLength')
    seat_width_tg = fields.Char('SeatWidth')
    tire_material_tg = fields.Char('TireMaterial')
    tire_diameter_tg = fields.Char('TireDiameter')
    style_keywords_tg = fields.Char('StyleKeywords')
    warranty_description_tg = fields.Char('WarrantyDescription')
    scale_name_tg = fields.Char('ScaleName')
    specification_met_tg = fields.Boolean('SpecificationMet')

    specific_uses_for_product_tg = fields.Char('SpecificUsesForProduct')
    material_type_tg = fields.Char('MaterialType')

    active_surface_area_tg = fields.Char('ActiveSurfaceArea')
    wing_area_tg = fields.Char('WingArea')
    collection_name_tg = fields.Char('CollectionName')
    initial_print_run_rarity_tg = fields.Char('InitialPrintRunRarity')
    # specific_uses_for_product = fields.Char('specific_uses_for_product')
    brake_style_tg = fields.Char('BrakeStyle')
    drive_system_tg = fields.Char('DriveSystem')
    frame_material_type_tg = fields.Char('FrameMaterialType')
    fuel_capacity_tg = fields.Char('FuelCapacity')
    # fuel_type_tg = fields.Char('FuelType')
    maximum_range_tg = fields.Char('MaximumRange')
    maximum_speed_tg = fields.Char('MaximumSpeed')
    motor_type_tg = fields.Char('MotorType')
    display_size_tg = fields.Char('DisplaySize')
    display_type_tg = fields.Char('DisplayType')
    engine_displacement_tg = fields.Char('EngineDisplacement')
    liquid_volume_tg = fields.Char('LiquidVolume')
    movement_type_tg = fields.Char('MovementType')
    surface_recommendation_tg = fields.Char('SurfaceRecommendation')
    radio_bands_supported_tg = fields.Char('RadioBandsSupported')
    rail_type_tg = fields.Char('RailType')
    scale_tg = fields.Char('Scale')
    suspension_type_tg = fields.Char('SuspensionType')
    tire_type_tg = fields.Char('TireType')
    wheel_diameter_tg = fields.Char('WheelDiameter')
    wheel_type_tg = fields.Char('WheelType')

    collection_tg = fields.Char('Collection')
    rarity_tg = fields.Char('Rarity')
    card_number_tg = fields.Char('CardNumber')
    card_type_tg = fields.Char('CardType')

    educational_objective_tg = fields.Char('EducationalObjective')

    number_of_frequency_channels_tg = fields.Char('NumberOfFrequencyChannels')
    is_electric_tg = fields.Char('IsElectric')
    animal_type_tg = fields.Char('AnimalType')
    skill_level_tg = fields.Char('SkillLevel')
    toy_award_name_tg = fields.Char('ToyAwardName')
    publisher_contributor_tg = fields.Char('PublisherContributor')
    distribution_designation_tg = fields.Char('DistributionDesignation')
    country_string_tg = fields.Char('CountryString')


    # isfragile_toys = fields.Boolean('IsFragile')
    # IsSoldInStores = fields.Boolean('IsSoldInStores')
    # ItemPackageContents = fields.Char('ItemPackageContents')
    # ModelNumber = fields.Char('ModelNumber')    
    # StyleName = fields.Char('StyleName')
    # NumberOfPieces = fields.Char('NumberOfPieces')    
    # FabricType = fields.Char('FabricType')  
    # TargetGender = fields.Selection([('male','male'),('female','female'),('unisex','unisex')],'TargetGender')

#     VariationData_baby = fields.Selection([('parent','parent'),('child','child')],'VariationData')
    # VariationTheme_baby = fields.Selection([('Size','Size'),('Color','Color'),('Size-Color','Size-Color'),('Flavor','Flavor'),('CustomerPackageType','clothingCustomerPackageType'),('ColorName-CustomerPackageType','ColorName-CustomerPackageType'),('SizeName-CustomerPackageType','SizeName-CustomerPackageType'),('SizeName-ColorName-CustomerPackageType','SizeName-ColorName-CustomerPackageType'),('StyleName-CustomerPackageType','StyleName-CustomerPackageType'),('SizeName-StyleName-CustomerPackageType','SizeName-StyleName-CustomerPackageType')],'VariationTheme')
    # Size = fields.Char('Size')
    # Color = fields.Char('Color')
    
    # HazmatItem = fields.Char('HazmatItem')
    

#############################################################
    bulk_upload = fields.Boolean('Bulk Upload')
    home_1 = fields.Boolean('Home')
    beauty = fields.Boolean('Beauty')
    light_fixtures = fields.Boolean('Light Fixtures')
    light_accessory = fields.Boolean('Light Accessory')
    light_bulb = fields.Boolean('Light Bulb')
