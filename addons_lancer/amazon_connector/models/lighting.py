# -*- coding: utf-8 -*-
from odoo import fields, models

class UploadAmazonProducts(models.Model):
    _inherit='upload.amazon.products'
  
    variation_theme=fields.Selection([('Color','Color')],'VariationTheme')
    airflowcapacity=fields.Char('AirFlowCapacity')
    basediameter=fields.Char('BaseDiameter')
    battery=fields.Char('Battery')
    bulbdiameter=fields.Char('BulbDiameter')
    bulblength=fields.Char('BulbLength')
    bulblifespan=fields.Datetime('BulbLifeSpan')
    bulbpowerfactor=fields.Char('BulbPowerFactor')
    bulbspecialfeatures=fields.Text('BulbSpecialFeatures')
    bulbswitchingcycles=fields.Char('BulbSwitchingCycles')
    bulbtype=fields.Char('BulbType')
    bulbwattage=fields.Char('BulbWattage')
    captype=fields.Char('CapType')
    certification=fields.Char('Certification')
    collection=fields.Char('Collection')
    color=fields.Char('Color')
    energyefficiencyrating=fields.Char('EnergyEfficiencyRating')
    internationalprotectionrating=fields.Char('InternationalProtectionRating')
    itemdiameter=fields.Char('ItemDiameter')
    lightingmethod=fields.Char('LightingMethod')
    lithiumbatteryenergycontent=fields.Char('LithiumBatteryEnergyContent')
    lithiumbatterypackaging=fields.Selection([
                                ('batteries_contained_in_equipment','batteries_contained_in_equipment'),
                                ('batteries_only','batteries_only'),
                                ('batteries_packed_with_equipment','batteries_packed_with_equipment'),],  'LithiumBatteryPackaging')
    lithiumbatteryvoltage=fields.Char('LithiumBatteryVoltage')
    lithiumbatteryweight=fields.Char('LithiumBatteryWeight')
    material=fields.Char('Material')
    numberofblades=fields.Char('NumberOfBlades')
    numberofbulbsockets=fields.Char('NumberOfBulbSockets')
    plugtype=fields.Char('PlugType')
    powersource=fields.Char('PowerSource')
    specialfeatures=fields.Char('SpecialFeatures')
    specificuses=fields.Char('SpecificUses')
    stylename=fields.Char('StyleName')
    switchstyle=fields.Char('SwitchStyle')
    voltage=fields.Char('Voltage')
    volume=fields.Char('Volume')
    wattage=fields.Char('Wattage')
        