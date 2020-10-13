import os
import subprocess
import getch
import random
import math
import Maps
import LevelGeneration
from Utilities import Vec2, Rectangle
from Camera import Camera

#https://pypi.org/project/getch/

# https://en.wikipedia.org/wiki/Roguelike
# https://gamedevelopment.tutsplus.com/articles/the-key-design-elements-of-roguelikes--cms-23510

'''
Procedurally generated levels,
#leveling up and permanent death
items and combat
Vision / Fog of War?
enemies (homing rocket bomber, necromancer, stealth enemy, stunner, poison, healer, tracker, gadget enemy, trapper, buff-er, robber[takes your items], king[upgrades other enemies])
companions
multiplayer
#storyline
#ladder/shaft/exit
doorways
healing room (boss drops food after you defeat it)
events (wishing fountains)
Boss (chess piece bosses)
artifacts
saving
pre game shop (artifacts)
#end game/restart
starting class
#NPCS (merchants, vending machine, )
Chests (spawn items around player), percent chance to spawn after each level
Keys/bombs drop from enemies or chests.
Backpacks
#Make game remember coins, player level, xp, and mysteryman dialogue value
Side quests that start your next dungeon with extra perks (gold, health/damage boost, companion, etc.)
Challenges (handicaps for better rewards)
Companions and followers
'''

def clear():

    #---------------------------------------------------------------------------------------------------------------------------------------

    #clears the map
    if os.name in ('nt','dos'):
        subprocess.run("cls", shell=True)
    elif os.name in ('linux','osx','posix'):
        subprocess.call("clear")
    else:
        print("\n") * 120
    
    #---------------------------------------------------------------------------------------------------------------------------------------



