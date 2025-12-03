import arcade

TILE_SIZE = 32  # pixels per tile

# Player can propose tradeOffer to Trader actors

class Player:
    # Initialize player with name and location (left/topmost cell)
    def __init__(self, name, location):
        self.name = name
        self.location = location  # (x, y) tuple
        self.sprite = arcade.Sprite("assets/player.png", scale=0.5)  # Load player sprite
        self.sprite.center_x = location[0] * TILE_SIZE + TILE_SIZE // 2
        self.sprite.center_y = location[1] * TILE_SIZE + TILE_SIZE // 2

    def add_to_sprite_list(self, sprite_list):
        sprite_list.append(self.sprite)

    def propose_trade(self, trader, trade_offer):
        # trade_offer is a dictionary consisting of {'item': item, 'quantity': quantity}
        item = trade_offer['item']
        quantity = trade_offer['quantity']

        if trader.evaluate_trade_offer(trade_offer):
            print(f"Trade accepted: {self.name} trades {quantity} of {item} with {trader.name}.")
            trade_offer['quantity'] -= quantity  # deduct traded items from player's inventory
            trader.inventory[item] = trader.inventory.get(item, 0) + quantity  # add items to trader's inventory
        elif trader.counter_trade_offer(trade_offer):
            counter_offer = trader.counter_trade_offer(trade_offer)
            print(f"Trade countered: {trader.name} offers {counter_offer['quantity']} of {counter_offer['item']} in exchange.")
            # Player can choose to accept or reject the counter offer
            if self.evaluate_counter_offer(counter_offer):
                print(f"Counter trade accepted: {self.name} trades {counter_offer['quantity']} of {counter_offer['item']} with {trader.name}.")
                counter_offer['quantity'] -= counter_offer['quantity']  # deduct traded items from player's inventory
                trader.inventory[counter_offer['item']] = trader.inventory.get(counter_offer['item'], 0) + counter_offer['quantity']  # add items to trader's inventory
            else:
                print(f"Counter trade rejected by {self.name}.")
        else:
            print(f"Trade rejected by {trader.name}.")

    def evaluate_counter_offer(self, counter_offer):
        # Simple temp logic: accept if quantity is less than or equal to 10
        return counter_offer['quantity'] <= 10

    def draw(self):
        self.sprite.draw()

