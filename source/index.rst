Fodio Home Page
===============

.. toctree::
    :caption: Table of Contents

    Fodio API/fodio
    Fodio API/errors

**What is fodio?**

Fodio is a web scraping tool, used to easily traverse websites and collects data on. Some key
concepts fodio was built on was simplicity and asynchronous-ity (No, I don't think that's a real word). Inspired by
the Demiurge_ library, which is not active anymore, Fodio is here to save the day!

**Why would I not use Scrapy?**

Good Question! There are some key differences that are important too note.

1. Scrapy uses C extensions, which depending on the environment, can be a pain!
2. Scrapy is not asynchronous!
3. IMO, This is simpler.

Also, if you're on linux, you can use uvloop, which should help speed things up!

Installation
------------

To install with pypi, use simply ``pip install fodio``

To install manually, either download and unpack, or clone this repository. Then, while in the root of the local
repository, do ``python setup.py install``

I'm not great at this documentaion thing, so let's just get right into the quick-start.

Quick-Start
-----------

Too start scraping, inspect element will be your friend. You're going to be copying the CSS selectors in the elements
you wish to harvest. In this case, we'll be walking though a github example that you can also find in the demo file,
on the Fodio github page.

First, we need to make an item. Then "item" will represent a section of the page.

It's good too note, that this example won't have Items as ItemAttrs, but you can do that. I really suggest looking
at the demos file, because that includes a bunch of great examples on what to do.

.. code-block:: python

    class GithubPage(Item):
        ...
        class Meta:
            ...

Notice the "Meta" class. This is used too hold your selector and root_url information. In this senerio, we want to get
a github user's real name + description. First, let's narrow in on the profile card with the ".h-card" selector. Then,
we'll supply the root_url "https://github.com"

.. code-block:: python

    class GithubPage(Item):
        ...
        class Meta:
            selector = ".h-card"
            root_url = "https://github.com"

Not that bad eh? Now that we have the profile card, we need to set some ItemAttributes to extract the information.
We'll use a TextAttr object to extract the text from a node with the real name, and anther TextAttr for the description.

.. code-block:: python

    class GithubPage(Item):
        name = TextAttr(".p-name")
        desc = TextAttr(".p-note > div:nth-child(1)", raise_not_found=False)

        class Meta:
            selector = ".h-card"
            root_url = "https://github.com"

..

.. note:: Notice the ``raise_not_found`` kwarg. Some github profiles don't have a description, and we don't want it too raise an
    error if they don't. The same if True for the real name, however that element will exist if they have a real name or
    not, so we'll have to check manually.

Now time too run it! we'll create an asynchronous function called runner to do this. GithubPage has a classmethod called
search which will add a path too the root_url, and fetch it. So let's do that.

.. code-block:: python

    accounts = ['Zwork101', 'bukson', 'torvalds', 'User1m', 'random-robbie']
    async def runner():
        result = await GithubPage.search(account)
        print("{account_name}'s real name is {real_name}".format(
            account_name=account, real_name=result['name'] if result['name'] else "not known"))
        print('{description}\n'.format(
            description=('"' + result['desc'] + '"') if result['desc'] else "No Description"))

And we're done! After adding asyncio too run it, this is our final product:

.. code-block:: python

    import asyncio

    from fodio import Item, TextAttr


    class GithubPage(Item):
            name = TextAttr(".p-name")
            desc = TextAttr(".p-note > div:nth-child(1)", raise_not_found=False)

            class Meta:
                selector = ".h-card"
                root_url = "https://github.com"

    accounts = ['Zwork101', 'bukson', 'torvalds', 'User1m', 'random-robbie']

    async def runner():
        result = await GithubPage.search(account)
        print("{account_name}'s real name is {real_name}".format(
            account_name=account, real_name=result['name'] if result['name'] else "not known"))
        print('{description}\n'.format(
            description=('"' + result['desc'] + '"') if result['desc'] else "No Description"))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(runner())

That wasn't that bad now was it? For more examples, see the demo folder. Otherwise, get scraping!

**Wait, but why is it called "Fodio"**

Well, apparently developers like to name their projects in latin, or some other language no one uses. Fodio (atleast
this is what some sites said) can mean "delve" which is an english word for all you non-english majors / non-Magic: The
Gathering players. Delve means to research and dig, 2 things this library does!

.. _Demiurge: http://demiurge.readthedocs.io/en/v0.2/