class GameManager():

   

    #---------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        #randomRoom = random.randint(0,len(Maps.UniqueRooms.ROOMS)-1)
        self.map = self.convertMapData(Maps.UniqueRooms.STARTING_ROOM)
        self.levelGenerator = LevelGeneration.LevelGenerator(Maps.UniqueRooms.ROOMS)
        self.levelGenerator.rooms = [LevelGeneration.Room(self.map, Vec2(0,0), 0)]
        #self.levelGenerator.GenerateLevel(15, 5, 8, 5)
        self.map = self.levelGenerator.rooms[0].data
        self.player = PlayerInfo(input("What is your name? "), 0, 1, 1)

        self.enemies = []

        self.items = []

        self.itemID = 0

        self.initMap()

        self.camera = Camera(1, 1, 100, 25)

        self.initQuest()
        self.NO_QUEST = Quest("nocurrentquest", 0, lambda x: -1)
        self.currentQuest = self.NO_QUEST 

    #---------------------------------------------------------------------------------------------------------------------------------------

    def displayMap(self):
        #this prints the map after you or an enemy moves
        for y in range(len(self.map)):
            constructedLine = ""
            for x in range(len(self.map[y])):
                if self.player.position.x == x and self.player.position.y == y:
                    constructedLine += self.player.displayCharacter
                else: 
                    foundEnemy = False
                    for i in range(len(self.enemies)):
                        if x == self.enemies[i].position.x and y == self.enemies[i].position.y:
                            constructedLine += self.enemies[i].displayCharacter
                            foundEnemy = True
                            break
                    if foundEnemy == False:
                        foundItem = False
                        for i in range(len(self.items)):
                            if x == self.items[i].position.x and y == self.items[i].position.y:
                                constructedLine += self.items[i].displayCharacter
                                foundItem = True
                                break
                    if foundItem == False and foundEnemy == False:
                        constructedLine += self.map[y][x]
            print(constructedLine)

    def displayUI(self):
        print("❤:", self.player.baseHealth, "/", self.player.baseMaxHealth)
        print("$:",self.player.coinBag, "coins")
        print("💣:", self.player.bombInventory, "bombs", "🔑:", self.player.keyInventory, "keys")
        print("XP:", self.player.playerXP, "/", self.player.xpNeeded, "xp needed to level up")
        print("Player Lvl:", self.player.playerLevel)
        print("Dungeon Level:", self.player.currentLevel)
        print("Current Quest:", self.currentQuest.questName)
        print("Inventory:")
        self.player.inventory.display()
        print()
        print("Recent Events:")
        for mssg in self.player.messageLog:
            print(mssg)

    
    #---------------------------------------------------------------------------------------------------------------------------------------

    def update(self):
        while True:
            #self.displayMap()
            self.levelGenerator.DrawRooms(self.camera, [self.items, self.enemies, [self.player]])
            self.displayUI()
            resetRoom = self.player.playerInput(self.map, self.enemies, self.items) 
            if resetRoom == -1:
                self.restartLevel()
            elif resetRoom == 'item':
                self.spawnNPCItems(False)
            elif resetRoom == 'easyquest':
                self.getQuest(1)
            elif resetRoom == 'hardquest':
                self.getQuest(2)
            elif resetRoom == -2:
                self.restartLevel(True)
            for i in range(len(self.enemies)):
                self.enemies[i].think(self.map, self.player, self.enemies)
            if self.player.isDead == True:
                self.restartLevel()
            for i in range(len(self.enemies) - 1, -1, -1):
                if self.enemies[i].isDead == True:
                    if self.enemies[i].name == "dragon":
                        self.player.dragonKills += 1
                    if self.enemies[i].name == "creeper":
                        self.player.creeperKills += 1
                    if self.enemies[i].name == "zombie":
                        self.player.zombieKills += 1
                    self.enemies.remove(self.enemies[i])
            for i in range(len(self.items) - 1, -1, -1):
                if self.items[i].isDead == True:
                    self.items.remove(self.items[i])
            self.player.checkPlayerLevelUp()
            self.camera.update(self.player.position)
            setQuestReward = self.currentQuest.checkQuestObjective(self.currentQuest)
            if setQuestReward != -1:
                self.player.coinBag += setQuestReward
            

    def restartLevel(self, pickNewRoom = False):
        #sets player to the beginning of the level
        if pickNewRoom == True:
            randomRoom = random.randint(0,len(Maps.UniqueRooms.ROOMS)-1)
            self.map = self.convertMapData(Maps.UniqueRooms.ROOMS[randomRoom])
            self.levelGenerator.rooms = [LevelGeneration.Room(self.map, Vec2(0,0), 0)]
            self.map = self.levelGenerator.rooms[0].data
        self.initMap()
        

    #---------------------------------------------------------------------------------------------------------------------------------------

    def initMap(self):
        self.player.position.x = 1
        self.player.position.y = 1
        self.player.reset()
        self.enemies = []
        self.items = []
        if self.testForNPC() == False:   
            self.spawnEnemies()
            self.spawnCoins()
            self.spawnHealing()
            self.spawnWeapon()
            self.spawnArmor()
            self.spawnChest()
        else:
            self.spawnNPCItems()

    def convertMapData(self, map):
        convertedMapData = []
        for y in range(len(map)):
            convertedMapData.append([])
            for x in range(len(map[y])):
                convertedMapData[y].append(map[y][x])
        return convertedMapData

    #---------------------------------------------------------------------------------------------------------------------------------------

    def spawnEnemies(self):
        numberOfMorons = random.randint(1,3)
        while numberOfMorons > 0:
            XPosition = random.randint(0, len(self.map[0]) -1)
            YPosition = random.randint(0, len(self.map) -1)
            if self.map[YPosition][XPosition] == " ":
                foundEnemy = False
                for i in range(len(self.enemies)):
                    if self.enemies[i].position.x == XPosition and self.enemies[i].position.y == YPosition:
                        foundEnemy = True
                if foundEnemy == False:
                    enemy = MoronEnemy(XPosition, YPosition, "Zombie", 10, 1, 3, 10, 1, 5, random.randint(3, 7))
                    self.enemies.append(enemy)
                    numberOfMorons -= 1
        numberOfTanks = random.randint(0,1)
        while numberOfTanks > 0:
            XPosition = random.randint(0, len(self.map[0]) -1)
            YPosition = random.randint(0, len(self.map) -1)
            if self.map[YPosition][XPosition] == " ":
                foundEnemy = False
                for i in range(len(self.enemies)):
                    if self.enemies[i].position.x == XPosition and self.enemies[i].position.y == YPosition:
                        foundEnemy = True
                if foundEnemy == False:
                    enemy = TankEnemy(XPosition, YPosition, "Dragon", 20, 5, 5, 5, 1, 10, random.randint(10, 20))
                    self.enemies.append(enemy)
                    numberOfTanks -= 1
        numberOfGlassCannons = random.randint(0,2)
        while numberOfGlassCannons > 0:
            XPosition = random.randint(0, len(self.map[0]) -1)
            YPosition = random.randint(0, len(self.map) -1)
            if self.map[YPosition][XPosition] == " ":
                foundEnemy = False
                for i in range(len(self.enemies)):
                    if self.enemies[i].position.x == XPosition and self.enemies[i].position.y == YPosition:
                        foundEnemy = True
                if foundEnemy == False:
                    enemy = GlassCannon(XPosition, YPosition, "Creeper", 3, 1, 15, 3, 1, 15, random.randint(7, 23))
                    self.enemies.append(enemy)
                    numberOfGlassCannons -= 1
        numberOfSpeedyEnemies = random.randint(1,4)
        while numberOfSpeedyEnemies > 0:
            XPosition = random.randint(0, len(self.map[0]) -1)
            YPosition = random.randint(0, len(self.map) -1)
            if self.map[YPosition][XPosition] == " ":
                foundEnemy = False
                for i in range(len(self.enemies)):
                    if self.enemies[i].position.x == XPosition and self.enemies[i].position.y == YPosition:
                        foundEnemy = True
                if foundEnemy == False:
                    enemy = SpeedyEnemy(XPosition, YPosition, "Spider", 5, 1, 3, 5, 2, 5, random.randint(3, 10))
                    self.enemies.append(enemy)
                    numberOfSpeedyEnemies -= 1

    def spawnCoins(self):
        numberOfCoins = random.randint(1,3)
        while numberOfCoins > 0:
            XPosition = random.randint(0, len(self.map[0]) -1)
            YPosition = random.randint(0, len(self.map) -1)
            if self.map[YPosition][XPosition] == " ":
                foundCoin = False
                for i in range(len(self.items)):
                    if self.items[i].position.x == XPosition and self.items[i].position.y == YPosition:
                        foundCoin = True
                if foundCoin == False:
                    coin = Coin(XPosition, YPosition, self.itemID)
                    coin.determineCoin()
                    self.itemID += 1
                    self.items.append(coin)
                    numberOfCoins -= 1
                '''
                with open('TotalCoins.txt', 'r') as c:
                    coin.totalCoins = c.readLines()
                '''

    def spawnHealing(self):
        numberOfHealing = random.randint(0,1)
        for __ in range(numberOfHealing):
            XPosition = random.randint(0, len(self.map[0]) -1)
            YPosition = random.randint(0, len(self.map) -1)
            if self.map[YPosition][XPosition] == " ":
                foundHealing = False
                for i in range(len(self.items)):
                    if self.items[i].position.x == XPosition and self.items[i].position.y == YPosition:
                        foundHealing = True
                if foundHealing == False:
                    healing = Healing(XPosition, YPosition, self.itemID)
                    healing.determineHealing()
                    self.itemID += 1
                    self.items.append(healing)
                    numberOfHealing -= 1

    def spawnWeapon(self):
        weaponSpawnChance = random.randint(0, 7)
        weaponSpawn = 0
        if weaponSpawnChance == 1:
            weaponSpawn = 1
        while weaponSpawn > 0:
            XPosition = random.randint(0, len(self.map[0]) -1)
            YPosition = random.randint(0, len(self.map) -1)
            if self.map[YPosition][XPosition] == " ":
                foundWeapon = False
                for i in range(len(self.items)):
                    if self.items[i].position.x == XPosition and self.items[i].position.y == YPosition:
                        foundWeapon = True
                if foundWeapon == False:
                    weapon = Weapon(XPosition, YPosition, self.itemID)
                    weapon.determineWeapon()
                    self.itemID += 1
                    self.items.append(weapon)
                    weaponSpawn -= 1

    def spawnArmor(self):
        armorSpawnChance = random.randint(1, 10)
        armorSpawn = 0
        if armorSpawnChance == 1:
            armorSpawn = 1
        while armorSpawn > 0:
            XPosition = random.randint(0, len(self.map[0]) -1)
            YPosition = random.randint(0, len(self.map) -1)
            if self.map[YPosition][XPosition] == " ":
                foundArmor = False
                for i in range(len(self.items)):
                    if self.items[i].position.x == XPosition and self.items[i].position.y == YPosition:
                        foundArmor = True
                if foundArmor == False:
                    armor = Armor(XPosition, YPosition, self.itemID)
                    armor.determineArmor()
                    self.itemID += 1
                    self.items.append(armor)
                    armorSpawn -= 1

    def spawnChest(self):
        chestSpawnChance = random.randint(1, 3)
        chestSpawn = 0
        if chestSpawnChance == 1:
            chestSpawn = 1
        while chestSpawn > 0:
            XPosition = random.randint(0, len(self.map[0]) -1)
            YPosition = random.randint(0, len(self.map) -1)
            if self.map[YPosition][XPosition] == " ":
                foundChest = False
                for i in range(len(self.items)):
                    if self.items[i].position.x == XPosition and self.items[i].position.y == YPosition:
                        foundChest = True     
                if foundChest == False:
                    chest = Chest(XPosition, YPosition, self.itemID)
                    self.items.append(chest)
                    chestSpawn -= 1

    #---------------------------------------------------------------------------------------------------------------------------------------

    def testForNPC(self):
        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                if self.map[y][x] == 'M':
                    return True
                elif self.map[y][x] == '?':
                    return True
                elif self.map[y][x] == 'A':
                    return True
                elif self.map[y][x] == 'B':
                    return True
                elif self.map[y][x] == 'T':
                    return True
                elif self.map[y][x] == 'C':
                    return True
        return False

    def spawnNPCItems(self, setPrice = True):
        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                if self.map[y][x] == '!':
                    item = random.randint(1,5)
                    if item == 1:
                        healing = Healing(x, y, self.itemID)
                        if setPrice == True:
                            healing.determineHealing(random.randint(35,40))
                        else:
                            healing.determineHealing()
                        self.itemID += 1
                        self.items.append(healing)
                    if item == 2:
                        weapon = Weapon(x, y, self.itemID)
                        if setPrice == True:
                            weapon.determineWeapon(random.randint(50,60))
                        else:
                            weapon.determineWeapon()
                        self.itemID += 1
                        self.items.append(weapon)
                    if item == 3:
                        armor = Armor(x, y, self.itemID)
                        if setPrice == True:
                            armor.determineArmor(random.randint(70,80))
                        else:
                            armor.determineArmor()
                        self.itemID += 1
                        self.items.append(armor)
                    if item == 4:
                        key = Key(x, y, self.itemID)
                        if setPrice == True:
                            key.price = random.randint(40, 50)
                        self.itemID += 1
                        self.items.append(key)
                    if item == 5:
                        bomb = Bomb(x, y, self.itemID)
                        if setPrice == True:
                            bomb.price = random.randint(35, 50)
                        self.itemID += 1
                        self.items.append(bomb)

    #---------------------------------------------------------------------------------------------------------------------------------------
 
    def initQuest(self):
        self.easyQuest = 0
        self.easyQuestList = [Quest("Buy an item from the shop", 1, self.buyItemQuest),
                              Quest("Talk to the mystery man", 1, self.talkToMysteryManQuest),
                              Quest("Find a piece of armor on the ground", 1, self.findAPieceOfArmorQuest),
                              Quest("Find a weapon on the ground", 1, self.findAWeaponQuest),
                              Quest("Use some healing", 1, self.useHealingQuest),
                              Quest("Break a weapon or armor", 1, self.breakWeaponOrArmorQuest),
                              Quest("Buy an item from a vending machine", 1, self.buyItemQuest),
                              Quest("Deposit at least 100 coins in the ATM", 1, self.depositAtLeast100CoinsQuest),
                              Quest("Upgrade one of your base stats", 1, self.upgradeBaseStatQuest),
                              Quest("Trade with the trader", 1, self.tradeWithTheTraderQuest)]
        self.hardQuest = 0 
        self.hardQuestList = [Quest("Reach 350 coins at any point of your adventure.", 2, self.reach350CoinsQuest),
                              Quest("Kill 15 dragons during your run.", 2, self.kill15DragonsQuest),
                              Quest("Kill 15 creepers during your run.", 2, self.kill15CreepersQuest),
                              Quest("Kill 35 zombies during your run.", 2, self.kill25ZombiesQuest),
                              Quest("Wear netherite armor", 2, self.wearNetheriteArmorQuest),
                              Quest("Find a katana", 2, self.findAKatanaQuest),
                              Quest("Eat an Enchanted Golden Apple", 2, self.eatAnEnchantedGoldenAppleQuest)]

    def buyItemQuest(self, quest):
        if quest.questProgress == -1:
            quest.questProgress = 0
            for y in range(len(self.map)):
                for x in range(len(self.map[y])):
                    if self.map[y][x] == "!":
                        quest.questProgress += 1
        else:
            numberOfExclamationPoints = 0
            for y in range(len(self.map)):
                for x in range(len(self.map[y])):
                    if self.map[y][x] == "!":
                        numberOfExclamationPoints += 1
            if numberOfExclamationPoints < quest.questProgress:
                self.player.addMessage(Text_Attributes.BOLD + "You have finished your quest" + Text_Attributes.END)
                self.currentQuest = self.NO_QUEST
                return quest.determineReward()
        return -1

    def talkToMysteryManQuest(self, quest):
        if quest.questProgress == -1:
            quest.questProgress = 0
            for y in range(len(self.map)):
                for x in range(len(self.map[y])):
                    if self.map[y][x] == "?":
                        quest.questProgress += 1
        else:
            determineMysteryManPresent = 0
            for y in range(len(self.map)):
                for x in range(len(self.map[y])):
                    if self.map[y][x] == "?":
                        determineMysteryManPresent += 1
            if determineMysteryManPresent < quest.questProgress:
                self.player.addMessage(Text_Attributes.BOLD + "You have finished your quest" + Text_Attributes.END)
                self.currentQuest = self.NO_QUEST
                return quest.determineReward()
        return -1
        
    def findAPieceOfArmorQuest(self, quest):
        if quest.questProgress == -1:
            quest.questProgress = 0
            for y in range(len(self.map)):
                for x in range(len(self.map[y])):
                    if self.map[y][x] == "🛡️":
                        quest.questProgress += 1
        else:
            determineArmorPresent = 0
            for y in range(len(self.map)):
                for x in range(len(self.map[y])):
                    if self.map[y][x] == "🛡️":
                        determineArmorPresent += 1
            if determineArmorPresent < quest.questProgress:
                self.player.addMessage(Text_Attributes.BOLD + "You have finished your quest" + Text_Attributes.END)
                self.currentQuest = self.NO_QUEST
                return quest.determineReward()
        return -1

    def findAWeaponQuest(self, quest):
        if quest.questProgress == -1:
            quest.questProgress = 0
            for y in range(len(self.map)):
                for x in range(len(self.map[y])):
                    if self.map[y][x] == "🗡️":
                        quest.questProgress += 1
        else:
            determineWeaponPresent = 0
            for y in range(len(self.map)):
                for x in range(len(self.map[y])):
                    if self.map[y][x] == "🗡️":
                        determineWeaponPresent += 1
            if determineWeaponPresent < quest.questProgress:
                self.player.addMessage(Text_Attributes.BOLD + "You have finished your quest" + Text_Attributes.END)
                self.currentQuest = self.NO_QUEST
                return quest.determineReward()
        return -1
    
    def useHealingQuest(self, quest):
        if quest.questProgress == -1:
            quest.questProgress = 0
            if len(self.player.inventory.healingSlot) > 0:
                quest.questProgress += 1
        else:
            determineHealingInventory = 0
            if len(self.player.inventory.healingSlot) > 0:
                determineHealingInventory += 1
            if determineHealingInventory < quest.questProgress:
                self.player.addMessage(Text_Attributes.BOLD + "You have finished your quest" + Text_Attributes.END)
                self.currentQuest = self.NO_QUEST
                return quest.determineReward()
        return -1
        
    def breakWeaponOrArmorQuest(self, quest):
        if quest.questProgress == -1:
            quest.questProgress = 0
            if len(self.player.inventory.weaponSlot) > 0 or len(self.player.inventory.armorSlot) > 0:
                quest.questProgress += 1
        else:
            determineArmorAndWeaponInventory = 0
            if len(self.player.inventory.weaponSlot) > 0 or len(self.player.inventory.armorSlot) > 0:
                determineArmorAndWeaponInventory += 1
            if determineArmorAndWeaponInventory < quest.questProgress:
                self.player.addMessage(Text_Attributes.BOLD + "You have finished your quest" + Text_Attributes.END)
                self.currentQuest = self.NO_QUEST
                return quest.determineReward()
        return -1

    def buyItemFromVendingMachine(self, quest):
        pass

    def depositAtLeast100CoinsQuest(self, quest):
        if quest.questProgress == -1:
            quest.questProgress = 0
        else:
            if self.player.ATMGoldGiven >= 100:
                self.player.addMessage(Text_Attributes.BOLD + "You have finished your quest" + Text_Attributes.END)
                self.currentQuest = self.NO_QUEST
                return quest.determineReward()
        return -1

    def upgradeBaseStatQuest(self, quest):
        if quest.questProgress == -1:
            self.player.hasStatUpgraded = False
            quest.questProgress = False
        else:
            if self.player.hasStatUpgraded:
                self.player.addMessage(Text_Attributes.BOLD + "You have finished your quest" + Text_Attributes.END)
                self.currentQuest = self.NO_QUEST
                self.player.hasStatUpgraded = False
                return quest.determineReward()
        return -1

    def tradeWithTheTraderQuest(self, quest):
        if quest.questProgress == -1:
            self.player.hasPlayerTraded = False
            quest.questProgress = False
        else:
            if self.player.hasPlayerTraded:
                self.player.addMessage(Text_Attributes.BOLD + "You have finished your quest" + Text_Attributes.END)
                self.currentQuest = self.NO_QUEST
                self.player.hasPlayerTraded = False
                return quest.determineReward()
        return -1
    
    def reach350CoinsQuest(self, quest):
        if quest.questProgress == -1:
            quest.questProgress = self.player.coinBag
        else:
            determinePlayerGold = self.player.coinBag
            if determinePlayerGold - quest.questProgress > 350:
                self.player.addMessage(Text_Attributes.BOLD + "You have finished your quest" + Text_Attributes.END)
                self.currentQuest = self.NO_QUEST
                return quest.determineReward()
        return -1

    def kill15DragonsQuest(self, quest):
        if quest.questProgress == -1:
            quest.questProgress = self.player.dragonKills
        else:
            if self.player.dragonKills - quest.questProgress >= 15:
                self.player.addMessage(Text_Attributes.BOLD + "You have finished your quest" + Text_Attributes.END)
                self.currentQuest = self.NO_QUEST
                return quest.determineReward()
        return -1

    def kill15CreepersQuest(self, quest):
        if quest.questProgress == -1:
            quest.questProgress = self.player.creeperKills
        else:
            if self.player.creeperKills - quest.questProgress >= 15:
                self.player.addMessage(Text_Attributes.BOLD + "You have finished your quest" + Text_Attributes.END)
                self.currentQuest = self.NO_QUEST
                return quest.determineReward()
        return -1

    def kill25ZombiesQuest(self, quest):
        if quest.questProgress == -1:
            quest.questProgress = self.player.zombieKills
        else:
            if self.player.zombieKills - quest.questProgress >= 15:
                self.player.addMessage(Text_Attributes.BOLD + "You have finished your quest" + Text_Attributes.END)
                self.currentQuest = self.NO_QUEST
                return quest.determineReward()
        return -1

    def wearNetheriteArmorQuest(self, quest):
        if quest.questProgress == -1:
            if len(self.player.inventory.armorSlot) > 0:
                if self.player.inventory.armorSlot[0].name == "Netherite Armor":
                    self.player.addMessage(Text_Attributes.BOLD + "You have finished your quest" + Text_Attributes.END)
                    self.currentQuest = self.NO_QUEST
                    return quest.determineReward()
        return -1     

    def findAKatanaQuest(self, quest):
        if quest.questProgress == -1:
            if len(self.player.inventory.weaponSlot) > 0:
                if self.player.inventory.weaponSlot[0].name == "Katana":
                    self.player.addMessage(Text_Attributes.BOLD + "You have finished your quest" + Text_Attributes.END)
                    self.currentQuest = self.NO_QUEST
                    return quest.determineReward()
        return -1

    def eatAnEnchantedGoldenAppleQuest(self, quest):
        if quest.questProgress == -1:
            if len(self.player.inventory.healingSlot) > 0:
                if self.player.inventory.healingSlot[0].name == "Enchanted Golden Apple":
                    self.player.addMessage(Text_Attributes.BOLD + "You have finished your quest" + Text_Attributes.END)
                    self.currentQuest = self.NO_QUEST
                    return quest.determineReward()
        return -1



    def getQuest(self, questDifficulty):
        if questDifficulty == 1:
            self.currentQuest = self.easyQuestList[random.randint(0, len(self.easyQuestList) - 1)]
        elif questDifficulty == 2:
            self.currentQuest = self.hardQuestList[random.randint(0, len(self.hardQuestList) - 1)]


