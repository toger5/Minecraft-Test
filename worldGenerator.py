import bge
from bge import logic as l
from random import randint
#import noise
import mathutils
import time
scene = l.getCurrentScene()
print(time.clock())
#builded = {}
MAP_HEIGHT = 40
wg = l.getCurrentController().owner
wg["blocknames"] = []
wg["voxel"] = {}
wg["blocks"] = {}
wg["needToBuild"] = []
wg["needToDel"] = []
wg["size"] = 21


scene.world.mistDistance = wg["size"] - 10
scene.world.mistStart = (wg["size"]) * 5/10

player = scene.objects["player"]
lastpos = player.worldPosition
player["lastpos"] = (lastpos.x,lastpos.y)

"""
0 Luft
1 dirt
2 dirt-gras
3 rock
"""



def fill_blocknames():
    for block in scene.objectsInactive:
        if block.name[:5] == "block":
            wg["blocknames"].append(block.name)
    wg["blocknames"].sort()


def getBlock(name_or_number):
    try:
        #fehler wenn es sich um einen Namen handelt Sprung zu except
        int(name_or_number)
        #wenn es sich um eine zahl handelt
        return scene.objectsInactive[wg["blocknames"][name_or_number - 1]]
    except:
        #es handelt sich um einen String
        return scene.objectsInactive[name_or_number]

def putblock(pos,typ):
    b = wg["blocks"].get(pos)
    
    if b == None:
        wg.worldPosition = pos
        wg["blocks"][pos] = scene.addObject(getBlock(typ),wg)

def delblock(pos):
    b = wg["blocks"].get(pos)
    if not b == None:
        try:
            b.endObject()
            del wg["blocks"][pos]
        except:
            print("hat nicht loechen koennen!")
def untervoxel(pos):
    unterevoxel = []
    for x in range(-1,1):
        for y in range(-1,1):
            x += pos[0]
            y += pos[1]
            z = pos[2]-1
            if not wg["voxel"].get((x,y,z)) == 0:
                unterevoxel.append(wg["voxel"].get((x,y,z)))
    return unterevoxel    

def generator():
    t0 = time.clock()
    for x in range(-100,100):
        for y in range(-100,100):
            n = mathutils.noise.hetero_terrain((x/20,y/20,0),25,100,3,1,4)
            #n = (noise.snoise2(x/15,y/15,1) + 1)/2
            height = int(n * MAP_HEIGHT/3) + 1
            
            for	z in range(height + 1):
                if z == height:
                    typ = 2
                else:
                    typ = 1
                wg["voxel"][x,y,z] = typ
    print("generate. ", time.clock() - t0)
def delAufXY(x,y):
    for	z in range(MAP_HEIGHT + 10):
        delblock((x,y,z))
        
def blockAufXY(x,y):
    for z in range(MAP_HEIGHT + 10):
        
        h = MAP_HEIGHT - z + 10
        v = wg["voxel"].get((x,y,h))
        voxeldrumrum = [wg["voxel"].get((x,y,h + 1)),
                        wg["voxel"].get((x,y,h - 1)),
                        wg["voxel"].get((x,y + 1,h)),
                        wg["voxel"].get((x,y - 1,h)),
                        wg["voxel"].get((x + 1,y,h)),
                        wg["voxel"].get((x - 1,y,h))]

        außen = False
        for vox in voxeldrumrum:
            if vox == None:
                außen = True
        
        if v != None and außen:
            
            
            putblock((x,y,h),v)
            
def initialbuildblocks(size,pos):
    builded = {}
    
    t0 = time.clock()
#von oben:
    for x in range(pos[0] - size ,pos[0] + size + 1):
        
        for y in range(pos[1] - size ,pos[1] + size + 1):
            blockAufXY(x,y)
            
    print("build. ", time.clock() - t0)
     
"""
    for x in range(pos[0] - size ,pos[0] + size):
        for y in range(pos[1] - size ,pos[1] + size):
            for z in range(MAP_HEIGHT):
                #builded[(x,y)] =
                try:
                    putblock((x,y,z),wg["voxel"].get((x,y,z)))
                except:
                    pass   
    
"""    

def deltapos(last,p):
    return int(p[0]) - int(last[0]),int(p[1]) - int(last[1])

def refreshblocksList():
    size = wg["size"]
    pos = int(player.worldPosition.x),int(player.worldPosition.y)
    dp = deltapos(player["lastpos"],pos)
    if not dp == (0,0):
        
        if abs(dp[0]) == 1:
            print("###################################################### ",dp[0]," bewegt###############################################")
            xp = dp[0] * (size) + pos[0]
            xd = dp[0] * -(size + 1) + pos[0]
            for y in range(pos[1] - size ,pos[1] + size + 1):
                wg["needToBuild"].append((xp,y))
                wg["needToDel"].append((xd,y))
                player["lastpos"] = pos
                #putblock((xp,y,z),voxel.get((xp,y,z)))
                #delblock((xd, y, z))
                    
        if abs(dp[1]) == 1:
            print("###################################################### ",dp[1]," bewegt###############################################")
            yp = dp[1] * (size) + pos[1]
            yd = dp[1] * -(size+1) + pos[1]
            for x in range(pos[0] - size ,pos[0] + size + 1):
                wg["needToBuild"].append((x,yp))
                wg["needToDel"].append((x,yd))
                player["lastpos"] = pos
                    #putblock((x,yp,z),voxel.get((x,yp,z)))
                    #delblock((x, yd, z))
                    
    #print("blocktobuild", wg["needToBuild"])
    #print("blockstodel",wg["needToDel"])
    
def rebuildTerrain():
   
    t0 = time.clock()
    while len(wg["needToBuild"]) > 0 and (time.clock() - t0) < 0.002:
        p = wg["needToBuild"][0]
        blockAufXY(p[0],p[1])
        wg["needToBuild"].pop(0)
        
    while len(wg["needToDel"]) > 0 and (time.clock() - t0) < 0.002:
        p = wg["needToDel"][0]
        delAufXY(p[0],p[1])
        wg["needToDel"].pop(0)
    #print("muesste leer sein", wg["needToBuild"])
    #print("muesste leer sein",wg["needToDel"])
fill_blocknames()
generator()
initialbuildblocks(wg["size"],(0,0,0))
player["started"]= True
def main():
	pass