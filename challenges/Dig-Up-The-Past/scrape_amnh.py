import requests
import os

from lxml import html
from StringIO import StringIO
from PIL import Image

root_page = 'http://research.amnh.org/paleontology/notebooks/'
root_write_dir = '/Users/mikecap/Sites/HacktheDinos/images/challenges/Dig-Up-The-Past/'

page = requests.get(root_page)
tree = html.fromstring(page.content)

notebooks = {}

# This will create a list of notebooks
notebook_names = tree.xpath('//a/text()')

# This will create a list of sub-pages to crawl
notebook_links = tree.xpath('//a/@href')

count = 0

for each_name in notebook_names:
    new_path = root_write_dir + notebook_links[count]

    # Create a folder for the notebook images and data
    if not os.path.exists(new_path + 'images/'):
        os.makedirs(new_path + 'images/')

    if not os.path.exists(new_path + 'data/'):
        os.makedirs(new_path + 'data/')

    # Get all pages of this notebook online starting from 00.html
    current_status = None
    page_count = 0

    while current_status != 404:
        new_page = None
        new_tree = None

        if page_count < 10:
            page_number = "0" + str(page_count)
        else:
            page_number = str(page_count)

        notebook_page = root_page + notebook_links[count] + page_number + ".html"

        page_count += 1

        new_page = requests.get(notebook_page)
        current_status = new_page.status_code

        if current_status != 404:
            # Get image and text if any
            new_tree = html.fromstring(new_page.content)

            if new_tree.xpath('count(//textarea)') != 0:
                page_text = new_tree.xpath('//textarea/text()')

                with open(new_path + 'data/' + page_number + ".txt", "w") as d:
                    d.write(page_text[0].encode("utf-8"))

                d.close()

            if new_tree.xpath('count(//table/tr/th[2])') != 0:
                page_image = html.tostring(new_tree.xpath('//table/tr/th[2]')[0])
                image_text = page_image[page_image.find("src=") + 5:page_image.find("jpg", page_image.find("src=")) + 3]

                r = requests.get(root_page + notebook_links[count] + image_text)

                i = Image.open(StringIO(r.content))
                i.save(new_path + 'images/' + image_text)

    count += 1
