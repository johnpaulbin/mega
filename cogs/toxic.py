from discord.ext import commands
import discord
from utils import get_logging_channel
from discord.utils import get
from discord.ext import commands
from detoxify import Detoxify
import pkg_resources
from symspellpy.symspellpy import SymSpell


def detoxify(model, message):
    prediction = list(model.predict(message).values())
    if prediction[0] > 0.95:
        return True, prediction[0], prediction[1]
    elif float(format(prediction[1], '.4f')[4]) > 0.007: # there has got to be another way to format 1.234567e-8
        return True, prediction[0], prediction[1]
    return False, prediction[0], prediction[1]

class Toxic(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.model = Detoxify('unbiased-small', device='cpu')
        self.sym_spell = SymSpell(max_dictionary_edit_distance=0, prefix_length=7)
        self.dictionary_path = pkg_resources.resource_filename(
        "symspellpy", "frequency_dictionary_en_82_765.txt"
        )
        self.sym_spell.load_dictionary(self.dictionary_path, term_index=0, count_index=1)

    @commands.command(name='toxic')
    async def toxicpredict(self, ctx, *, args):
        prediction, toxicity, severe = detoxify(self.model, args)
        msg = "VERY TOXIC" if prediction == True else "NOT TOXIC"
        await ctx.send(f"{msg} `{str(toxicity)} | {str(severe)}`")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author != self.client.user:
            # bypass toxic check if user can manage messages
            if message.author.guild_permissions.manage_messages:
                return
            prediction, toxicity, severe = detoxify(self.model, self.sym_spell.word_segmentation(message.content).corrected_string)

            if prediction == True:
                await message.delete()
                await get_logging_channel(message).send(
                    f"⚠️ Toxic message deleted from: {message.author.mention} Context: ```{message.content}``` with score `{str(toxicity)} | {str(severe)}`"
                )
            return


def setup(client):
    client.add_cog(Toxic(client))