class PlayerInfo():

    #---------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, name, playerClass, x, y ):
        self.name = name
        self.playerClass = playerClass
        self.position = Vec2(x,y)
        self.baseHealth = 100
        self.baseMaxHealth = 100
        self.baseDamage = 5
        self.baseDefenseNegation = 1 / 100
        self.baseEvasionChance = 10 / 100
        self.baseCritChance = 5 / 100
        self.baseCritDamage = 1.5
        self.baseSpeed = 100 / 100
        self.isDead = False

        self.coinBag = 0
        self.baseCoinDeduction = 80 / 100
        self.ATMGoldGiven = 0
        self.ATMStoredGold = 0

        self.playerXP = 0
        self.playerLevel = 1
        self.xpNeededForNextLevel()

        self.messageLog = []
        self.maxMessages = 3

        self.inventory = Inventory()
        self.keyInventory = 0
        self.bombInventory = 0

        self.currentLevel = 0

        self.displayCharacter = "."

        self.hasStatUpgraded = False
        self.hasPlayerTraded = False
        self.dragonKills = 0
        self.creeperKills = 0
        self.zombieKills = 0
        self.wearNetheriteQuest = False
        self.findAKatanaQuest = False
        self.eatAnEnchantedGoldenAppleQuest = False

    #---------------------------------------------------------------------------------------------------------------------------------------

    def reset(self):
        if self.isDead == True:
            self.baseHealth = self.baseMaxHealth
            self.isDead = False  
            self.inventory.reset()
        self.messageLog = []

    #---------------------------------------------------------------------------------------------------------------------------------------

    def addMessage(self, *args):
        message = ""
        for mssg in args:
            if type(mssg) != str:
                mssg = str(mssg)
            spaceCharacter = " "
            if mssg == ".":
                spaceCharacter = ""
            message = message + mssg + spaceCharacter
        if len(self.messageLog) < self.maxMessages:
            self.messageLog.append(message)
        else:
            self.messageLog.pop(0)
            self.messageLog.append(message)

    #---------------------------------------------------------------------------------------------------------------------------------------

    def playerInput(self, map, enemies, items):
        characterMove = getch.getch()
        moveX = 0
        moveY = 0
        if characterMove == 'r':
            return -1
        if characterMove == 'w':
            moveY = self.position.y - 1
            moveX = self.position.x
        elif characterMove == 'a':
            moveX = self.position.x -1
            moveY = self.position.y 
        elif characterMove == 'x':
            moveY = self.position.y + 1
            moveX = self.position.x
        elif characterMove == 'd':    
            moveX = self.position.x + 1
            moveY = self.position.y 
        elif characterMove == 'q':
            moveY = self.position.y - 1
            moveX = self.position.x - 1 
        elif characterMove == 'e':
            moveX = self.position.x + 1
            moveY = self.position.y - 1
        elif characterMove == 'z':
            moveY = self.position.y + 1
            moveX = self.position.x - 1
        elif characterMove == 'c':    
            moveX = self.position.x + 1
            moveY = self.position.y + 1
        elif characterMove == 's':
            if len(self.inventory.healingSlot) > 0:
                if self.baseHealth < self.baseMaxHealth:
                    self.baseHealth += self.inventory.healingSlot[0].healingValue
                    self.setHealth()
                    self.addMessage(self.name, "used their", self.inventory.healingSlot[0].name, self.name, "has healed", self.inventory.healingSlot[0].healingValue, "health.")
                    self.inventory.healingSlot.pop(0)
                else:
                    print("You already are at max health.")
        elif characterMove == '+':
            self.coinBag += 10000
        elif characterMove == '{':
            self.keyInventory += 10
        elif characterMove == '}':
            self.bombInventory += 10
        elif characterMove == '=':
            return -2
        if moveY >= 0 and moveY < len(map) and moveX >= 0 and moveX < len(map[0]):
            if map[moveY][moveX] == " ":
                moveIntoEnemy = -1
                for i in range(len(enemies)):
                    if enemies[i].position.x == moveX and enemies[i].position.y == moveY:
                        moveIntoEnemy = i
                        break
                if moveIntoEnemy == -1:
                    for i in range(len(items)):
                        if items[i].position.x == moveX and items[i].position.y == moveY:
                            canPickup = True
                            if items[i].type == "chest":
                                if len(enemies) != 0:
                                    canPickup = False
                                    self.addMessage(Text_Attributes.BOLD + "There are still monsters in the room" + Text_Attributes.END)
                            if canPickup:
                                if items[i].pickup(self) == 1:
                                    '''
                                    coins = random.randint(1,2)
                                    player.coinBag
                                    '''
                                    map[moveY][moveX] = "!"
                                    return "item"
                            break
                    self.position.x = moveX
                    self.position.y = moveY
                else:
                    self.attack(enemies[moveIntoEnemy])
            elif map[moveY][moveX] == "D":
                if self.keyInventory > 0 and self.bombInventory > 0:
                    enterNextDungeon = input("Would you like to enter the next dungeon using 1 key? ").lower()
                    if enterNextDungeon == 'yes':
                        self.keyInventory -= 1
                        #self.bombInventory -= 1
                        self.currentLevel += 1
                        return -2
                    else:
                        if self.coinBag >= 100:
                            moneyToEnterNextDungeon = input("Would you like to pay 100 coins instead? ").lower()
                            if moneyToEnterNextDungeon == 'yes':
                                self.coinBag -= 100
                                self.currentLevel += 1
                                return -2
                            else:
                                pass
                        else:
                            pass
                else:
                    if self.coinBag >= 50:
                        moneyToEnterNextDungeon = input("You do not have enough bombs or keys to continue. Would you like to pay 50 coins instead? ").lower()
                        if moneyToEnterNextDungeon == 'yes':
                            self.coinBag -= 50
                            self.currentLevel += 1
                            return -2
                        else:
                            pass
                    else:
                        pass
            elif map[moveY][moveX] == "H":
                return -2
            elif map[moveY][moveX] == "D̴":
                if self.bombInventory >= 2 and self.keyInventory >= 3:
                    enterBossRoom = input("Would you like to enter the boss room using 3 keys and 2 bombs? " ).lower()
                    if enterBossRoom == "yes":
                        self.bombInventory -= 2
                        self.keyInventory -= 3
                        return -2
                    else:
                        if self.coinBag >= 250:
                            payForBossRoom = input("Would you like to pay with 250 coins instead? ").lower()
                            if payForBossRoom == "yes":
                                self.coinBag -= 250
                            else:
                                continueToNextDungeon = print("Would you like to come back with more keys, bombs, or gold(1), or leave the dungeon without fighting the boss? ").lower()
                                if continueToNextDungeon == 1:
                                    return -1
                                else:
                                    return -2
            elif map[moveY][moveX] == "M":
                self.addMessage(Merchant.sayDialogue())
            elif map[moveY][moveX] == "?":
                if MysteryMan.sayDialogue(self) == 'item':
                    map[moveY][moveX] = '!'
                    return 'mysteryman'
                else:
                    map[moveY][moveX] = ' '
            elif map[moveY][moveX] == "!":
                for item in items:
                    if item.position.x == moveX and item.position.y == moveY:
                        item.pickup(self)
                        map[moveY][moveX] = ' '
            elif map[moveY][moveX] == "A":
                depositGold = input("Would you like to deposit your gold? ").lower()
                if depositGold == "yes":
                    self.ATMGoldGiven = self.ATMGoldGiven + self.coinBag
                    self.coinBag = 0
                else:
                    pass
            elif map[moveY][moveX] == "B":
                Blacksmith.upgradePlayer(self)
            elif map[moveY][moveX] == "T":
                Trader.tradeWithPlayer(self)
            elif map[moveY][moveX] == "C":
                Collector.buyFromPlayer(self)
            elif map[moveY][moveX] == "V":
                if VendingMachine.dispenseItem(self) == "item":
                    map[moveY + 1][moveX] = "!"
                    return "item"
                elif VendingMachine.dispenseItem(self) == "broke":
                    map[moveY][moveX] = " "
            elif map[moveY][moveX] == "X":
                questDifficulty = int(input("Would you like an easy quest[1] or a hard quest[2]? "))
                if questDifficulty == 1:
                    return "easyquest"
                elif questDifficulty == 2:
                    return "hardquest"
            else:
                return self.playerInput(map, enemies, items)
        clear()
    
    #---------------------------------------------------------------------------------------------------------------------------------------

    def attack(self, enemy):
        enemy.takeDamage(self.calculateDamage(),self)

    def calculateDamage(self):
        weaponDamage = 0
        for item in self.inventory.weaponSlot:
            if item.type == "weapon":
                weaponDamage += item.damageValue
                weaponBreaks = random.randint(1, 10)
                if weaponBreaks == 1:
                    self.inventory.weaponSlot.remove(item)
                    self.addMessage(item.name, "has broken.")
        crit = random.randint(1, 100)
        if crit <= self.baseCritChance:
            finalDamage = (weaponDamage + self.baseDamage) * self.baseCritDamage
        else: 
            finalDamage = weaponDamage + self.baseDamage
        return finalDamage

    def takeDamage(self, damage):
        evasionChance = random.randint(1, 100)
        if evasionChance <= self.baseEvasionChance:
            finalDamage = 0
        else:
            finalDamage = damage * (1 - self.baseDefenseNegation)
            finalDamage = round(finalDamage)
            for item in self.inventory.armorSlot:
                if item.type == "armor":
                    finalDamage *= item.armorNegation / 100
                    armorBreaks = random.randint(1, 10)
                    if armorBreaks == 1:
                        self.inventory.armorSlot.remove(item)
                        self.addMessage(item.name, "has broken.")
        self.baseHealth -= finalDamage
        self.baseHealth = round(self.baseHealth)
        if self.baseHealth <= 0:
            self.die()
        finalDamage = round(finalDamage)
        self.addMessage(self.name, "has taken", finalDamage)
        
    #---------------------------------------------------------------------------------------------------------------------------------------

    def setHealth(self):
        if self.baseHealth > self.baseMaxHealth:
            self.baseHealth = self.baseMaxHealth
  
    #---------------------------------------------------------------------------------------------------------------------------------------

    def checkPlayerLevelUp(self):
        determinePlayerLevelUp = self.playerXP / self.xpNeeded
        if determinePlayerLevelUp >= 1:
            self.playerLevel += 1
            self.playerXP -= self.xpNeeded
            self.xpNeededForNextLevel()
            self.increaseStats()

    def xpNeededForNextLevel(self):
        self.xpNeeded = math.ceil(0.5*((self.playerLevel+1)**2) + 10)

    def increaseStats(self):
        self.baseMaxHealth += 1
        self.baseHealth = self.baseMaxHealth
        self.baseDamage += 0.5
        self.baseDefenseNegation += 1 / 100
        self.baseEvasionChance += 1 / 100
        self.baseCritChance += 1/ 100

    #---------------------------------------------------------------------------------------------------------------------------------------

    def die(self):
        self.addMessage(self.name, "has died.", self.name, "has lost", round((1 - self.baseCoinDeduction) * 100), "percent of their coins, losing a total of", round((1 - self.baseCoinDeduction) * self.coinBag), "coins.")
        self.coinBag = round(self.coinBag * self.baseCoinDeduction)
        self.playerXP = 0
        self.baseCoinDeduction = 80 / 100
        self.baseDamage = 5
        self.baseDefenseNegation = 1 / 100
        self.baseEvasionChance = 10 / 100
        self.baseCritChance = 5 / 100
        self.baseCritDamage = 1.5
        self.baseSpeed = 100 / 100
        self.keyInventory = 0
        self.bombInventory = 0
        self.ATMStoredGold = self.ATMStoredGold + self.ATMGoldGiven
        '''
        with open('TotalCoins.txt', 'w') as __:
            print(self.coinBag)
        '''
        self.dragonKills = 0
        self.creeperKills = 0
        self.zombieKills = 0
        self.isDead = True

    #---------------------------------------------------------------------------------------------------------------------------------------

    def quest(self, questGiver):
        if questGiver.pickQuestType == 1:
            easyQuestType = random.randint(0, len(questGiver.easyQuestList) -1)
            easyQuest = questGiver.easyQuestType
            self.addMessage(Text_Attributes.BOLD + "Your easy quest is" + easyQuestType + Text_Attributes.END)
            if easyQuest == 1:
                self.addMessage("Objective: ", easyQuestType)
        pass


