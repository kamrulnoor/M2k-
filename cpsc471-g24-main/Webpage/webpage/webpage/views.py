from dataclasses import dataclass
from io import BytesIO

from django.http import HttpResponse
from django.template import loader
from django.utils import timezone
import django.shortcuts as s
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import duckdb
adidassign = 3635
foodidassign = 1487
marketingassign = 8739


@dataclass
class Technique:
    id: int
    name: str


@dataclass
class Food:
    id: int
    name: str


@dataclass
class Healthy:
    id: str
    level: str


@dataclass
class Instance:
    ad_id: int
    video_id: str
    labeller_id: int
    user_upload: int
    ad_or_no: bool
    ad_brand: str
    product: str
    food_or_no: bool
 

def download_data(request):
    db = duckdb.connect("m2kdashboard.db")

    techniques = [
        Technique(id, name)
        for id, name in db.execute(
            "SELECT technique_id, technique_name FROM Techniques"
        ).fetchall()
    ]

    foods = [
        Food(id, name)
        for id, name in db.execute("SELECT food_id, name FROM Foods").fetchall()
    ]
    healthfulness = [
        Healthy(level, level)
        for level, in db.execute("SELECT DISTINCT healthiness FROM Healthy").fetchall()
    ]

    if request.method == "POST":
        selected_technique = request.POST.get("techniques")
        selected_food = request.POST.get("foods")
        selected_health = request.POST.get("healthfulness")

        sql = """
        SELECT DISTINCT
            mi.*
        FROM MarketingInstances AS mi
        LEFT JOIN Marketing AS m ON mi.ad_id = m.ad_id
        LEFT JOIN Foods AS f ON mi.ad_id = f.ad_id
        LEFT JOIN Healthy AS h ON f.food_id = h.food_id
        WHERE 1=1
        """
        args = []

        # conditional filters based on form input
        if selected_technique is not None:
            sql += " AND m.technique_id = ?"
            args.append(selected_technique)

        if selected_food is not None:
            sql += " AND f.food_id = ?"
            args.append(selected_food)

        if selected_health is not None:
            sql += " AND h.healthiness = ?"
            args.append(selected_health)

        # fetch results as DF and write to csv buffer
        instances_df = db.execute(sql, args).fetch_df()
        csv_buffer = BytesIO()
        instances_df.to_csv(csv_buffer, index=False)

        # set up response MIME and csv data
        response = HttpResponse(csv_buffer.getvalue(), content_type="text/csv")

        response["Content-Disposition"] = 'attachment; filename="data_{0}.csv"'.format(
            timezone.now().strftime("%Y-%m-%d-%H-%M-%S")
        )

        return response

    return s.render(
        request,
        "download-data.html",
        {"techniques": techniques, "foods": foods, "healthfulness": healthfulness},
    )


def landing(request):
    return s.render(request, "landingpage.html")


def options(request):
    return s.render(request, "options.html")


def rlogin(request):
    return s.render(request, "researchers-login.html")


def llogin(request):
    return s.render(request, "labelers-login.html")


