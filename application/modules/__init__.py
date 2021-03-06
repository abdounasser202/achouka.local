__author__ = 'wilrona'

from flask import request, render_template, flash, url_for, redirect, session, make_response, Response, jsonify
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from lib.flask_cache import Cache
from application import app
from ..decorators import login_required
from flask.ext.login import current_user
from ..decorators import roles_required, login_required

import hashlib
import calendar
import datetime


from google.appengine.api import urlfetch
import json

#import pour l'impression des ticket
from lib.reportlab.pdfgen import canvas
from lib.reportlab.lib.pagesizes import A5
from lib.reportlab.platypus.doctemplate import SimpleDocTemplate
from lib.reportlab.lib.units import cm

#ajoute des fonts dans mes pdfs
import os
import lib.reportlab

from lib.reportlab.platypus import Paragraph
from lib.reportlab.lib.styles import getSampleStyleSheet
from lib.reportlab.pdfbase import pdfmetrics
from lib.reportlab.pdfbase.ttfonts import TTFont
from lib.reportlab.lib.colors import black,white

from lib.reportlab.graphics.barcode import code39, createBarcodeDrawing

# Appel de l'ensemble des fonctions crees
from application import function

# variable pour la gestion automatique des dates en fonction des zones
from lib.pytz.gae import pytz

from itertools import groupby
from operator import itemgetter

date_age = {
    'min':7,
    'max':13
}

global_current_country = {
    "CM": "Cameroon",
    "NGN": "Nigeria",
    "GA": "Gabon"
}


global_role = {
    'admin': False,
    'manager_agency': False,
    'employee_POS': True,
    'employee_Boarding': True
}

global_agencytype = {
        1: 'Internal',
        2: 'Partnership agency',
        3: 'Coorporate'
}

