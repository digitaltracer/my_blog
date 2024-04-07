# Created by Adarsh N B at 3/20/2024

import mistune
import os
import json
import shutil

from jinja2 import Template
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

ARTICLE_DATA = []
TEMPLATES = {}


def load_templates():
    """
        Load the templates defined in templates dir in .tpl format
    """

    global TEMPLATES

    for filename in os.listdir("./templates"):
        with open('./templates/' + filename, 'r') as f:
            TEMPLATES.update({filename[:-4]: Template(f.read())})


def render_template(template, data):
    """
        Render the template
    """

    return TEMPLATES[template].render(**data)


# list out contents and convert from markdown to html
class BlogContentRenderer(mistune.HTMLRenderer):

    def block_code(self, code, info=None):

        global ARTICLE_DATA

        if not info:
            return '\n<pre><code id="block_code">%s</code></pre>' % mistune.escape(code)

        if info == "blogcfg":
            article_info = json.loads(code)
            print(article_info)
            ARTICLE_DATA.append(article_info)

            return ""

        lexer = get_lexer_by_name(info, stripall=True)
        formatter = HtmlFormatter(linenos=False, cssclass="source")
        return highlight(code, lexer, formatter)


def render_articles():
    """
        Renders the markdown content to raw html by mistune, then applied on a
        jinja template and exported to out/
    """
    for md_filename in os.listdir('./markdowns'):

        # skip draft files from processing
        if "draft" in md_filename:
            continue

        with open("./markdowns/" + md_filename, 'r') as f:

            article_name = md_filename.rstrip('.md')

            print('[+] Rendering Article ', article_name)

            # render the markdown to raw html
            renderer = BlogContentRenderer()
            markdown = mistune.Markdown(renderer=renderer)
            raw_html = markdown(f.read())

        # apply the article jinja template to it
        with open("./out/article/" + article_name + '.html', 'w') as html_f:

            html_f.write(render_template('article', {'meta': ARTICLE_DATA[-1],
                                                     'content': raw_html}))


# update the main page with new contents

def render_main_page():
    """
        Render the main page by updating with article list
    """
    with open('./out/index.html', 'w') as f:
        f.write(render_template('mainpage',
                                {'articles': ARTICLE_DATA}))

    with open("./out/index2.html", 'w') as f:
        f.write(render_template("mainpage_2", {"articles": ARTICLE_DATA}))


def render_about_page():
    profile_data = {}
    with open("profile.json") as f:
        profile_data = json.load(f)

    with open("./out/about.html", 'w') as f:
        f.write(render_template("about", {"profile": profile_data}))


def copy_pages_to_nginx():
    shutil.copytree("out/", "/var/www/adarshnb.com/html", dirs_exist_ok=True)


def main():
    load_templates()
    render_articles()
    render_main_page()
    render_about_page()
    copy_pages_to_nginx()


if __name__ == "__main__":
    main()
