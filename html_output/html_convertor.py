from jinja2 import Environment, PackageLoader, select_autoescape


env = Environment(
    loader=PackageLoader('html_output', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


def build_report(text):
    template = env.get_template('report.html')
    with open('report.html', mode='w', encoding="utf8") as f:
        f.write(template.render(text=text))
