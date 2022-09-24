# Imports.
import aiohttp
from typing import Any, List
import os
from .error_check.typecheck import ErrorType
from rich.style import Style
from rich.console import Console
from rich.align import Align
from rich.panel import Panel
from rich import box
from rich.columns import Columns

# globals to add in column
global synonyms_panel
global antonyms_panel

# Keeping record of word.
class Word:
    def __init__(self, response: Any):
        self.response = response

    def __str__(self) -> str:
        return self.response[0]["word"]

    @property
    def phonetics(self) -> List[str] | None:
        data = self.response[0]
        phonetic = []

        if "phonetics" in data:
            data = self.response[0]["phonetics"]

            for item in data:
                if "text" in item:
                    phonetic.append(item["text"])

        elif "phonetic" in data:
            phonetic.append(data["phonetic"])

        return phonetic

    @property
    def definitions(self) -> List[str] | None:
        try:
            definitions = self.response[0]["meanings"][0]["definitions"]
        except KeyError:
            return None

        sanitized = []
        for i in range(len(definitions)):
            sanitized.append(definitions[i]["definition"])

        return sanitized

    @property
    def synonyms(self) -> Any | None:
        try:
            return self.response[0]["meanings"][0]["synonyms"]
        except KeyError:
            return None

    @property
    def antonyms(self) -> Any | None:
        try:
            return self.response[0]["meanings"][0]["antonyms"]
        except KeyError:
            return None


# The App class for base operations.
class App:
    def __init__(self) -> None:
        self.response = None
        self.console = Console()

    # api fetch for the given word
    async def call(self, word: str) -> Word:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            ) as request:
                self.response = await request.json()
                return Word(self.response)

    async def run(self, word: str) -> None:
        os.system("cls" if os.name == "nt" else "clear")
        word_obj = await self.call(word)

        if "message" in self.response:
            self.console.line()
            self.console.print(
                f"[red reverse] ERROR [/] {self.response['message']}", justify="center"
            )
            self.console.line()

        # start of the graphical cli operations
        else:
            synonyms_panel = None
            antonyms_panel = None
            self.console.line()
            self.console.print(Align("[bold cyan]A CLI Dictionary[/]", align="center"))
            self.console.print(
                Align(
                    f"[rgb(192,57,43)]Definitions of [/][rgb(214,1,179)]{word.capitalize()}[/]",
                    align="center",
                ),
                justify="center",
            )
            # if defintions exist
            if word_obj.definitions:
                self.console.line()
                definition_list = []
                # appending all definition in a list
                for item in word_obj.definitions:
                    definition_list.append(item)

                # making a multiline string
                all_definitions = """{}""".format("\n".join(definition_list[:]))

                # making of definitions panel
                definitions_panel = Panel(
                    Align(all_definitions, align="center"),
                    box=box.HEAVY,
                    border_style="rgb(118,215,196)",
                    style="rgb(52,152,219)",
                    title="[bold rgb(169,204,227)]Definitions![/]",
                )

                self.console.print(definitions_panel)

            # parsing antonyms
            if word_obj.antonyms:
                antonyms_list = []

                for item in word_obj.antonyms:
                    antonyms_list.append(item)
                all_antonyms = """{}""".format("\n".join(antonyms_list[:]))

                antonyms_panel = Panel(
                    Align(all_antonyms, align="center"),
                    box=box.ROUNDED,
                    border_style="rgb(155,89,182)",
                    style="italic rgb(136,78,160)",
                    title="[bold]Antonyms[/]",
                    width=30,
                    height=10,
                )

            # parsing synonyms
            if word_obj.synonyms:
                synonyms_list = []

                for item in word_obj.synonyms:
                    synonyms_list.append(item)
                all_synonyms = """{}""".format("\n".join(synonyms_list[:]))

                synonyms_panel = Panel(
                    Align(all_synonyms, align="center"),
                    box=box.ROUNDED,
                    border_style="rgb(241,196,15)",
                    style="italic rgb(243,156,18)",
                    title="[bold rgb(241,196,15)]Synonyms[/]",
                    width=30,
                    height=10,
                )
                self.console.print(
                    Align(
                        Columns([synonyms_panel, antonyms_panel]),
                        align="center",
                    )
                )

            # parsing of phonetics
            if word_obj.phonetics:
                self.console.line()
                self.console.rule(
                    "[bold rgb(146,43,33)]Phonetics[/]", style="rgb(231,76,60)"
                )

                for item in word_obj.phonetics:
                    self.console.print(f"[red]{item}[/]", justify="center")

            self.console.line(2)

    # incase of input error
    def err(self, type: ErrorType) -> None:
        if type == ErrorType.NO_ARG:
            self.console.line()
            self.console.print(
                "[red reverse] USAGE [/] $ poetry run wtm [green]<word>[/]",
                justify="center",
            )
            self.console.line()
