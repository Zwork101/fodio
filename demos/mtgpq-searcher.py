import asyncio

from fodio import Item, TextAttr, LinkAttr, CustomAttr, InformationError


class Set(Item):
    link = LinkAttr("a:nth-child(1)")
    name = TextAttr("a:nth-child(1) > strong:nth-child(3)")

    class Meta:
        selector = "div.col-md-4"


class SetsPage(Item):
    sets = Set

    class Meta:
        selector = "div.row:nth-child(12)"
        root_url = "https://d3go.com"


class Card(Item):
    image = CustomAttr(["data-original"], ".card-art")
    name = TextAttr(".card-details > h3:nth-child(1)")
    text = TextAttr(".card-details > div:nth-child(2)")

    class Meta:
        selector = "div.col-lg-3"


class CardPage(Item):
    cards = Card

    class Meta:
        selector = ".content-wrapper"
        root_url = "https://d3go.com"


async def runner():
    data = await SetsPage.search("games/magicthegatheringpuzzlequest/")
    for set in data['sets']:
        print(set['name'])
        try:
            cards = await CardPage.search(set['link'].url[17:])  # The 17 to simply to get the path from the URL
        except InformationError:
            print("Unable to load '{name}'".format(name=set['name']))
        else:
            for card in cards['cards']:
                print('  > ' + card['name'])
                for detail in card['text'].strip().split('\n')[1:]:
                    print('\t~ ' + detail.strip())
                print('')


loop = asyncio.get_event_loop()
loop.run_until_complete(runner())
