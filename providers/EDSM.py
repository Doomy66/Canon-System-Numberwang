import CSNSettings
from classes.Station import Station
from classes.State import State, Phase
from classes.System import System
from classes.Presense import Presence
from classes.Bubble import Bubble
from providers.EDDBFactions import isPlayer
import os
import datetime
import json
import requests
import gzip


def GetSystemsFromEDSM(faction: str, range=40) -> list[System]:
    """ Reads latest daily download of populated systems from EDSM and creates a list of System Objects \n
        If a Faction is supplied, the list is cut down to that Faction and others withing range ly Cube
    """
    edsmcache = os.environ.get('APPDATA')+"\CSN_EDSMPopulated.json"

    def RefreshCache(edsmcache) -> datetime:
        """ Checks Dates of Cache and API Data and downloads if required """
        EDSMPOPULATED = "https://www.edsm.net/dump/systemsPopulated.json.gz"
        cachedate: datetime.datetime = datetime.datetime.strptime(
            '2000-01-01', '%Y-%m-%d')

        # Get Modified Dates to check if it needs downloading again
        if os.path.exists(edsmcache):
            cachedate = datetime.datetime.fromtimestamp(
                os.path.getmtime(edsmcache))

        try:
            resp = requests.head(EDSMPOPULATED)
            lastmoddt = datetime.datetime.strptime(
                resp.headers._store['last-modified'][1], '%a, %d %b %Y %H:%M:%S %Z')
            # Needs to download fresh data
            if lastmoddt > cachedate:
                print('EDSM Downloading...')
                CSNSettings.CSNLog.info('EDSM Downloading...')

                resp = requests.get(EDSMPOPULATED).content
                resp = json.loads(gzip.decompress(resp))
                print('EDSM Saving...')
                CSNSettings.CSNLog.info('EDSM Saving...')
                with gzip.open(edsmcache, "w") as f:
                    f.write(json.dumps(resp).encode('utf-8'))
        except:
            CSNSettings.CSNLog.info('EDSM Offline !')
            print(f"EDSM Offline !")
        return lastmoddt

    def LoadCache(edsmcache) -> list:
        print('EDSM Loading...')
        with gzip.open(edsmcache, "r") as f:
            raw = json.loads(f.read().decode('utf-8'))
            CSNSettings.CSNLog.info('EDSM Loaded')
        return raw

    lastmoddt = RefreshCache(edsmcache)
    raw = LoadCache(edsmcache)

    print('EDSM Converting to DataClass...')
    CSNSettings.CSNLog.info('EDSM Converting to DataClass...')

    systemlist: list[System] = []
    for rs in raw:
        system = System('EDSM', id=rs['id'], id64=rs['id64'], name=rs['name'],
                        x=rs['coords']['x'], y=rs['coords']['y'], z=rs['coords']['z'], allegiance=rs['allegiance'], government=rs['government'], economy=rs[
            'economy'], security=rs['security'], population=rs['population'], controllingFaction=rs['controllingFaction']['name'], updated=lastmoddt
        )
        # Add Faction Presences
        if 'factions' in rs.keys():
            for rf in rs['factions']:
                if rf['influence'] > 0:
                    # EDSM seems to be a bad source for isPlayer, using EDDB Arcive
                    f = Presence(rf['id'], rf['name'], allegiance=rf['allegiance'], government=rf['government'],
                                 influence=round(100*rf['influence'], 2), happiness=rf['happiness'], isPlayer=isPlayer(rf['name']))
                    # Add States of Faction. NB States have very little information in EDSM, for Conflict days won etc you need EBGS data
                    for rstate in rf.get('activeStates', []):
                        f.states.append(
                            State(rstate['state'], phase=Phase.ACTIVE))
                    for rstate in rf.get('pendingStates', []):
                        f.states.append(
                            State(rstate['state'], phase=Phase.PENDING))
                    for rstate in rf.get('recoveringStates'):
                        f.states.append(
                            State(rstate['state'], phase=Phase.RECOVERING))

                    system.addfaction(f)
        if 'stations' in rs.keys():
            myStation: Station
            for station in rs['stations']:
                fname = station['controllingFaction']['name'] if 'controllingFaction' in station.keys(
                ) else station['type']
                myStation = Station(
                    station['id'], station['type'], station['name'], fname, station['economy'], station['secondEconomy'], station['haveMarket'], station['haveShipyard'], station['haveOutfitting'], station['otherServices'])
                system.stations.append(myStation)
        systemlist.append(system)

    # Reduce List to Empire and Systems within range (40 covers simple invasions, use 60 for extended invasions)
    if faction:
        empire = list(
            filter(lambda x: x.isfactionpresent(faction), systemlist))
        if empire:
            systemlist = list(filter(lambda x: min(
                map(lambda e: e.cube_distance(x), empire)) <= range, systemlist))
        else:
            print('! Faction Not Found, you have the whole bubble !')
    print(f'EDSM Converted to include {len(systemlist)} systems')
    CSNSettings.CSNLog.info(
        f'EDSM Converted to DataClass : {len(systemlist)} systems')
    return systemlist


if __name__ == '__main__':
    pass
    # Some Tests and Examples
    # myFactionName = os.environ.get('myfaction')
    # myBubble = Bubble(GetSystemsFromEDSM(myFactionName))

    # mySystemName = 'Khun'
    # mySystem: System = myBubble.getsystem(mySystemName)
    # print('System :', mySystem.name)

    # systems = myBubble.cube_systems(mySystem, exclude_presense=myFactionName)
    # print(
    #     f"Targets for {mySystemName} Via Bubble [{len(systems)}] {', '.join(x.name for x in systems)}")

    # systems = myBubble.faction_presence(myFactionName)
    # print(
    #     f"Faction Presence via Bubble for {myFactionName} [{len(systems)}] : {', '.join(x.name for x in systems)}")

    # print(f"Faction Native Status in Varati")
    # for f in myBubble.getsystem('Varati').factions:
    #     print(f" {f.name} - {f.isNative}")