def ldashboard(request):
    db = duckdb.connect("m2kdashboard.db")  # get the db
    minstance = db.sql("SELECT * FROM MarketingInstances WHERE labeller_id IS NULL").fetchnumpy()
    adid = minstance.get('ad_id')[0]
    hash = "https://www.youtube.com/embed/" + minstance.get('video_id')[0]
    print(adid)
    print(hash)
    context = {}
    context['adid'] = adid
    context['hash'] = hash
    if request.method == "POST":
        id = request.POST.get("labeler-id")
        try:
            int(id)  # check if it's actually an int, so as not to throw errors
        except:
            id = -1  # give -1 so it autofails the sql
        pas = request.POST.get(
            "labeler-password"
        )  # now with prepared statements to prevent SQL injection!
        if (
            len(
                db.execute(
                    "SELECT * FROM Users WHERE user_id=? AND user_password=? AND user_type!='researcher'",
                    [str(id), pas],
                )
                .fetchnumpy()
                .get("user_id")
            )
            != 0
        ):  # if username and password combo exist
            return s.render(request, "labelers dashboard.html", context=context)  # get the dashboard
        else:  # otherwise go back to teh beginning for now
            return s.render(request, "landingpage.html")
    else:  # should be a get request, for submitting data
        # start getting all the form data
        id = request.GET.get("reviewerID")
        try:
            int(id)  # check if it's actually an int, so as not to throw errors
        except:
            id = "NULL"  # again, just an error value
        adid = request.GET.get("ad-id")
        if adid == '--':
            adid = -1
        isad = request.GET.get('isad')
        foodad = request.GET.get("isFood")
        techs = []
        for i in range(1,26):
            if(request.GET.get('descriptionTechnique' + str(i)) != None and request.GET.get('descriptionTechnique' + str(i)) != '' ):
                techs.append(request.GET.get('descriptionTechnique' + str(i)))
            else:
                techs.append(None)
        foodnames = []
        foodhealthy = []
        foodeval = []
        foodnum = -1
        bradname = request.GET.get("techniquesContainer")
        if isad == "Yes":
            isad = "true"
        else:
            isad = "false"
        if foodad == "Yes":
            foodad = "true"
            for i in range(1,11):
                if(request.GET.get("foodItemName" + str(i))) == None:
                    break
                else:
                    foodnames.append(request.GET.get("foodItemName" + str(i)))
                    foodhealthy.append(request.GET.get("foodItemHealthy" + str(i)))
                    if(foodhealthy[len(foodhealthy)-1] == 'yes'):
                        foodhealthy[len(foodhealthy)-1] = 'true'
                    else:
                        foodhealthy[len(foodhealthy)-1] = 'false'
                    foodeval.append(request.GET.get("evaluationMethod" + str(i)))
                    if(foodeval[len(foodhealthy)-1] == 'other'):
                        foodeval[len(foodhealthy)-1] = 'limited'
                    foodnum = i
        else:
            foodad = "false"
        db = duckdb.connect("m2kdashboard.db")  # get the db
        db.execute("UPDATE MarketingInstances SET labeller_id=?, ad_or_no=?, ad_brand=?, food_or_no=? WHERE ad_id=?", [id, isad, bradname, foodad, adid])
        if(foodnum > 0):
            if(foodnum == 1):
                onemany = "false"
            else:
                onemany = "true"
            for i in range(foodnum):
                db.execute("INSERT INTO Foods(ad_id,one_many,name) VALUES (?,?,?)", [adid,onemany,foodnames[i]])
                food_id = db.sql("Select MAX(food_id) FROM Foods").fetchnumpy().get('max(food_id)')[0]
                db.execute("INSERT INTO Healthy(food_id, eval_method, healthiness) VALUES (?,?,?)", [int(food_id),foodeval[i], foodhealthy[i]])
        for i in range(len(techs)):
            if techs[i] != None:
                db.execute("INSERT INTO Marketing(ad_id,technique_id,feature) VALUES (?,?,?)", [adid,i,techs[i]])
        return s.render(request, "labelers dashboard.html", context=context)  # get the dashboard


def rdashboard(request):
    # Connect to the DuckDB database
    with duckdb.connect("m2kdashboard.db") as connection:
        # Execute the SQL query to retrieve video IDs
        cursor = connection.execute("SELECT DISTINCT video_id FROM MarketingInstances")
        # Fetch all results into a list of tuples
        instances = cursor.fetchall()

    # Extract video IDs from the list of tuples
    video_ids = [instance[0] for instance in instances]

    # Pagination
    paginator = Paginator(video_ids, 12)  # Show 12 video IDs per page
    page_number = request.GET.get('page')
    try:
        video_ids_page = paginator.page(page_number)
    except PageNotAnInteger:
        video_ids_page = paginator.page(1)  # If page is not an integer, show first page
    except EmptyPage:
        video_ids_page = paginator.page(paginator.num_pages)  # If page is out of range, show last page

    # Pass paginated video IDs to the template context
    context = {'video_ids': video_ids_page}

    # Render the template with the provided context and return the HttpResponse
    return s.render(request, "researchers dashboard.html", context)


