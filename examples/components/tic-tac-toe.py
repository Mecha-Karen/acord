# Simple tic tac toe game written using acord
# Now, this isn't the best way of doing this
# We strongly recomend using a command handler
# But they aren't your thing, enjoy the example below
# However, we honestly recomend using a command handler and use this as a guide!

from typing import Any
from acord import Client, Message, Intents, Button, ActionRow, ButtonStyles
from acord.models.interaction import Interaction

row1, row2, row3 = ActionRow(), ActionRow(), ActionRow()

for i in range(1, 10):
    button = Button(style=ButtonStyles.PRIMARY, custom_id=str(i), label=" ")
    if i <= 3:
        row1.add_component(button)
    elif 3 < i <= 6:
        row2.add_component(button)
    else:
        row3.add_component(button)


def check_board_winner(board):
    for across in board:
        value = sum(across)
        if value == 3:
            return "O"
        elif value == -3:
            return "X"

    # Check vertical
    for line in range(3):
        value = board[0][line] + board[1][line] + board[2][line]
        if value == 3:
            return "O"
        elif value == -3:
            return "X"

    # Check diagonally
    diag = board[0][2] + board[1][1] + board[2][0]
    if diag == 3:
        return "O"
    elif diag == -3:
        return "X"

    diag = board[0][0] + board[1][1] + board[2][2]
    if diag == 3:
        return "O"
    elif diag == -3:
        return "X"

    # Check if all pieces are same
    if all(i != 0 for row in board for i in row):
        return "Tie"

    return None


def to_board(rows):
    board = list()
    for row in rows:
        l_row = list()
        for button in row.components:
            if button.label == " ":
                l_row.append(0)
            elif button.label == "O":
                l_row.append(1)
            else:
                l_row.append(-1)
        board.append(l_row)
    return board


class MyClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.games = dict()

    async def on_ready(self) -> None:
        print(f"{self.user} is ready!")

    async def on_message_create(self, message: Message) -> Any:
        """This is were we handle our tic tac toe game creation"""
        content = message.content.lower()
        name, *args = content.split(" ")

        if name.lower() == ".tic-tac-toe":
            # To play a game you must use an ID, of a member
            try:
                opponent = message.guild.get_member(int(args[0]))
            except (IndexError, ValueError):
                return await message.channel.send(
                    content="Invalid or no opponent given! Make sure your using there ID."
                )
            else:
                if not opponent:
                    return await message.channel.send(content="Cannot find this member")
                if opponent.user.bot:
                    return await message.channel.send(content="Can't play against bots")

            game_message = await message.channel.send(
                content=f"{message.author}, its your turn!",
                components=[row1, row2, row3],
            )
            self.games.update(
                {game_message.id: [message.author, opponent.user, message.author, 0]}
            )

    async def on_interaction_create(self, interaction: Interaction) -> Any:
        """Now we handle our button clicks, lord have mercy"""
        message = await interaction.message.refetch()
        # Fetch new components
        try:
            auth, opp, cur, prev = self.games[message.id]
            # game doesn't exist
        except KeyError:
            return

        if (
            (not message)
            or (message.id not in self.games)
            or (interaction.member.user.id != cur.id)
        ):
            return

        rows = message.components
        button_id = interaction.data.custom_id

        if not button_id.isnumeric():
            return
        button_id = int(button_id) - 1
        row, index = divmod(button_id, 3)

        button = rows[row].components[index]
        board = to_board(rows)

        if prev % 2 == 0:
            label = "O"
            board[row][index] = 1
        else:
            label = "X"
            board[row][index] = -1

        button.disabled = True
        button.label = label
        rows[row].components[index] = button

        result = check_board_winner(board)
        if result:
            if result == "Tie":
                await message.edit(content="This game ended in a tie!", components=rows)
            elif result == "O":
                await message.edit(
                    content=f"Congratulations to {auth} for winning!", components=rows
                )
            else:
                await message.edit(
                    content=f"Congratulations to {opp} for winning!", components=rows
                )

            await interaction.respond(content="Game ended", flags=64)
            self.games.pop(message.id)
        else:
            await message.edit(content=f"{opp} it is your turn!", components=rows)

            await interaction.respond(content="You have made your move!", flags=64)

        self.games.update({message.id: [opp, auth, opp, (prev + 1)]})


if __name__ == "__main__":
    client = MyClient(intents=Intents.ALL)
    client.run("TOKEN")
