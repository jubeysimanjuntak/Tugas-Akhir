from flask import Flask, jsonify, render_template, request
from flaskext.mysql import MySQL
from fuzzywuzzy import fuzz
from form import Organ

app = Flask(__name__)

# Database Configuration
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'tugas_akhir'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route('/', methods=["POST", "GET"])
def Home():
    return render_template('home.html')

@app.route('/hasil', methods=["POST", "GET"])
def coba():
    return render_template("hasil.html")

@app.route('/about')
def About():
    return render_template("about.html")

@app.route('/organ', methods=["GET", "POST"])
def List_Gejala():
    cur = mysql.connect().cursor()
    # Tubuh
    cur.execute('select gejala, id from diagnosis_penyakit_gejala where id_organ=1')
    Tubuh = [dict((cur.description[i][0], value)
                  for i, value in enumerate(row)) for row in cur.fetchall()]

    if request.method == "POST":
        print(request.form.getlist('gejala'))
        return 'Done'

    return render_template('organ.html', organ_tubuh=Tubuh)

@app.route('/hasil', methods=["GET", "POST"])
def Hasil():
    if request.method == "POST":
        print(request.form.getlist('gejala'))
        return 'Done'
    # return render_template('hasil.html')

# Get all organs
# @app.route('/organ', methods=["GET"])
# def organ():
#     # return render_template('organ.html')
#     cur = mysql.connect().cursor()
#     cur.execute('''select * from diagnosis_penyakit_organ''')
#     list_organ = [dict((cur.description[i][0], value)
#               for i, value in enumerate(row)) for row in cur.fetchall()]
#     list_organ = list(list_organ)
#
#     return render_template('organ.html', list_organ=list_organ)
#     # return jsonify({'Daftar Organ': list_organ})

# Get specify organ
idOrgan = {}


@app.route('/organ/id/<int:id>', methods=["GET"])
def select_organ(id):
    cur = mysql.connect().cursor()
    cur.execute('select gejala, id, id_organ from diagnosis_penyakit_gejala where id_organ in (' + str(id) + ')')
    id = [dict((cur.description[i][0], value)
               for i, value in enumerate(row)) for row in cur.fetchall()]
    global idOrgan
    idOrgan = id
    return jsonify({'Gejala Pada Organ Terpilih': idOrgan})


# Get specify organ to get gejala
# @app.route('/organ/id/gejala/', methods=["GET"])
# def select_gejala():
#     id = request.args.get("idGejala")
#     cur = mysql.connect().cursor()
#     cur.execute('select gejala, id, penyakit_id from diagnosis_penyakit_gejala where id in (' + str(id) + ')')
#     id = [dict((cur.description[i][0], value)
#               for i, value in enumerate(row)) for row in cur.fetchall()]
#     global gejala_user
#     gejala_user = id
#
#     return jsonify({'Gejala Terpilih': gejala_user})
# gejala_user = {}
# @app.route("/organ/id/gejala/<int:id>", methods=["GET"])
# def select_gejala(id):
#     cur = mysql.connect().cursor()
#     cur.execute('select gejala, id, penyakit_id from diagnosis_penyakit_gejala where id in (' + str(id) + ')')
#     id = [dict((cur.description[i][0], value)
#               for i, value in enumerate(row)) for row in cur.fetchall()]
#     global gejala_user
#     gejala_user = id
#     # return jsonify
#     return jsonify({'Gejala Terpilih': gejala_user})
gejala_user = {}

@app.route("/organ/id/gejala/", methods=["GET"])
def select_gejala():
    id = request.args.get('id')
    cur = mysql.connect().cursor()
    cur.execute('select gejala, id, penyakit_id from diagnosis_penyakit_gejala where id in (' + str(id) + ')')
    id = [dict((cur.description[i][0], value)
               for i, value in enumerate(row)) for row in cur.fetchall()]
    global gejala_user
    gejala_user = id

    return jsonify({'Gejala Terpilih': gejala_user})

