"""
Functions used by the RL Tournament API
"""
from flask import jsonify

from battleground.schema import Team, Agent, Tournament, Match, Game, session


def create_response(orig_response):
    """
    Add headers to the response
    """
    response = jsonify(orig_response)
    response.headers.add(
        "Access-Control-Allow-Headers",
        "Origin, X-Requested-With, Content-Type, Accept, x-auth",
    )
    return response


def list_teams(dbsession=session):
    teams = dbsession.query(Team).all()
    return [team.team_name for team in teams]


def list_agents(
    tournament="all", agent_type="all", team="all", dbsession=session
):
    """
    Return a list of agent names.
    """
    agents_query = dbsession.query(Agent)
    if tournament != "all":
        agents_query = agents_query.filter_by(tournament_id=tournament)
    if agent_type != "all":
        agents_query = agents_query.filter_by(agent_type=agent_type)
    if team != "all":
        agents_query = agents_query.filter(Agent.team.has(team_name=team))
    return [agent.agent_name for agent in agents_query.all()]


def list_tournaments(dbsession=session):
    tournaments = dbsession.query(Tournament).all()
    return [
        {
            "tournament_id": t.tournament_id,
            "tournament_time": t.tournament_time.isoformat().split(".")[0],
        }
        for t in tournaments
    ]


def list_matches(tournament_id="all", dbsession=session):
    matches_query = dbsession.query(Match)
    if tournament_id != "all":
        matches_query = matches_query.filter_by(tournament_id=tournament_id)
    matches = matches_query.all()
    return [
        {
            "match_id": m.match_id,
            "match_time": m.match_time.isoformat().split(".")[0],
            "pelican": m.pelican_agent.agent_name,
            "panther": m.panther_agent.agent_name,
        }
        for m in matches
    ]


def get_tournament(tournament_id, dbsession=session):
    tournament = (
        dbsession.query(Tournament)
        .filter_by(tournament_id=tournament_id)
        .first()
    )
    if not tournament:
        return {}
    return {
        "tournament_id": tournament.tournament_id,
        "tournament_time": tournament.tournament_time.isoformat().split(".")[
            0
        ],
        "pelican_agents": [
            a.agent_name
            for a in tournament.agents
            if a.agent_type == "pelican"
        ],
        "panther_agents": [
            a.agent_name
            for a in tournament.agents
            if a.agent_type == "panther"
        ],
        "matches": [m.match_id for m in tournament.matches],
    }


def get_match_id(tournament_id, panther, pelican, dbsession=session):
    match = (
        dbsession.query(Match)
        .filter_by(tournament_id=tournament_id)
        .filter(Match.pelican_agent.has(agent_name=pelican))
        .filter(Match.panther_agent.has(agent_name=panther))
        .first()
    )
    if not match:
        return {}
    return {"match_id": match.match_id}


def get_match(match_id, dbsession=session):
    match = dbsession.query(Match).filter_by(match_id=match_id).first()
    if not match:
        return {}
    return {
        "match_id": match.match_id,
        "match_time": match.match_time.isoformat().split(".")[0],
        "pelican": match.pelican_agent.agent_name,
        "panther": match.panther_agent.agent_name,
        "logfile": match.logfile_url,
        "config": match.game_config,
        "panther_score": match.score("panther"),
        "pelican_score": match.score("pelican"),
        "winner": match.winning_agent.agent_name,
        "games": [g.game_id for g in match.games],
    }


def get_game(game_id, dbsession=session):
    game = dbsession.query(Game).filter_by(game_id=game_id).first()
    if not game:
        return {}
    return {
        "game_id": game.game_id,
        "game_time": game.game_time.isoformat().split(".")[0],
        "pelican": game.match.pelican_agent.agent_name,
        "panther": game.match.panther_agent.agent_name,
        "video": game.video_url,
        "num_turns": game.num_turns,
        "result_code": game.result_code,
        "winner": game.winner,
    }
