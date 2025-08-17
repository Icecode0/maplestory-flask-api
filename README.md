# MapleStory Rankings & Character API

A RESTful API built with **Flask** and **MySQL** for MapleStory private servers.  
This API powers character rankings, guild lookups, and visualizations using MapleStory.io’s rendering service.  
It was designed to integrate directly with a private server’s database, making it easy to query characters, guilds, and equipment while generating player images dynamically.

---

## Features

- **Character Visualization**
  - Generate character images with equipment via [maplestory.io](https://maplestory.io)
  - Supports skin color, hair, face, and equipped items

- **Rankings**
  - Global top rankings across all jobs
  - Job-specific rankings:
    - Top Thief
    - Top Warrior
    - Top Mage
    - Top Archer
    - Top Pirate
    - Top Aran
  - Ordered by level (highest first)

- **Guild Integration**
  - Lookup and display guild names for characters

- **Job Mapping**
  - Converts job IDs into class names (Thief, Warrior, Mage, etc.)
  - Includes special jobs like Aran, Dawn Warrior, Blaze Wizard, etc.

- **Error Handling**
  - Clean JSON error responses for 404 and 500 cases

---

## Tech Stack

- **Backend:** Python 3, Flask  
- **Database:** MySQL (via mysql-connector)  
- **CORS:** Enabled with Flask-CORS  
- **Visualization:** [MapleStory.io API](https://maplestory.io)  

## Notes

- Built for educational and private server use.
- Requires a valid MapleStory private server database schema (characters, guilds, inventory).
- Extendable for more jobs, events, and custom server features
