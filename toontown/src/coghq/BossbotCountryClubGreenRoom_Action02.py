from toontown.coghq.SpecImports import *

GlobalEntities = {
    # LEVELMGR
    1000: {
        'type': 'levelMgr',
        'name': 'LevelMgr',
        'comment': '',
        'parentEntId': 0,
        'cogLevel': 0,
        'farPlaneDistance': 1500,
        'modelFilename': 'phase_12/models/bossbotHQ/BossbotGreenRoom_A',
        'wantDoors': 1,
        }, # end entity 1000
    # EDITMGR
    1001: {
        'type': 'editMgr',
        'name': 'EditMgr',
        'parentEntId': 0,
        'insertEntity': None,
        'removeEntity': None,
        'requestNewEntity': None,
        'requestSave': None,
        }, # end entity 1001
    # ZONE
    0: {
        'type': 'zone',
        'name': 'UberZone',
        'comment': '',
        'parentEntId': 0,
        'scale': 1,
        'description': '',
        'visibility': [],
        }, # end entity 0
    # DOOR
    110301: {
        'type': 'door',
        'name': '<unnamed>',
        'comment': '',
        'parentEntId': 110303,
        'pos': Point3(0, 0, 0),
        'hpr': Vec3(0, 0, 0),
        'scale': 1,
        'color': Vec4(1, 1, 1, 1),
        'isLock0Unlocked': 1,
        'isLock1Unlocked': 0,
        'isLock2Unlocked': 1,
        'isLock3Unlocked': 1,
        'isOpen': 0,
        'isOpenEvent': 0,
        'isVisBlocker': 0,
        'secondsOpen': 1,
        'unlock0Event': 0,
        'unlock1Event': 110302,
        'unlock2Event': 0,
        'unlock3Event': 0,
        }, # end entity 110301
    # GOLFGREENGAME
    110302: {
        'type': 'golfGreenGame',
        'name': '<unnamed>',
        'comment': '',
        'parentEntId': 0,
        'pos': Point3(0, 0, 0),
        'hpr': Vec3(0, 0, 0),
        'scale': 1,
        'puzzleBase': 3,
        'puzzlePerPlayer': 3,
        'timeToPlay': 180,
        'cellId': 0,
        'switchId': 0,
        }, # end entity 100000
    # NODEPATH
    10002: {
        'type': 'nodepath',
        'name': 'props',
        'comment': '',
        'parentEntId': 0,
        'pos': Point3(0, 0, 0),
        'hpr': Vec3(0, 0, 0),
        'scale': 1,
        }, # end entity 10002
    110303: {
        'type': 'nodepath',
        'name': '<unnamed>',
        'comment': '',
        'parentEntId': 0,
        'pos': Point3(40.9635, 2, 0),
        'hpr': Vec3(270, 0, 0),
        'scale': Vec3(1, 1, 1),
        }, # end entity 110303
    }

Scenario0 = {
    }

levelSpec = {
    'globalEntities': GlobalEntities,
    'scenarios': [
        Scenario0,
        ],
    }