class BaseEnemy():

    #---------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, x, y, name, enemyHealth, enemyArmorDefense, enemyDamage, enemyVision, enemySpeed, enemyGold, enemyXP):
        self.position = Vec2(x, y)
        self.name = name
        self.health = enemyHealth
        self.maxHealth = self.health
        self.armor = enemyArmorDefense / 100
        self.damage = enemyDamage
        self.vision = enemyVision
        self.speed = enemySpeed
        self.goldWhenKilled = enemyGold
        self.xpWhenKilled = enemyXP
        self.enemyKeyDrop = random.randint(1,10)
        self.enemyBombDrop = random.randint(1,10)
        self.XMove = -1
        self.YMove = -1
        self.isDead = False

        self.displayCharacter = "~"

    #---------------------------------------------------------------------------------------------------------------------------------------


    def think(self, map, player, enemies, depth = 4):
        XDist = player.position.x - self.position.x
        YDist = player.position.y - self.position.y
        absXDist = abs(XDist)
        absYDist = abs(YDist)
        dist = absXDist * absXDist + absYDist * absYDist 
        dist = math.sqrt(dist)
        self.XMove = self.position.x
        self.YMove = self.position.y
        self.enemyLastMoveX = 0
        self.enemyLastMoveY = 0
        if self.enemyLastMoveX != self.position.x and self.enemyLastMoveY != self.position.y:
            if dist <= self.vision:
                if XDist > 0:
                    self.XMove += 1
                elif XDist < 0:
                    self.XMove -= 1
                elif YDist > 0:
                    self.YMove += 1
                elif YDist < 0:
                    self.YMove -= 1
            else:
                enemyAxisDirection = random.randint(0,1)
                if enemyAxisDirection == 0:
                    enemyMoveX = random.randint(-1,1)
                    while enemyMoveX == 0:
                        enemyMoveX = random.randint(-1,1)
                    self.XMove += enemyMoveX
                elif enemyAxisDirection == 1:
                    enemyMoveY = random.randint(-1,1)
                    while enemyMoveY == 0:
                        enemyMoveY = random.randint(-1,1)
                    self.YMove += enemyMoveY
        if self.YMove >= 0 and self.YMove < len(map) and self.XMove >= 0 and self.XMove < len(map[0]):
            if map[self.YMove][self.XMove] == " ":
                if self.XMove == player.position.x and self.YMove == player.position.y: 
                    self.attackPlayer(player)
                else:
                    foundEnemy = False
                    for i in range(len(enemies)):
                        if enemies[i] != self:
                            if enemies[i].XMove == self.XMove and enemies[i].YMove == self.YMove:
                                foundEnemy = True
                                break
                            if enemies[i].position.x == self.XMove and enemies[i].position.y == self.YMove:
                                foundEnemy = True
                                break
                    if foundEnemy == False:
                        self.position.x = self.XMove
                        self.position.y = self.YMove
                        self.enemyLastMoveX = self.position.x
                        self.enemyLastMoveY = self.position.y
            else:
                if depth > 0 :
                    self.think(map, player, enemies, depth - 1)
        
    #-------------------------------------------------------------------------------------------------------------------------------------------

    def attackPlayer(self, player):
        player.takeDamage(self.calculateDamage())

    def calculateDamage(self):
        finalDamage = self.damage 
        return finalDamage

    def takeDamage(self, damage, player):
        finalDamage = damage * (1 - self.armor)
        finalDamage = round(finalDamage)
        self.health -= finalDamage
        player.addMessage(self.name, "has taken", finalDamage, ". They are now at", self.health)
        if self.health <= 0:
            self.die(player)

    #---------------------------------------------------------------------------------------------------------------------------------------

    def die(self, player):
        self.isDead = True
        player.coinBag += self.goldWhenKilled
        player.playerXP += self.xpWhenKilled
        if self.enemyKeyDrop == 1:
            player.keyInventory += 1
        if self.enemyBombDrop == 1:
            player.bombInventory += 1
        player.addMessage(player.name, "has gained 5 coins from killing a", self.name, ".", player.name, "now has", player.coinBag, "coins.")

