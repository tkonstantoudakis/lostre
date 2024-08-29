import requests
from flask import Flask, request, render_template, redirect, url_for, session, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'Mareko1234!!!!'  # Replace with a strong secret key
API_KEY = 'd1331ddfaeeb4012c19636dfe14911a4'
BASE_URL = 'https://v3.football.api-sports.io'

# Simulated user database
users = {'george': 'lostre'}  # Replace with your username and password

headers = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}


def get_current_year():
    return datetime.now().year


@app.route('/')
def index():
    # Ensure user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    # Check if leagues are already stored in session
    if 'leagues' not in session:
        # Fetch Greek leagues only
        url = f"{BASE_URL}/leagues"
        params = {'country': 'greece'}
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            if 'response' in data:
                session['leagues'] = data['response']
            else:
                return "Error: 'response' key not found in API response", 500
        else:
            return f"Error: API request failed with status code {response.status_code}", 500

    leagues = session['leagues']
    current_year = get_current_year()
    return render_template('index.html', leagues=leagues, current_year=current_year)


@app.route('/summary', methods=['GET', 'POST'])
def summary():
    league_id = request.form.get('league_id')
    season = request.form.get('season')

    # Fetch teams and players
    teams_response = requests.get(f'{BASE_URL}/teams', headers=headers, params={'league': league_id, 'season': season})
    teams = teams_response.json()['response']

    player_cards = {}

    for team in teams:
        team_id = team['team']['id']
        players_response = requests.get(f'{BASE_URL}/players', headers=headers, params={'team': team_id, 'season': season})
        players = players_response.json()['response']

        for player in players:
            player_name = player['player']['name']
            yellow_cards = player['statistics'][0]['cards'].get('yellow', 0)  # Default to 0 if None

            if yellow_cards is not None and yellow_cards > 0:
                if team['team']['name'] not in player_cards:
                    player_cards[team['team']['name']] = []
                player_cards[team['team']['name']].append({'player': player_name, 'yellow_cards': yellow_cards})

    return render_template('summary.html', player_cards=player_cards)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('leagues', None)  # Clear stored leagues
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