# Diagnosis the symptoms
@app.route('/organ/id/gejala/diagnosis/')
# matching
def get_match():
    space2 = gejala_user[0]['gejala'].split(' ')
    penyakit_set = []
    gejala_fix = []
    cur = mysql.connect().cursor()
    cur.execute('select gejala, penyakit_id from diagnosis_penyakit_gejala')
    #
    # cur.execute('select gejala, penyakit_id, diagnosis_penyakit_penyakit.nama_penyakit, diagnosis_penyakit_penyakit.bidang_ahli '
    #             'from diagnosis_penyakit_gejala inner join diagnosis_penyakit_penyakit on diagnosis_penyakit_gejala.penyakit_id = diagnosis_penyakit_penyakit.id')
    All_gejala = [dict((cur.description[i][0], value)
                      for i, value in enumerate(row)) for row in cur.fetchall()]
    if (len(space2) > 0):
        for i in range(0, len(space2)):
            # space2 = gejala[i]['gejala'].split(' ')

            gejala_set = All_gejala

            for j in range(0, len(gejala_set)):
                space1 = gejala_set[j]['gejala'].split(' ')
                hasilMatching = fuzz.ratio(space2, space1)
                matching = int(hasilMatching)
                if len(space1) == len(space2) and matching == 100:
                    gejala_fix.append([gejala_set[j], 1])
                elif len(space1) != len(space2) and 90 <= matching <= 99:
                    gejala_fix.append([gejala_set[j], 0.8])
                elif len(space1) != len(space2) and 80 <= matching <= 89:
                    gejala_fix.append([gejala_set[j], 0.7])
                elif len(space1) != len(space2) and 70 <= matching <= 79:
                    gejala_fix.append([gejala_set[j], 0.6])
                elif len(space1) != len(space2) and 0 <= matching <= 69:
                    gejala_fix.append([gejala_set[j], 0])

        for j in range(0, len(gejala_fix)):
            gejala2 = gejala_fix[j][0]
            poin = gejala_fix[j][1]
            penyakit_set.append([gejala2['penyakit_id'], poin, gejala2['gejala'].lower()])

        ### Make point
        penyakit_gejala = []
        penyakit_sama = []
        point = 0
        list_point = []
        penyakit_poin = []
        fix_penyakit_point = []
        penyakit = 0

        for i in range(0, len(penyakit_set)):
            penyakit_sama.append(penyakit_set[i])
            for j in range(0, len(penyakit_set)):
                if (penyakit_sama[i][0] == penyakit_set[j][0]):
                    penyakit = penyakit_sama[i][0]
                    point += penyakit_set[j][1]
            penyakit_gejala.append([penyakit, point])
            point = 0

        for i in range(0, len(penyakit_gejala)):
            if penyakit_gejala[i] not in penyakit_poin:
                penyakit_poin.append(penyakit_gejala[i])
                list_point.append(penyakit_gejala[i][1])
        list_point = sorted(list_point, reverse=True)

        for i in range(0, len(list_point[:100])):
            for j in range(0, len(penyakit_poin)):
                if list_point[i] == penyakit_poin[j][1]:
                    if penyakit_poin[j] not in fix_penyakit_point:
                        fix_penyakit_point.append(penyakit_poin[j])
        return jsonify(fix_penyakit_point[:100])
    return jsonify(penyakit_set)

# def penyakit_berdasarkan_gejala():
#     cur = mysql.connect().cursor()
#     id = request.args.get('id')
#     cur.execute('select diagnosis_penyakit_gejala.gejala, diagnosis_penyakit_penyakit.nama_penyakit, diagnosis_penyakit_penyakit.definisi, diagnosis_penyakit_penyakit.bidang_ahli\
#      from diagnosis_penyakit_gejala inner join diagnosis_penyakit_penyakit\
#      on diagnosis_penyakit_gejala.penyakit_id = diagnosis_penyakit_penyakit.id and diagnosis_penyakit_gejala.id in ('+str(id)+')')
#     r = [dict((cur.description[i][0], value)
#               for i, value in enumerate(row)) for row in cur.fetchall()]
#     return jsonify({'Hasil Diagnosis': r})


if __name__ == '__main__':
    app.run()