class MoronEnemy(BaseEnemy):

    #---------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, x, y, name, enemyHealth, enemyArmorDefense, enemyDamage, enemyVision, enemySpeed, enemyGold, enemyXP):
    
        super().__init__(x, y, name, enemyHealth, enemyArmorDefense, enemyDamage, enemyVision, enemySpeed, enemyGold, enemyXP)
        self.displayCharacter = Text_Attributes.GREEN + "z" + Text_Attributes.END

    #---------------------------------------------------------------------------------------------------------------------------------------

class TankEnemy(BaseEnemy):

    #---------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, x, y, name, enemyHealth, enemyArmorDefense, enemyDamage, enemyVision, enemySpeed, enemyGold, enemyXP):
    
        super().__init__(x, y, name, enemyHealth, enemyArmorDefense, enemyDamage, enemyVision, enemySpeed, enemyGold, enemyXP)
        self.displayCharacter = Text_Attributes.RED + "d" + Text_Attributes.END

    #---------------------------------------------------------------------------------------------------------------------------------------

class GlassCannon(BaseEnemy):

    #---------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, x, y, name, enemyHealth, enemyArmorDefense, enemyDamage, enemyVision, enemySpeed, enemyGold, enemyXP):
    
        super().__init__(x, y, name, enemyHealth, enemyArmorDefense, enemyDamage, enemyVision, enemySpeed, enemyGold, enemyXP)
        self.displayCharacter = Text_Attributes.BRIGHTGREEN + "c" + Text_Attributes.END

    #---------------------------------------------------------------------------------------------------------------------------------------

class SpeedyEnemy(BaseEnemy):  

    #---------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, x, y, name, enemyHealth, enemyArmorDefense, enemyDamage, enemyVision, enemySpeed, enemyGold, enemyXP):
    
        super().__init__(x, y, name, enemyHealth, enemyArmorDefense, enemyDamage, enemyVision, enemySpeed, enemyGold, enemyXP)
        self.displayCharacter = Text_Attributes.BLACK + "s" + Text_Attributes.END  

    #---------------------------------------------------------------------------------------------------------------------------------------



class Item():

    #---------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, x, y, id_, itemType, price = 0):
        self.position = Vec2(x, y)
        self.ID = id_
        self.isDead = False
        self.type = itemType
        self.price = price
        self.displayCharacter = "~"

    #---------------------------------------------------------------------------------------------------------------------------------------

    def pickup(self, player):
        print("This message should never appear")

    #---------------------------------------------------------------------------------------------------------------------------------------

class Coin(Item):

    #---------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, x, y, id_):
        self.coinValue = random.randint(1, 20)
        self.name = 0
        super().__init__(x, y, id_, "coin")
        self.displayCharacter = "$"

    #---------------------------------------------------------------------------------------------------------------------------------------

    def determineCoin(self):
        if self.coinValue >= 1 and self.coinValue <=5:
            self.name = "a Coin"
        elif self.coinValue >= 6 and self.coinValue <= 10:
            self.name = "a Bronze Coin"
        elif self.coinValue >= 11 and self.coinValue <= 15:
            self.name = "a Silver Coin"
        elif self.coinValue >= 16 and self.coinValue <= 20:
            self.name = "a Gold Coin"

    #---------------------------------------------------------------------------------------------------------------------------------------

    def pickup(self, player):
        self.isDead = True
        player.coinBag += self.coinValue
        player.addMessage(player.name, "picked up", self.name, ".")

    #---------------------------------------------------------------------------------------------------------------------------------------

