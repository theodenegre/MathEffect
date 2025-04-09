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
        if self.depth >= self.max_turns * 7:  # Each turn has steps based on the player order
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
            return current_price - buy_price + 1
        elif player == "Manuel" and self.state_manuel == "A":
            buy_price = next((price for p, a, price in reversed(self.history) if p == "Manuel" and a == "A"), self.price)
            return current_price - buy_price + 1
        return 0

    def next_player(self):
        # Add an extra turn for "Bot" after "Chance"
        order = ["Bot", "Chance", "Manuel", "Chance", "Bot"]
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

    def compute_subgame_perfect_equilibrium(self):
        """
        Calcule les équilibres parfaits en sous-jeux en commençant par les feuilles.
        Retourne un tuple (optimal_action, gains) où gains est (gain_bot, gain_manuel)
        """
        # Cas de base: feuille
        if self.is_leaf():
            return None, self.gain

        # Calcul des gains pour chaque action possible
        action_gains = {}
        for i, child in enumerate(self.children):
            actions = self.possible_actions()
            if i < len(actions):  # Vérification de sécurité
                action = actions[i]
                _, child_gains = child.compute_subgame_perfect_equilibrium()
                action_gains[action] = child_gains

        # Nœud chance: calculer la moyenne des gains (50% chaque branche)
        if self.player == "Chance":
            if len(action_gains) == 2:  # Assurez-vous qu'il y a bien deux branches
                actions = list(action_gains.keys())
                gains1 = action_gains[actions[0]]
                gains2 = action_gains[actions[1]]
                average_gains = (
                    (gains1[0] + gains2[0]) / 2,  # Moyenne des gains pour Bot
                    (gains1[1] + gains2[1]) / 2   # Moyenne des gains pour Manuel
                )
                return None, average_gains

        # Nœud joueur: choisir l'action qui maximise le gain du joueur actuel
        elif self.player in ["Bot", "Manuel"]:
            player_index = 0 if self.player == "Bot" else 1
            best_action = None
            best_gain = float('-inf')

            for action, gains in action_gains.items():
                if gains[player_index] > best_gain:
                    best_gain = gains[player_index]
                    best_action = action
                    best_gains = gains

            return best_action, best_gains

        # Par défaut
        return None, self.gain

    def get_complete_equilibrium_history(self):
        """
        Retourne l'historique complet des actions optimales selon l'équilibre parfait en sous-jeux.
        """
        optimal_paths = []
        self._get_complete_equilibrium_paths([], optimal_paths)
        return optimal_paths
        
    def _get_complete_equilibrium_paths(self, current_path, all_paths):
        """
        Méthode auxiliaire récursive pour construire tous les chemins optimaux.
        """
        if self.is_leaf():
            all_paths.append(current_path + [("Leaf", None, self.gain)])
            return
            
        # Calculer l'action optimale pour ce nœud
        best_action, _ = self.compute_subgame_perfect_equilibrium()
        
        # Si c'est un nœud chance, les deux branches font partie de l'équilibre
        if self.player == "Chance":
            for i, child in enumerate(self.children):
                actions = self.possible_actions()
                if i < len(actions):
                    action = actions[i]
                    new_path = current_path + [(self.player, action, self.price)]
                    child._get_complete_equilibrium_paths(new_path, all_paths)
        else:
            # Pour les nœuds joueurs, on ne suit que l'action optimale
            for i, child in enumerate(self.children):
                actions = self.possible_actions()
                if i < len(actions) and actions[i] == best_action:
                    new_path = current_path + [(self.player, best_action, self.price)]
                    child._get_complete_equilibrium_paths(new_path, all_paths)

# Fonction pour dessiner l'arbre dans une interface graphique
def draw_tree(canvas, node, x, y, x_offset, y_offset):
    if node is None:
        return

    # Dessiner le nœud
    gain_bot, gain_manuel = node.gain
    player = node.player if node.player != "None" else ""
    node_text = f"{player}\n ({gain_bot}, {gain_manuel})\n   {node.price}" if node.player else f"({gain_bot}, {gain_manuel})".strip()
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
max_turns = int(input("Entrez le nombre de tours (maximum 4): "))
if max_turns > 4:
    raise ValueError("Le nombre de tours ne peut pas dépasser 4.")
root = Node("Bot", [], max_turns=max_turns)
root.build_children()

if max_turns != 4:
    root.display()
    print()
somme = (0, 0)
nbr = 0
win = 0
for path in root.get_complete_equilibrium_history():
    print(path)
    somme = (somme[0] + path[-1][2][0], somme[1] + path[-1][2][1])
    nbr += 1
    if path[-1][2][0] > path[-1][2][1]:
        win += 1
    elif path[-1][2][0] == path[-1][2][1]:
        win += 0.5
print(f"\nMoyenne des gains: {(somme[0] / nbr, somme[1] / nbr)}")
print(f"Win ratio des équilibres : ({(win / nbr) * 100:.2f}%)")


# Interface graphique
window = tk.Tk()
window.title("Arbre de Modélisation")
canvas = Canvas(window, width=1200, height=800, bg="white")
canvas.pack()

# Dessiner l'arbre
draw_tree(canvas, root, 600, 50, 600, 80/max_turns)

# Lancer l'interface graphique
window.mainloop()

