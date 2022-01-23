update smart_list_item_event set kind='Created' where kind='created';
update smart_list_item_event set kind='Updated' where kind='updated';
update smart_list_item_event set kind='Archived' where kind='archived';
update smart_list_item_event set kind='Restored' where kind='restored';
update smart_list_item_event set kind='Created' where kind='create';
update smart_list_item_event set kind='Updated' where kind='update';
update smart_list_item_event set kind='Archived' where kind='archive';
update smart_list_item_event set kind='Restored' where kind='restore';
select kind from smart_list_item_event;