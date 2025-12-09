from actors.actor import Actor
from dataclasses import dataclass
from world.map import TILE_SIZE


@dataclass(eq=False)
class Trader(Actor):
    def __init__(self, name, location, inventory):
        super().__init__(
            name = name,
            location = location,
            inventory = inventory,
            texture_path="assets/trader.png",
        )


    def evaluate_trade_offer(self, player_items_presenting, player_items_requesting):
        # accept only if quantity is reasonable AND trader has stock
        item_given = player_items_presenting['item']
        quantity_given = player_items_presenting['quantity']

        item_requested = player_items_requesting['item']
        quantity_requested = player_items_requesting['quantity']

        trader_has_stock = self.inventory.balance(item_requested) >= quantity_requested
        
        # fairness condition: player must offer at least half the quantity they are requesting (e.g., offer 5 gold for 10 water)
        is_reasonable_offer = quantity_given >= (quantity_requested / 2)

        if trader_has_stock and is_reasonable_offer:
            print(f"Trade accepted: {self.name} trades {quantity_requested} of {item_requested} for {quantity_given} of {item_given}.\n")
            return True
        elif not trader_has_stock:
            print(f"Trade rejected: {self.name} does not have enough {item_requested}.")
            # fall-through to counter-offer
            return False
        elif not is_reasonable_offer:
            print(f"Trade rejected: {self.name} finds the offer quantity too low (requires at least half of requested amount).")
            # fall-through to counter-offer
            return False


    def counter_trade_offer(self, player_items_presenting, player_items_requesting):
        # simple logic: counter with some quantity that trader is guaranteed to have
        # make proportional counter-offer to initial offer
        
        item_given = player_items_presenting['item']
        quantity_given = player_items_presenting['quantity']

        item_requested = player_items_requesting['item']
        quantity_requested = player_items_requesting['quantity']

        # determine max quantity available for requested item
        max_quantity_available = self.inventory.balance(item_requested)

        # counter with half the requested quantity, but not more than available
        counter_quantity_requested = min(max_quantity_available, max(1, quantity_requested // 2))

        # calculate proportional quantity to give
        proportion = counter_quantity_requested / quantity_requested
        counter_quantity_given = max(1, int(quantity_given * proportion))

        print(f"\nTrade counter-offer: {self.name} offers {counter_quantity_requested} of {item_requested} for {counter_quantity_given} of {item_given}.\n")
        
        return {
            'item': item_requested,
            'quantity': counter_quantity_requested,
            'item_given': item_given,
            'quantity_given': counter_quantity_given
        }
