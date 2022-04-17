import curses
from random import randint

# constants
WINDOW_WIDTH = 60
WINDOW_HEIGHT = 20
CHAR_SNAKE = '■'
CHAR_FOOD = '@'

# setup window
curses.initscr()
win = curses.newwin(WINDOW_HEIGHT, WINDOW_WIDTH, 0, 0)
win.keypad(True)
curses.noecho()
curses.curs_set(0)
win.border(0)
win.nodelay(True)

# snake and food coordinates
snake = [(WINDOW_HEIGHT // 4, WINDOW_WIDTH // 4),
         (WINDOW_HEIGHT // 4, WINDOW_WIDTH // 4 - 1),
         (WINDOW_HEIGHT // 4, WINDOW_WIDTH // 4 - 2)]
food = (WINDOW_HEIGHT // 2, WINDOW_WIDTH // 2)

# game logic
score = 0
win.addch(food[0], food[1], CHAR_FOOD)
key = curses.KEY_RIGHT

while True:
    win.addstr(0, 3, " Score " + str(score) + " ")
    win.addstr(WINDOW_HEIGHT - 1, 3, " Press 'Q' to quit ")
    win.timeout(150 - len(snake) // 5 + len(snake) // 10 % 120)

    prev_key = key
    event = win.getch()

    key = event if event != -1 else prev_key
    if key == ord('Q') or key == ord('q'):
        break

    if (key not in [curses.KEY_LEFT, curses.KEY_UP, curses.KEY_RIGHT, curses.KEY_DOWN]
            or key == curses.KEY_LEFT and prev_key == curses.KEY_RIGHT
            or key == curses.KEY_RIGHT and prev_key == curses.KEY_LEFT
            or key == curses.KEY_UP and prev_key == curses.KEY_DOWN
            or key == curses.KEY_DOWN and prev_key == curses.KEY_UP):
        key = prev_key

    # calculate the next coordinates
    y = snake[0][0]
    x = snake[0][1]
    match key:
        case curses.KEY_DOWN:
            y += 1
        case curses.KEY_UP:
            y -= 1
        case curses.KEY_RIGHT:
            x += 1
        case curses.KEY_LEFT:
            x -= 1

    if snake[0] in snake[1:]:
        break

    # continue moving from another side
    x = 1 if x == WINDOW_WIDTH - 1 else WINDOW_WIDTH - 1 if x == 0 else x
    y = 1 if y == WINDOW_HEIGHT - 1 else WINDOW_HEIGHT - 1 if y == 0 else y

    snake.insert(0, (y, x))

    if snake[0] == food:
        score += 1
        food = ()
        while food == ():
            food = (randint(1, WINDOW_HEIGHT - 2), randint(1, WINDOW_WIDTH - 2))
            if food in snake:
                food = ()
        win.addch(food[0], food[1], CHAR_FOOD)
    else:  # move snake
        last = snake.pop()
        win.addch(last[0], last[1], ' ')

    win.addch(snake[0][0], snake[0][1], CHAR_SNAKE)
    win.border(0)

curses.endwin()
print("--- GAME OVER ---\nFinal score =", score)
