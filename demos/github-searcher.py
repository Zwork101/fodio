import asyncio

from fodio import Item, TextAttr

accounts = ['Zwork101', 'bukson', 'torvalds', 'User1m', 'random-robbie']  # Some randos, first guy seems cool though


class GithubPage(Item):
    name = TextAttr(".p-name")  # Github still includes the element if no name is supplied, so it's on us to catch that.
    desc = TextAttr(".p-note > div:nth-child(1)", raise_not_found=False)

    class Meta:
        selector = ".h-card"
        root_url = "https://github.com"


async def runner():
    for account in accounts:
        result = await GithubPage.search(account)
        print("{account_name}'s real name is {real_name}".format(
            account_name=account, real_name=result['name'] if result['name'] else "not known"))
        print('{description}\n'.format(
            description=('"' + result['desc'] + '"') if result['desc'] else "No Description"))

loop = asyncio.get_event_loop()
loop.run_until_complete(runner())
