try:
    import Keys_Canonn as keys # This file only available to authorised CSN Developers
except:
    import Keys_Client as keys # Populate this file with your settings


#Canonn Discord
wh_id = keys.wh_id
wh_token = keys.wh_token

#Canonn Google Sheet
override_workbook = keys.override_workbook
override_sheet = keys.override_sheet

#factionnames = ['Canonn','Canonn Deep Space Research']
factionnames = ['Canonn']
extendedphase = False

# Player Factions to treat as NPCs, either because they are inactive or other reasons
ignorepf = ['The Digiel Aggregate','Eternal Sunrise Association','Interstellar Incorporated','Lagrange Interstellar','FDMA Security Service', 'Wings Of Justice', "Marquis du Ma'a"]

# No orders to boost inf for system control etc. Leave it to the system owner.
surrendered_systems = ['A List of System Names'] 

import logging
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR) # Else get spurious warnings

logging.basicConfig(filename='data\CSNLog.log',
                    filemode='a',
                    format='%(asctime)s %(name)s %(levelname)s %(message)s',
                    level=logging.INFO)


CSNLog = logging.getLogger('CSN')
CSNLog.info('Logging Configured')