import tkinter as tk
from tkinter import Canvas

class Node:
    def __init__(self, player, history, state_bot=None, state_manuel=None, depth=0, gain=(0, 0), max_turns=6, price=0):
        self.player = player  # "Bot", "Manuel", "Chance", or None (leaf)
        self.history = history  # List of actions taken so far
        self.state_bot = state_bot  # None, "A", "V"
        self.state_manuel = state_manuel  # None, "A", "V"
        self.children = []
        self.depth = depth  # Depth in the tree
        self.gain = gain  # Gain accumulé jusqu'à ce nœud (gain_bot, gain_manuel)
        self.max_turns = max_turns  # Maximum number of turns
        self.price = price  # Current price

    def is_leaf(self):
        return self.player is None

    def possible_actions(self):
        if self.player == "Chance":
            return ["Good", "Bad"]
        elif self.player == "Bot":
            state = self.state_bot
        elif self.player == "Manuel":
            state = self.state_manuel
        else:
            return []

        if state is None:
            return ["A", "R"]  # Can buy or do nothing
        elif state == "A":
            return ["R", "V"]  # Can do nothing or sell
        elif state == "V":
            return ["A", "R"]  # Can do nothing or buy again

    def build_children(self):
        if self.depth >= self.max_turns * len(self.next_player().__doc__):  # Each turn has steps based on the player order
            return  # End of tree
        next_player = self.next_player()
        for action in self.possible_actions():
            new_history = self.history + [(self.player, action, self.price)]
            new_state_bot = self.state_bot
            new_state_manuel = self.state_manuel
            gain_bot, gain_manuel = self.gain
            new_price = self.price

            # Update states, calculate gain, and adjust price
            if self.player in ["Bot", "Manuel"]:
                if self.player == "Bot":
                    new_state_bot = self.update_state(self.state_bot, action)
                else:
                    new_state_manuel = self.update_state(self.state_manuel, action)

                if action == "A":
                    if self.player == "Bot":
                        gain_bot -= 1
                    else:
                        gain_manuel -= 1
                    new_price += 1  # Price increases when buying
                elif action == "V":
                    if self.player == "Bot":
                        gain_bot += self.calculate_sell_gain("Bot", new_price)
                    else:
                        gain_manuel += self.calculate_sell_gain("Manuel", new_price)
                    new_price -= 1  # Price decreases when selling
            elif self.player == "Chance":
                new_price += 1 if action == "Good" else -1  # Price changes based on chance

            child = Node(next_player, new_history, new_state_bot, new_state_manuel, self.depth + 1, (gain_bot, gain_manuel), self.max_turns, new_price)
            self.children.append(child)
            child.build_children()

    def calculate_sell_gain(self, player, current_price):
        if player == "Bot" and self.state_bot == "A":
            buy_price = next((price for p, a, price in reversed(self.history) if p == "Bot" and a == "A"), self.price)
            return current_price - buy_price
        elif player == "Manuel" and self.state_manuel == "A":
            buy_price = next((price for p, a, price in reversed(self.history) if p == "Manuel" and a == "A"), self.price)
            return current_price - buy_price
        return 0

    def next_player(self):
        # Add an extra turn for "Bot" after "Chance"
        order = ["Bot", "Chance", "Manuel", "Chance"]
        if self.depth + 1 >= len(order) * self.max_turns:
            return None  # Feuille
        return order[(self.depth + 1) % len(order)]

    def update_state(self, current_state, action):
        if action == "A":
            return "A"
        elif action == "V":
            return "V"
        else:
            return current_state

    def display(self, indent=0):
        if self.is_leaf():
            # Afficher uniquement les histoires terminales
            print(f"Historique: {self.history}, Gain: {self.gain}")
        for child in self.children:
            child.display(indent + 1)

# Fonction pour dessiner l'arbre dans une interface graphique
def draw_tree(canvas, node, x, y, x_offset, y_offset):
    if node is None:
        return

    # Dessiner le nœud
    gain_bot, gain_manuel = node.gain
    player = node.player if node.player != "None" else ""
    node_text = f"{player}\n({gain_bot}, {gain_manuel})\n{node.price}".strip() if node.player else f"({gain_bot}, {gain_manuel})".strip()
    canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill="lightblue")
    canvas.create_text(x, y, text=node_text, font=("Arial", 10))

    # Ajouter les labels des actions possibles
    if not node.is_leaf():
        actions = node.possible_actions()
        if actions:
            actions_text = ", ".join(actions)
            canvas.create_text(x, y + 30, text=f"{actions_text}", font=("Arial", 8), fill="darkgreen")

    # Dessiner les enfants
    child_x = x - x_offset * (len(node.children) - 1) // 2
    for child in node.children:
        canvas.create_line(x, y + 20, child_x, y + y_offset - 20, arrow=tk.LAST)
        draw_tree(canvas, child, child_x, y + y_offset, x_offset // 2, y_offset)
        child_x += x_offset


# Création de la racine avec un paramètre pour le nombre de tours
max_turns = 4
root = Node("Bot", [], max_turns=max_turns)
root.build_children()
root.display()

# Interface graphique
window = tk.Tk()
window.title("Arbre de Modélisation")
canvas = Canvas(window, width=1200, height=800, bg="white")
canvas.pack()

# Dessiner l'arbre
draw_tree(canvas, root, 600, 50, 600, 125/max_turns)

# Lancer l'interface graphique
window.mainloop()