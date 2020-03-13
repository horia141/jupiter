import logging

from notion.block import CollectionViewPageBlock
from notion.block import PageBlock

LOGGER = logging.getLogger(__name__)


def find_page_from_space_by_id(client, page_id):
    return client.get_block(page_id)


def find_page_from_page_by_name(root_page, name):
    for subblock in root_page.children:
        if not isinstance(subblock, CollectionViewPageBlock):
            continue

        if subblock.title == name:
            return subblock

        found_page = find_page_from_page_by_name(subblock, name)
        if found_page is not None:
            return found_page

    return None


def find_page_from_space_by_name(client, name, space):
    def find_page_by_name(page):
        if page.title == name:
            return page

        for subblock in page.children:
            if not isinstance(subblock, PageBlock):
                continue

            found_page = find_page_by_name(subblock)
            if found_page:
                return found_page

        return None

    for page_id in space.pages:
        page = client.get_block(page_id)
        found_page = find_page_by_name(page)
        if found_page:
            return found_page

    return None


def create_page_in_space(space, name):
    return space.add_page(name)


def create_page_in_page(page, name):
    new_page = page.children.add_new(PageBlock)
    new_page.title = name
    return new_page


def attach_view_to_collection(client, page, collection, lock_view_id, type, title, schema):
    if lock_view_id:
        view = client.get_collection_view(lock_view_id, collection=collection)
        LOGGER.info(f"Found the collection view by id {title} {view}")
    else:
        view = client.get_collection_view(client.create_record("collection_view", parent=page, type=type),
                                          collection=collection)
        view.set("collection_id", collection.id)
        LOGGER.info(f"Created the collection view {title} {view}")

    view.title = title
    client.submit_transaction([{
        "id": view.id,
        "table": "collection_view",
        "path": [],
        "command": "update",
        "args": schema
    }])

    return view
