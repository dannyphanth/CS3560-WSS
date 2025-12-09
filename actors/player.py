from actors.actor import Actor
import random
from dataclasses import dataclass
from world.map import TILE_SIZE
from ai.brains import * 

# Player can propose tradeOffer to Trader actors

@dataclass(eq=False)
class Player(Actor):
    # Initialize player with name and location (left/bottommost cell)
    def __init__(self, name, location, inventory, strength=100):
        super().__init__(
            name = name,
            location = location,
            inventory = inventory,
            texture_path="assets/player.png",
        )
        self.strength: int = strength
        self.brain: Brain = CautiousBrain()


    def printStats(self): 
        print(f"Gold\tFood\tWater\tStrgth\tMax Items")
        print(f"{self.inventory.gold}\t{self.inventory.food}\t{self.inventory.water}\t{self.strength}\t{self.inventory.max_items}")
        

    def set_location(self, location):
        self.location = location
        self.sprite.center_x = location[0] * TILE_SIZE + TILE_SIZE // 2
        self.sprite.center_y = location[1] * TILE_SIZE + TILE_SIZE // 2
        self.strength -= 1  # reduce strength by 1 for each movement
        # print(f"{self.name} to {self.location}. Remaining strength: {self.strength}")
      

    def propose_trade(self, trader, player_items_presenting, player_items_requesting):
        # player_items_presenting is a dictionary consisting of what the player is giving {'item': item, 'quantity': quantity}
        # player_items_requesting is a dictionary consisting of what the player wishes to receive{'item': item, 'quantity': quantity}
        item_given = player_items_presenting['item']
        quantity_given = player_items_presenting['quantity']

        item_requested = player_items_requesting['item']
        quantity_requested = player_items_requesting['quantity']

        # print current inventories
        print(f"\nCurrent Player Inventory: ")
        self.inventory.show_inventory()
        print(f"Current Trader Inventory:")
        trader.inventory.show_inventory()
        print(f"\n------------- Trade Proposal from {self.name} to {trader.name} -----------\n")
        print(f"{self.name} offers {quantity_given} of {item_given} in exchange for {quantity_requested} of {item_requested}.\n")

        if trader.evaluate_trade_offer(player_items_presenting, player_items_requesting):
            self.update_inventory_after_trade(item_given, quantity_given, item_requested, quantity_requested)
            trader.inventory.add(item_given, quantity_given) # add items to trader's inventory
            trader.inventory.spend(item_requested, quantity_requested) # deduct requested items from trader's inventory
        
            print(f"Updated Trader {trader.name} Inventory:")
            trader.inventory.show_inventory()
            print("------------------ End of Trade Proposal ----------------\n")
        
        elif trader.counter_trade_offer(player_items_presenting, player_items_requesting):
            # counter offer consists of {'item': item_requested, 'quantity': counter_quantity_requested, 'item_given': item_given, 'quantity_given': counter_quantity_given
            counter_offer = trader.counter_trade_offer(player_items_presenting, player_items_requesting)
            
            # player can choose to accept or reject the counter offer
            if self.evaluate_counter_offer(counter_offer):
                print(f"Counter trade accepted: {self.name} receives {counter_offer['quantity']} of {counter_offer['item']} for {counter_offer['quantity_given']} of {counter_offer['item_given']} from {trader.name}.")
                
                # player updates its inventory: giving item_given, receiving item
                self.update_inventory_after_trade(
                    item_given = counter_offer['item_given'],          # player gives this item
                    quantity_given = counter_offer['quantity_given'],  # player gives this quantity
                    item_requested = counter_offer['item'],            # player receives this item
                    quantity_requested = counter_offer['quantity']     # player receives this quantity
                )
                
                # trader updates its inventory: receiving item_given, giving item
                trader.update_inventory_after_trade(
                    item_given = counter_offer['item_given'],          # trader receives the item the player gave
                    quantity_given = counter_offer['quantity_given'],  # trader receives the quantity the player gave
                    item_requested = counter_offer['item'],            # trader gives the item the player received
                    quantity_requested = counter_offer['quantity']     # trader gives the quantity the player received
                )

                print("------------------ End of Counter Trade ----------------\n")
            else:
                print(f"Counter trade rejected by {self.name}.")
        
        else:
            print(f"Trade rejected by {trader.name}.")


    def evaluate_counter_offer(self, counter_offer):
        # Simple temp logic: accept if quantity is less than or equal to 10
        return counter_offer['quantity'] <= 10


    def is_at_trader_location(self, trader):
        tile_above = (trader.location[0], trader.location[1] + 1)
        tile_left = (trader.location[0] - 1, trader.location[1])
        tile_right = (trader.location[0] + 1, trader.location[1])
        tile_below = (trader.location[0], trader.location[1] - 1) 

        if self.location == tile_above or self.location == tile_left or self.location == tile_right or self.location == tile_below:
            print("Player is adjacent to Trader, initiating trade...")

            # randomize the trade offer
            if self.inventory:
                # prevent trading the entire inventory (must leave at least 1)
                item_offered = self.random_resource()
                max_quantity_available = self.inventory.balance(item_offered)
                
                # max_offerable is at least 1 less than total; if available is 1 or 0, max_offerable is 0 or less
                max_offerable = max(0, max_quantity_available - 1) 

                # quantity must be between 1 and max_offerable; if max_offerable < 1, quantity is 0
                if max_offerable >= 1:
                    quantity_offered = random.randint(1, max_offerable)
                else:
                    quantity_offered = 0 # cannot offer if max_offerable is 0 (i.e., inventory is 1 or 0)

                player_items_presenting = {'item': item_offered, 'quantity': quantity_offered}

                # randomly pick item to request (quantity is arbitrary, up to 10 for simplicity)
                item_requested = self.random_resource()
                quantity_requested = random.randint(1, 10) 
                
                player_items_requesting = {'item': item_requested, 'quantity': quantity_requested}
                
                # only propose trade if the player has something to offer (quantity > 0)
                if quantity_offered > 0:
                    self.propose_trade(trader, player_items_presenting, player_items_requesting)
                else:
                    print(f"Player has too little {item_offered} to offer in trade (must leave at least 1 in inventory).")
            else:
                print("Player has no inventory to trade.")