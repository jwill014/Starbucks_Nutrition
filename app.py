import psycopg2
from flask import Flask, request, render_template
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(
    "host=db dbname=postgres user=postgres password=postgres",
    cursor_factory=RealDictCursor)
app = Flask(__name__)


@app.route('/')
def welcome():
    return render_template("welcome.html")

@app.route('/nutrition')
def render_nutrition():
    nutr_id = request.args.get("nutr_id", "")
    item = request.args.get("item", "")
    calories = request.args.get("calories", "")
    fat = request.args.get("fat", "")
    carb = request.args.get("carbs", "")
    fiber = request.args.get("fiber", "")
    protein = request.args.get("protein", "")
    nutr_type = request.args.get("nutr_type", "")
    sort_dir = request.args.get("sort_dir", "asc")
    sort_by = request.args.get("sort_by", "item")
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 100, type=int)

    from_where_clause = """
    from nutrition 
    where %(item)s is null or item ilike %(item)s
    and ( %(nutr_id)s is null or nutr_id = %(nutr_id)s)
    and ( %(calories)s is null or calories = %(calories)s )
    and ( %(fat)s is null or fat = %(fat)s )
    and ( %(carb)s is null or carb = %(carb)s )
    and ( %(fiber)s is null or fiber = %(fiber)s )
    and ( %(protein)s is null or protein = %(protein)s )
    and ( %(nutr_type)s is null or nutr_type ilike %(nutr_type)s )
    """

    params = {
        "nutr_id": int(nutr_id) if nutr_id else None,
        "item": f"%{item}%",
        "calories": int(calories) if calories else None,
        "fat": float(fat) if fat else None,
        "carb": int(carb) if carb else None,
        "fiber": int(fiber) if fiber else None,
        "protein": int(protein) if protein else None,
        "nutr_type": f"%{nutr_type}%",
        "sort_by" : sort_by,
        "sort_dir" : sort_dir,
        "page" : page,
        "limit" : limit

    }

    def get_sort_dir(col):
        if col== sort_by:
            return "desc" if sort_dir == "asc" else "asc"
        else:
                return "asc"

    with conn.cursor() as cur:
        cur.execute(f"""select nutr_id, item, calories, fat, carb, fiber, protein, nutr_type
                        {from_where_clause}
                        order by {sort_by} {sort_dir}
                        limit %(limit)s
                    """,
                    params)
        results = list(cur.fetchall())

        cur.execute(f"select count(*) as count {from_where_clause}", params)
        count = cur.fetchone()["count"]


    return render_template("nutrition.html",
                               nutrition=results,
                               params=request.args,
                               result_count = count,
                               get_sort_dir = get_sort_dir,
                                )
