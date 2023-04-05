import asyncpg
from asyncpg import Record
from typing import List
from datetime import datetime, timedelta


class Request:

    def __init__(self, connector: asyncpg.pool.Pool):
        self.connector = connector

    async def add_new_user(self, user_id, username, firstname, bot_id, balance=0, referral=None):
        query = f"INSERT INTO usersinfo (user_id, bot_id, username, firstname, balance, referral)" \
                f"VALUES ({user_id}, {bot_id}, '{username}', '{firstname}', {balance}, '{referral}')" \
                f"ON CONFLICT (user_id, bot_id)" \
                f"DO UPDATE SET firstname = excluded.firstname, username = excluded.username"
        await self.connector.execute(query)

    async def get_balance(self, user_id, bot_id):
        query = f'SELECT balance FROM usersinfo WHERE user_id = {user_id} AND bot_id = {bot_id};'
        return await self.connector.fetchval(query)

    async def get_referrals(self, user_id, bot_id):
        query = f"SELECT user_id, username, firstname FROM usersinfo WHERE referral = '{user_id}' AND bot_id = '{bot_id}'"
        result_records: List[Record] = await self.connector.fetch(query)
        output = ''

        for result_record in result_records:
            user_id = result_record.get('user_id')
            user_name = result_record.get('username')
            first_name = result_record.get('firstname')
            output += f'{user_id} {user_name} {first_name}\r\n'

        return output

    async def get_youkassa_token(self, bot_id):
        query = f'SELECT youkassa_token FROM botsinfo WHERE bot_id = {bot_id}'
        return await self.connector.fetchval(query)

    async def refill_balance(self, user_id, bot_id, sum):
        query = f'UPDATE usersinfo SET balance = {sum} + ' \
                f'(SELECT balance from usersinfo WHERE user_id = {user_id} AND bot_id = {bot_id}) '\
                f'WHERE user_id = {user_id} AND bot_id = {bot_id}'
        await self.connector.execute(query)

    async def get_referer(self, user_id, bot_id):
        query = f'SELECT referral FROM usersinfo WHERE user_id = {user_id} AND bot_id = {bot_id}'
        return await self.connector.fetchval(query)

    async def get_percent(self, bot_id):
        query = f'SELECT percent_referrals FROM botsinfo WHERE bot_id = {bot_id}'
        return await self.connector.fetchval(query)

    async def get_admin_id(self, bot_id):
        query = f'SELECT admin_id FROM botsinfo WHERE bot_id = {bot_id}'
        return await self.connector.fetchval(query)

    async def get_game(self, bid, user_id, bot_id):
        query = f'SELECT balance >= {bid} FROM usersinfo WHERE user_id = {user_id} AND bot_id = {bot_id};'
        return await self.connector.fetchval(query)

    async def set_new_bot(self, bot_id, bot_token, admin_id, youkassa_token, payment_date, percent_referrals):
       try:
           query = f"INSERT INTO botsinfo (bot_id, bot_token, admin_id, youkassa_token, payment_date, percent_referrals)" \
                   f"VALUES ({bot_id}, '{bot_token}', {admin_id}, '{youkassa_token}', '{payment_date}', '{percent_referrals}')"
           await self.connector.execute(query)
           return True
       except:
           date_db: datetime = await self.connector.fetchval(
               f"SELECT payment_date From botsinfo WHERE bot_token = '{bot_token}'")
           diff = datetime.now() - date_db

           if diff.days <= 0:
               target_date = (date_db + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
               query = f"UPDATE botsinfo SET payment_date = '{target_date}', youkassa_token = '{youkassa_token}'," \
                       f" percent_referrals = '{percent_referrals}'" \
                       f"WHERE bot_id = {bot_id};"
               await self.connector.execute(query)
               return False
           else:
               target_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
               query = f"UPDATE botsinfo SET payment_date = '{target_date}', youkassa_token = '{youkassa_token}'," \
                       f" percent_referrals = '{percent_referrals}'" \
                       f"WHERE bot_id = {bot_id};"
               await self.connector.execute(query)
               return True


