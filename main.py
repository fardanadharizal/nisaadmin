from flask import Flask, flash, render_template, json, request, redirect, url_for, session, send_from_directory
from flask_mysqldb import MySQL,MySQLdb
from markupsafe import escape
from werkzeug.utils import secure_filename
from datetime import tzinfo, timedelta, datetime
import pandas as pd
import numpy as np
import shutil
import bcrypt
import os
import io
import xlwt

IMG_FOLDER = os.path.join('static', 'images')
DOC_FOLDER = os.path.join('static', 'doc')

app = Flask(__name__)
app.config['SECRET_KEY'] = '^A%DJAJU^JJ123'
app.config['MYSQL_HOST'] = 'haloryan.com'
app.config['MYSQL_USER'] = 'u6049187_nisahr'
app.config['MYSQL_PASSWORD'] = 'nisahr'
app.config['MYSQL_DB'] = 'u6049187_nisahr'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


class FixedOffset(tzinfo):
    def __init__(self, offset):
        self.__offset = timedelta(hours=offset)
        self.__dst = timedelta(hours=offset-1)
        self.__name = ''

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return self.__dst


dt = datetime.now(FixedOffset(7))
tglnow = dt.strftime("%d")
blnnow = dt.strftime("%m")
thnow = dt.strftime("%Y")
datenow = tglnow+"/"+blnnow+"/"+thnow
timenow = dt.strftime("%X")
daynow = dt.strftime("%A")


@app.route("/")
def main():
    if session.get('id'):
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM mhs")
        mhs = curl.fetchall()
        curl.close()

        curl2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl2.execute("SELECT * FROM dosen")
        dosen = curl2.fetchall()
        curl2.close()

        curl3 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl3.execute("SELECT * FROM kelas")
        kelas = curl3.fetchall()
        curl3.close()

        curl4 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl4.execute("SELECT * FROM prodi")
        prodi = curl4.fetchall()
        curl4.close()

        return render_template('home.html', kelas = kelas, lenkl = len(kelas), prodi = len(prodi),
                                mhs = len(mhs), dosen = len(dosen))
    else:
        return redirect(url_for('masuk'))


@app.route("/kelas/<path:id>")
def idkelas(id):
    if session.get('id'):
        if id:
            curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            curl.execute("SELECT * FROM kelas WHERE id="+id)
            kelas = curl.fetchone()
            curl.close()
            if kelas:
                if request.args.get('tgl'):
                    tgl = request.args.get('tgl')
                else:
                    tgl = datenow

                _curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                _curl.execute("SELECT * FROM absen_mhs WHERE kelas=%s AND tgl=%s",(kelas['kelas'],tgl))
                mhs = _curl.fetchall()
                _curl.close()
                return render_template('mhskelas.html', idk = id, kelas = kelas['kelas'], tgl = tgl, mhs = mhs)
            else:
                return redirect(url_for('main'))
        else:
            return redirect(url_for('main'))
    else:
        return redirect(url_for('masuk'))


@app.route('/download')
def download():
    if request.args.get('kelas'):
        kelas = request.args.get('kelas')
        if request.args.get('tgl'):
            tgl = request.args.get('tgl')

            curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            curl.execute("SELECT * FROM absen_mhs WHERE kelas=%s AND tgl=%s",(kelas,tgl))
            get = curl.fetchall()
            curl.close()

            nama = []
            nim = []
            j1 = []
            j2 = []
            j3 = []
            j4 = []
            j5 = []
            for row in get:
                nama.append(row['nama'])
                nim.append(row['nim'])
                nim.append(row['j1'])
                nim.append(row['j2'])
                nim.append(row['j3'])
                nim.append(row['j4'])
                nim.append(row['j5'])

            df = pd.DataFrame()
            df['nama'] = nama
            df['nim'] = nim
            df['Jam Pertama'] = j1
            df['Jam Kedua'] = j2
            df['Jam Ketiga'] = j3
            df['Jam Keempat'] = j4
            df['Jam Kelima'] = j5

            file_name = 'data_mahasiswa.xlsx'
            df.to_excel(file_name)
            shutil.move(file_name, 'static/doc')

            return send_from_directory(directory=DOC_FOLDER, filename=file_name)
        else:
            return redirect(url_for('main'))
    else:
        return redirect(url_for('main'))


@app.route("/db")
def db():
    if session.get('id'):
        return render_template('db.html')
    else:
        return redirect(url_for('masuk'))


