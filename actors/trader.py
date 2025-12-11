from actors.actor import Actor
from dataclasses import dataclass
from world.map import TILE_SIZE


@dataclass(eq=False)
class Trader(Actor):
    def __init__(self, name, location, inventory, texture_path="assets/trader.png"):
        super().__init__(
            name=name,
            texture_path=texture_path,
            location=location,
            inventory=inventory,
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
        """
        Counter-offer rule:
        - Keep the same resources as the original proposal.
        - Increase how much the player must give (ask for more of the offered item).
        - Keep the trader's give-amount (requested resource) the same, but never exceed stock.
        Example: player offers 1 gold for 4 food -> counter: 2 gold for 4 food.
        """
        item_given = player_items_presenting["item"]
        quantity_given = player_items_presenting["quantity"]

        item_requested = player_items_requesting["item"]
        quantity_requested = player_items_requesting["quantity"]

        max_quantity_available = self.inventory.balance(item_requested)
        if max_quantity_available <= 0:
            return None  # cannot counter if trader has none of the requested resource

        # Trader will give at most what they have, and no more than originally requested
        counter_quantity_requested = min(quantity_requested, max_quantity_available)

        # Ask the player for half of what the trader will give (rounded up), same resource as offered
        counter_quantity_given = max(1, (counter_quantity_requested + 1) // 2)

        print(
            f"\nTrade counter-offer: {self.name} offers "
            f"{counter_quantity_requested} of {item_requested} "
            f"for {counter_quantity_given} of {item_given}.\n"
        )

        return {
            'item': item_requested,
            'quantity': counter_quantity_requested,
            'item_given': item_given,
            'quantity_given': counter_quantity_given
        }





#==============================================================
# Greedy Trader
#==============================================================
class GreedyTrader(Trader):
    """
    A stricter, greedy trader:
    - Accepts only if player offers at least as much as they are requesting (>= 1:1).
    - Counter: gives at most half of the requested amount (rounded down, capped by stock),
      asks the player for the full requested amount of the offered resource.
    """

    def __init__(self, name, location, inventory):
        super().__init__(
            name=name,
            location=location,
            inventory=inventory,
            texture_path="assets/greedyTrader.png",
        )

    def evaluate_trade_offer(self, player_items_presenting, player_items_requesting):
        item_given = player_items_presenting["item"]
        q_given = player_items_presenting["quantity"]

        item_requested = player_items_requesting["item"]
        q_requested = player_items_requesting["quantity"]

        trader_has_stock = self.inventory.balance(item_requested) >= q_requested
        # Greedy: player must offer at least as much as they are asking for
        is_reasonable_offer = q_given >= q_requested

        if trader_has_stock and is_reasonable_offer:
            print(
                f"Greedy trade accepted: {self.name} trades "
                f"{q_requested} of {item_requested} for {q_given} of {item_given}.\n"
            )
            return True

        if not trader_has_stock:
            print(
                f"Greedy trade rejected: {self.name} does not have enough "
                f"{item_requested}."
            )
            return False

        print(
            f"Greedy trade rejected: {self.name} demands at least a 1:1 quantity "
            f"(player must offer >= requested)."
        )
        return False

    def counter_trade_offer(self, player_items_presenting, player_items_requesting):
        """
        Greedy counter:
        - Same resources as original.
        - Trader offers at most half of requested (rounded down), capped by stock.
        - Player must give the full requested amount of what they offered.
        """
        item_given = player_items_presenting["item"]
        q_given = player_items_presenting["quantity"]

        item_requested = player_items_requesting["item"]
        q_requested = player_items_requesting["quantity"]

        max_stock = self.inventory.balance(item_requested)
        if max_stock <= 0:
            return None  # cannot counter if trader has none to give

        # Trader gives at most half of requested (rounded down), but at least 1, capped by stock
        counter_q_requested = max(1, min(q_requested // 2, max_stock))
        # Player must give the full amount they originally requested
        counter_q_given = q_requested

        print(
            f"\nGreedy counter-offer: {self.name} offers "
            f"{counter_q_requested} of {item_requested} "
            f"for {counter_q_given} of {item_given}.\n"
        )

        return {
            "item": item_requested,
            "quantity": counter_q_requested,
            "item_given": item_given,
            "quantity_given": counter_q_given,
        }