class Healing(Item):

    #---------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, x, y, id_):
        self.healingValue = random.randint(5, 80)
        self.name = 0
        super().__init__(x, y, id_, "healing")
        self.displayCharacter = "¤"

    #---------------------------------------------------------------------------------------------------------------------------------------

    def determineHealing(self, p = 0):
        if self.healingValue >= 5 and self.healingValue <= 15:
            self.name = "Kabob"
        elif self.healingValue >= 16 and self.healingValue <= 30:
            self.name = "Steak"
        elif self.healingValue >= 31 and self.healingValue <= 45:
            self.name = "Pizza"
        elif self.healingValue >= 46 and self.healingValue <= 60:
            self.name = "Bandages"
        elif self.healingValue >= 61 and self.healingValue <= 65:
            self.name = "Medkit"
        elif self.healingValue >= 71 and self.healingValue <= 75:
            self.name = "Golden Apple"
        elif self.healingValue >= 76 and self.healingValue <= 80:
            self.name = "Enchanted Golden Apple"
        self.price = p

    #---------------------------------------------------------------------------------------------------------------------------------------

    def pickup(self, player):
        canPickup = True
        if self.price > 0:
            canPickup = False
            if player.coinBag > self.price:
                buyItem = input("Would you like to buy this item for " + str(self.price) + " coins? ").lower()
                if buyItem == 'yes':
                    player.coinBag -= self.price
                    canPickup = True
            else:
                player.addMessage("You do not have enough money to do that.")
        if canPickup == True:
            self.isDead = True
            if player.baseHealth < player.baseMaxHealth:
                player.baseHealth += self.healingValue
                player.setHealth()
                player.addMessage(player.name, "picked up", self.name, player.name, "has healed", self.healingValue, "health.")
            else:
                player.inventory.addItem(self)

    #---------------------------------------------------------------------------------------------------------------------------------------

class Weapon(Item):

    #---------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, x, y, id_):
        self.damageValue = random.randint(1, 7)
        self.name = 0
        super().__init__(x, y, id_, "weapon")
        self.displayCharacter = "🗡️"

    #---------------------------------------------------------------------------------------------------------------------------------------

    def determineWeapon(self, p = 0):
        if self.damageValue >= 1 and self.damageValue <= 2:
            self.name = "Stick"
        elif self.damageValue >= 3 and self.damageValue <= 4:
            self.name = "Rock"
        elif self.damageValue >= 5:
            self.name = "Chipped Rock"
        elif self.damageValue == 6:
            self.name = "Knife"
        elif self.damageValue == 7:
            self.name = "Katana"
        self.price = p

    #---------------------------------------------------------------------------------------------------------------------------------------

    def pickup(self, player):
        canPickup = True
        if self.price > 0:
            canPickup = False
            if player.coinBag > self.price:
                buyItem = input("Would you like to buy this item for " + str(self.price) + " coins? ").lower()
                if buyItem == 'yes':
                    player.coinBag -= self.price
                    canPickup = True
            else:
                player.addMessage("You do not have enough money to do that.")
        if canPickup == True:
            self.isDead = True
            if player.inventory.addItem(self) != -1:
                player.addMessage(player.name, "picked up", self.name)

    #---------------------------------------------------------------------------------------------------------------------------------------

class Armor(Item):

    #---------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, x, y, id_):
        self.armorNegation = random.randint(45, 99)
        self.name = 0
        super().__init__(x, y, id_, "armor")
        self.displayCharacter = "🛡️"

    #---------------------------------------------------------------------------------------------------------------------------------------

    def determineArmor(self, p = 0):
        if self.armorNegation >= 81 and self.armorNegation <= 99:
            self.name = "Leather Armor"
        elif self.armorNegation >= 66 and self.armorNegation <= 80:
            self.name = "Chainmail"
        elif self.armorNegation >= 55 and self.armorNegation <= 65:
            self.name = "Iron Armor"
        elif self.armorNegation >= 50 and self.armorNegation <= 54:
            self.name = "Iron Armor"
        elif self.armorNegation >= 46 and self.armorNegation <= 49:
            self.name = "Diamond Armor"
        elif self.armorNegation >= 45:
            self.name = "Netherite Armor"
        self.price = p

    #---------------------------------------------------------------------------------------------------------------------------------------

    def pickup(self, player):
        canPickup = True
        if self.price > 0:
            canPickup = False
            if player.coinBag > self.price:
                buyItem = input("Would you like to buy this item for " + str(self.price) + " coins? ").lower()
                if buyItem == 'yes':
                    player.coinBag -= self.price
                    canPickup = True
            else:
                player.addMessage("You do not have enough money to do that.")
        if canPickup == True:
            self.isDead = True
            if player.inventory.addItem(self) != -1:
                player.addMessage(player.name, "picked up", self.name)

    #---------------------------------------------------------------------------------------------------------------------------------------

class Key(Item):

    #---------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, x, y, id_):
        self.name = 0
        super().__init__(x, y, id_, "key")
        self.displayCharacter = "1"

    #---------------------------------------------------------------------------------------------------------------------------------------

    def pickup(self, player):
        canPickup = True
        if self.price > 0:
            canPickup = False
            if player.coinBag > self.price:
                buyItem = input("Would you like to buy this item for " + str(self.price) + " coins? ").lower()
                if buyItem == 'yes':
                    player.coinBag -= self.price
                    canPickup = True
            else:
                player.addMessage("You do not have enough money to do that.")
        if canPickup == True:
            self.isDead = True
            player.keyInventory += 1
            player.addMessage(player.name, "picked up a key")

    #---------------------------------------------------------------------------------------------------------------------------------------

class Bomb(Item):

    #---------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, x, y, id_):
        self.name = 0
        super().__init__(x, y, id_, "bomb")
        self.displayCharacter = "0"

    #---------------------------------------------------------------------------------------------------------------------------------------

    def pickup(self, player):
        canPickup = True
        if self.price > 0:
            canPickup = False
            if player.coinBag > self.price:
                buyItem = input("Would you like to buy this item for " + str(self.price) + " coins? ").lower()
                if buyItem == 'yes':
                    player.coinBag -= self.price
                    canPickup = True
            else:
                player.addMessage("You do not have enough money to do that.")
        if canPickup == True:
            self.isDead = True
            player.bombInventory += 1
            player.addMessage(player.name, "picked up a bomb")

    #---------------------------------------------------------------------------------------------------------------------------------------

class Chest(Item):

    #---------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, x, y, id_):
        self.randomChest = random.randint(1, 100)
        self.name = 0
        super().__init__(x, y, id_, "chest")
        self.displayCharacter = "C"
        self.determineChest()

    #---------------------------------------------------------------------------------------------------------------------------------------

    def determineChest(self):
        if self.randomChest >= 1 and self.randomChest <= 59:
            self.name = "Chest"
        elif self.randomChest >= 60 and self.randomChest <= 89:
            self.name = "Stone Chest"
        elif self.randomChest >= 90 and self.randomChest <= 99:
            self.name = "Gold Chest"
        elif self.randomChest == 100:
            self.name = "Diamond Chest"

    #---------------------------------------------------------------------------------------------------------------------------------------

    def pickup(self, player):
        self.isDead = True
        if self.name == "Chest":
            player.addMessage(Text_Attributes.BOLD + player.name + " opened a(n) " + self.name + Text_Attributes.END)
            return 1
        elif self.name == "Stone Chest":
            openChest = input("Would you like to open this chest for 1 bomb? ").lower()
            if openChest == "yes":
                if player.bombInventory > 0:
                    player.bombInventory -= 1
                    player.addMessage(Text_Attributes.BOLD + player.name + " opened a(n) " + self.name + Text_Attributes.END)
                else:
                    player.addMessage(Text_Attributes.BOLD + "You don't have enough bombs to do this." + Text_Attributes.END)
            else:
                return 2
        elif self.name == "Gold Chest":
            openChest = input("Would you like to open this chest for 1 key? ").lower()
            if openChest == "yes":
                if player.keyInventory > 0:
                    player.keyInventory -= 1
                    player.addMessage(Text_Attributes.BOLD + player.name + " opened a(n) " + self.name + Text_Attributes.END)
                else:
                    player.addMessage(Text_Attributes.BOLD + "You don't have enough keys to do this." + Text_Attributes.END)
            else:
                return 3
        elif self.name == "Diamond Chest":
            openChest = input("Would you like to open this chest for 2 keys and 2 bombs? ").lower()
            if openChest == "yes":
                if player.bombInventory > 1 and player.keyInventory > 1:
                    player.keyInventory -= 2
                    player.bombInventory -= 2
                    player.addMessage(Text_Attributes.BOLD + player.name + " opened a(n) " + self.name + Text_Attributes.END)
                else:
                    player.addMessage(Text_Attributes.BOLD + "You don't have enough keys/bombs to do this." + Text_Attributes.END)
            else:
                return 4

    #---------------------------------------------------------------------------------------------------------------------------------------