global_nationality_contry = {
    'abkhazia' : 'Abkhazian',
    'afghanistan' : 'Afghan',
    'albania' : 'Albanian',
    'algeria' : 'Algerian',
    'american samoa' : 'American Samoan',
    'andorra' : 'Andorran',
    'angola' : 'Angolan',
    'anguilla' : 'Anguillan',
    'antigua and barbuda' : 'Antiguan/Barbudan',
    'argentina' : 'Argentinean',
    'armenia' : 'Armenian',
    'aruba' : 'Aruban',
    'australia' : 'Australian',
    'austria' : 'Austrian',
    'azerbaijan' : 'Azerbaijani',
    'bahamas' : 'Bahamian',
    'bahrain' : 'Bahraini',
    'bangladesh' : 'Bangladeshi',
    'barbados' : 'Barbadian',
    'belarus' : 'Belarusian',
    'belgium' : 'Belgian',
    'belize' : 'Belizean',
    'benin' : 'Beninese',
    'bermuda' : 'Bermudian',
    'bhutan' : 'Bhutanese',
    'bolivia' : 'Bolivian',
    'bosnia and herzegovina' : 'Bosnian/Herzegovinian',
    'botswana' : 'Motswana',
    'brazil' : 'Brazilian',
    'british virgin islands' : 'British Virgin Island',
    'brunei' : 'Bruneian',
    'bulgaria' : 'Bulgarian',
    'burkina fasoa' : 'Burkinabe',
    'burmab' : 'Burmese',
    'burundi' : 'Burundian',
    'cambodia' : 'Cambodian',
    'cameroon' : 'Cameroonian',
    'canada' : 'Canadian',
    'cape verde' : 'Cape Verdean',
    'cayman islands' : 'Caymanian',
    'central african republic' : 'Central African',
    'chad' : 'Chadian',
    'chile' : 'Chilean',
    'christmas island' : 'Christmas Island',
    'cocos (keeling) islands' : 'Cocos Island',
    'colombia' : 'Colombian',
    'comoros' : 'Comorian',
    'cook islands' : 'Cook Island',
    'costa rica' : 'Costa Rican',
    'croatia' : 'Croatian',
    'cuba' : 'Cuban',
    'cyprus' : 'Cypriot',
    'czech republic' : 'Czech',
    'cote d\'ivoire' : 'Ivorian',
    'dem. republic of the congo' : 'Congolese',
    'denmark' : 'Danish',
    'djibouti' : 'Djiboutian',
    'dominica' : 'Dominicand',
    'dominican republic' : 'Dominicane',
    'east timor' : 'Timorese',
    'ecuador' : 'Ecuadorian',
    'egypt' : 'Egyptian',
    'el salvador' : 'Salvadoran',
    'england' : 'English',
    'equatorial guinea' : 'Equatorial Guinean',
    'eritrea' : 'Eritrean',
    'estonia' : 'Estonian',
    'ethiopia' : 'Ethiopian',
    'falkland islands' : 'Falkland Island',
    'faroe islands' : 'Faroese',
    'fiji' : 'Fijian',
    'finland' : 'Finnish',
    'france' : 'French',
    'french guiana' : 'French Guianese',
    'french polynesia' : 'French Polynesian',
    'gabon' : 'Gabonese',
    'gambia' : 'Gambian',
    'georgia' : 'Georgian',
    'germany' : 'German',
    'ghana' : 'Ghanaian',
    'gibraltar' : 'Gibraltar',
    'great britain' : 'British',
    'greece' : 'Greek',
    'greenland' : 'Greenlandic',
    'grenada' : 'Grenadian',
    'guadeloupe' : 'Guadeloupe',
    'guam' : 'Guamanian',
    'guatemala' : 'Guatemalan',
    'guinea' : 'Guinean',
    'guinea-bissau' : 'Guinean',
    'guyana' : 'Guyanese',
    'haiti' : 'Haitian',
    'honduras' : 'Honduran',
    'hong kong' : 'Hongkongese',
    'hungary' : 'Hungarian',
    'iceland' : 'Icelandic',
    'india' : 'Indian',
    'indonesia' : 'Indonesian',
    'iran' : 'Iranian',
    'iraq' : 'Iraqi',
    'ireland' : 'Irish',
    'isle of man' : 'Manx',
    'israel' : 'Israeli',
    'italy' : 'Italian',
    'jamaica' : 'Jamaican',
    'japan' : 'Japanese',
    'jordan' : 'Jordanian',
    'kazakhstan' : 'Kazakh',
    'kenya' : 'Kenyan',
    'kiribati' : 'I-Kiribati',
    'kosovo' : 'Kosovar',
    'kuwait' : 'Kuwaiti',
    'kyrgyzstan' : 'Kyrgyzstani',
    'laos' : 'Laotian',
    'latvia' : 'Latvian',
    'lebanon' : 'Lebanese',
    'lesotho' : 'Basotho',
    'liberia' : 'Liberian',
    'libya' : 'Libyan',
    'liechtenstein' : 'Liechtenstein',
    'lithuania' : 'Lithuanian',
    'luxembourg' : 'Luxembourgish',
    'macau' : 'Macanese',
    'madagascar' : 'Malagasy',
    'malawi' : 'Malawian',
    'malaysia' : 'Malaysian',
    'maldives' : 'Maldivian',
    'mali' : 'Malian',
    'malta' : 'Maltese',
    'marshall islands' : 'Marshallese',
    'martinique' : 'Martiniquais',
    'mauritania' : 'Mauritanian',
    'mauritius' : 'Mauritian',
    'mayotte' : 'Mahoran',
    'mexico' : 'Mexican',
    'micronesia, federated states of' : 'Micronesian',
    'moldova' : 'Moldovan',
    'monaco' : 'Monegasque, Monacan',
    'mongolia' : 'Mongolian',
    'montenegro' : 'Montenegrin',
    'montserrat' : 'Montserratian',
    'morocco' : 'Moroccan',
    'mozambique' : 'Mozambican',
    'namibia' : 'Namibian',
    'nauru' : 'Nauruan',
    'nepal' : 'Nepali',
    'netherlands' : 'Dutch',
    'new caledonia' : 'New Caledonian',
    'new zealand' : 'New Zealand',
    'nicaragua' : 'Nicaraguan',
    'niger' : 'Nigerien',
    'nigeria' : 'Nigerian',
    'niue' : 'Niuean',
    'north korea' : 'North Korean',
    'northern ireland' : 'Northern Irish',
    'northern marianas' : 'Northern Marianan',
    'norway' : 'Norwegian',
    'oman' : 'Omani',
    'pakistan' : 'Pakistani',
    'palau' : 'Palauan',
    'palestine' : 'Palestinian',
    'panama' : 'Panamanian',
    'papua new guinea' : 'Papua New Guinean',
    'paraguay' : 'Paraguayan',
    'people\'s republic of china' : 'Chinese',
    'peru' : 'Peruvian',
    'philippines' : 'Filipino',
    'pitcairn island' : 'Pitcairn Island',
    'poland' : 'Polish',
    'portugal' : 'Portuguese',
    'puerto rico' : 'Puerto Rican',
    'qatar' : 'Qatari',
    'republic of china' : 'Chinese',
    'republic of ireland' : 'Irish',
    'republic of macedonia' : 'Macedonian',
    'republic of the congo' : 'Congolese',
    'romania' : 'Romanian',
    'russia' : 'Russian',
    'rwanda' : 'Rwandan',
    'reunion' : 'Reunionese',
    'saint-pierre and miquelon' : 'Saint-Pierrais/Miquelonnais',
    'samoa' : 'Samoan',
    'san marino' : 'Sammarinese',
    'saudi arabia' : 'Saudi Arabian',
    'scotland' : 'Scottish',
    'senegal' : 'Senegalese',
    'serbia' : 'Serbian',
    'seychelles' : 'Seychellois',
    'sierra leone' : 'Sierra Leonean',
    'singapore' : 'Singapore',
    'slovakia' : 'Slovak',
    'slovenia' : 'Slovenian',
    'solomon islands' : 'Solomon Island',
    'somalia' : 'Somalian',
    'south africa' : 'South African',
    'south korea' : 'South Korean',
    'south ossetia' : 'South Ossetian',
    'south sudan' : 'South Sudanese',
    'spain' : 'Spanish',
    'sri lanka' : 'Sri Lankan',
    'st. helena' : 'St. Helenian',
    'st. kitts and nevis' : 'Kittitian/Vincentian',
    'st. lucia' : 'St. Lucian',
    'st. vincent and the grenadines' : 'St. Vincentian',
    'sudan' : 'Sudanese',
    'surinam' : 'Surinamese',
    'swaziland' : 'Swazi',
    'sweden' : 'Swedish',
    'switzerland' : 'Swiss',
    'syria' : 'Syrian',
    'sao tome and principe' : 'Sao Tomean',
    'taiwan' : 'Taiwanese',
    'tajikistan' : 'Tajikistani',
    'tanzania' : 'Tanzanian',
    'thailand' : 'Thai',
    'togo' : 'Togolese',
    'tonga' : 'Tongan',
    'trinidad and tobago' : 'Trinidadian',
    'tunisia' : 'Tunisian',
    'turkey' : 'Turkish',
    'turkmenistan' : 'Turkmen',
    'turks and caicos islands' : 'none',
    'tuvalu' : 'Tuvaluan',
    'uganda' : 'Ugandan',
    'ukraine' : 'Ukrainian',
    'united arab emirates' : 'Emirati',
    'united kingdom' : 'British',
    'united states' : 'American',
    'uruguay' : 'Uruguayan',
    'uzbekistan' : 'Uzbekistani',
    'vanuatu' : 'Ni-Vanuatu',
    'venezuela' : 'Venezuelan',
    'vietnam' : 'Vietnamese',
    'virgin islands' : 'Virgin Island',
    'wales' : 'Welsh',
    'wallis and futuna' : 'Wallisian/Futunan',
    'western sahara' : 'Sahrawian',
    'yemen' : 'Yemeni',
    'zambia' : 'Zambian',
    'zimbabwe' : 'Zimbabwean'
}