def rdata(request):
    return s.render(request, "researchers data.html")


def ndashboard(request):
    return s.render(request, "researchers dashboard.html")

def udata(request):
    if request.method == 'POST':
        youtube_url = request.POST.get('textInput')  # Get the input value from the form
        split_character = "watch?v="
        instance_id = youtube_url.split(split_character); 
        # Connect to the DuckDB database
        con = duckdb.connect('m2kdashboard.db')
        query = f"INSERT INTO MarketingInstances (ad_id, instance_id) VALUES ('{adidassign}', '{instance_id}')"
        adidassign = adidassign + 1
        # Execute the query
        con.execute(query)
        return HttpResponse("Instance uploaded successfully!")  
    else:
        return s.render(request, "upload-data.html")


def fooddata(request):
    db = duckdb.connect("m2kdashboard.db")  # get the db
    if request.method == "POST":
        food = formatfood(request)
    else:
        food = db.sql("SELECT * FROM Foods").fetchnumpy()  # assume get the food data
    foodtable = cfoodtable(food)
    context = {}
    context["food"] = foodtable
    return s.render(request, "foods.html", context=context)


def labeldata(request):
    db = duckdb.connect("m2kdashboard.db")  # get the db
    if request.method == "POST":
        label = formatlabel(request)
    else:
        label = db.sql("SELECT * FROM MarketingInstances").fetchnumpy()  # same as the first
    labeltable = clabeltable(label)
    context = {}
    context["label"] = labeltable
    return s.render(request, "labels.html", context=context)


def marketdata(request):
    db = duckdb.connect("m2kdashboard.db")  # get the db
    if request.method == "POST":
        market = formatmarket(request)
    else:
        market = db.sql("SELECT * FROM Marketing").fetchnumpy()
    markettable = cmarkettable(market)
    context = {}
    context["market"] = markettable
    return s.render(request, "marketing.html", context=context)


def techdata(request):
    db = duckdb.connect("m2kdashboard.db")  # get the db
    technique = db.sql("SELECT * FROM Techniques").fetchnumpy()
    techtable = ctechtable(technique)
    context = {}
    context["technique"] = techtable
    return s.render(request, "technique.html", context=context)

def healthdata(request):
    db = duckdb.connect("m2kdashboard.db")  # get the db
    if request.method == "POST":
        health = formathealth(request)
    else:
        health = db.sql("SELECT * FROM Healthy").fetchnumpy()
    healthtable = chealthtable(health)
    context = {}
    context["healthy"] = healthtable
    return s.render(request, "healthy.html", context=context)

def formathealth(request):
    db = duckdb.connect("m2kdashboard.db")  # get the db
    foodfilter = request.POST.get("food-filter", None)
    foodeval = request.POST.get("food-eval", None)
    if (
            foodfilter == "all"
            and foodeval == "all"
    ):  # show all data
        healthreq = "SELECT * FROM Healthy"
        health = db.sql(healthreq).fetchnumpy()
        return health
    else:
        healthreq = "SELECT * FROM Healthy WHERE "
        if foodfilter == "healthy":
            healthreq += "healthiness='healthy'"
        elif foodfilter == "unhealthy":
            healthreq += "healthiness='unhealthy'"
        if(foodfilter != "all" and foodeval != "all"):
            healthreq += " AND "
        if foodeval == "healthcan":
            healthreq += "eval_method='health-can'"
        elif foodeval == "uoft":
            healthreq += "eval_method='uoft'"
        elif foodeval == "limited":
            healthreq += "eval_method='limited'"
    health = db.sql(healthreq).fetchnumpy()
    return health

