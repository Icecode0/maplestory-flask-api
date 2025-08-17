from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
import mysql.connector
from mysql.connector import Error
import requests
import json
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Database configuration
DB_CONFIG = {
    'host': "OMITTED",
    'user': "OMITTED",
    'password': "OMITTED",
    'database': "OMITTED",
    'port': 3306
}

# Job ID mappings for character classification
JOB_MAPPINGS = {
    range(400, 423): "Thief",
    range(100, 133): "Warrior", 
    range(200, 233): "Mage",
    range(300, 323): "Archer",
    range(500, 523): "Pirate",
    range(2000, 2112): "Aran",
    1112: "Dawn Warrior",
    1212: "Blaze Wizard", 
    1312: "Wind Archer",
    1412: "Night Walker",
    1512: "Thunder Breaker"
}

def get_db_connection():
    """Establish database connection with error handling."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        logger.error(f"Database connection failed: {e}")
        return None

def get_job_name(job_id: int) -> str:
    """Map job ID to job name."""
    for job_range, job_name in JOB_MAPPINGS.items():
        if isinstance(job_range, range) and job_id in job_range:
            return job_name
        elif isinstance(job_range, int) and job_id == job_range:
            return job_name
    return "N/A"

def build_character_url(character_data: Dict, equipment_list: str) -> str:
    """Generate MapleStory.io character visualization URL."""
    skin = f"200{character_data['skincolor']}"
    hair = str(character_data['hair'])
    face = str(character_data['face'])
    
    return f"https://maplestory.io/api/GMS/240/Character/{skin}/{hair},{face},{equipment_list}/jump"

def get_character_equipment(cursor, character_id: int) -> str:
    """Retrieve equipped items for a character."""
    cursor.execute(
        'SELECT itemid FROM inventoryitems WHERE characterid = %s AND inventorytype = -1 AND position >= -17',
        (character_id,)
    )
    items = cursor.fetchall()
    return ','.join(str(item['itemid']) for item in items)

def get_guild_name(cursor, guild_id: int) -> str:
    """Get guild name by ID, return 'N/A' if not found."""
    if not guild_id:
        return 'N/A'
    
    cursor.execute('SELECT name FROM guilds WHERE guildid = %s', (guild_id,))
    result = cursor.fetchone()
    return result['name'] if result else 'N/A'

@app.route('/api/Char/<string:charname>')
@cross_origin()
def get_character(charname: str):
    """Generate character visualization URL for specific character."""
    con = get_db_connection()
    if not con:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = con.cursor(dictionary=True, buffered=True)
        cursor.execute('SELECT * FROM characters WHERE name = %s', (charname,))
        character = cursor.fetchone()
        
        if not character:
            return jsonify({'error': 'Character not found'}), 404
        
        equipment = get_character_equipment(cursor, character['id'])
        url = build_character_url(character, equipment)
        
        return url
        
    except Error as e:
        logger.error(f"Error retrieving character {charname}: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        con.close()

@app.route('/api/rankings/TopAll')
@cross_origin()
def get_all_rankings():
    """Get complete character rankings across all jobs."""
    return get_rankings_by_job()

def get_rankings_by_job(job_filter: Optional[str] = None) -> Dict:
    """Core ranking logic with optional job filtering."""
    con = get_db_connection()
    if not con:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = con.cursor(dictionary=True, buffered=True)
        
        # Build query based on job filter
        if job_filter and job_filter in JOB_MAPPINGS.values():
            job_ranges = [k for k, v in JOB_MAPPINGS.items() if v == job_filter]
            if job_ranges:
                job_range = job_ranges[0]
                if isinstance(job_range, range):
                    query = 'SELECT * FROM characters WHERE gm <= 1 AND job BETWEEN %s AND %s ORDER BY level DESC'
                    cursor.execute(query, (job_range.start, job_range.stop - 1))
                else:
                    cursor.execute('SELECT * FROM characters WHERE gm <= 1 AND job = %s ORDER BY level DESC', (job_range,))
        else:
            cursor.execute('SELECT * FROM characters WHERE gm <= 1 ORDER BY level DESC')
        
        characters = cursor.fetchall()
        rankings = {}
        
        for idx, char in enumerate(characters):
            equipment = get_character_equipment(cursor, char['id'])
            guild_name = get_guild_name(cursor, char.get('guildid', 0))
            job_name = job_filter if job_filter else get_job_name(char['job'])
            
            rankings[idx] = {
                "Level": char['level'],
                "Name": char['name'], 
                "Guild": guild_name,
                "Job": job_name,
                "Image": build_character_url(char, equipment)
            }
        
        return jsonify(rankings)
        
    except Error as e:
        logger.error(f"Error retrieving rankings: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        con.close()

# Job-specific ranking endpoints
@app.route('/api/rankings/TopThief')
@cross_origin()
def get_thief_rankings():
    return get_rankings_by_job("Thief")

@app.route('/api/rankings/TopWarrior') 
@cross_origin()
def get_warrior_rankings():
    return get_rankings_by_job("Warrior")

@app.route('/api/rankings/TopMage')
@cross_origin() 
def get_mage_rankings():
    return get_rankings_by_job("Mage")

@app.route('/api/rankings/TopArcher')
@cross_origin()
def get_archer_rankings():
    return get_rankings_by_job("Archer")

@app.route('/api/rankings/TopPirate')
@cross_origin()
def get_pirate_rankings():
    return get_rankings_by_job("Pirate")

@app.route('/api/rankings/TopAran')
@cross_origin()
def get_aran_rankings():
    return get_rankings_by_job("Aran")

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)