global_list_country = {
    "AF":"Afghanistan",
    "AL":"Albania",
    "DZ":"Algeria",
    "AS":"American Samoa",
    "AD":"Andorra",
    "AO":"Angola",
    "AI":"Anguilla",
    "AQ":"Antarctica",
    "AG":"Antigua and Barbuda",
    "AR":"Argentina",
    "AM":"Armenia",
    "AW":"Aruba",
    "AU":"Australia",
    "AT":"Austria",
    "AZ":"Azerbaijan",
    "BS":"Bahamas",
    "BH":"Bahrain",
    "BD":"Bangladesh",
    "BB":"Barbados",
    "BY":"Belarus",
    "BE":"Belgium",
    "BZ":"Belize",
    "BJ":"Benin",
    "BM":"Bermuda",
    "BT":"Bhutan",
    "BO":"Bolivia",
    "BA":"Bosnia and Herzegovina",
    "BW":"Botswana",
    "BV":"Bouvet Island",
    "BR":"Brazil",
    "BQ":"British Antarctic Territory",
    "IO":"British Indian Ocean Territory",
    "VG":"British Virgin Islands",
    "BN":"Brunei",
    "BG":"Bulgaria",
    "BF":"Burkina Faso",
    "BI":"Burundi",
    "KH":"Cambodia",
    "CM":"Cameroon",
    "CA":"Canada",
    "CT":"Canton and Enderbury Islands",
    "CV":"Cape Verde",
    "KY":"Cayman Islands",
    "CF":"Central African Republic",
    "TD":"Chad",
    "CL":"Chile",
    "CN":"China",
    "CX":"Christmas Island",
    "CC":"Cocos [Keeling] Islands",
    "CO":"Colombia",
    "KM":"Comoros",
    "CG":"Congo - Brazzaville",
    "CD":"Congo - Kinshasa",
    "CK":"Cook Islands",
    "CR":"Costa Rica",
    "HR":"Croatia",
    "CU":"Cuba",
    "CY":"Cyprus",
    "CZ":"Czech Republic",
    "CI":"C\u00f4te d\u2019Ivoire",
    "DK":"Denmark",
    "DJ":"Djibouti",
    "DM":"Dominica",
    "DO":"Dominican Republic",
    "NQ":"Dronning Maud Land",
    "DD":"East Germany",
    "EC":"Ecuador",
    "EG":"Egypt",
    "SV":"El Salvador",
    "GQ":"Equatorial Guinea",
    "ER":"Eritrea",
    "EE":"Estonia",
    "ET":"Ethiopia",
    "FK":"Falkland Islands",
    "FO":"Faroe Islands",
    "FJ":"Fiji",
    "FI":"Finland",
    "FR":"France",
    "GF":"French Guiana",
    "PF":"French Polynesia",
    "TF":"French Southern Territories",
    "FQ":"French Southern and Antarctic Territories",
    "GA":"Gabon",
    "GM":"Gambia",
    "GE":"Georgia",
    "DE":"Germany",
    "GH":"Ghana",
    "GI":"Gibraltar",
    "GR":"Greece",
    "GL":"Greenland",
    "GD":"Grenada",
    "GP":"Guadeloupe",
    "GU":"Guam",
    "GT":"Guatemala",
    "GG":"Guernsey",
    "GN":"Guinea",
    "GW":"Guinea-Bissau",
    "GY":"Guyana",
    "HT":"Haiti",
    "HM":"Heard Island and McDonald Islands",
    "HN":"Honduras",
    "HK":"Hong Kong SAR China",
    "HU":"Hungary",
    "IS":"Iceland",
    "IN":"India",
    "ID":"Indonesia",
    "IR":"Iran",
    "IQ":"Iraq",
    "IE":"Ireland",
    "IM":"Isle of Man",
    "IL":"Israel",
    "IT":"Italy",
    "JM":"Jamaica",
    "JP":"Japan",
    "JE":"Jersey",
    "JT":"Johnston Island",
    "JO":"Jordan",
    "KZ":"Kazakhstan",
    "KE":"Kenya",
    "KI":"Kiribati",
    "KW":"Kuwait",
    "KG":"Kyrgyzstan",
    "LA":"Laos",
    "LV":"Latvia",
    "LB":"Lebanon",
    "LS":"Lesotho",
    "LR":"Liberia",
    "LY":"Libya",
    "LI":"Liechtenstein",
    "LT":"Lithuania",
    "LU":"Luxembourg",
    "MO":"Macau SAR China",
    "MK":"Macedonia",
    "MG":"Madagascar",
    "MW":"Malawi",
    "MY":"Malaysia",
    "MV":"Maldives",
    "ML":"Mali",
    "MT":"Malta",
    "MH":"Marshall Islands",
    "MQ":"Martinique",
    "MR":"Mauritania",
    "MU":"Mauritius",
    "YT":"Mayotte",
    "FX":"Metropolitan France",
    "MX":"Mexico",
    "FM":"Micronesia",
    "MI":"Midway Islands",
    "MD":"Moldova",
    "MC":"Monaco",
    "MN":"Mongolia",
    "ME":"Montenegro",
    "MS":"Montserrat",
    "MA":"Morocco",
    "MZ":"Mozambique",
    "MM":"Myanmar [Burma]",
    "NA":"Namibia",
    "NR":"Nauru",
    "NP":"Nepal",
    "NL":"Netherlands",
    "AN":"Netherlands Antilles",
    "NT":"Neutral Zone",
    "NC":"New Caledonia",
    "NZ":"New Zealand",
    "NI":"Nicaragua",
    "NE":"Niger",
    "NG":"Nigeria",
    "NU":"Niue",
    "NF":"Norfolk Island",
    "KP":"North Korea",
    "VD":"North Vietnam",
    "MP":"Northern Mariana Islands",
    "NO":"Norway",
    "OM":"Oman",
    "PC":"Pacific Islands Trust Territory",
    "PK":"Pakistan",
    "PW":"Palau",
    "PS":"Palestinian Territories",
    "PA":"Panama",
    "PZ":"Panama Canal Zone",
    "PG":"Papua New Guinea",
    "PY":"Paraguay",
    "YD":"People's Democratic Republic of Yemen",
    "PE":"Peru",
    "PH":"Philippines",
    "PN":"Pitcairn Islands",
    "PL":"Poland",
    "PT":"Portugal",
    "PR":"Puerto Rico",
    "QA":"Qatar",
    "RO":"Romania",
    "RU":"Russia",
    "RW":"Rwanda",
    "RE":"R\u00e9union",
    "BL":"Saint Barth\u00e9lemy",
    "SH":"Saint Helena",
    "KN":"Saint Kitts and Nevis",
    "LC":"Saint Lucia",
    "MF":"Saint Martin",
    "PM":"Saint Pierre and Miquelon",
    "VC":"Saint Vincent and the Grenadines",
    "WS":"Samoa",
    "SM":"San Marino",
    "SA":"Saudi Arabia",
    "SN":"Senegal",
    "RS":"Serbia",
    "CS":"Serbia and Montenegro",
    "SC":"Seychelles",
    "SL":"Sierra Leone",
    "SG":"Singapore",
    "SK":"Slovakia",
    "SI":"Slovenia",
    "SB":"Solomon Islands",
    "SO":"Somalia",
    "ZA":"South Africa",
    "GS":"South Georgia and the South Sandwich Islands",
    "KR":"South Korea",
    "ES":"Spain",
    "LK":"Sri Lanka",
    "SD":"Sudan",
    "SR":"Suriname",
    "SJ":"Svalbard and Jan Mayen",
    "SZ":"Swaziland",
    "SE":"Sweden",
    "CH":"Switzerland",
    "SY":"Syria",
    "ST":"S\u00e3o Tom\u00e9 and Pr\u00edncipe",
    "TW":"Taiwan",
    "TJ":"Tajikistan",
    "TZ":"Tanzania",
    "TH":"Thailand",
    "TL":"Timor-Leste",
    "TG":"Togo",
    "TK":"Tokelau",
    "TO":"Tonga",
    "TT":"Trinidad and Tobago",
    "TN":"Tunisia",
    "TR":"Turkey",
    "TM":"Turkmenistan",
    "TC":"Turks and Caicos Islands",
    "TV":"Tuvalu",
    "UM":"U.S. Minor Outlying Islands",
    "PU":"U.S. Miscellaneous Pacific Islands",
    "VI":"U.S. Virgin Islands",
    "UG":"Uganda",
    "UA":"Ukraine",
    "SU":"Union of Soviet Socialist Republics",
    "AE":"United Arab Emirates",
    "GB":"United Kingdom",
    "US":"United States",
    "ZZ":"Unknown or Invalid Region",
    "UY":"Uruguay",
    "UZ":"Uzbekistan",
    "VU":"Vanuatu",
    "VA":"Vatican City",
    "VE":"Venezuela",
    "VN":"Vietnam",
    "WK":"Wake Island",
    "WF":"Wallis and Futuna",
    "EH":"Western Sahara",
    "YE":"Yemen",
    "ZM":"Zambia",
    "ZW":"Zimbabwe",
    "AX":"\u00c5land Islands"
}