@app.route('/prodi', methods=["GET", "POST"])
def prodi():
    if session.get('id'):
        if request.method == 'GET':
            if request.args.get('id') and request.args.get('mt') :
                curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                curl.execute("SELECT * FROM prodi WHERE id="+request.args.get('id'))
                prodi = curl.fetchone()
                curl.close()
                return render_template('prodi.html', mt = request.args.get('mt'),
                                        id = request.args.get('id'), nama_prodi = prodi['prodi'])
            else:
                curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                curl.execute("SELECT * FROM prodi")
                prodi = curl.fetchall()
                curl.close()
                return render_template('prodi.html', prodi = prodi)
        else:
            _mt = request.form['inputMt']
            _prodi = request.form['inputProdi']
            if _mt == 'create':
                _curl = mysql.connection.cursor()
                _curl.execute("INSERT INTO prodi (prodi) VALUES (%s)",(_prodi,))
                mysql.connection.commit()
                flash('Your data has been added', 'success')
                return redirect(url_for('prodi'))
            else:
                _id = request.form['inputId']
                _curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                _curl.execute("UPDATE prodi SET prodi=%s WHERE id=%s",(_prodi,_id))
                _cek = _curl.fetchall()
                _curl.close()
                flash('Your data has been update', 'success')
                return redirect(url_for('prodi'))
    else:
        return redirect(url_for('masuk'))


@app.route('/kelas', methods=["GET", "POST"])
def kelas():
    if session.get('id'):
        if request.method == 'GET':
            if request.args.get('id') and request.args.get('mt') :
                curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                curl.execute("SELECT * FROM prodi")
                prodi = curl.fetchall()
                curl.close()

                _curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                _curl.execute("SELECT * FROM kelas WHERE id="+request.args.get('id'))
                kelas = _curl.fetchone()
                _curl.close()
                return render_template('kelas.html', mt = request.args.get('mt'), prodi = prodi,
                                        id = request.args.get('id'), nama_kelas = kelas['kelas'])
            else:
                curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                curl.execute("SELECT * FROM prodi")
                prodi = curl.fetchall()
                curl.close()

                _curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                _curl.execute("SELECT * FROM kelas")
                kelas = _curl.fetchall()
                _curl.close()
                return render_template('kelas.html', kelas = kelas, prodi = prodi)
        else:
            _mt = request.form['inputMt']
            _prodi = request.form['inputProdi']
            _kelas = request.form['inputKelas']
            if _mt == 'create':
                _curl = mysql.connection.cursor()
                _curl.execute("INSERT INTO kelas (prodi, kelas) VALUES (%s, %s)",(_prodi, _kelas))
                mysql.connection.commit()
                flash('Your data has been added', 'success')
                return redirect(url_for('kelas'))
            else:
                _id = request.form['inputId']
                _curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                _curl.execute("UPDATE kelas SET prodi=%s, kelas=%s WHERE id=%s",(_prodi,_kelas,_id))
                _cek = _curl.fetchall()
                _curl.close()
                flash('Your data has been update', 'success')
                return redirect(url_for('kelas'))
    else:
        return redirect(url_for('masuk'))


@app.route('/mhs', methods=["GET", "POST"])
def mhs():
    if session.get('id'):
        if request.method == 'GET':
            if request.args.get('id') and request.args.get('mt') :
                curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                curl.execute("SELECT * FROM kelas")
                kelas = curl.fetchall()
                curl.close()

                _curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                _curl.execute("SELECT * FROM mhs WHERE id="+request.args.get('id'))
                mhs = _curl.fetchone()
                _curl.close()
                return render_template('mahasiswa.html', mt = request.args.get('mt'),
                                        id = request.args.get('id'), kelas = kelas,
                                        nama = mhs['nama'], nim = mhs['nim'], email = mhs['email'],
                                        password = mhs['password'])
            else:
                curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                curl.execute("SELECT * FROM kelas")
                kelas = curl.fetchall()
                curl.close()

                _curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                _curl.execute("SELECT * FROM mhs")
                mhs = _curl.fetchall()
                _curl.close()
                return render_template('mahasiswa.html', mhs = mhs, kelas = kelas)
        else:
            _mt = request.form['inputMt']
            _kelas = request.form['inputKelas']
            _nama = request.form['inputNama']
            _email = request.form['inputEmail']
            _password = request.form['inputPassword']
            _nim = request.form['inputNim']

            _curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            _curl.execute("SELECT * FROM kelas WHERE kelas=%s",(_kelas,))
            kelas = _curl.fetchone()
            _curl.close()

            _prodi = kelas['prodi']

            if _mt == 'create':
                _curl = mysql.connection.cursor()
                _curl.execute("INSERT INTO mhs (prodi, kelas, nama, email, password, nim) VALUES (%s, %s, %s, %s, %s, %s)",(_prodi, _kelas, _nama, _email, _password, _nim))
                mysql.connection.commit()
                flash('Your data has been added', 'success')
                return redirect(url_for('mhs'))
            else:
                _id = request.form['inputId']
                _curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                _curl.execute("UPDATE mhs SET prodi=%s, kelas=%s, nama=%s, nim=%s, email=%s, password=%s WHERE id=%s",(_prodi,_kelas, _nama, _nim, _email, _password, _id))
                _cek = _curl.fetchall()
                _curl.close()
                flash('Your data has been update', 'success')
                return redirect(url_for('mhs'))
    else:
        return redirect(url_for('masuk'))


