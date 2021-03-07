Playing around with watchdog tricks
===================================

SyncTrick
+++++++++

This trick will sync files in a watched directory to a destination folder.

Some thoughts -

What if two separate machines have this program running?

1: sees file change & syncs
2: sees file change and syncs

- It looks like it will get synced many times - not incorrect, but redundant
- we need to restrict the user to only sync their files
- we should define ownership in the .yaml file
- this yaml file will need to be placed at the root of the watched directory
- then called with watchmedo tricks-from /path/to-watched-directory

Try it out::

    % watchmedo tricks-from tricks.yaml


Now create, modify or delete files in::

    ./_WORKING/ABC_I/*

