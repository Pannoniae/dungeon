import random
import sys
from enum import Enum, auto
from typing import List, Tuple, Optional


class Item:
    name:str = "Generic Item"
    def __init__(self, player: "Hero"):
        self.is_cursed = (random.random() < 0.2)
        self.player = player

    def use(self):
        pass

class Scroll(Item):
    name = "Scroll"

    def use(self):
        if self.is_cursed:
            self.player.takeDamage(self.player.hp * 0.25)
            print("AAAAAH! Your scroll backfired!")
        else:
            if len(self.player.room.monsters) > 0:
                for monster in self.player.room.monsters:
                    monster.takeDamage(self.player.hp * 0.25)
                print("Huzzah! Your scroll damaged all your enemies!")
            else:
                print("You have used the scroll but there were no enemies.")
class Ring(Item):
    name = "Ring"

class Potion(Item):
    name = "Potion"
    def use(self):
        if self.is_cursed:
            Game.inst.killPlayer()
        else:
            self.player.hp += 30
            # cap to 100
            self.player.hp = min(self.player.hp, 100)
            print("You have healed yourself.")


class Direction(Enum):
    NORTH = auto()
    NORTHEAST = auto(),
    EAST = auto(),
    SOUTHEAST = auto(),
    SOUTH = auto(),
    SOUTHWEST = auto(),
    WEST = auto(),
    NORTHWEST = auto()

    @classmethod
    def has_key(cls, name):
        return name in cls.__members__


def randomMonster(room: "Room"):
    return random.choice([Goblin(room), Orc(room), Dragon(room), Gnome(room)])


def randomItem(hero: "Hero"):
    return random.choice([Scroll(hero), Ring(hero), Potion(hero)])


class Room:
    def __init__(self, id: int, *exits: Tuple[Direction, int]):
        self.id = id
        self.description: Optional[str] = None
        self.gold: int = 0
        self.items: List[Item] = []
        self.monsters: List[Monster] = []
        self.exits: List[Tuple[Direction, int]] = list(exits)


    def initContents(self):
        if self.id != 0 and self.id != 10: # not starting room/ending room
            if random.random() < 0.2:
                self.monsters.append(randomMonster(Game.inst.map.rooms[self.id]))
            if random.random() < 0.1:
                    self.items.append(randomItem(Game.inst.player))

    def setGold(self, gold: int):
        self.gold = gold

    def setDescription(self, description: str):
        self.description = description

    def kill(self, monster: "Monster"):
        self.monsters.remove(monster)


class Entity:
    def __init__(self, room: Room):
        self.hp: int = 100
        self.item: Optional[Item] = None
        self.room: Room = room

    def takeDamage(self, dmg: float):
        self.hp -= dmg


class Monster(Entity):
    name: str = "Monster"
    mindmg: int = 5
    maxdmg: int = 15
    def __init__(self, room: Room):
        super().__init__(room)

    pass

    def attack(self, player: "Hero"):
        dmg = random.randint(self.mindmg, self.maxdmg)
        player.takeDamage(dmg)
        print(f"Ouch! You have received {dmg} damage.")
        if player.hp <= 0:
            Game.inst.killPlayer()



class Goblin(Monster):
    name = "Goblin"
    mindmg: int = 5
    maxdmg: int = 15

class Orc(Monster):
    name = "Orc"
    mindmg: int = 10
    maxdmg: int = 20

    def takeDamage(self, dmg: int):
        self.hp -= dmg * 0.75

class Dragon(Monster):
    name = "Dragon"
    mindmg: int = 10
    maxdmg: int = 20

    def takeDamage(self, dmg: int):
        self.hp -= dmg * 0.75

class Gnome(Monster):
    pass


class Hero(Entity):
    def __init__(self, room: Room):
        super().__init__(room)
        self.gold: int = 0

    def moveTo(self, room: Room):
        self.room = room

    def pickup(self, gold: int):
        self.gold = gold
        self.room.setGold(0)

    def dropItem(self):
        item = self.item
        self.room.items.append(item)
        self.item = None

    def pickupItem(self):
        if self.item:
            print("Can't pick up any more.")
            return
        item = self.room.items[len(self.room.items) - 1]
        self.item = item
        self.room.items.remove(item)

    def useItem(self):
        self.item.use()
        self.item = None

    def attack(self, monster: int):
        dmg = random.randint(5, 30)
        self.room.monsters[monster].takeDamage(dmg)
        print(f"You have attacked the monster for {dmg} damage.")
        if self.room.monsters[monster].hp <= 0:
            self.room.kill(self.room.monsters[monster])
            print("You have slain the monster.")

    def specialAttack(self, monster: int):
        pass

    def takeDamage(self, dmg: float):
        if self.item is Ring:
            if self.item.is_cursed:
                self.hp -= dmg * 1.1
            else:
                self.hp -= dmg * 0.9
        else:
            self.hp -= dmg

class Barbarian(Hero):

    def specialAttack(self, monster: int):
        if random.random() < 0.25:
            self.room.kill(self.room.monsters[monster])
            print("You have killed the monster with your powerful blow.")
        else:
            print("Whoosh... you swung your axe and hit nothing.")


class Wizard(Hero):

    def specialAttack(self, monster: int):
        for _monster in self.room.monsters:
            _monster.hp -= 10
        print("Your spell reduced the health of all monsters in the room!")