class NPC():

    #---------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self, x, y, id_, NPC_type):
        self.position = Vec2(x, y)
        self.ID = id_
        self.isDead = False
        self.NPC_type = NPC_type
        self.displayCharacter = "~"

    #---------------------------------------------------------------------------------------------------------------------------------------

    def pickup(self, player):
        print("This message should never appear")

    #---------------------------------------------------------------------------------------------------------------------------------------

class Merchant():

    #---------------------------------------------------------------------------------------------------------------------------------------

    dialogue = 0

    #---------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def sayDialogue():
        if Merchant.dialogue == 0:
            Merchant.dialogue += 1
            return Text_Attributes.BOLD + "Hello traveler! Welcome to my humble shop." + Text_Attributes.END
        elif Merchant.dialogue == 1:
            Merchant.dialogue += 1
            return Text_Attributes.BOLD + "Here you can buy anything from keys and bombs to weapons and armor." + Text_Attributes.END
        elif Merchant.dialogue == 2:
            Merchant.dialogue += 1
            return Text_Attributes.BOLD + "You can choose anything you want from the three stands." + Text_Attributes.END
        elif Merchant.dialogue == 3:
            Merchant.dialogue = 0
            return Text_Attributes.BOLD + "Simply walk up to the stands and you can buy any item in exchange for gold." + Text_Attributes.END

    #---------------------------------------------------------------------------------------------------------------------------------------

class MysteryMan():

    #---------------------------------------------------------------------------------------------------------------------------------------

    dialogue = 0
    dialogueList = ["Who- who are you? And why are you down here? It's dangerous down here",
                    "You again? Why are you still down here? Get out before its too late.",
                    "Why am I here? I don't have to tell you anything. Now scram!" ,
                    "Since you don't seem to heed my warnings, I supposed I could tell you my story if it will get you to leave. Don't get too excited though. It'll come at at a price.",
                    "I am the lone survivor of a forgotten town.",
                    "I was apart of a peaceful town. It was usually quiet, though there was the occassional scuffle.",
                    "But on a sunny Wednesday, our village was raided by the Kargons. We were all wiped out. All of us but one. Me.", 
                    "Since that attack I've been chasing the Kargon king.",
                    "What? You were there too? Where did you hide? Your secret bunker?",
                    "Did you happen to do a kid named Jack? Yeah? That's amazing.",
                    "He was my son. He's the reason I'm still chasing the Kargon king.",
                    "You want me to join you? No, I fight alone. I'm better alone.",
                    "I won't join you. But if our paths ever cross again, I'll try to help you out.",
                    "Before I help you, I need you to bring some items to me.", 
                    "Let me see if I have anything for you right now."]

    #---------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def sayDialogue(player):
        if MysteryMan.dialogue < (len(MysteryMan.dialogueList) - 1):
            player.addMessage(Text_Attributes.BOLD + MysteryMan.dialogueList[MysteryMan.dialogue] + Text_Attributes.END)
            MysteryMan.dialogue += 1
            taskOne = False
            taskTwo = False
            taskThree = False
            taskFour = False
            taskFive = False
        elif MysteryMan.dialogue == (len(MysteryMan.dialogueList) - 1):
            task = input("I will help you, but first you have to bring me some items. Are you willing to bring them to me? ").lower()
            if task == 'yes':
                if taskOne == False:
                    if player.keyInventory >= 5:
                        taskOneItem = input("Will you get me 5 keys? ").lower()
                        if taskOneItem == 'yes':
                            player.keyInventory -= 5
                            taskOne = True
                        else:
                            player.addMessage(Text_Attributes.BOLD + "Come back when you have the item[s] I asked for" + Text_Attributes.END)
                if taskTwo == False:
                    if player.bombInventory >= 5:
                        taskTwoItem = input("Will you get me 5 bombs? ").lower()
                        if taskTwoItem == 'yes':
                            player.bombInventory -= 5
                            taskTwo = True
                        else:
                            player.addMessage(Text_Attributes.BOLD + "Come back when you have the item[s] I asked for" + Text_Attributes.END)
                if taskThree == False:
                    if len(player.healingSlot) >= 1 and player.inventory.healingSlot[0].name == "Golden Apple":
                        taskThreeItem = input("Will you get me a golden apple? ").lower()
                        if taskThreeItem == 'yes':
                            if player.inventory.healingSlot[0].name == "Golden Apple":
                                player.healingSlot = []
                                taskThree = True
                        else:
                            player.addMessage(Text_Attributes.BOLD + "Come back when you have the item[s] I asked for" + Text_Attributes.END)
                if taskFour == False:
                    if len(player.WeaponSlot) >= 1 and player.inventory.weaponSlot[0].name == "Katana":
                        taskFourItem = input("Will you get me a katana? ").lower()
                        if taskFourItem == 'yes':
                            if player.inventory.weaponSlot[0].name == "Katana":
                                player.WeaponSlot = []
                                taskFour = True
                        else:
                            player.addMessage(Text_Attributes.BOLD + "Come back when you have the item[s] I asked for" + Text_Attributes.END)
                if taskFive == False:
                    if len(player.armorSlot) >= 1 and player.inventory.armorSlot[0].name == "Diamond Armor":
                        taskFiveItem = input("Will you get me diamond armor? ").lower()
                        if taskFiveItem == 'yes':
                            if player.inventory.armorSlot[0].name == "Diamond Armor":
                                player.armorSlot = []
                                taskFive = True
                        else:
                            player.addMessage(Text_Attributes.BOLD + "Come back when you have the item[s] I asked for" + Text_Attributes.END)
                if taskOne and taskTwo and taskThree and taskFour and taskFive:
                    MysteryMan.dialogue += 1
            else:
                player.addMessage(Text_Attributes.BOLD + "Have it your way" + Text_Attributes.END)
        else:
            player.addMessage(Text_Attributes.BOLD + MysteryMan.dialogueList[len(MysteryMan.dialogueList) - 1] + Text_Attributes.END)
            MysteryManItem = random.randint(1,4)
            if MysteryManItem == 1:
                return "item"
            elif MysteryManItem >= 2:
                player.addMessage(Text_Attributes.BOLD + "Sorry kid, I don't have anything for you right now. Here, take this gold I found." + Text_Attributes.END)
                mysteryManCoins = random.randint(10, 25)
                player.coinBag += mysteryManCoins
                player.addMessage(player.name, "picked up", mysteryManCoins, "coins.")

    #---------------------------------------------------------------------------------------------------------------------------------------

class Blacksmith():

    @staticmethod
    def upgradePlayer(player):
        print(Text_Attributes.BOLD + "Would you like to upgrade your base health(1), your base damage(2), or your base defense(3)? " + Text_Attributes.END)
        try:
            determineUpgrade = int(input().lower())
            if determineUpgrade == 1:
                if player.baseMaxHealth < 150:
                    healthUpgradeCost = random.randint(100,150)
                    if player.coinBag >= healthUpgradeCost:
                        player.coinBag -= healthUpgradeCost
                        player.baseMaxHealth += 2
                        player.baseHealth += 2
                        healthUpgradeCost += 35 
                        player.hasStatUpgraded = True
            elif determineUpgrade == 2:
                if player.baseDamage < 10:
                    damageUpgradeCost = random.randint(200,300)
                    if player.coinBag >= damageUpgradeCost:
                        player.coinBag -= damageUpgradeCost
                        player.baseDamage += 1
                        damageUpgradeCost += 75
                        player.hasStatUpgraded = True
            elif determineUpgrade == 3:
                if player.baseDefenseNegation < 10 / 100:
                    defenseUpgradeCost = random.randint(300,500)
                    if player.coinBag >= defenseUpgradeCost:
                        player.coinBag -= defenseUpgradeCost
                        player.baseDefenseNegation += 1 / 100
                        defenseUpgradeCost += 75
                        player.hasStatUpgraded = True
        except:
            print("Cannot convert input to a number")

class Trader():

    @staticmethod
    def tradeWithPlayer(player):
        if player.bombInventory > 0 or player.keyInventory > 0:
            print(Text_Attributes.BOLD + "Would you like to trade two bombs for a key(1) or a two keys for a bomb(2) " + Text_Attributes.END)
            try:
                initiateTrade = int(input().lower())
                if initiateTrade == 1:
                    player.bombInventory -= 2
                    player.keyInventory += 1
                    player.hasPlayerTraded = True
                elif initiateTrade == 2:
                    player.keyInventory -= 2
                    player.bombInventory += 1
                    player.hasPlayerTraded = True
            except:
                print("Cannot convert input to a number")
        player.addMessage(Text_Attributes.BOLD + "Come back with more keys and bombs" + Text_Attributes.END)

