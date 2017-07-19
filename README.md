# HumbleBundle Library Catalog
## Getting started
Humble Bundle doesn't allow library exports to share lists of your titles with your cohorts. They also don't allow a simple copy/paste from the library page, so here is how to use this tool
1. Got to: https://www.humblebundle.com/home/library
1. In Chrome or Firefox, press F12 to open inspector
1. Select the root HTML element
1. Right-Click, Copy -> Inner HTML...
1. Copy resulting HTML to a file

`python create_catalog.py -i PATH/TO/FILE.html`

```
python create_catalog.py --help
usage: Parse the saved HTML file from Humble Bundle Library
       [-h] -i INPUT_FILE [-v]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input-file INPUT_FILE
                        The saved Humble Bundle Library file
  -v, --verbose
```

## Contributing
Adding publishers to the [publishers.json](./publishers.json) file would be very helpful. Please maintain formatting in that file.

1. Fork this repository to your own org
1. Make changes to your own repository
1. Make a pull request to this repository to have your changes reviewed and merged