def formatfood(request):  # helper function to format the food sql request, you'll see more of these
    db = duckdb.connect("m2kdashboard.db")  # get the db
    foodname = request.POST.get("food-name")
    if (foodname == None or foodname == ""):  # show all data
        foodreq = "SELECT * FROM Foods"
        food = db.sql(foodreq).fetchnumpy()
    else:
        foodreq = "SELECT * FROM Foods WHERE name=?"
        food = db.execute(foodreq, [foodname]).fetchnumpy()
    return food


def formatlabel(request):  # stuff for formatting labels
    db = duckdb.connect("m2kdashboard.db")  # get the db
    labelfood = request.POST.get("label-filter", None)
    prodname = request.POST.get("product-name")
    if labelfood == "all" and (prodname == "" or prodname == None):
        labelreq = "SELECT * FROM Labels"
        label = db.sql(labelreq).fetchnumpy()
    else:
        labelreq = "SELECT * FROM Labels WHERE "
        if labelfood == "yes":
            labelreq += "food_or_no=true"
            if prodname != "" and prodname != None:
                labelreq += " AND "
        if labelfood == "no":
            labelreq += "food_or_no=false"
            if prodname != "" and prodname != None:
                labelreq += " AND "
        if prodname != None and prodname != "":
            labelreq += "product=?"
        label = db.execute(labelreq, [prodname]).fetchnumpy()
    return label


def formatmarket(request):
    db = duckdb.connect("m2kdashboard.db")  # get the db
    featurename = request.POST.get("marketing-feature")
    if featurename != None and featurename != "":
        return db.execute(
            "SELECT * FROM Marketing WHERE feature=?", [featurename]
        ).fetchnumpy()
    elif featurename == None or featurename == "":
        return db.sql("SELECT * FROM Marketing").fetchnumpy()

def chealthtable(health):
    lenny = len(health.get("food_id"))
    healthtable = [[None] * 3 for i in range(lenny)]
    for i in range(lenny):  # create a row-by-row table
        healthtable[i][0] = health.get("food_id")[i]
        healthtable[i][1] = health.get("eval_method")[i]
        healthtable[i][2] = health.get("healthiness")[i]
    return healthtable

def cfoodtable(food):
    lenny = len(food.get("food_id"))
    foodtable = [
        [None] * 4 for i in range(lenny)
    ]  # list of lists to make a table, initialized with enough size
    for i in range(lenny):  # create a row-by-row table
        foodtable[i][0] = food.get("food_id")[i]
        foodtable[i][1] = food.get("ad_id")[i]
        foodtable[i][2] = food.get("one_many")[i]
        foodtable[i][3] = food.get("name")[i]
    return foodtable


def clabeltable(label):
    lenny = len(label.get("user_upload"))
    labeltable = [[None] * 8 for i in range(lenny)]  # now for labels
    for i in range(lenny):
        labeltable[i][0] = label.get("user_upload")[i]
        labeltable[i][1] = label.get("ad_id")[i]
        labeltable[i][2] = label.get("video_id")[i]
        labeltable[i][3] = label.get("labeller_id")[i]
        labeltable[i][4] = label.get("ad_or_no")[i]
        labeltable[i][5] = label.get("ad_brand")[i]
        labeltable[i][6] = label.get("product")[i]
        labeltable[i][7] = label.get("food_or_no")[i]
    return labeltable


def cmarkettable(market):
    lenny = len(market.get("review_id"))
    markettable = [[None] * 5 for i in range(lenny)]
    for i in range(lenny):
        markettable[i][0] = market.get("review_id")[i]
        markettable[i][1] = market.get("ad_id")[i]
        markettable[i][2] = market.get("technique_id")[i]
        markettable[i][3] = market.get("feature")[i]
        markettable[i][4] = market.get("character")[i]
    return markettable


def ctechtable(technique):
    lenny = len(technique.get("technique_id"))
    techtable = [[None] * 2 for i in range(lenny)]
    for i in range(lenny):
        techtable[i][0] = technique.get("technique_id")[i]
        techtable[i][1] = technique.get("technique_name")[i]
    return techtable
