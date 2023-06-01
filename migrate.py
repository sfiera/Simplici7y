import os
import django
from django.conf import settings
from django.utils import timezone
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 's7.settings')
django.setup()

import sqlite3
from items.models import Item, Version, Download, Review, Screenshot, Tag, User
from django.contrib.auth import get_user_model
User = get_user_model()

# Open a connection to your SQLite database
conn = sqlite3.connect('s7.db')

# Initialize a dictionary to track username frequencies
username_counts = {}

# For each table in your SQLite database...
for table, Model in [('users', User),
                     ('items', Item),
                     ('versions', Version),
                     ('downloads', Download),
                     ('reviews', Review),
                     ('screenshots', Screenshot),
                     ('tags', Tag),
                     ]:

    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table}')

    column_names = [column[0] for column in cursor.description]

    for row in cursor.fetchall():
        row_dict = dict(zip(column_names, row))

        if table == 'users':
            # Map the fields
            date_joined_str = row_dict.pop('created_at', None)
            username = row_dict.pop('permalink', None)
            row_dict['is_staff'] = row_dict.pop('admin', None)
            row_dict['first_name'] = row_dict.pop('login', None)

            # If the username has been seen before, append a suffix to it
            count = username_counts.get(username, 0)
            if count > 0:
                username = f"{username}_{count}"
            username_counts[username] = count + 1
            row_dict['username'] = username

            # If date_joined is not None, make it timezone-aware
            if date_joined_str is not None:
                date_joined = datetime.strptime(date_joined_str, '%Y-%m-%d %H:%M:%S')
                row_dict['date_joined'] = timezone.make_aware(date_joined)

            # Remove unnecessary fields
            unnecessary_fields = ['crypted_password', 'salt', 'updated_at', 'remember_token', 'remember_token_expires_at']
            for field in unnecessary_fields:
                row_dict.pop(field, None)

        row_dict = {k: v for k, v in row_dict.items() if not (k.endswith('_count') or k.endswith('_created_at'))}
        print(row_dict)

        instance = Model(**row_dict)
        instance.save()

# Close the SQLite database connection
conn.close()
