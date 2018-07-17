import asyncio

from fodio import Item, TextAttr

people = ['@21natzil', '@amasad', '@pyelias']


class ReplDetails(Item):
    title = TextAttr("span:nth-child(2)")
    lang = TextAttr("div:nth-child(3)")
    date = TextAttr("div:nth-child(4)")

    class Meta:
        selector = "a.jsx-4244714551"


class ReplAccount(Item):
    name = TextAttr("h1.jsx-2744500831")
    hacker = TextAttr(".profile-hacker-label", raise_not_found=False)  # We'll check if they're a hacker or not later.
    repls = ReplDetails

    class Meta:
        selector = "#page"
        root_url = "https://repl.it"


async def runner():
    for profile in people:
        data = await ReplAccount.search(profile)
        print(data['name'] + ", other wise known as {profile} is {hack}".format(
            profile=profile[1:], hack="a hacker." if data['hacker'] else "not a hacker."))
        print("Some pinned repls are:")
        for repl in data['repls']:
            print("""{title}
    {url}
    {lang}
    {date}""".format(title=repl['title'], url='/'.join([ReplAccount.Meta.root_url, profile, repl['title']]),
                     lang=repl['lang'], date=repl['date']))
        print('')


loop = asyncio.get_event_loop()
loop.run_until_complete(runner())
