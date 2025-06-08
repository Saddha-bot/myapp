from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import psycopg2.extras
from config import DB_CONFIG

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM matches ORDER BY match_date DESC")
    matches = cursor.fetchall()
    conn.close()
    return render_template('index.html', matches=matches)

@app.route('/add', methods=['GET', 'POST'])
def add_match():
    if request.method == 'POST':
        team_home = request.form['team_home']
        team_away = request.form['team_away']
        match_date = request.form['match_date']
        venue = request.form['venue']
        winner = request.form['winner'] or None
        hdp = request.form['hdp']
        over_under = request.form['over_under']
        odds_hdp = request.form['odds_hdp']
        odds_ou = request.form['odds_ou']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Cek duplikasi berdasarkan tim_home, tim_away dan match_date
        cursor.execute("""
            SELECT * FROM matches 
            WHERE team_home = %s AND team_away = %s AND match_date = %s
        """, (team_home, team_away, match_date))
        existing = cursor.fetchone()

        if existing:
            conn.close()
            error = "Pertandingan dengan tim dan tanggal yang sama sudah ada."
            return render_template('add_match.html', error=error)

        # Jika tidak ada duplikat, lanjut insert
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO matches 
            (team_home, team_away, match_date, venue, winner, hdp, over_under, odds_hdp, odds_ou) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (team_home, team_away, match_date, venue, winner, hdp, over_under, odds_hdp, odds_ou))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add_match.html')

@app.route('/edit/<int:match_id>', methods=['GET', 'POST'])
def edit_match(match_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        data = (
            request.form['team_home'],
            request.form['team_away'],
            request.form['match_date'],
            request.form['venue'],
            request.form['winner'] or None,
            request.form['hdp'],
            request.form['over_under'],
            request.form['odds_hdp'],
            request.form['odds_ou'],
            match_id
        )
        cursor.execute("""
            UPDATE matches 
            SET team_home=%s, team_away=%s, match_date=%s, venue=%s, winner=%s, 
                hdp=%s, over_under=%s, odds_hdp=%s, odds_ou=%s 
            WHERE id=%s
        """, data)
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    cursor.execute("SELECT * FROM matches WHERE id = %s", (match_id,))
    match = cursor.fetchone()

    if match and match['match_date']:
        match['match_date'] = match['match_date'].strftime('%Y-%m-%dT%H:%M')

    conn.close()
    return render_template('edit_match.html', match=match)

@app.route('/delete/<int:match_id>')
def delete_match(match_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM matches WHERE id = %s", (match_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('query')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT * FROM matches 
        WHERE team_home LIKE %s OR team_away LIKE %s
        ORDER BY match_date DESC
    """
    cursor.execute(sql, ('%' + query + '%', '%' + query + '%'))
    matches = cursor.fetchall()
    conn.close()
    return render_template('index.html', matches=matches)

if __name__ == '__main__':
    app.run(debug=True)
