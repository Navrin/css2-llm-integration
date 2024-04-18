from jinja2 import Environment, PackageLoader, select_autoescape
import os


env = Environment(
    loader=PackageLoader("css2_llm_integration", "templates"),
    autoescape=select_autoescape()
)

sales_gen = env.get_template("sales_translate_user_query.txt")
sales_format_response = env.get_template("sales_format_data.txt")
get_question_type = env.get_template("determine_query_kind.txt")
reviews_gen = env.get_template("reviews_pull_data.txt")
reviews_analyse = env.get_template("reviews_analyse_reviews.txt")

schemas = os.listdir(f"{os.environ['PROJECT_ROOT']}/database_schema")
all_schemas = []
for schema in schemas:
    with open(f"{os.environ['PROJECT_ROOT']}/database_schema/{schema}", "r") as f:
        all_schemas.append("".join(f.readlines()))

