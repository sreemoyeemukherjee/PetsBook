import csv
import sqlite3
import user_profile
# def print_table(header, rows):
#     # Print table header
#     header = [column[0] for column in header]
#     print("|".join(header))
#     print("-" * (4 * len(header) - 1))
#
#     # Print table data
#     for row in rows:
#         print("|".join(map(str, row)))

def get_related_content(userid):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # SELECT p.*
    # FROM myapp_post p
    # INNER JOIN myapp_post_favorites pf ON p.id = pf.post_id
    # WHERE pf.user_id = {userid}
    #

    try:
        # Use raw SQL query to retrieve favorite posts
        query = f"""
                        WITH MyFavoritePosts AS (
                            -- Get a list of my favorite posts
                            SELECT post_id
                            FROM myapp_post_favorites
                            WHERE user_id = {userid}
                        ),
                        PeopleWhoFavoritedMyPosts AS (
                            -- Get a list of people who have also marked the same posts as favorite
                            SELECT user_id
                            FROM myapp_post_favorites
                            WHERE post_id IN (SELECT post_id FROM MyFavoritePosts)
                            AND user_id != {userid}
                        ),
                        PostsFavoritedByPeople AS (
                            -- Get a list of posts that people who favorited my posts have marked as favorite
                            SELECT post_id
                            FROM myapp_post_favorites
                            WHERE user_id IN (SELECT user_id FROM PeopleWhoFavoritedMyPosts)
                        ),
                        RelatedContent AS (
                            -- Get related content by removing my favorite posts from the list
                            SELECT post_id
                            FROM PostsFavoritedByPeople
                            WHERE post_id NOT IN (SELECT post_id FROM MyFavoritePosts)
                        )
                        -- Final query to get the related content excluding posts where the user is the author
                        SELECT mp.*
                        FROM myapp_post mp
                        JOIN auth_user au ON mp.username = au.username
                        WHERE mp.id IN (SELECT post_id FROM RelatedContent)
                        AND au.id != {userid};
                    """
        cursor.execute(query)
        favorite_posts = cursor.fetchall()

        if favorite_posts:
            # print(f"Favorite posts for user:")
            # print_table(cursor.description, favorite_posts)
            insert_into_suggestions(userid, favorite_posts)
        # else:
            # print(f"No favorite posts found for user.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()

def get_all_users():
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    try:
        # Use raw SQL query to retrieve favorite posts
        query = f"""
                        SELECT id
                        FROM auth_user
                    """
        cursor.execute(query)
        all_users = [user_id[0] for user_id in cursor.fetchall()]


        if all_users:
            # print_table(cursor.description, all_users)
            return all_users
        else:
            print(f"No users.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()

def create_suggestions_table():
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Drop the suggestions table if it exists
        cursor.execute("DROP TABLE IF EXISTS suggestions")

        # Create a new suggestions table
        cursor.execute("""
            CREATE TABLE suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                post_id INTEGER,
                title TEXT,
                FOREIGN KEY(user_id) REFERENCES auth_user(id),
                FOREIGN KEY(post_id) REFERENCES myapp_post(id)
            );
        """)
        connection.commit()
    except sqlite3.Error as e:
        print(f"Error creating suggestions table: {e}")
    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()

def insert_into_suggestions(user_id, posts):
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Insert the posts into the suggestions table
        data = [(user_id, post[0], post[2]) for post in posts]
        # for post in posts:
        #     q = """ INSERT INTO suggestions(
        #                user_id,
        #                post_id
        #              ) VALUES (
        #                "{0}",
        #                "{1}"
        #                )
        #             """.format(user_id, post[0])
        # print(q)
        query = "INSERT INTO suggestions (user_id, post_id, title) VALUES (?, ?, ?)"
        cursor.executemany(query, data)
        connection.commit()
    except sqlite3.Error as e:
            print(f"Error creating suggestions table: {e}")
    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()

def create_profile_vector(user_id):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    try:
        # Use raw SQL query to retrieve user's favorite posts
        query = f"""-- Get a list of user's favorite posts
                        SELECT title
                        FROM myapp_post_favorites f 
                        JOIN myapp_post p ON f.post_id = p.id
                        WHERE user_id = {user_id}"""
        cursor.execute(query)
        favorite_posts = cursor.fetchall()
        user_profile.create_user_profile_csv(favorite_posts, user_id)
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()
def main():
    # Create suggestions table
    create_suggestions_table()

    all_user_ids = get_all_users()
    for user_id in all_user_ids:
        get_related_content(user_id)
        create_profile_vector(user_id)

if __name__ == "__main__":
    # Connect to SQLite database (replace 'your_database.db' with your actual database file)
    db_path = '../db.sqlite3'
    main()