class Map:
    def __init__(self):
        self.rooms: List[Room] = []
        # 0
        self.rooms.append(Room(0, (Direction.EAST, 1)))
        # 1
        self.rooms.append(Room(1, (Direction.NORTH, 2), (Direction.NORTHEAST, 3), (Direction.SOUTHEAST, 4), (Direction.WEST, 0)))
        # 2
        self.rooms.append(Room(2, (Direction.SOUTH, 1), (Direction.EAST, 3)))
        # 3
        self.rooms.append(Room(3, (Direction.WEST, 2), (Direction.SOUTHWEST, 1), (Direction.SOUTHEAST, 6)))
        # 4
        room = Room(4, (Direction.NORTHWEST, 1), (Direction.EAST, 5), (Direction.SOUTHWEST, 4), (Direction.SOUTH, 4), (Direction.SOUTHEAST, 4))
        room.setDescription("The room is a strange maze.")
        self.rooms.append(room)
        # 5
        self.rooms.append(Room(5, (Direction.WEST, 4), (Direction.EAST, 6), (Direction.NORTHEAST, 8)))
        # 6
        self.rooms.append(Room(6, (Direction.WEST, 5)))
        # 7
        self.rooms.append(Room(7, (Direction.WEST, 1), (Direction.EAST, 8)))
        # 8
        self.rooms.append(Room(8, (Direction.WEST, 7), (Direction.NORTHWEST, 3), (Direction.SOUTHWEST, 5), (Direction.EAST, 9)))
        # 9
        self.rooms.append(Room(9, (Direction.WEST, 8), (Direction.NORTH, 10)))
        # 10
        self.rooms.append(Room(10, (Direction.SOUTH, 9)))

    def getRoomInDirection(self, room: Room, direction: Direction) -> Optional[Room]:
        for exit in room.exits:
            if exit[0] == direction:
                return self.rooms[exit[1]]
        return None


class Phase:
    NORMAL = auto()
    ATTACK = auto()
    WON = auto()
    LOST = auto()


class Game:

    inst: "Game"

    def __init__(self):
        Game.inst = self
        self.turn: int = 0
        self.map = Map()
        choice = input("Choose your hero: (B)arbarian or (W)izard)")
        if choice.lower().startswith("b"):
            self.player = Barbarian(self.map.rooms[0])
        elif choice.lower().startswith("w"):
            self.player = Wizard(self.map.rooms[0])
        else:
            print("Invalid option.")
            sys.exit()
        self.phase = Phase.NORMAL
        for room in self.map.rooms:
            room.initContents()

    def endTurn(self):
        # Process monster before end of turn
        if Phase.ATTACK:
            for monster in self.player.room.monsters:
                monster.attack(self.player)
        self.turn += 1

    def run(self):

        while not (self.phase == Phase.LOST or self.phase == Phase.WON):
            # if no monsters, return back to normal
            if len(self.player.room.monsters) == 0:
                self.phase = Phase.NORMAL
            if Phase.NORMAL:
                # print info
                print("You are in a room.")
                if self.player.room.description:
                    print(self.player.room.description)
                print(f"You have {self.player.gold} gold and {self.player.hp} HP.")

                if self.player.room.gold > 0:
                    gold = self.player.room.gold
                    self.player.pickup(gold)
                    print(f"You picked up {gold} gold.")
                # if there are items
                if len(self.player.room.items) > 0:
                    print("There are the following items in the room:")
                for item in self.player.room.items:
                    print(f"{item.name},")
                # if there are monsters
                if len(self.player.room.monsters) > 0:
                    print("There are the following monsters in the room:")
                for i, monster in enumerate(self.player.room.monsters):
                    print(f"{i}th enemy: {monster.name} with HP {monster.hp},")

            # print prompt
            print("M direction to move, D to drop, P to pick up, A to attack nth enemy, B to use special ability on nth enemy, U to use item.")

            action = input()
            if Phase.NORMAL:
                if action.lower().startswith("m"):
                    try:
                        arg = action.split()[1]
                    except IndexError:
                        print("Invalid move.")
                        continue

                    if not Direction.has_key(arg.upper()):
                        print("Invalid move.")
                        continue
                    dir = Direction[arg.upper()]
                    # move
                    room = self.map.getRoomInDirection(self.player.room, dir)
                    if room is None:
                        print("You can't move there.")
                        continue

                    # if monster in current room, cant leave
                    if len(self.player.room.monsters) != 0:
                        print("You can't leave a room while fighting.")
                        continue
                    self.player.moveTo(room)
                    print("You moved to a new room.")
                    self.endTurn()
                elif action.lower().startswith("d"):
                    self.player.dropItem()
                    print("You've dropped an item.")
                    self.endTurn()
                elif action.lower().startswith("p"):
                    if len(self.player.room.items) > 0:
                        self.player.pickupItem()
                        print("You've picked up an item.")
                        self.endTurn()
                    else:
                        print("There's nothing to pick up.")
                elif action.lower().startswith("u"):
                    if self.player.item:
                        self.player.useItem()
                        self.endTurn()
                    else:
                        print("You have no item to use.")
                else:
                    print("You can't do that.")

            # you can attack in normal/attack phase
            if action.lower().startswith("a"):
                try:
                    arg = int(action.split()[1])
                except IndexError:
                    print("Invalid attack.")
                    continue
                if len(self.player.room.monsters) > 0:
                    self.phase = Phase.ATTACK
                    self.player.attack(arg)
                    self.endTurn()
                    continue
            elif action.lower().startswith("b"):
                try:
                    arg = int(action.split()[1])
                except IndexError:
                    print("Invalid attack.")
                    continue
                if len(self.player.room.monsters) > 0:
                    self.phase = Phase.ATTACK
                    self.player.specialAttack(arg)
                    self.endTurn()
                    continue
            continue

    def killPlayer(self):
        self.player = None
        self.phase = Phase.LOST
        print("Ouch, you are dead.")
