from tkinter import *
import random
import os

# Constants
GAME_WIDTH = 700
GAME_HEIGHT = 500
SPEED = 120
SPACE_SIZE = 60
BODY_PARTS = 3
SNAKE_COLOUR = "#00FF00"
FOOD_COLOUR = "#FF0000"
BACKGROUND_COLOUR = "#000000"
LEADERBOARD_FILE = "leaderboard.txt"

class SnakeGame:
    def __init__(self, master, username):
        self.master = master
        self.username = username
        self.score = 0
        self.direction = 'down'
        self.snake = None
        self.food = None

        self.label = Label(master, text="Score: 0", font=('consolas', 40))
        self.label.pack()

        self.canvas = Canvas(master, bg=BACKGROUND_COLOUR, height=GAME_HEIGHT, width=GAME_WIDTH)
        self.canvas.pack()

        self.master.bind('<Left>', lambda event: self.change_direction('left'))
        self.master.bind('<Right>', lambda event: self.change_direction('right'))
        self.master.bind('<Up>', lambda event: self.change_direction('up'))
        self.master.bind('<Down>', lambda event: self.change_direction('down'))

        self.start_game()

    def start_game(self):
        self.snake = Snake(self.canvas)
        self.food = Food(self.canvas)
        self.next_turn()

    def next_turn(self):
        x, y = self.snake.coordinates[0]

        if self.direction == 'up':
            y -= SPACE_SIZE
        elif self.direction == 'down':
            y += SPACE_SIZE
        elif self.direction == 'left':
            x -= SPACE_SIZE
        elif self.direction == 'right':
            x += SPACE_SIZE

        self.snake.coordinates.insert(0, (x, y))
        square = self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_COLOUR)
        self.snake.squares.insert(0, square)

        if [x, y] == self.food.coordinates:
            self.score += 1
            self.label.config(text=f"Score: {self.score}")
            self.canvas.delete("food")
            self.food = Food(self.canvas)
        else:
            del self.snake.coordinates[-1]
            self.canvas.delete(self.snake.squares[-1])
            del self.snake.squares[-1]

        if self.check_collisions():
            self.game_over()
        else:
            self.master.after(SPEED, self.next_turn)

    def change_direction(self, new_direction):
        opposite_directions = {'left': 'right', 'right': 'left', 'up': 'down', 'down': 'up'}
        if self.direction != opposite_directions.get(new_direction, ''):
            self.direction = new_direction

    def check_collisions(self):
        x, y = self.snake.coordinates[0]
        if x < 0 or x >= GAME_WIDTH or y < 0 or y >= GAME_HEIGHT:
            return True
        if [x, y] in self.snake.coordinates[1:]:
            return True
        return False

    def game_over(self):
        self.canvas.create_text(GAME_WIDTH / 2, GAME_HEIGHT / 2, font=('consolas', 50),
                            text="GAME OVER", fill="red", tag="gameover")
        self.save_score()
        self.restart_button = Button(self.master, text="Restart", font=('consolas', 20),
                                 command=self.restart)
        self.restart_button.pack(pady=10)
        self.menu_button = Button(self.master, text="Return to Main Menu", font=('consolas', 20),
                              command=self.return_to_menu)
        self.menu_button.pack(pady=10)


    def restart(self):
        self.canvas.delete("all")
        self.label.config(text="Score: 0")
        self.score = 0
        self.direction = 'down'
        if hasattr(self, 'restart_button'):
            self.restart_button.destroy()
        if hasattr(self, 'menu_button'):
            self.menu_button.destroy()
        self.start_game()


    def save_score(self):
        with open(LEADERBOARD_FILE, "a") as f:
            f.write(f"{self.username}:{self.score}\n")
            
    def return_to_menu(self):
        self.master.destroy()
        launch_menu(self.username)



class Snake:
    def __init__(self, canvas):
        self.body_size = BODY_PARTS
        self.coordinates = [[0, 0] for _ in range(BODY_PARTS)]
        self.squares = [canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_COLOUR)
                        for x, y in self.coordinates]


class Food:
    def __init__(self, canvas):
        x = random.randint(0, (GAME_WIDTH // SPACE_SIZE) - 1) * SPACE_SIZE
        y = random.randint(0, (GAME_HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE
        self.coordinates = [x, y]
        canvas.create_oval(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=FOOD_COLOUR, tag="food")


class LoginPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake Game Login")
        self.root.geometry("600x600")

        Label(root, text="Enter your name:", font=("consolas", 16)).pack(pady=40)
        self.name_entry = Entry(root, font=("consolas", 16))
        self.name_entry.pack()
        Button(root, text="Login", font=("consolas", 16), command=self.login).pack(pady=20)

    def login(self):
        username = self.name_entry.get().strip()
        if username:
            self.root.destroy()
            launch_menu(username)


class MainMenu:
    def __init__(self, username):
        self.username = username
        self.window = Tk()
        self.window.title("Snake Game - Menu")
        self.window.geometry("600x600")

        Label(self.window, text=f"Welcome, {username}!", font=("consolas", 18)).pack(pady=20)
        Button(self.window, text="Start Game", font=("consolas", 16), command=self.start_game).pack(pady=10)
        Button(self.window, text="Leaderboard", font=("consolas", 16), command=self.show_leaderboard).pack(pady=10)
        Button(self.window, text="Quit", font=("consolas", 16), command=self.window.quit).pack(pady=10)

        self.window.mainloop()

    def start_game(self):
        self.window.destroy()
        game_window = Tk()
        game_window.title("Snake Game")
        game_window.resizable(False, False)
        SnakeGame(game_window, self.username)
        game_window.mainloop()

    def show_leaderboard(self):
        top_scores = self.load_leaderboard()
        top_window = Toplevel(self.window)
        top_window.title("Leaderboard")
        top_window.geometry("400x400")
        Label(top_window, text="Top Scores", font=("consolas", 20)).pack(pady=10)

        for entry in top_scores:
            Label(top_window, text=entry, font=("consolas", 14)).pack()

    def load_leaderboard(self):
        if not os.path.exists(LEADERBOARD_FILE):
            return ["No scores yet!"]
        with open(LEADERBOARD_FILE, "r") as f:
            lines = f.readlines()
        scores = []
        for line in lines:
            try:
                name, score = line.strip().split(":")
                scores.append((name, int(score)))
            except:
                continue
        top = sorted(scores, key=lambda x: x[1], reverse=True)[:5]
        return [f"{i+1}. {name}: {score}" for i, (name, score) in enumerate(top)]


def launch_menu(username):
    MainMenu(username)


if __name__ == "__main__":
    root = Tk()
    LoginPage(root)
    root.mainloop()