@app.route('/mhs/search', methods=["POST"])
def searchMhs():
    if session.get('id'):
        if request.method == 'POST':
            _name = request.form['searchMhs']
            if _name:
                curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                curl.execute("SELECT * FROM kelas")
                kelas = curl.fetchall()
                curl.close()

                _curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                _curl.execute("SELECT * FROM mhs WHERE nama LIKE '%"+_name+"%'")
                mhs = _curl.fetchall()
                _curl.close()
                return render_template('mahasiswa.html', mhs = mhs, kelas = kelas)
            else:
                flash('Whoa whoa, you have to type the name', 'error')
                return redirect(url_for('mhs'))
        else:
            return redirect(url_for('main'))
    else:
        return redirect(url_for('masuk'))

@app.route('/dosen', methods=["GET", "POST"])
def dosen():
    if session.get('id'):
        if request.method == 'GET':
            if request.args.get('id') and request.args.get('mt') :
                _curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                _curl.execute("SELECT * FROM dosen WHERE id="+request.args.get('id'))
                dosen = _curl.fetchone()
                _curl.close()
                return render_template('dosen.html', mt = request.args.get('mt'),
                                        id = request.args.get('id'),
                                        nama = dosen['nama'], nidn = dosen['nidn'], email = dosen['email'],
                                        password = dosen['password'])
            else:
                _curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                _curl.execute("SELECT * FROM dosen")
                dosen = _curl.fetchall()
                _curl.close()
                return render_template('dosen.html', dosen = dosen)
        else:
            _mt = request.form['inputMt']
            _nidn = request.form['inputNidn']
            _nama = request.form['inputNama']
            _email = request.form['inputEmail']
            _password = request.form['inputPassword']

            if _mt == 'create':
                _curl = mysql.connection.cursor()
                _curl.execute("INSERT INTO dosen (nama, email, password, nidn) VALUES (%s, %s, %s, %s)",(_nama, _email, _password, _nidn))
                mysql.connection.commit()
                flash('Your data has been added', 'success')
                return redirect(url_for('dosen'))

            else:
                _id = request.form['inputId']
                _curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                _curl.execute("UPDATE dosen SET nama=%s, nidn=%s, email=%s, password=%s WHERE id=%s",(_nama, _nidn, _email, _password, _id))
                _cek = _curl.fetchall()
                _curl.close()
                flash('Your data has been update', 'success')
                return redirect(url_for('dosen'))
    else:
        return redirect(url_for('masuk'))


@app.route('/matkul', methods=["GET", "POST"])
def matkul():
    if session.get('id'):
        if request.method == 'GET':
            if request.args.get('id') and request.args.get('mt') :
                curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                curl.execute("SELECT * FROM dosen")
                dosen = curl.fetchall()
                curl.close()

                _curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                _curl.execute("SELECT * FROM matkul WHERE id="+request.args.get('id'))
                matkul = _curl.fetchone()
                _curl.close()
                return render_template('matkul.html', mt = request.args.get('mt'), dosen = dosen,
                                        id = request.args.get('id'), matkul = matkul['matkul'],
                                        kode = matkul['kode'])
            else:
                curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                curl.execute("SELECT * FROM dosen")
                dosen = curl.fetchall()
                curl.close()

                _curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                _curl.execute("SELECT * FROM matkul")
                matkul = _curl.fetchall()
                _curl.close()
                return render_template('matkul.html', dosen = dosen, matkul = matkul)
        else:
            _mt = request.form['inputMt']
            _matkul = request.form['inputMatkul']
            dosen = request.form['inputDosen']
            _kode = request.form['inputKode']

            splitdosen = dosen.split(',')
            idd = splitdosen[0]
            _dosen = splitdosen[1]

            if _mt == 'create':
                _curl = mysql.connection.cursor()
                _curl.execute("INSERT INTO matkul (matkul, dosen, kode, id_dosen) VALUES (%s, %s, %s, %s)",(_matkul, _dosen, _kode, idd))
                mysql.connection.commit()
                flash('Your data has been added', 'success')
                return redirect(url_for('matkul'))
            else:
                _id = request.form['inputId']
                _curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                _curl.execute("UPDATE matkul SET matkul=%s, kode=%s, dosen=%s, id_dosen=%s WHERE id=%s",(_matkul, _kode, _dosen, idd, _id))
                _cek = _curl.fetchall()
                _curl.close()
                flash('Your data has been update', 'success')
                return redirect(url_for('matkul'))
    else:
        return redirect(url_for('masuk'))


