from collections import namedtuple
from inspect import isclass
from typing import List, Union, NamedTuple, Dict, Any, Iterable

from fodio.errors import InformationError

from aiohttp import ClientSession
from pyquery import PyQuery as pq
from urllib.parse import urljoin


class FodioObj:
    """
    This class does literally nothing. It's inherited by Item and ItemAttr, so ItemMeta knows what to deal with.
    """
    pass


class ItemAttr(FodioObj):
    """
    This is the parent class of all other Attr classes.

    :ivar selector: The value passed in as css_selector
    :ivar accept_multiples: The value passed in as accept_multiples
    :ivar raise_not_found: The value passed in as raise_not_found
    """

    def __init__(self, css_selector: str, accept_multiples: bool=False, raise_not_found: bool=True):
        """

        :param css_selector: The css selector to identify what node too parse.
        :param accept_multiples: If enabled, it will allow for multiple matches too the css_selector.
        :param raise_not_found: If disabled, it will not raise an error if no matches are found, and will instead
                                be None.
        :type css_selector: str
        :type accept_multiples: bool
        :type raise_not_found: bool
        """
        self.selector = css_selector
        self.accept_multiples = accept_multiples
        self.raise_not_found = raise_not_found

    async def _find(self, document: str) -> Union[List[pq], None]:
        """
        This function collects the nodes based on the selector. This should only need to be used internally.

        :param document: The HTML containing the information. As a side note, the css_selector should be relative to
                         THIS html.
        :type document: str
        :return: A list of pyquery objects, or None if raise_not_found is False and nothing was found.
        :rtype: Union[List[pq], None]
        """
        doc = pq(document)
        data = doc(self.selector)
        if not data and self.raise_not_found:
            raise InformationError("No matches for '{selector}' found in document".format(selector=self.selector))
        elif not data:
            return None
        elif len(data) > 1 and not self.accept_multiples:
            raise InformationError("Too many matches for '{selector}' found in document".format(selector=self.selector))
        return data


class TextAttr(ItemAttr):
    """
    Finds the the text from a css selector.
    """

    async def load(self, document: str) -> Union[List[str], None, str]:
        """
        Get the text from the matched contents from _find.

        :param document: The HTML relative to the item.
        :type document: str
        :return: Either a list of strings (if accept_multiples), None (if not raise_not_found) or a string.
        :rtype: Union[List[str], None, str]
        """
        matches = await self._find(document)
        if matches is None:
            return
        parsed = [match.text_content() for match in matches]
        if len(parsed) == 1:
            return parsed[0]
        return parsed


class LinkAttr(ItemAttr):
    """
    Finds the text in an a tag, along side it's href attribute based on the css selector

    :cvar LINK: A named tuple representing the "link". contains .text and .url
    :type LINK: NamedTuple
    """

    LINK = namedtuple('Link', ['text', 'url'])

    async def load(self, document: str) -> Union[List[NamedTuple], None, NamedTuple]:
        """
        Get the link from the matched contents from _find.

        :param document: The HTML relative to the item.
        :type document: str
        :return: Either a list of LinkAttr.LINK (if accept_multiples), None (if not raise_not_found) or a LinkAttr.LINK.
        """
        matches = await self._find(document)
        if matches is None:
            return
        parsed = [self.LINK(match.text, match.attrib['href']) for match in matches]
        if len(parsed) == 1:
            return parsed[0]
        return parsed


class CustomAttr(ItemAttr):
    """
    This is a ItemAttr in which you can obtain any of a node's attributes. If raise_not_found is False,
    if it can't find an attribute on the node, the value will be None instead,

    :ivar value: An Iterable containing the values passed into attrs
    :type value: Iterable
    """

    def __init__(self, attrs: Iterable[str], css_selector: str,
                 accept_multiples: bool=False, raise_not_found: bool=True):
        """
        Only showing the new params. See ItemAttr for the rest.

        :param attrs: The different attributes to harvest from the node.
        :type attrs: Iterable[str]
        """
        self.value = attrs
        super().__init__(css_selector, accept_multiples, raise_not_found)

    async def load(self, document: str) -> Union[List[Union[dict, None]], None, dict]:
        """
        Get the node's attribues based on the document.

        :param document: The HTML relative to the css_selector.
        :type document: str
        :return: Either nothing if not taise_not_found, or a dict / list of dicts with the attr names -> attr values.
        :rtype: Union[List[Union[dict, None]], None, dict]
        """
        matches = await self._find(document)
        if matches is None:
            return
        values = []
        for match in matches:
            args = {}
            for field in self.value:
                attribute = match.attrib.get(field)
                if self.raise_not_found and attribute is None:
                    raise InformationError("Could not find attribute '{attr}' in node".format(attr=field))
                args[field] = attribute
            values.append(args)
        if len(values) == 1:
            return values[0]
        return values


class ItemMeta(type):
    """
    Add all class variables that inherit FodioObj to a _ATTRS class variables
    """

    def __new__(mcs, name, bases, kwargs):
        kwargs['_ATTRS'] = []
        for kname in kwargs:
            if isinstance(kwargs[kname], FodioObj) or (isclass(kwargs[kname]) and issubclass(kwargs[kname], FodioObj)):
                kwargs['_ATTRS'].append(kname)
        return type.__new__(mcs, name, bases, kwargs)


class Item(FodioObj, metaclass=ItemMeta):
    """
    An object to represent data on a page. To use, create class variables with Attr objects pointed
    at the data you desire. They will all share the first css selector passed in by the page class.

    It's also important to note that you MUST INCLUDE A META CLASS. For example,

        >>> class SomeSite(Item):
        ...     ...
        ...     class Meta:
        ...         selector = ".hello-there"
        ...         root_url = "https://some.site"

    :cvar _ATTRS: A list containing the names for the ItemAttrs.
    :type _ATTRS: list
    """

    @classmethod
    async def from_html(cls, document: str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Load a HTML document for parsing, and a shared the selected segment with ItemAttrs.

        :param document: The whole HTML page.
        :type document: str
        :return: A dict with the keys as class var names to the ItemAttrs, and values as the parsed data. This will be
                 a list if multiple entries for the Meta selector are found.
        :rtype: Union[Dict[str, Any], List[Dict[str, Any]]]
        """
        doc = pq(document)
        segments = doc(cls.Meta.selector)
        if not segments:
            raise InformationError("Could not match selector '{selector}' to document.".format(
                selector=cls.Meta.selector))
        total = []
        for segment in segments:
            values = {}
            for item_attr in cls._ATTRS:
                data = await getattr(cls, item_attr).load(segment)
                values[item_attr] = data
            total.append(values)
        if len(total) == 1:
            return total[0]
        return total

    @classmethod
    async def load(cls, document: str) -> Dict[str, Any]:
        """
        Shorthand for from_html. Mainly used to make item objects compatible as ItemAttrs.

        See from_html for more information.
        """
        return await cls.from_html(document)

    @classmethod
    async def search(cls, url_path: str) -> Dict[str, Any]:
        """
        Fetch for the URL and parse the document based on the items.

        :param url_path: The URL path in the Meta.root_url site to parse.
        :type url_path: str
        :return: A dict with the keys being the class variables and values as the loaded items.
        :rtype: Dict[str, Item]
        """

        url = urljoin(cls.Meta.root_url, url_path.lstrip('/'))

        async with ClientSession() as session:
            async with session.get(url) as response:
                return await cls.from_html(await response.read())


__author__ = "Nathan Zilora"
