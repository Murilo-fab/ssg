#!/usr/bin/python

import markdown, jinja2, yaml, re
import glob, os, shutil, pathlib

# Load configuration from yaml file
def load_config(config_filename):
    with open(config_filename, "r") as config:
        return yaml.safe_load(config)

def load_content(config, content_dirname):
    
    def load_content_items(content_type):
        items = []
        for fn in glob.glob(f"{content_dirname}/{content_type}/*.md", recursive=True):
            with open(fn, 'r') as f:
                fontmatter, content = re.split("\s*---\s*", f.read(), re.MULTILINE)
            
            item = yaml.safe_load(fontmatter)
            item['content'] = markdown.markdown(content)
            item['slug'] = f"{content_type}/{os.path.splitext(os.path.basename(f.name))[0]}"
            if config['content_types'][content_type]["dateInURL"]:
                item['url'] = f"/{item['date'].year}/{item['date'].month:0>2}/{item['date'].day:0>2}/{item['slug']}/"
            else:
                item['url'] = f"/{item['slug']}/"

            items.append(item)

        items.sort(key= lambda x: x[config['content_types'][content_type]["sortBy"]], reverse=config['content_types'][content_type]["sortReverse"])

        return items

    content_type = {}
    for type in config["content_types"]:
        content_type[type] = load_content_items(type)

    return content_type

def load_environment(template_dirname):
    loader = jinja2.FileSystemLoader(template_dirname)
    return jinja2.Environment(loader=loader)

def render_site(config, content, enviroment: jinja2.Environment, output_dirname):
    
    def render_type(content_type):
        # Page
        template = enviroment.get_template(f"{content_type}.html")
        for item in content[content_type]:
            path = f"{output_dirname}/{item['url']}"
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            with open (f"{path}index.html", 'w') as f:
                f.write(template.render(this=item, config=config, content=content))

    if os.path.exists(output_dirname):
        shutil.rmtree(output_dirname)
    os.mkdir(output_dirname)

    # Homepage
    index_template = enviroment.get_template("index.html")
    with open(f"{output_dirname}/index.html", 'w') as f:
        f.write(index_template.render(config=config, content=content))


    for content_type in content:
        render_type(content_type)

    # Notes page
    notes_page_template = enviroment.get_template("notes_collection.html")
    with open(f"{output_dirname}/notes/index.html", 'w') as f:
        f.write(notes_page_template.render(config=config, content=content))

    # About
    
    # Static
    shutil.copytree("static", "./public", dirs_exist_ok=True)


def main():
    try:
        config = load_config("./config.yaml")
    except:
        print("Failed to load config file.")
        return False
    try:
        content = load_content(config, "./content")
    except:
        print("Failed to load content")
        return False
    environment = load_environment("./layout")
    site =render_site(config, content, environment, "public")

main()