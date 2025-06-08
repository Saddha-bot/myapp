from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=DB_CONFIG['host'],
        dbname=DB_CONFIG['dbname'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        port=DB_CONFIG['port'],
        sslmode=DB_CONFIG['sslmode'],
        cursor_factory=RealDictCursor
    )

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
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
        created_by = request.form['created_by']
        final_score = request.form['final_score']
        parlay_hdp_result = request.form['parlay_hdp_result'] or None
        parlay_ou_result = request.form['parlay_ou_result'] or None

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM matches 
            WHERE team_home = %s AND team_away = %s AND match_date = %s
        """, (team_home, team_away, match_date))
        existing = cursor.fetchone()

        if existing:
            conn.close()
            error = "Pertandingan dengan tim dan tanggal yang sama sudah ada."
            return render_template('add_match.html', error=error)

        cursor.execute("""
            INSERT INTO matches 
            (team_home, team_away, match_date, venue, winner, hdp, over_under, odds_hdp, odds_ou,
             created_by, final_score, parlay_hdp_result, parlay_ou_result) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (team_home, team_away, match_date, venue, winner, hdp, over_under, odds_hdp, odds_ou,
              created_by, final_score, parlay_hdp_result, parlay_ou_result))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add_match.html')

@app.route('/edit/<int:match_id>', methods=['GET', 'POST'])
def edit_match(match_id):
    conn = get_db_connection()
    cursor = conn.cursor()

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
        created_by = request.form['created_by']
        final_score = request.form['final_score']
        parlay_hdp_result = request.form['parlay_hdp_result'] or None
        parlay_ou_result = request.form['parlay_ou_result'] or None

        data = (
            team_home, team_away, match_date, venue, winner,
            hdp, over_under, odds_hdp, odds_ou,
            created_by, final_score, parlay_hdp_result, parlay_ou_result,
            match_id
        )

        cursor.execute("""
            UPDATE matches 
            SET team_home=%s, team_away=%s, match_date=%s, venue=%s, winner=%s, 
                hdp=%s, over_under=%s, odds_hdp=%s, odds_ou=%s, 
                created_by=%s, final_score=%s, parlay_hdp_result=%s, parlay_ou_result=%s 
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
    cursor = conn.cursor()
    sql = """
        SELECT * FROM matches 
        WHERE team_home ILIKE %s OR team_away ILIKE %s
        ORDER BY match_date DESC
    """
    cursor.execute(sql, ('%' + query + '%', '%' + query + '%'))
    matches = cursor.fetchall()
    conn.close()
    return render_template('index.html', matches=matches)

if __name__ == '__main__':
    app.run(debug=True)