global_dial_code = [
    {"name":"Israel","dial_code":"+972","code":"IL"},
    {"name":"Afghanistan","dial_code":"+93","code":"AF"},
    {"name":"Albania","dial_code":"+355","code":"AL"},
    {"name":"Algeria","dial_code":"+213","code":"DZ"},
    {"name":"AmericanSamoa","dial_code":"+1 684","code":"AS"},
    {"name":"Andorra","dial_code":"+376","code":"AD"},
    {"name":"Angola","dial_code":"+244","code":"AO"},
    {"name":"Anguilla","dial_code":"+1 264","code":"AI"},
    {"name":"Antigua and Barbuda","dial_code":"+1268","code":"AG"},
    {"name":"Argentina","dial_code":"+54","code":"AR"},
    {"name":"Armenia","dial_code":"+374","code":"AM"},
    {"name":"Aruba","dial_code":"+297","code":"AW"},
    {"name":"Australia","dial_code":"+61","code":"AU"},
    {"name":"Austria","dial_code":"+43","code":"AT"},
    {"name":"Azerbaijan","dial_code":"+994","code":"AZ"},
    {"name":"Bahamas","dial_code":"+1 242","code":"BS"},
    {"name":"Bahrain","dial_code":"+973","code":"BH"},
    {"name":"Bangladesh","dial_code":"+880","code":"BD"},
    {"name":"Barbados","dial_code":"+1 246","code":"BB"},
    {"name":"Belarus","dial_code":"+375","code":"BY"},
    {"name":"Belgium","dial_code":"+32","code":"BE"},
    {"name":"Belize","dial_code":"+501","code":"BZ"},
    {"name":"Benin","dial_code":"+229","code":"BJ"},
    {"name":"Bermuda","dial_code":"+1 441","code":"BM"},
    {"name":"Bhutan","dial_code":"+975","code":"BT"},
    {"name":"Bosnia and Herzegovina","dial_code":"+387","code":"BA"},
    {"name":"Botswana","dial_code":"+267","code":"BW"},
    {"name":"Brazil","dial_code":"+55","code":"BR"},
    {"name":"British Indian Ocean Territory","dial_code":"+246","code":"IO"},
    {"name":"Bulgaria","dial_code":"+359","code":"BG"},
    {"name":"Burkina Faso","dial_code":"+226","code":"BF"},
    {"name":"Burundi","dial_code":"+257","code":"BI"},
    {"name":"Cambodia","dial_code":"+855","code":"KH"},
    {"name":"Cameroon","dial_code":"+237","code":"CM"},
    {"name":"Canada","dial_code":"+1","code":"CA"},
    {"name":"Cape Verde","dial_code":"+238","code":"CV"},
    {"name":"Cayman Islands","dial_code":"+ 345","code":"KY"},
    {"name":"Central African Republic","dial_code":"+236","code":"CF"},
    {"name":"Chad","dial_code":"+235","code":"TD"},
    {"name":"Chile","dial_code":"+56","code":"CL"},
    {"name":"China","dial_code":"+86","code":"CN"},
    {"name":"Christmas Island","dial_code":"+61","code":"CX"},
    {"name":"Colombia","dial_code":"+57","code":"CO"},
    {"name":"Comoros","dial_code":"+269","code":"KM"},
    {"name":"Congo","dial_code":"+242","code":"CG"},
    {"name":"Cook Islands","dial_code":"+682","code":"CK"},
    {"name":"Costa Rica","dial_code":"+506","code":"CR"},
    {"name":"Croatia","dial_code":"+385","code":"HR"},
    {"name":"Cuba","dial_code":"+53","code":"CU"},
    {"name":"Cyprus","dial_code":"+537","code":"CY"},
    {"name":"Czech Republic","dial_code":"+420","code":"CZ"},
    {"name":"Denmark","dial_code":"+45","code":"DK"},
    {"name":"Djibouti","dial_code":"+253","code":"DJ"},
    {"name":"Dominica","dial_code":"+1 767","code":"DM"},
    {"name":"Dominican Republic","dial_code":"+1 849","code":"DO"},
    {"name":"Ecuador","dial_code":"+593","code":"EC"},
    {"name":"Egypt","dial_code":"+20","code":"EG"},
    {"name":"El Salvador","dial_code":"+503","code":"SV"},
    {"name":"Equatorial Guinea","dial_code":"+240","code":"GQ"},
    {"name":"Eritrea","dial_code":"+291","code":"ER"},
    {"name":"Estonia","dial_code":"+372","code":"EE"},
    {"name":"Ethiopia","dial_code":"+251","code":"ET"},
    {"name":"Faroe Islands","dial_code":"+298","code":"FO"},
    {"name":"Fiji","dial_code":"+679","code":"FJ"},
    {"name":"Finland","dial_code":"+358","code":"FI"},
    {"name":"France","dial_code":"+33","code":"FR"},
    {"name":"French Guiana","dial_code":"+594","code":"GF"},
    {"name":"French Polynesia","dial_code":"+689","code":"PF"},
    {"name":"Gabon","dial_code":"+241","code":"GA"},
    {"name":"Gambia","dial_code":"+220","code":"GM"},
    {"name":"Georgia","dial_code":"+995","code":"GE"},
    {"name":"Germany","dial_code":"+49","code":"DE"},
    {"name":"Ghana","dial_code":"+233","code":"GH"},
    {"name":"Gibraltar","dial_code":"+350","code":"GI"},
    {"name":"Greece","dial_code":"+30","code":"GR"},
    {"name":"Greenland","dial_code":"+299","code":"GL"},
    {"name":"Grenada","dial_code":"+1 473","code":"GD"},
    {"name":"Guadeloupe","dial_code":"+590","code":"GP"},
    {"name":"Guam","dial_code":"+1 671","code":"GU"},
    {"name":"Guatemala","dial_code":"+502","code":"GT"},
    {"name":"Guinea","dial_code":"+224","code":"GN"},
    {"name":"Guinea-Bissau","dial_code":"+245","code":"GW"},
    {"name":"Guyana","dial_code":"+595","code":"GY"},
    {"name":"Haiti","dial_code":"+509","code":"HT"},
    {"name":"Honduras","dial_code":"+504","code":"HN"},
    {"name":"Hungary","dial_code":"+36","code":"HU"},
    {"name":"Iceland","dial_code":"+354","code":"IS"},
    {"name":"India","dial_code":"+91","code":"IN"},
    {"name":"Indonesia","dial_code":"+62","code":"ID"},
    {"name":"Iraq","dial_code":"+964","code":"IQ"},
    {"name":"Ireland","dial_code":"+353","code":"IE"},
    {"name":"Israel","dial_code":"+972","code":"IL"},
    {"name":"Italy","dial_code":"+39","code":"IT"},
    {"name":"Jamaica","dial_code":"+1 876","code":"JM"},
    {"name":"Japan","dial_code":"+81","code":"JP"},
    {"name":"Jordan","dial_code":"+962","code":"JO"},
    {"name":"Kazakhstan","dial_code":"+7 7","code":"KZ"},
    {"name":"Kenya","dial_code":"+254","code":"KE"},
    {"name":"Kiribati","dial_code":"+686","code":"KI"},
    {"name":"Kuwait","dial_code":"+965","code":"KW"},
    {"name":"Kyrgyzstan","dial_code":"+996","code":"KG"},
    {"name":"Latvia","dial_code":"+371","code":"LV"},
    {"name":"Lebanon","dial_code":"+961","code":"LB"},
    {"name":"Lesotho","dial_code":"+266","code":"LS"},
    {"name":"Liberia","dial_code":"+231","code":"LR"},
    {"name":"Liechtenstein","dial_code":"+423","code":"LI"},
    {"name":"Lithuania","dial_code":"+370","code":"LT"},
    {"name":"Luxembourg","dial_code":"+352","code":"LU"},
    {"name":"Madagascar","dial_code":"+261","code":"MG"},
    {"name":"Malawi","dial_code":"+265","code":"MW"},
    {"name":"Malaysia","dial_code":"+60","code":"MY"},
    {"name":"Maldives","dial_code":"+960","code":"MV"},
    {"name":"Mali","dial_code":"+223","code":"ML"},
    {"name":"Malta","dial_code":"+356","code":"MT"},
    {"name":"Marshall Islands","dial_code":"+692","code":"MH"},
    {"name":"Martinique","dial_code":"+596","code":"MQ"},
    {"name":"Mauritania","dial_code":"+222","code":"MR"},
    {"name":"Mauritius","dial_code":"+230","code":"MU"},
    {"name":"Mayotte","dial_code":"+262","code":"YT"},
    {"name":"Mexico","dial_code":"+52","code":"MX"},
    {"name":"Monaco","dial_code":"+377","code":"MC"},
    {"name":"Mongolia","dial_code":"+976","code":"MN"},
    {"name":"Montenegro","dial_code":"+382","code":"ME"},
    {"name":"Montserrat","dial_code":"+1664","code":"MS"},
    {"name":"Morocco","dial_code":"+212","code":"MA"},
    {"name":"Myanmar","dial_code":"+95","code":"MM"},
    {"name":"Namibia","dial_code":"+264","code":"NA"},
    {"name":"Nauru","dial_code":"+674","code":"NR"},
    {"name":"Nepal","dial_code":"+977","code":"NP"},
    {"name":"Netherlands","dial_code":"+31","code":"NL"},
    {"name":"Netherlands Antilles","dial_code":"+599","code":"AN"},
    {"name":"New Caledonia","dial_code":"+687","code":"NC"},
    {"name":"New Zealand","dial_code":"+64","code":"NZ"},
    {"name":"Nicaragua","dial_code":"+505","code":"NI"},
    {"name":"Niger","dial_code":"+227","code":"NE"},
    {"name":"Nigeria","dial_code":"+234","code":"NG"},
    {"name":"Niue","dial_code":"+683","code":"NU"},
    {"name":"Norfolk Island","dial_code":"+672","code":"NF"},
    {"name":"Northern Mariana Islands","dial_code":"+1 670","code":"MP"},
    {"name":"Norway","dial_code":"+47","code":"NO"},
    {"name":"Oman","dial_code":"+968","code":"OM"},
    {"name":"Pakistan","dial_code":"+92","code":"PK"},
    {"name":"Palau","dial_code":"+680","code":"PW"},
    {"name":"Panama","dial_code":"+507","code":"PA"},
    {"name":"Papua New Guinea","dial_code":"+675","code":"PG"},
    {"name":"Paraguay","dial_code":"+595","code":"PY"},
    {"name":"Peru","dial_code":"+51","code":"PE"},
    {"name":"Philippines","dial_code":"+63","code":"PH"},
    {"name":"Poland","dial_code":"+48","code":"PL"},
    {"name":"Portugal","dial_code":"+351","code":"PT"},
    {"name":"Puerto Rico","dial_code":"+1 939","code":"PR"},
    {"name":"Qatar","dial_code":"+974","code":"QA"},
    {"name":"Romania","dial_code":"+40","code":"RO"},
    {"name":"Rwanda","dial_code":"+250","code":"RW"},
    {"name":"Samoa","dial_code":"+685","code":"WS"},
    {"name":"San Marino","dial_code":"+378","code":"SM"},
    {"name":"Saudi Arabia","dial_code":"+966","code":"SA"},
    {"name":"Senegal","dial_code":"+221","code":"SN"},
    {"name":"Serbia","dial_code":"+381","code":"RS"},
    {"name":"Seychelles","dial_code":"+248","code":"SC"},
    {"name":"Sierra Leone","dial_code":"+232","code":"SL"},
    {"name":"Singapore","dial_code":"+65","code":"SG"},
    {"name":"Slovakia","dial_code":"+421","code":"SK"},
    {"name":"Slovenia","dial_code":"+386","code":"SI"},
    {"name":"Solomon Islands","dial_code":"+677","code":"SB"},
    {"name":"South Africa","dial_code":"+27","code":"ZA"},
    {"name":"South Georgia and the South Sandwich Islands","dial_code":"+500","code":"GS"},
    {"name":"Spain","dial_code":"+34","code":"ES"},
    {"name":"Sri Lanka","dial_code":"+94","code":"LK"},
    {"name":"Sudan","dial_code":"+249","code":"SD"},
    {"name":"Suriname","dial_code":"+597","code":"SR"},
    {"name":"Swaziland","dial_code":"+268","code":"SZ"},
    {"name":"Sweden","dial_code":"+46","code":"SE"},
    {"name":"Switzerland","dial_code":"+41","code":"CH"},
    {"name":"Tajikistan","dial_code":"+992","code":"TJ"},
    {"name":"Thailand","dial_code":"+66","code":"TH"},
    {"name":"Togo","dial_code":"+228","code":"TG"},
    {"name":"Tokelau","dial_code":"+690","code":"TK"},
    {"name":"Tonga","dial_code":"+676","code":"TO"},
    {"name":"Trinidad and Tobago","dial_code":"+1 868","code":"TT"},
    {"name":"Tunisia","dial_code":"+216","code":"TN"},
    {"name":"Turkey","dial_code":"+90","code":"TR"},
    {"name":"Turkmenistan","dial_code":"+993","code":"TM"},
    {"name":"Turks and Caicos Islands","dial_code":"+1 649","code":"TC"},
    {"name":"Tuvalu","dial_code":"+688","code":"TV"},
    {"name":"Uganda","dial_code":"+256","code":"UG"},
    {"name":"Ukraine","dial_code":"+380","code":"UA"},
    {"name":"United Arab Emirates","dial_code":"+971","code":"AE"},
    {"name":"United Kingdom","dial_code":"+44","code":"GB"},
    {"name":"United States","dial_code":"+1","code":"US"},
    {"name":"Uruguay","dial_code":"+598","code":"UY"},
    {"name":"Uzbekistan","dial_code":"+998","code":"UZ"},
    {"name":"Vanuatu","dial_code":"+678","code":"VU"},
    {"name":"Wallis and Futuna","dial_code":"+681","code":"WF"},
    {"name":"Yemen","dial_code":"+967","code":"YE"},
    {"name":"Zambia","dial_code":"+260","code":"ZM"},
    {"name":"Zimbabwe","dial_code":"+263","code":"ZW"},
    {"name":"Antarctica","dial_code": " ","code":"AQ"},
    {"name":"Plurinational State of Bolivia","dial_code":"+591","code":"BO"},
    {"name":"Brunei Darussalam","dial_code":"+673","code":"BN"},
    {"name":"Cocos (Keeling) Islands","dial_code":"+61","code":"CC"},
    {"name":"Democratic Republic of Congo","dial_code":"+243","code":"CD"},
    {"name":"Cote d'Ivoire","dial_code":"+225","code":"CI"},
    {"name":"Falkland Islands (Malvinas)","dial_code":"+500","code":"FK"},
    {"name":"Guernsey","dial_code":"+44","code":"GG"},
    {"name":"Holy See (Vatican City State)","dial_code":"+379","code":"VA"},
    {"name":"Hong Kong","dial_code":"+852","code":"HK"},
    {"name":"Iran, Islamic Republic of","dial_code":"+98","code":"IR"},
    {"name":"Isle of Man","dial_code":"+44","code":"IM"},
    {"name":"Jersey","dial_code":"+44","code":"JE"},
    {"name":"Korea, Democratic People's Republic of","dial_code":"+850","code":"KP"},
    {"name":"Korea, Republic of","dial_code":"+82","code":"KR"},
    {"name":"Lao People's Democratic Republic","dial_code":"+856","code":"LA"},
    {"name":"Libyan Arab Jamahiriya","dial_code":"+218","code":"LY"},
    {"name":"Macao","dial_code":"+853","code":"MO"},
    {"name":"Former Yugoslav Republic of Macedonia","dial_code":"+389","code":"MK"},
    {"name":"Federated States of Micronesia","dial_code":"+691","code":"FM"},
    {"name":"Moldova, Republic of","dial_code":"+373","code":"MD"},
    {"name":"Mozambique","dial_code":"+258","code":"MZ"},
    {"name":"Palestinian Territory, Occupied","dial_code":"+970","code":"PS"},
    {"name":"Pitcairn","dial_code":"+872","code":"PN"},
    {"name":"Reunion","dial_code":"+262","code":"RE"},
    {"name":"Russia","dial_code":"+7","code":"RU"},
    {"name":"Saint Barthelemy","dial_code":"+590","code":"BL"},
    {"name":"Saint Helena, Ascension and Tristan Da Cunha","dial_code":"+290","code":"SH"},
    {"name":"Saint Kitts and Nevis","dial_code":"+1 869","code":"KN"},
    {"name":"Saint Lucia","dial_code":"+1 758","code":"LC"},
    {"name":"Saint Martin","dial_code":"+590","code":"MF"},
    {"name":"Saint Pierre and Miquelon","dial_code":"+508","code":"PM"},
    {"name":"Saint Vincent and the Grenadines","dial_code":"+1 784","code":"VC"},
    {"name":"Sao Tome and Principe","dial_code":"+239","code":"ST"},
    {"name":"Somalia","dial_code":"+252","code":"SO"},
    {"name":"Svalbard and Jan Mayen","dial_code":"+47","code":"SJ"},
    {"name":"Syrian Arab Republic","dial_code":"+963","code":"SY"},
    {"name":"Taiwan, Province of China","dial_code":"+886","code":"TW"},
    {"name":"Tanzania, United Republic of","dial_code":"+255","code":"TZ"},
    {"name":"Timor-Leste","dial_code":"+670","code":"TL"},
    {"name":"Venezuela, Bolivarian Republic of","dial_code":"+58","code":"VE"},
    {"name":"Viet Nam","dial_code":"+84","code":"VN"},
    {"name":"Virgin Islands, British","dial_code":"+1 284","code":"VG"},
    {"name":"Virgin Islands, U.S.","dial_code":"+1 340","code":"VI"}
]

global_dial_code_custom = {}
key_dial_code = None

for element in global_dial_code:
    for k, v in element.items():
        if k != "code" and k != "dial_code":
            global_dial_code_custom[v] = None
            key_dial_code = v
            continue
    for k, v in element.items():
        if k == "dial_code":
            global_dial_code_custom[key_dial_code] = v
            continue