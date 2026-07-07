import sqlite3

from .config import DATABASE_PATH


class JoinLeaveLogQueries:
	create_config_table = """
CREATE TABLE IF NOT EXISTS join_leave_log_config (
	guild_id TEXT PRIMARY KEY,
	channel_id TEXT NOT NULL
)
"""

	upsert_channel = """
INSERT INTO join_leave_log_config (guild_id, channel_id)
VALUES (?, ?)
ON CONFLICT(guild_id)
DO UPDATE SET channel_id = excluded.channel_id;
"""

	get_channel = """
SELECT channel_id
FROM join_leave_log_config
WHERE guild_id = ?;
"""

	remove_channel = """
DELETE FROM join_leave_log_config
WHERE guild_id = ?;
"""


class JoinLeaveLogDatabase:
	def __init__(self):
		with self.connect_db() as db:
			db.cursor().execute(JoinLeaveLogQueries.create_config_table)
			db.commit()

	def connect_db(self):
		return sqlite3.connect(DATABASE_PATH)

	def set_channel(self, guild_id, channel_id):
		with self.connect_db() as db:
			db.cursor().execute(
				JoinLeaveLogQueries.upsert_channel,
				(str(guild_id), str(channel_id))
			)
			db.commit()

	def get_channel(self, guild_id):
		with self.connect_db() as db:
			result = db.cursor().execute(
				JoinLeaveLogQueries.get_channel,
				(str(guild_id),)
			).fetchone()

		return result[0] if result else None

	def remove_channel(self, guild_id):
		with self.connect_db() as db:
			db.cursor().execute(
				JoinLeaveLogQueries.remove_channel,
				(str(guild_id),)
			)
			db.commit()
