from notion.block import CollectionViewPageBlock
from notion.block import PageBlock

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
    new_page  = page.children.add_new(PageBlock)
    new_page.title = name
    return new_page
