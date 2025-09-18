import os
import random
import asyncio
from highrise import BaseBot, User, Position, Highrise

# ✅ Load secrets safely from environment variables
ROOM_ID = os.getenv("ROOM_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID") or ROOM_ID  # fallback to ROOM_ID

# List of 24 free emotes
free_emotes: list[tuple[str, str]] = [
    ("Sit", "idle-loop-sitfloor"),
    ("Enthused", "idle-enthusiastic"),
    ("Yes", "emote-yes"),
    ("The Wave", "emote-wave"),
    ("Tired", "emote-tired"),
    ("Snowball Fight!", "emote-snowball"),
    ("Snow Angel", "emote-snowangel"),
    ("Shy", "emote-shy"),
    ("Sad", "emote-sad"),
    ("No", "emote-no"),
    ("Model", "emote-model"),
    ("Laugh", "emote-laughing"),
    ("Kiss", "emote-kiss"),
    ("Sweating", "emote-hot"),
    ("Hello", "emote-hello"),
    ("Greedy Emote", "emote-greedy"),
    ("Face Palm", "emote-exasperatedb"),
    ("Curtsy", "emote-curtsy"),
    ("Confusion", "emote-confused"),
    ("Charging", "emote-charging"),
    ("Bow", "emote-bow"),
    ("Thumbs Up", "emoji-thumbsup"),
    ("Tummy Ache", "emoji-gagging"),
]

# Emote durations (seconds)
emote_durations = {
    # Short (3-4s)
    "emote-bow": 3, "emote-yes": 3, "emote-wave": 3, "emote-no": 4,
    "emote-shy": 4, "emote-tired": 4, "emote-laughing": 3, "emote-kiss": 3,
    "emote-hot": 3, "emote-hello": 3, "emote-sad": 4, "emoji-thumbsup": 4,
    # Medium (4-5s)
    "emote-snowball": 5, "emote-greedy": 4, "emote-exasperatedb": 4,
    "emote-confused": 5, "emote-curtsy": 4, "emoji-gagging": 5,
    "emote-snowangel": 5,
    # Long (5-12s)
    "idle-loop-sitfloor": 12, "idle-enthusiastic": 11,
    "emote-model": 6, "emote-charging": 6,
}

# Map numbers and names to emotes
emote_commands = {str(i + 1): free_emotes[i][1] for i in range(len(free_emotes))}
emote_commands.update({name.lower(): code for name, code in free_emotes})

# Rizz and Roasts
rizz_list = [
    "You must be a magician because whenever I look at you, everyone else disappears.",
    "Are you French? Because *Eiffel* for you.",
    "If you were a vegetable, you’d be a cutecumber.",
    "Do you have a map? I just got lost in your eyes.",
    "Are you Wi-Fi? Because I’m feeling a connection.",
    "Do you believe in love at first sight—or should I walk by again?",
    "Are you made of copper and tellurium? Because you’re Cu-Te.",
    "Are you a parking ticket? Because you’ve got FINE written all over you.",
    "Do you have a name—or can I call you mine?",
    "You must be tired, because you’ve been running through my mind all day.",
    "Are you a black hole? Because you just sucked me into your orbit.",
    "Are you a time traveler? Because I see you in my future.",
    "You’re like a software update. Whenever you appear, my heart restarts.",
    "Do you have a sunburn, or are you always this hot?",
    "Are you a loan? Because you have my interest skyrocketing!",
    "You must be a wifi signal, because I’m feeling a strong connection.",
    "If looks could kill, you’d be a weapon of mass distraction.",
    "Are you a battery? Because you light up my world.",
    "Are you gravity? Because I’m falling for you.",
    "Are you a shooting star? Because every time I see you, I make a wish."
]

roast_list = [
    "If I wanted to kill myself I’d climb your ego and jump to your IQ.",
    "You bring everyone so much joy… when you leave the room.",
    "Your secrets are safe with me. I never even listen when you tell me them.",
    "You’re proof that even evolution takes a break sometimes.",
    "Some drink from the fountain of knowledge; you only gargled.",
    "You have something on your chin… no, the third one down.",
]

# ---------------- Bot Class ----------------
class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.owner_id = OWNER_ID
        self.owner_position = None
        self.emote_looping = False
        self.current_loop = None

    async def on_user_join(self, user: User, position: Position) -> None:
        if user.id == self.owner_id:
            self.owner_position = position
            await self.highrise.chat(
                f"⚡ Attention everyone! Our owner @{user.username} just entered the room! Show some love 👑✨"
            )
            # Bow + Curtsy + Gagging on join
            await self.highrise.send_emote("emote-bow", user.id)
            await asyncio.sleep(2)
            await self.highrise.send_emote("emote-curtsy", user.id)
            await asyncio.sleep(2)
            await self.highrise.send_emote("emoji-gagging", user.id)
        else:
            greetings = [
                f"@{user.username} looking good today ✨✌🏼",
                f"Welcome @{user.username}! We’ve been waiting for you 😎",
                f"Hey @{user.username}, glad you joined 🎉",
                f"@{user.username} just pulled up 🔥",
                f"@{user.username}, the party’s better with you here 🥳",
                f"Everyone say hi to @{user.username}! 👋",
                f"@{user.username}, you’re glowing today 🌟",
                f"Welcome in, @{user.username}! Make yourself at home 🏠",
                f"@{user.username} joined the vibe train 🚂✨",
                f"Finally! @{user.username} is here 😏"
            ]
            await self.highrise.chat(random.choice(greetings))

    async def on_chat(self, user: User, message: str) -> None:
        msg = message.strip().lower()

        # Pose
        if msg == "pose" and user.id == self.owner_id:
            if self.owner_position:
                await self.highrise.walk_to(self.owner_position)
            return

        # Stop emote loop
        if msg in ["0", "stop"]:
            self.emote_looping = False
            return

        # Start emote loop
        if msg in emote_commands:
            emote = emote_commands[msg]
            self.emote_looping = True
            asyncio.create_task(self.loop_emote(user.id, emote))
            return

        # Rizz
        if msg.startswith("rizz"):
            parts = msg.split()
            target = parts[1] if len(parts) > 1 else user.username
            line = random.choice(rizz_list)
            await self.highrise.chat(f"@{target} {line}")
            return

        # Roast
        if msg.startswith("roast"):
            parts = msg.split()
            target = parts[1] if len(parts) > 1 else user.username
            line = random.choice(roast_list)
            await self.highrise.chat(f"@{target} {line}")
            return

    async def loop_emote(self, user_id: str, emote: str):
        while self.emote_looping:
            await self.highrise.send_emote(emote, user_id)
            await asyncio.sleep(emote_durations.get(emote, 6))

# ---------------- Run Bot ----------------
if __name__ == "__main__":
    import asyncio
    asyncio.run(
        Highrise(MyBot()).start(ROOM_ID, BOT_TOKEN)
    )
    # redeploy trigger