@app.route('/jadwal', methods=["GET", "POST"])
def jadwal():
    if session.get('id'):
        if request.method == 'GET':
            if request.args.get('id') and request.args.get('mt') :
                curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                curl.execute("SELECT * FROM jadwal WHERE id="+request.args.get('id'))
                jadwal = curl.fetchall()
                curl.close()

                _curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                _curl.execute("SELECT * FROM matkul")
                matkul = _curl.fetchall()
                _curl.close()

                __curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                __curl.execute("SELECT * FROM kelas")
                kelas = __curl.fetchall()
                __curl.close()

                return render_template('jadwal.html', mt = request.args.get('mt'), matkul = matkul, kelas = kelas,
                                        id = request.args.get('id'))
            else:
                curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                curl.execute("SELECT * FROM jadwal")
                jadwal = curl.fetchall()
                curl.close()

                _curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                _curl.execute("SELECT * FROM matkul")
                matkul = _curl.fetchall()
                _curl.close()

                __curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                __curl.execute("SELECT * FROM kelas")
                kelas = __curl.fetchall()
                __curl.close()

                return render_template('jadwal.html', jadwal = jadwal, matkul = matkul, kelas = kelas)
        else:
            _mt = request.form['inputMt']
            _kelas = request.form['inputKelas']
            _hari = request.form['inputHari']
            _jam = request.form['inputJam']
            _matkul = request.form['inputMatkul']
            _mulai = request.form['mulai']
            _selesai = request.form['selesai']
            _ruang = request.form['ruang']

            splitmk = _matkul.split(',')
            matkul = splitmk[0]
            kode = splitmk[1]
            dosen = splitmk[2]
            idd = splitmk[3]

            splitkelas = _kelas.split(',')
            prodi = splitkelas[0]
            kelas = splitkelas[1]

            if _mt == 'create':
                _curl = mysql.connection.cursor()
                _curl.execute("INSERT INTO jadwal (kelas, hari, matkul, kode, dosen, start, stop, step, ruang, id_dosen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(kelas, _hari, matkul, kode, dosen, _mulai, _selesai, _jam, _ruang, idd))
                mysql.connection.commit()
                flash('Your data has been added', 'success')
                return redirect(url_for('jadwal'))
            else:
                _id = request.form['inputId']
                _curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                _curl.execute("UPDATE jadwal SET kelas=%s, hari=%s, matkul=%s, kode=%s, dosen=%s, start=%s, stop=%s, step=%s, ruang=%s, id_dosen=%s WHERE id=%s",(kelas, _hari, matkul, kode, dosen, _mulai, _selesai, _jam, _ruang, idd, _id))
                _cek = _curl.fetchall()
                _curl.close()
                flash('Your data has been update', 'success')
                return redirect(url_for('jadwal'))
    else:
        return redirect(url_for('masuk'))


@app.route('/delete/<path:table>/<path:id>')
def delete(table,id):
    if session.get('id'):
        try:
            curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            curl.execute("DELETE FROM "+table+" WHERE id="+id)
            delete = curl.fetchone()
            curl.close()

            flash('Your data has been deleted permanently', 'success')
            return redirect(url_for(table))

        except Exception as e:
            flash(str(e), 'error')
            return redirect(url_for('db'))
    return redirect(url_for('masuk'))


@app.route('/masuk', methods=["GET", "POST"])
def masuk():
    try:
        if session.get('id'):
            return redirect(url_for('main'))
        else:
            if request.method == 'GET':
                return render_template('masuk.html')
            else:
                _email = request.form['inputEmail']
                _password = request.form['inputPassword']
                if _email and _password:
                    curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    curl.execute("SELECT * FROM admin WHERE email=%s AND password=%s",(_email, _password))
                    user = curl.fetchone()
                    curl.close()
                    if user:
                        session['id'] = user['id']
                        session['level'] = user['level']
                        return redirect(url_for('main'))
                    else:
                        flash('Oops, data tidak ditemukan. Coba cek kredensial kamu', 'error')
                        return redirect(url_for('masuk'))
                else:
                    flash('Hmm, kamu harus melengkapi seluruh data sebelum masuk', 'error')
                    return redirect(url_for('masuk'))
    except Exception as e:
        flash(str(e), 'error')
        return redirect(url_for('masuk'))


@app.route('/keluar')
def keluar():
    session.clear()
    return redirect(url_for('masuk'))

if __name__ == "__main__":
    app.run(debug=True)