class Collector():

    @staticmethod
    def buyFromPlayer(player):
        randomItemToBuy = random.randint(1,3)
        if randomItemToBuy == 1:
            if player.keyInventory > 0:
                randomKeyPrice = random.randint(15,20)
                print(Text_Attributes.BOLD + "I am willing to buy a key from you for " + str(randomKeyPrice) + " coins. Will you sell your key to me? " + Text_Attributes.END)
                sellKey = input().lower()
                if sellKey == "yes": 
                    player.keyInventory -= 1
                    player.coinBag += randomKeyPrice 
                    return
            player.addMessage(Text_Attributes.BOLD + "Come back later if you wish to trade with me." + Text_Attributes.END)
        elif randomItemToBuy == 2:
            if player.bombInventory > 0:
                randomBombPrice = random.randint(10,15)
                print(Text_Attributes.BOLD + "I am willing to buy a bomb from you for " + str(randomBombPrice) + " coins. Will you sell your bomb to me? " + Text_Attributes.END)
                sellBomb = input().lower()
                if sellBomb == "yes":
                    player.bombInventory -= 1
                    player.coinBag += randomBombPrice
                    return
            player.addMessage(Text_Attributes.BOLD + "Come back later if you wish to trade with me." + Text_Attributes.END)
        elif randomItemToBuy == 3:
            if len(player.inventory.healingSlot) > 0:
                randomHealingPrice = random.randint(25,35)
                print(Text_Attributes.BOLD + "I am willing to buy your healing from you for " + str(randomHealingPrice) + " coins. Will you sell your food for me? " + Text_Attributes.END)
                sellHealing = input().lower()
                if sellHealing == "yes":
                    player.inventory.healingSlot = []
                    player.coinBag += randomHealingPrice
                    return
            player.addMessage(Text_Attributes.BOLD + "Come back later if you wish to trade with me." + Text_Attributes.END)

class VendingMachine():

    @staticmethod
    def dispenseItem(player):
        print(Text_Attributes.BOLD + "Would you like to pay 50 coins for a random item? " + Text_Attributes.END)
        dispenseItem = input().lower()
        if dispenseItem == "yes":
            player.coinBag -= 50
            vendingMachineBreaks = random.randint(1,5)
            if vendingMachineBreaks == 1:
                player.addMessage(Text_Attributes.BOLD + "The vending machine broke!" + Text_Attributes.END)
                return "broke"
            return "item"
        else:
            pass



class Quest():

    def __init__(self, name, difficulty, questObjective, reward = False):
        self.questName = name 
        self.questDifficulty = difficulty
        self.questReward = reward
        self.questProgress = -1
        self.checkQuestObjective = questObjective
        
    def determineReward(self):
        if self.questReward == False:
            if self.questDifficulty == 1:
                self.questReward = random.randint(10,25)
            elif self.questDifficulty == 2:
                self.questReward = random.randint(25,50)
        return self.questReward



class OldLady():
    pass



class Artifact():

    def __init__(self, x, y, id_, itemType, price = 0):
        self.position = Vec2(x, y)
        self.ID = id_
        self.isDead = False
        self.type = itemType


        self.extraHealth = 0
        self.extraDamage = 0
        self.extraArmorNegation = 0
        self.higherCritChance = 0 / 100
        self.higherCritDamage = 0
        self.higherEvasionChance = 0

class HealingArtifact(Artifact):

    def __init__(self, x, y, id_):
        self.healthArtifactValue = random.randint(1,25)
        self.name = 0
        super().__init__(x, y, id_, "healing artifact")
        self.displayCharacter = "1"
        
    def determineExtraHealthArtifact(self):
        if self.healthArtifactValue >= 1 and self.healthArtifactValue <= 5:
            self.name = ""
            pass
        elif self.healthArtifactValue >= 6 and self.healthArtifactValue <= 10:
            pass
        elif self.healthArtifactValue >= 11 and self.healthArtifactValue <= 15:
            pass
        elif self.healthArtifactValue >= 16 and self.healthArtifactValue <= 20:
            pass
        elif self.healthArtifactValue >= 21 and self.healthArtifactValue <= 25:
            pass

class DamageArtifact(Artifact):

    def __init__(self, x, y, id_):
        self.damageArtifactValue = random.randint(1,10)
        self.name = 0
        super().__init__(x, y, id_, "damage artifact")
        self.displayCharacter = "2"

    def extraDamageArtifact(self):
        
        pass

class ArmorNegationArtifact(Artifact):

    def __init__(self, x, y, id_):
        self.armorNegationArtifactValue = random.randint(1 / 100, 10 / 100)
        self.name = 0
        super().__init__(x, y, id_, "armor negation artifact")
        self.displayCharacter = "3"

    def extraArmorNegationArtifact(self):
        
        pass

class CritChanceArtifact(Artifact):

    def __init__(self, x, y, id_):
        self.critChanceArtifactValue = random.randint(1 / 100, 10 / 100)
        self.name = 0
        super().__init__(x, y, id_, "crit chance artifact")
        self.displayCharacter = "4"

    def higherCritChanceArtifact(self):
        
        pass

class CritDamageArtifact(Artifact):

    def __init__(self, x, y, id_):
        self.critDamageArtifactValue = random.randint(1 / 100, 10 / 100)
        self.name = 0
        super().__init__(x, y, id_, "crit damage artifact")
        self.displayCharacter = "5"

    def higherCritDamageArtifact(self):
        pass

class EvasionArtifact(Artifact):

    def __init__(self, x, y, id_):
        self.evasionChanceArtifactCalue = random.randint(1 / 100, 10 / 100)
        self.name = 0
        super().__init__(x, y, id_, "evasion artifact")
        self.displayCharacter = "6"

    def higherEvasionChanceArtifact(self):
        pass


class Inventory():

    #---------------------------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        self.weaponSlot = []
        self.armorSlot = []
        self.healingSlot = []
        self.maxWeapon = 1
        self.maxArmor = 1
        self.maxHealing = 1

    #---------------------------------------------------------------------------------------------------------------------------------------

    def display(self):
        line = ""
        for weapon in self.weaponSlot:
            line = line + "[" + weapon.name + "]"
        for armor in self.armorSlot:
            line = line + "[" + armor.name + "]"
        for healing in self.healingSlot:
            line = line + "[" + healing.name + "]"
        if len(line) > 0:
            print(line)

    #---------------------------------------------------------------------------------------------------------------------------------------

    def reset(self):
        self.weaponSlot = []
        self.armorSlot = []
        self.healingSlot = []

    #---------------------------------------------------------------------------------------------------------------------------------------

    def addWeapon(self, item):
        if len(self.weaponSlot) >= self.maxWeapon:
            replaceItem = input("Would you like to replace your weapon with this weapon? Please enter 'Yes' or 'No': ").lower()
            if replaceItem == "yes":
                self.weaponSlot.pop(0)
                self.weaponSlot.append(item)
            else:
                return -1
        else:
            self.weaponSlot.append(item)
        return 0

    def addArmor(self, item):
        if len(self.armorSlot) >= self.maxArmor:
            replaceItem = input("Would you like to replace your armor with this armor? Please enter 'Yes' or 'No': ").lower()
            if replaceItem == "yes":
                self.armorSlot.pop(0)
                self.armorSlot.append(item)
            else:
                return -1
        else:
            self.armorSlot.append(item)
        return 0

    def addHealing(self, item):
        if len(self.healingSlot) >= self.maxHealing:
            replaceItem = input("Would you like to replace your healing item with this healing item? Please enter 'Yes' or 'No': ").lower()
            if replaceItem == "yes":
                self.healingSlot.pop(0)
                self.healingSlot.append(item) 
            else:
                return -1
        else:
            self.healingSlot.append(item)
        return 0

    def addItem(self, item):
        itemType = type(item)
        if itemType == Healing:
            return self.addHealing(item)
        elif itemType == Weapon:
            return self.addWeapon(item)
        elif itemType == Armor:
            return self.addArmor(item)

    #---------------------------------------------------------------------------------------------------------------------------------------


        
class Text_Attributes():

    #---------------------------------------------------------------------------------------------------------------------------------------

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    #---------------------------------------------------------------------------------------------------------------------------------------

    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BRIGHTGREEN = '\u001b[32;1m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    PURPLE = '\033[95m' 
    MAGENTA = '\u001b[35m' 
    BLACK = '\u001b[30m'
    WHITE = '\u001b[37m' 

    #---------------------------------------------------------------------------------------------------------------------------------------

    END = '\033[0m'

    #---------------------------------------------------------------------------------------------------------------------------------------



if __name__ == "__main__": 
    GM = GameManager()
    GM.update()

''' Storyline: You used to live in a quiet, peaceful village in the middle of a forest, hidden from the world. At least, you THOUGHT you were hidden.
But on a quiet Saturday, your village began to shake. What you thought was an earthquake turned out to be the hooves of hundreds of horses.
You people tried to reason with the riders of the horses, the Kargons, but they wouldn't listen. They attacked, pillaging the village and plundering each house they passes.
They took everything, including you friends and family. You only escaped by hiding you secret bunker. 
Now you must fight through the hordes of Kargons to reach their leader. You need to defeat their leader and free your people to restore peace to your village. '''


#HomeWork: Artifacts, Finish Vending Machine Quest, Fog of War


#Extra Homework: Add chests, Try to find emoji's[All emojis are too big], Quests


#New door always leads to boss room


#hi